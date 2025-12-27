from flask import Blueprint, request, jsonify
from sqlalchemy import func
from ..models.models import db, Location, Category, Review, Tag, review_tags, WikiSuggestion, LocationView, User
from .auth import token_required, wiki_editor_required 
# --- 新增：导入 datetime ---
import datetime
# --- 新增：导入 logging ---
import logging

# --- 新增：配置日志记录器 ---
log = logging.getLogger(__name__)

location_bp = Blueprint('location_api', __name__, url_prefix='/api/location')

# --- 核心重构：替换 create_location_wiki 函数 ---
@location_bp.route('/wiki', methods=['POST'])
@wiki_editor_required
def create_location_wiki(current_user, is_admin=False):
    """
    创建新的地点 Wiki，严格遵循前端 API 文档。
    - 只有 Wiki 管理员可以创建。
    - 自动处理 category 名称到 ID 的转换（找不到则创建）。
    - 成功后返回包含 id 和 name 的 JSON 对象。
    """
    data = request.get_json()
    if not data:
        return jsonify({"message": "Request body cannot be empty"}), 400

    # 1. 权限检查：只有 Wiki 管理员/Admin 才能创建
    if not is_admin:
        return jsonify({"message": "权限不足，只有 Wiki 管理员可以创建"}), 403

    # 2. 验证必要字段
    if not data.get('name'):
        return jsonify({"message": "地点名称(name)是必填项"}), 400

    # 3. 创建新地点实例
    new_location = Location(
        name=data.get('name'),
        address=data.get('address'),
        main_image=data.get('mainImage'),
        rich_content=data.get('richContent'),
        structured_info=data.get('structuredInfo'),
        status='published' # 新创建的 Wiki 直接设为已发布状态
    )

    # 4. 特殊处理：根据 category 名称查找或创建分类
    category_name = data.get('category')
    if category_name:
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            # 如果分类不存在，则自动创建
            category = Category(name=category_name)
            db.session.add(category)
            db.session.flush()  # 立即执行插入以获取新分类的 ID
        
        new_location.category_id = category.id

    # 5. 保存到数据库
    try:
        db.session.add(new_location)
        db.session.commit()
        
        # 6. 返回前端期望的格式
        return jsonify({
            "id": new_location.id, 
            "name": new_location.name
        }), 201
    except Exception as e:
        db.session.rollback()
        log.error(f"[Wiki创建] 数据库错误: {str(e)}")
        return jsonify({"message": f"数据库错误: {str(e)}"}), 500

@location_bp.route('/<int:location_id>/wiki', methods=['GET'])
@token_required(optional=True) # <-- 核心修改：应用可选认证
def get_location_wiki(current_user, location_id): # <-- 核心修改：添加 current_user 参数
    loc = Location.query.get_or_404(location_id)
    
    # --- 核心修复：直接从 Review 模型构建查询，而不是在列表上调用 .subquery() ---
    reviews_query = Review.query.filter(Review.location_id == location_id)

    # --- 核心修改：添加地点浏览日志记录 ---
    try:
        view_log = LocationView(
            location_id=loc.id,
            # --- 核心修改：记录浏览用户的ID ---
            user_id=current_user.id if current_user else None
        )
        db.session.add(view_log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error logging location view: {e}") # 记录错误，但不影响主流程

    # 计算评分分布
    rating_dist = db.session.query(
        Review.rating, 
        func.count(Review.id)
    ).filter(Review.location_id == location_id).group_by(Review.rating).all()
    
    # 计算平均分和总数
    stats = db.session.query(
        func.avg(Review.rating),
        func.count(Review.id)
    ).filter(Review.location_id == location_id).first()

    average_rating = stats[0] or 0
    reviews_count = stats[1] or 0

    # 聚合数据
    rating_info = {
        "average": float(round(average_rating, 1)), # 确保是 float 类型
        "count": int(reviews_count), # 确保是 int 类型
        "distribution": [{"stars": r, "count": c} for r, c in rating_dist]
    }

    # 构造 categoryPath
    category_path = []
    cat = loc.category
    while cat:
        category_path.insert(0, {"name": cat.name})
        cat = cat.parent
    
    # 获取 buildingId：优先使用 building_id，其次从 structured_info 获取，最后 fallback 到 wiki_id
    building_id = loc.building_id
    if building_id is None and loc.structured_info:
        building_id = loc.structured_info.get('building_id')
    if building_id is None:
        building_id = loc.id  # 最后 fallback 到 wiki_id

    # --- 核心修复：安全地获取 tag 的 color 属性 ---
    tags_list = []
    for t in loc.tags:
        # 使用 getattr 安全地获取 color，如果不存在则提供一个默认值
        tag_color = getattr(t, 'color', '#808080') # 默认灰色
        tags_list.append({"id": t.id, "name": t.name, "color": tag_color})

    return jsonify({
        "id": loc.id,
        "buildingId": building_id,  # 添加 buildingId 字段
        "name": loc.name,
        "address": loc.address,
        "mainImage": loc.main_image,
        "category": loc.category.name if loc.category else None,
        "categoryPath": category_path,
        "richContent": loc.rich_content,
        "structuredInfo": loc.structured_info,
        "rating": rating_info,
        "tags": tags_list,
        "latitude": loc.latitude,
        "longitude": loc.longitude,
        "canEdit": True # 此处应加入真实权限判断逻辑
    })

# --- ✅ 问题 2 修复：使用新逻辑完整替换 update_location_wiki 函数 ---
# --- 新增：根据前端指南，实现 Wiki 编辑保存接口 ---
# --- 核心修复：修改函数签名以接收 is_admin 参数 ---
@location_bp.route('/<int:location_id>/wiki', methods=['PUT'])
@wiki_editor_required
def update_location_wiki(current_admin, location_id, is_admin=False):
    """
    更新地点 Wiki 信息。
    严格遵循 "Wiki编辑保存功能-后端检查指南.md" 文档。
    """
    # 1. 权限检查
    if current_admin.role not in ['admin', 'wiki_admin']:
        return jsonify({
            'success': False,
            'message': '权限不足，只有 Wiki 管理员或超级管理员可以编辑'
        }), 403

    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求体不能为空'}), 400

        # 2. 验证必填字段
        required_fields = ['name', 'address', 'richContent', 'latitude', 'longitude']
        for field in required_fields:
            if data.get(field) is None: # 必须检查 None，因为 0 是有效值
                return jsonify({
                    'success': False,
                    'message': f'缺少必填字段: {field}'
                }), 400
        
        # 2.1 验证经纬度
        try:
            latitude = float(data.get('latitude'))
            longitude = float(data.get('longitude'))
            if not (-90 <= latitude <= 90):
                return jsonify({'success': False, 'message': '纬度必须在 -90 到 90 之间'}), 400
            if not (-180 <= longitude <= 180):
                return jsonify({'success': False, 'message': '经度必须在 -180 到 180 之间'}), 400
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': '经纬度必须是有效的数字'}), 400

        # 3. 获取并验证地点是否存在
        location = Location.query.get(location_id)
        if not location:
            return jsonify({'success': False, 'message': '地点不存在'}), 404

        # 4. 更新数据库字段 (处理 camelCase 到 snake_case 的映射)
        location.name = data.get('name')
        location.address = data.get('address')
        location.latitude = latitude
        location.longitude = longitude
        location.main_image = data.get('mainImage')
        location.rich_content = data.get('richContent')
        
        # 处理 category (如果提供了)
        category_name = data.get('category')
        if category_name:
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                category = Category(name=category_name)
                db.session.add(category)
            location.category = category

        # 更新结构化信息 (映射到独立字段)
        structured_info = data.get('structuredInfo', {})
        if isinstance(structured_info, dict):
            location.open_time = structured_info.get('openTime')
            location.average_cost = structured_info.get('averageCost')
            location.phone = structured_info.get('phone')
            location.website = structured_info.get('website')
            # 同时保留原始 JSON 对象
            location.structured_info = structured_info

        # 更新修改时间
        location.updated_at = datetime.datetime.utcnow()

        # 5. 提交到数据库
        db.session.commit()

        # 6. 返回成功响应
        # 假设 Location 模型有 to_dict 方法，如果没有，需要手动构建
        response_data = location.to_dict() if hasattr(location, 'to_dict') else {"id": location.id, "name": location.name}
        
        return jsonify({
            'success': True,
            'message': '保存成功',
            'data': response_data
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'保存失败: {str(e)}'
        }), 500

@location_bp.route('/wiki-list', methods=['GET'])
def get_wiki_list():
    keyword = request.args.get('keyword')
    tag_name = request.args.get('tag')
    
    query = Location.query
    if keyword:
        query = query.filter(Location.name.ilike(f'%{keyword}%'))
    if tag_name:
        query = query.join(Location.tags).filter(Tag.name == tag_name)
        
    locations = query.all()
    
    items = [{
        # 直接从模型字段读取 building_id，如果为空则默认使用 wiki_id
        "buildingId": loc.building_id if loc.building_id is not None else loc.id,
        "wikiId": loc.id,
        "name": loc.name,
        "description": (loc.rich_content or '')[:100],
        "imageUrl": loc.main_image,
        "address": loc.address,
        "tags": [t.name for t in loc.tags]
    } for loc in locations]
    
    return jsonify({"items": items})

# --- 核心重构：用一个统一的函数替换所有旧的 wiki suggestion 路由 ---
@location_bp.route('/wiki/suggestion', methods=['POST'])
@token_required(optional=True) # 认证可选，支持匿名建议
def submit_wiki_suggestion(current_user=None):
    """
    统一处理通用建议和针对具体地点的建议。
    严格遵循 WIKI_SUGGESTION_API.md 文档规范。
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的请求', 'message': '请求体不能为空'}), 400

        # 1. 获取并验证字段
        content = data.get('content', '').strip()
        suggestion_type = data.get('type')
        location_id = data.get('locationId') # 前端使用 locationId

        if not content or len(content) < 10:
            return jsonify({'error': '无效的请求', 'message': '建议内容至少需要 10 个字符'}), 400
        
        if suggestion_type not in ['general', 'location']:
            return jsonify({'error': '无效的请求', 'message': 'type 必须是 "general" 或 "location"'}), 400

        # 2. 如果是针对地点的建议，验证 location_id
        if suggestion_type == 'location':
            if not location_id:
                return jsonify({'error': '无效的请求', 'message': '当 type 为 "location" 时，locationId 不能为空'}), 400
            # 验证地点是否存在
            if not Location.query.get(location_id):
                return jsonify({'error': '无效的请求', 'message': f'ID 为 {location_id} 的地点不存在'}), 404
        else:
            location_id = None # 确保通用建议的 location_id 为空

        # 3. 获取用户 ID (如果已登录)
        user_id = current_user.id if current_user else None

        # 4. 创建并保存建议到数据库
        suggestion = WikiSuggestion(
            content=content,
            type=suggestion_type,
            location_id=location_id,
            user_id=user_id,
            status='pending'
        )
        db.session.add(suggestion)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '建议已提交'
        }), 201

    except Exception as e:
        db.session.rollback()
        log.error(f"[Wiki建议] 提交失败: {str(e)}")
        return jsonify({
            'error': '提交失败',
            'message': str(e)
        }), 500
    
# --- 新增：获取热门标签 ---
@location_bp.route('/<int:location_id>/tags/popular', methods=['GET'])
def get_popular_tags(location_id):
    """
    获取某个地点的热门标签
    """
    limit = request.args.get('limit', 20, type=int)
    
    # 统计该地点评论中的标签使用次数
    tag_counts = db.session.query(
        Tag.name,
        db.func.count(review_tags.c.review_id).label('count')
    ).join(
        review_tags, Tag.id == review_tags.c.tag_id
    ).join(
        Review, Review.id == review_tags.c.review_id
    ).filter(
        Review.location_id == location_id
    ).group_by(
        Tag.name
    ).order_by(
        db.desc('count')
    ).limit(limit).all()
    
    tags = [{"name": name, "count": count} for name, count in tag_counts]
    
    return jsonify({"tags": tags})

# --- 新增：根据 MAP_BUILDINGS_API.md 文档，实现地图建筑数据接口 ---
@location_bp.route('/map-buildings', methods=['GET'])
def get_map_buildings():
    """
    获取所有已发布的、带有地理位置信息的建筑，用于地图展示。
    严格遵循 MAP_BUILDINGS_API.md 文档规范。
    """
    try:
        # 1. 查询所有已发布的、且包含有效经纬度的地点
        #    - 使用 dedicated latitude/longitude 字段进行高效查询
        #    - 预加载 category 关系以避免 N+1 查询
        locations = Location.query.options(
            db.joinedload(Location.category)
        ).filter(
            Location.status == 'published',
            Location.latitude.isnot(None),
            Location.longitude.isnot(None)
        ).all()
        
        buildings = []
        for loc in locations:
            # 2. 安全地从 structured_info 获取附加信息
            structured_info = loc.structured_info or {}
            
            # 3. 按照文档格式构建每个建筑的数据
            building_data = {
                'id': loc.building_id or loc.id,
                'name': loc.name,
                'type': loc.category.name if loc.category else '其他',
                'position': [loc.longitude, loc.latitude], # 格式: [经度, 纬度]
                'description': (loc.rich_content or loc.address or '')[:100], # 简短描述
                'openTime': structured_info.get('openTime', ''),
                'address': loc.address or '',
                'phone': structured_info.get('phone', ''),
                'facilities': structured_info.get('facilities', []),
                'mainImage': loc.main_image,
                'wikiId': loc.id,
            }
            buildings.append(building_data)
        
        # 4. 返回最终的 JSON 响应
        return jsonify({
            'buildings': buildings,
            'total': len(buildings)
        })

    except Exception as e:
        log.error(f"[地图建筑数据] 获取失败: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500
    