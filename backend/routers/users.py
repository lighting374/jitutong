from flask import Blueprint, request, jsonify, current_app
from ..models.models import db, User, Favorite, History, Message, Review, Location, UserLog, UserLoginLog, ReviewReply
# 导入真实的认证模块
from .auth import create_token, token_required
import datetime
# --- 新增：导入缺失的模块 ---
import os
from werkzeug.utils import secure_filename
from datetime import timezone

user_bp = Blueprint('user_api', __name__, url_prefix='/api/user')

# --- 新增：日志记录辅助函数 ---
def log_user_action(user, action, detail=None):
    """记录用户操作日志的辅助函数"""
    try:
        log = UserLog(
            user_id=user.id,
            action=action,
            detail=str(detail) if detail else None,
            ip=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(log)
        # 注意：这里不 commit，由调用它的主函数统一 commit
    except Exception as e:
        # 即使日志记录失败，也不应中断主流程
        print(f"Error logging user action: {e}")

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    phone = data.get('phone')
    password = data.get('password')
    if not phone or not password:
        return jsonify({"message": "Phone and password are required"}), 400
    if User.query.filter_by(phone=phone).first():
        return jsonify({"message": "Phone number already registered"}), 409
    
    new_user = User(phone=phone, nickname=data.get('nickname') or f'user_{phone[-4:]}')
    new_user.set_password(password)
    db.session.add(new_user)
    # --- 核心修复：在这里刷入会话以获取 new_user.id ---
    db.session.flush()
    log_user_action(new_user, 'REGISTER')
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(phone=data.get('phone')).first()
    if user and user.check_password(data.get('password')):
        # 使用 auth.py 中的函数生成 JWT 和过期时间
        token, expires_in = create_token(user.id)
        if user.status != 'banned': 
            log_user_action(user, 'LOGIN')
            db.session.commit() # 登录也需要 commit 日志
            # --- 核心修改：添加登录日志记录 ---
            try:
                login_log = UserLoginLog(
                    user_id=user.id,
                    ip_address=request.remote_addr
                )
                db.session.add(login_log)
                # 更新用户的最后登录时间
                user.last_login = datetime.datetime.utcnow()
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error logging user login: {e}") # 记录错误，但不影响登录流程

        return jsonify({
            "token": token,
            "expiresIn": expires_in,
            "user": {
                "id": user.id,
                "nickname": user.nickname,
                "avatar": user.avatar_url,
                "status": user.status
            }
        })
    log_user_action(user, 'LOGIN_FAILED')
    db.session.commit() # 登录也需要 commit 日志
    return jsonify({"message": "Invalid credentials"}), 401

@user_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify({
        "id": current_user.id,
        "phone": current_user.phone,
        "nickname": current_user.nickname,
        "avatar_url": current_user.avatar_url,
        "bio": current_user.bio
    })

# --- 更新：文件上传配置 ---
# 子目录，相对于 app.config['UPLOAD_FOLDER']
AVATAR_SUBFOLDER = 'avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

# --- 新增：定义 allowed_file 函数 ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@user_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """
    更新用户资料，支持头像上传 (multipart/form-data) 和纯文本更新 (json)
    """
    avatar_url = current_user.avatar_url
    
    # 1. 检查是否有文件上传 (multipart/form-data)
    if 'avatar' in request.files:
        file = request.files['avatar']
        
        # 验证文件
        if file.filename == '':
            return jsonify({'success': False, 'message': '未选择文件'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': '只支持图片格式（jpg, png, gif, webp）'}), 415
        
        # 检查文件大小 (通过读取内容长度)
        if len(file.read()) > MAX_FILE_SIZE:
            return jsonify({'success': False, 'message': '文件大小不能超过 2MB'}), 413
        file.seek(0) # 重置文件指针
        
        # 生成唯一文件名
        timestamp = int(datetime.datetime.now().timestamp())
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = secure_filename(f"user{current_user.id}_{timestamp}.{ext}")
        
        # 确保上传目录存在
        # 使用 current_app 获取全局配置
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], AVATAR_SUBFOLDER)
        os.makedirs(upload_path, exist_ok=True)
        filepath = os.path.join(upload_path, filename)
        
        # 删除旧头像
        if current_user.avatar_url:
            # 从 URL 转换为本地文件系统路径
            # URL 示例: /uploads/avatars/user1_123.jpg
            # app.static_folder 是 'backend/backend/static'
            old_file_path = os.path.join(current_app.static_folder, current_user.avatar_url.lstrip('/'))
            if os.path.exists(old_file_path):
                try:
                    os.remove(old_file_path)
                except OSError as e:
                    print(f"Error deleting old avatar: {e}")

        # 保存新文件
        file.save(filepath)
        
        # 更新数据库的头像 URL (使用相对路径)
        avatar_url = f"/uploads/{AVATAR_SUBFOLDER}/{filename}".replace('\\', '/')
     
        # 获取其他表单字段
        nickname = request.form.get('nickname', current_user.nickname)
        bio = request.form.get('bio', current_user.bio)
    
    else:
        # 2. 没有文件上传，处理 JSON 数据
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求体不能为空'}), 400
        nickname = data.get('nickname', current_user.nickname)
        bio = data.get('bio', current_user.bio)
    
    # 3. 验证昵称
    if not (2 <= len(nickname) <= 16):
        return jsonify({'success': False, 'message': '昵称长度必须在 2 到 16 个字符之间'}), 400
    
    # 4. 更新数据库
    current_user.nickname = nickname
    current_user.bio = bio
    current_user.avatar_url = avatar_url
    # --- 添加日志 ---
    log_user_action(current_user, 'UPDATE_PROFILE', detail=f"Avatar: {avatar_url}, Nickname: {nickname}, Bio: {(bio[:20] if bio else 'None')}")
    db.session.commit()
    
    # 5. 返回更新后的用户信息
    # 构造完整的头像 URL
    full_avatar_url = None
    if avatar_url:
        # Flask 的静态文件服务会自动处理，直接返回相对 URL 即可
        full_avatar_url = avatar_url

    return jsonify({
        'success': True,
        'message': '资料更新成功',
        'user': {
            'id': current_user.id,
            'phone': current_user.phone,
            'nickname': current_user.nickname,
            'bio': current_user.bio,
            'avatar': full_avatar_url, # 返回相对 URL
            'status': current_user.status,
            'createdAt': current_user.created_at.isoformat() + 'Z'
        }
    }), 200

# --- 收藏夹 Favorites ---
@user_bp.route('/favorites', methods=['GET'])
@token_required
def get_favorites(current_user):
    favorites = current_user.favorites
    items = []
    
    for fav in favorites:
        # 通过收藏记录中的 wiki_id 查询完整的 location 信息
        location = Location.query.get(fav.wiki_id)
        if location:
            items.append({
                'buildingId': fav.building_id,
                'wikiId': fav.wiki_id,
                'name': location.name,
                'description': location.address, # 使用地址作为描述
                'imageUrl': location.main_image,
                'type': location.structured_info.get('type', '') if location.structured_info else ''
            })
            
    return jsonify({"items": items})

@user_bp.route('/favorites', methods=['POST'])
@token_required
def add_favorite(current_user):
    data = request.get_json()
    building_id = data.get('buildingId')
    wiki_id = data.get('wikiId')

    # --- 核心修复：确保两个 ID 都存在且不为 None ---
    if building_id is None and wiki_id is None:
        return jsonify({"message": "Both buildingId and wikiId are required"}), 400
    
    # 防止重复收藏
    existing = Favorite.query.filter_by(user_id=current_user.id, wiki_id=wiki_id).first()
    if not existing:
        fav = Favorite(user_id=current_user.id, building_id=building_id, wiki_id=wiki_id)
        db.session.add(fav)
        # --- 添加日志 ---
        log_user_action(current_user, 'ADD_FAVORITE', detail={"building_id": building_id})
        db.session.commit()
        return jsonify({"message": "Favorite added"}), 201
    else:
        return jsonify({"message": "Already in favorites"}), 200 # 或者返回 200 OK

@user_bp.route('/favorites', methods=['DELETE']) # 移除了路径中的 <int:building_id>
@token_required
def remove_favorite(current_user): # 移除了函数参数中的 building_id
    # 从查询参数中获取 building_id
    building_id = request.args.get('buildingId', type=int)
    
    if not building_id:
        return jsonify({"message": "buildingId is required"}), 400

    fav = Favorite.query.filter_by(user_id=current_user.id, building_id=building_id).first()
    if fav:
        db.session.delete(fav)
        # --- 添加日志 ---
        log_user_action(current_user, 'REMOVE_FAVORITE', detail={"building_id": building_id})
        db.session.commit()
        return jsonify({"message": "Favorite removed"}), 200
    
    # 即使找不到也返回成功，因为最终状态是“未收藏”
    return jsonify({"message": "Favorite not found"}), 200


@user_bp.route('/favorites/status', methods=['GET'])
@token_required
def get_favorite_status(current_user):
    building_id = request.args.get('buildingId')
    wiki_id = request.args.get('wikiId')
    
    query = Favorite.query.filter_by(user_id=current_user.id)
    if building_id:
        query = query.filter_by(building_id=building_id)
    elif wiki_id:
        query = query.filter_by(wiki_id=wiki_id)
    else:
        return jsonify({"favorited": False})

    is_favorited = query.first() is not None
    return jsonify({"favorited": is_favorited})

# --- 浏览历史 History ---
@user_bp.route('/history', methods=['GET'])
@token_required
def get_browsing_history(current_user):
    history_items = History.query.filter_by(user_id=current_user.id).order_by(History.last_visited.desc()).limit(50).all()
    items = [
        {
            "id": h.id,
            "buildingId": h.building_id,
            "wikiId": h.wiki_id,
            "name": h.name,
            "lastVisited": h.last_visited.isoformat() + 'Z',
            "imageUrl": h.image_url
        } for h in history_items
    ]
    return jsonify({"items": items})

@user_bp.route('/history', methods=['POST'])
@token_required
def add_browsing_history(current_user):
    data = request.get_json()
    # 查找是否已有记录，如果有则更新时间，没有则创建
    history_item = History.query.filter_by(user_id=current_user.id, building_id=data.get('buildingId')).first()
    if history_item:
        history_item.last_visited = datetime.datetime.utcnow()
    else:
        history_item = History(
            user_id=current_user.id,
            building_id=data.get('buildingId'),
            wiki_id=data.get('wikiId'),
            name=data.get('name'),
            image_url=data.get('imageUrl'),
            address=data.get('address')
        )
        db.session.add(history_item)
    log_user_action(current_user, 'ADD_HISTORY', detail={"building_id": data.get('buildingId')})
    db.session.commit()
    return jsonify({"message": "History added"}), 201

@user_bp.route('/history', methods=['DELETE'])
@token_required
def clear_history(current_user):
    History.query.filter_by(user_id=current_user.id).delete()
    log_user_action(current_user, 'CLEAR_HISTORY')
    db.session.commit()
    return "", 204

# --- 消息通知 Messages (已根据文档重构) ---

@user_bp.route('/messages', methods=['GET'])
@token_required
def get_user_messages(current_user):
    """获取当前用户的消息列表，支持按类型和已读状态筛选"""
    message_type = request.args.get('type')
    unread_only = request.args.get('unread') == 'true'
    
    query = Message.query.filter_by(user_id=current_user.id)
    
    if message_type:
        query = query.filter_by(type=message_type)
    
    if unread_only:
        query = query.filter_by(is_read=False)
        
    messages = query.order_by(Message.created_at.desc()).all()
    
    message_list = [{
        "id": m.id,
        "type": m.type,
        "content": m.content,
        "relatedComment": m.related_comment,
        "linkUrl": m.link,
        "isRead": m.is_read,
        "createdAt": m.created_at.isoformat() + 'Z'
    } for m in messages]
    
    unread_count = Message.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    return jsonify({
        "messages": message_list,
        "unreadCount": unread_count
    })

@user_bp.route('/messages/<int:message_id>/read', methods=['PUT'])
@token_required
def mark_message_read(current_user, message_id):
    """将单条消息标记为已读"""
    msg = Message.query.filter_by(id=message_id, user_id=current_user.id).first()
    if not msg:
        return jsonify({"message": "消息不存在"}), 404
    
    if not msg.is_read:
        msg.is_read = True
        log_user_action(current_user, 'MARK_MESSAGE_READ', detail={"message_id": message_id})
        db.session.commit()
        
    return jsonify({"success": True, "message": "已标记为已读"})

@user_bp.route('/messages/<int:message_id>', methods=['DELETE'])
@token_required
def delete_message(current_user, message_id):
    """删除单条消息"""
    msg = Message.query.filter_by(id=message_id, user_id=current_user.id).first()
    if msg:
        db.session.delete(msg)
        log_user_action(current_user, 'DELETE_MESSAGE', detail={"message_id": message_id})
        db.session.commit()
    return jsonify({"success": True, "message": "消息已删除"})

@user_bp.route('/messages/read-all', methods=['PUT'])
@token_required
def mark_all_messages_read(current_user):
    """将所有未读消息标记为已读"""
    updated_count = Message.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    log_user_action(current_user, 'MARK_ALL_MESSAGES_READ', detail={"count": updated_count})
    db.session.commit()
    return jsonify({"success": True, "message": "已全部标记为已读", "count": updated_count})

@user_bp.route('/messages/clear', methods=['DELETE'])
@token_required
def clear_all_messages(current_user):
    """清空当前用户的所有消息"""
    deleted_count = Message.query.filter_by(user_id=current_user.id).delete()
    log_user_action(current_user, 'CLEAR_ALL_MESSAGES', detail={"count": deleted_count})
    db.session.commit()
    return jsonify({"success": True, "message": "已清空所有消息", "count": deleted_count})

@user_bp.route('/messages/unread-count', methods=['GET'])
@token_required
def get_unread_count(current_user):
    """获取未读消息数量"""
    count = Message.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({"count": count})


# # --- 我的评论 My Reviews ---
# @user_bp.route('/my-comments', methods=['GET'])
# @token_required
# def get_my_reviews(current_user):
#     reviews = Review.query.filter_by(user_id=current_user.id).order_by(Review.created_at.desc()).all()
#     items = []
#     for r in reviews:
#         items.append({
#             "id": r.id,
#             "locationId": r.location_id,
#             # --- 核心修复：通过 r.location 关系获取地点名称 ---
#             "locationName": r.location.name if r.location else "未知地点",
#             "rating": r.rating,
#             "comment": r.comment,
#             "createdAt": r.created_at.isoformat() + 'Z'
#         })
#     return jsonify({"items": items})

# --- 新增：获取用户所有评论和回复的接口 ---
@user_bp.route('/my-comments', methods=['GET'])
@token_required
def get_my_reviews(current_user):
    """
    获取当前用户发布的所有顶级评论和回复。
    """
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)

    # 1. 获取用户的顶级评论
    top_level_reviews = Review.query.filter_by(user_id=current_user.id).all()
    
    # 2. 获取用户的回复
    replies = ReviewReply.query.filter_by(user_id=current_user.id).all()

    # 3. 格式化并合并两种评论
    all_my_comments = []
    # 处理顶级评论
    for review in top_level_reviews:
        all_my_comments.append({
            "id": review.id,
            "type": "review", # 内部使用的类型
            "wikiId": review.location_id, # 假设 Location 模型有关联到 Wiki
            "locationId": review.location_id,
            "locationName": review.location.name,
            "rating": review.rating,
            "comment": review.comment,
            "createdAt": review.created_at.replace(tzinfo=timezone.utc).isoformat(),
            "parentId": None,
            "parentUserName": None,
            "parentComment": None
        })
    # 处理回复
    for reply in replies:
        parent_review = reply.review # 获取被回复的顶级评论
        all_my_comments.append({
            "id": reply.id,
            "type": "reply", # 内部使用的类型
            "wikiId": parent_review.location_id,
            "locationId": parent_review.location_id,
            "locationName": parent_review.location.name,
            "rating": None, # 回复没有评分
            "comment": reply.content,
            "createdAt": reply.created_at.replace(tzinfo=timezone.utc).isoformat(),
            "parentId": parent_review.id,
            "parentUserName": parent_review.author.nickname,
            "parentComment": parent_review.comment
        })

    # 4. 按创建时间降序排序
    all_my_comments.sort(key=lambda x: x['createdAt'], reverse=True)

    # 5. 手动分页
    total_items = len(all_my_comments)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_items = all_my_comments[start:end]

    # 移除内部使用的 'type' 字段
    for item in paginated_items:
        del item['type']

    return jsonify({
        "items": paginated_items,
        "total": total_items,
        "page": page,
        "pageSize": page_size,
        "pages": (total_items + page_size - 1) // page_size
    }), 200
