from flask import Blueprint, jsonify, request # --- 新增导入 request ---
from sqlalchemy import func
from datetime import datetime, timedelta
from collections import Counter

from ..models.models import db, SearchLog, Location, User # --- 新增导入 User ---
from .auth import token_required # --- 新增导入 token_required ---

search_bp = Blueprint('search_api', __name__, url_prefix='/api/search')

# --- 新增：热门搜索词路由 ---
@search_bp.route('/hot', methods=['GET'])
def get_hot_searches():
    """
    获取热门搜索词。
    统计最近7天内搜索日志中出现频率最高的关键词。
    """
    try:
        # 1. 定义时间范围：最近7天
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        # 2. 从数据库查询最近7天的搜索关键词列表
        #    使用 with_entities 只选择 keyword 列，提高效率
        recent_searches = db.session.query(SearchLog.keyword).filter(
            SearchLog.created_at >= seven_days_ago
        ).all()
        
        # 如果没有搜索记录，可以返回一组预设的默认值或空列表
        if not recent_searches:
            default_keywords = ['图书馆', '食堂', '体育馆', '教学楼', '宿舍']
            return jsonify({"keywords": default_keywords})

        # 3. 清洗和统计关键词频率
        #    - log[0] 是因为查询结果是元组 (keyword,)
        #    - 过滤掉空字符串和过短的词
        keywords = [
            log[0].strip() for log in recent_searches 
            if log[0] and len(log[0].strip()) > 1
        ]
        keyword_counts = Counter(keywords)
        
        # 4. 获取频率最高的10个关键词
        hot_keywords = [keyword for keyword, count in keyword_counts.most_common(10)]
        
        return jsonify({"keywords": hot_keywords})
        
    except Exception as e:
        # 记录错误日志
        print(f"Error fetching hot searches: {e}")
        return jsonify({
            "error": "获取热门搜索词失败",
            "message": str(e)
        }), 500

# --- 主搜索接口 (重构：移除日志记录逻辑) ---
@search_bp.route('', methods=['GET'])
def search_locations():
    """
    根据关键词搜索地点。
    这个接口现在只负责搜索，不再记录日志。
    """
    keyword = request.args.get('q', '').strip()

    if not keyword:
        return jsonify({"message": "搜索关键词不能为空"}), 400

    # --- 执行搜索查询 ---
    results = Location.query.filter(
        db.or_(
            Location.name.ilike(f'%{keyword}%'),
            Location.address.ilike(f'%{keyword}%')
        )
    ).limit(20).all()

    # 格式化返回结果
    items = [{
        "id": loc.id,
        "name": loc.name,
        "address": loc.address,
        "mainImage": loc.main_image
    } for loc in results]

    return jsonify({"items": items})

# --- 新增：记录搜索行为的路由 ---
@search_bp.route('/record', methods=['POST'])
@token_required(optional=True) # 使用 optional=True 允许匿名和登录用户
def record_search(current_user=None):
    """
    记录用户的搜索行为。
    - 接收 JSON 请求体: {"keyword": "..."}
    - 如果用户已登录 (提供了 token)，则记录 user_id。
    """
    data = request.get_json()
    if not data or 'keyword' not in data:
        return jsonify({"error": "无效的请求", "message": "keyword 字段不能为空"}), 400
    
    keyword = data.get('keyword', '').strip()
    if not keyword:
        return jsonify({"error": "无效的请求", "message": "keyword 字段不能为空"}), 400

    user_id = current_user.id if current_user else None

    try:
        search_log = SearchLog(keyword=keyword, user_id=user_id)
        db.session.add(search_log)
        db.session.commit()
        
        return jsonify({"success": True, "message": "搜索记录已保存"}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error saving search log: {e}")
        return jsonify({"error": "记录搜索失败", "message": str(e)}), 500
    