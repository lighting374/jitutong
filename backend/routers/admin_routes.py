from flask import Blueprint, request, jsonify, current_app # <-- 新增导入 current_app
from sqlalchemy import or_, func, distinct
from ..models.models import (
    db, User, Location, Review, WikiSuggestion, Admin, ActionLog, 
    SystemSetting, ReviewReport, Category,
    # --- 新增导入 ---
    UserLoginLog, LocationView, SearchLog, UserLog, Tag
)
from sqlalchemy.exc import IntegrityError # <-- 新增导入
from werkzeug.utils import secure_filename # <-- 新增导入
import os # <-- 新增导入
import csv # <-- 新增导入
import io  # <-- 新增导入
from .auth import admin_required, create_admin_token, wiki_editor_required
import datetime
import jwt
import json
admin_bp = Blueprint('admin_api', __name__, url_prefix='/api/admin')

def create_admin_token(admin):
    """为管理员创建JWT (已根据前端要求更新)"""
    # 设置过期时间为24小时
    expires_delta = datetime.timedelta(days=1)
    expires_in_seconds = int(expires_delta.total_seconds())
    
    payload = {
        'exp': datetime.datetime.utcnow() + expires_delta,
        'iat': datetime.datetime.utcnow(),
        'sub': str(admin.id),          # 管理员 ID
        'type': 'admin',          # 令牌类型，必须为 'admin'
        'role': admin.role        # 管理员角色
    }
    token = jwt.encode(
        payload,
        current_app.config.get('SECRET_KEY'),
        algorithm='HS256'
    )
    # 返回令牌和过期秒数
    return token, expires_in_seconds

# --- 登录和信息 (已更新) ---
@admin_bp.route('/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    admin = Admin.query.filter_by(username=data.get('username')).first()
    if admin and admin.check_password(data.get('password')):
        admin.last_login = datetime.datetime.utcnow()
        db.session.commit()
        
        # 接收令牌和过期时间 (传入整个 admin 对象)
        token, expires_in = create_admin_token(admin)
        
        # 构建新的响应格式
        return jsonify({
            "token": token,
            "user": {
                "id": str(admin.id),
                "username": admin.username,
                "role": admin.role
            },
            "expiresIn": expires_in
        })
    return jsonify({"message": "Invalid admin credentials"}), 401

@admin_bp.route('/info', methods=['GET'])
@admin_required
def get_admin_info(current_admin):
    """获取当前登录的管理员信息 (已更新，关联用户昵称和头像)"""
    # 根据 admins.username (手机号) 查找对应的 users 表记录
    user = User.query.filter_by(phone=current_admin.username).first()
    
    return jsonify({
        "id": current_admin.id,
        "username": current_admin.username,  # 登录账号（手机号）
        "nickname": user.nickname if user else current_admin.username,  # 新增：用户昵称，若无则返回用户名
        "avatar": user.avatar_url if user else None,  # 新增：用户头像
        "role": current_admin.role,
        "lastLogin": current_admin.last_login.isoformat() + 'Z' if current_admin.last_login else None
    })

@admin_bp.route('/stats', methods=['GET'])
@admin_required
def get_stats(current_admin):
    user_count = User.query.count()
    active_count = User.query.filter_by(status='active').count()
    banned_count = User.query.filter_by(status='banned').count()
    return jsonify({
        "totalUsers": user_count,
        "activeUsers": active_count,
        "bannedUsers": banned_count,
        "totalLocations": Location.query.count(),
        "pendingReviews": Review.query.filter_by(status='pending').count()
    })

# --- 新增：头像上传配置 (根据文档) ---
AVATAR_UPLOAD_FOLDER = 'static/uploads/avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- 账号管理 (已更新) ---
@admin_bp.route('/account/list', methods=['GET'])
@admin_required
def get_accounts_list(current_admin):
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    q = request.args.get('q', '')
    
    query = User.query
    if q:
        query = query.filter(or_(User.nickname.ilike(f'%{q}%'), User.phone.ilike(f'%{q}%')))
        
    pagination = query.order_by(User.id.desc()).paginate(page=page, per_page=page_size, error_out=False)
    users = pagination.items
    
    return jsonify({
        "items": [{
            "id": u.id, 
            "nickname": u.nickname, 
            "phone": u.phone, 
            "status": u.status, 
            "role": u.role,
            "avatar": u.avatar_url,  # --- 核心修改：添加 avatar 字段 ---
            "createdAt": u.created_at.isoformat() + 'Z'
        } for u in users],
        "total": pagination.total,
        "page": page,
        "pageSize": page_size
    })

# --- 新增：用户头像上传接口 (根据文档) ---
@admin_bp.route('/account/<int:user_id>/avatar', methods=['POST'])
@admin_required
def upload_user_avatar(current_admin, user_id):
    """上传用户头像"""
    if current_admin.role != 'admin':
        return jsonify({"message": "权限不足"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "用户不存在"}), 404
    
    if 'avatar' not in request.files:
        return jsonify({"message": "未上传文件"}), 400
    
    file = request.files['avatar']
    
    if file.filename == '':
        return jsonify({"message": "未选择文件"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"message": "不支持的文件格式，仅支持 JPG、PNG、GIF"}), 400
    
    # 检查文件大小
    file.seek(0, os.SEEK_END)
    if file.tell() > MAX_FILE_SIZE:
        return jsonify({"message": f"文件过大，最大支持 {MAX_FILE_SIZE / 1024 / 1024}MB"}), 413
    file.seek(0)
    
    # 生成安全且唯一的文件名
    ext = file.filename.rsplit('.', 1)[1].lower()
    timestamp = int(datetime.datetime.now().timestamp())
    filename = secure_filename(f"user_{user_id}_{timestamp}.{ext}")
    
    # 确保上传目录存在
    upload_path = os.path.join(current_app.root_path, AVATAR_UPLOAD_FOLDER)
    os.makedirs(upload_path, exist_ok=True)
    
    filepath = os.path.join(upload_path, filename)
    
    # 删除旧头像 (可选但推荐)
    if user.avatar_url:
        try:
            # 假设 avatar_url 存储的是 /static/images/avatars/filename.jpg 格式
            old_filename = os.path.basename(user.avatar_url)
            old_filepath = os.path.join(upload_path, old_filename)
            if os.path.exists(old_filepath):
                os.remove(old_filepath)
        except Exception as e:
            print(f"删除旧头像失败: {e}") # 记录错误，但不中断流程

    # 保存新文件
    file.save(filepath)
    
    # 更新数据库中的头像URL
    avatar_url = f"/uploads/avatars/{filename}"
    user.avatar_url = avatar_url
    db.session.commit()
    
    return jsonify({
        "message": "头像上传成功",
        "avatarUrl": avatar_url
    }), 200

@admin_bp.route('/account/ban', methods=['POST'])
@admin_required
def ban_account(current_admin):
    data = request.get_json()
    # 修复：前端发送 'id' 而不是 'accountId'
    user = User.query.get(data.get('id'))
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    user.status = 'banned'
    user.ban_reason = data.get('reason')
    if data.get('until'):
        user.ban_until = datetime.datetime.fromisoformat(data['until'].replace('Z', ''))
    else:
        user.ban_until = None
    db.session.commit()
    return jsonify({"message": "Account banned successfully"}), 200

@admin_bp.route('/account/unban', methods=['POST'])
@admin_required
def unban_account(current_admin):
    data = request.get_json()
    # 修复：前端发送 'id' 而不是 'accountId'
    user = User.query.get(data.get('id'))
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    user.status = 'active'
    user.ban_reason = None
    user.ban_until = None
    db.session.commit()
    return jsonify({"message": "Account unbanned successfully"}), 200

@admin_bp.route('/account/delete', methods=['POST'])
@admin_required
def delete_account(current_admin):
    data = request.get_json()
    # 修复：前端发送 'id' 而不是 'accountId'
    user = User.query.get(data.get('id'))
    if not user:
        return jsonify({"message": "User not found"}), 404

    if data.get('hard', False):
        db.session.delete(user)
    else:
        user.status = 'deleted'
    
    db.session.commit()
    return jsonify({"message": "Account deleted successfully"}), 200

@admin_bp.route('/account/update', methods=['PUT'])
@admin_required
def update_account(current_admin):
    data = request.get_json()
    user = User.query.get(data.get('id'))
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    if 'nickname' in data:
        user.nickname = data['nickname']
    if 'role' in data:
        user.role = data['role']
    db.session.commit()
    return jsonify({"message": "Account updated successfully"}), 200


# --- 专门用于更新权限的路由 (已修复逻辑) ---
@admin_bp.route('/account/permission', methods=['PUT'])
@admin_required
def update_permission(current_admin):
    data = request.get_json()
    user_id = data.get('id')
    new_role = data.get('role')

    if not user_id or not new_role:
        return jsonify({"message": "User ID and role are required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # 检查角色是否真的改变了
    if user.role == new_role:
        return jsonify({"message": "Permission is already set to this role"}), 200

    # 更新用户表中的角色
    user.role = new_role

    # --- 核心逻辑：同步 admins 表 ---
    # 定义所有具备后台登录权限的角色
    ADMIN_ROLES = ['admin', 'wiki_admin']
    
    admin_username = user.phone
    existing_admin = Admin.query.filter_by(username=admin_username).first()

    # 1. 如果新角色是管理员角色之一
    if new_role in ADMIN_ROLES:
        # 如果 admins 表中不存在该用户，则创建
        if not existing_admin:
            new_admin = Admin(
                username=admin_username,
                # 直接复制用户的密码哈希
                password_hash=user.password_hash,
                # 将新角色赋予 admin 账户
                role=new_role
            )
            db.session.add(new_admin)
            db.session.commit()
            return jsonify({"message": "Permission updated and admin account created successfully"}), 200
        else:
            # 如果已存在，更新其角色
            existing_admin.role = new_role
            db.session.commit()
            return jsonify({"message": "Permission updated and existing admin account role confirmed"}), 200

    # 2. 如果新角色不是管理员角色 (即降级)
    else:
        # 如果 admins 表中存在该用户，则删除，撤销其后台登录权限
        if existing_admin:
            db.session.delete(existing_admin)
            db.session.commit()
            return jsonify({"message": "Permission updated and admin account removed successfully"}), 200

    # 如果只是普通用户之间的角色切换，且不涉及 admin
    db.session.commit()
    return jsonify({"message": "Permission updated successfully"}), 200

# --- 新增：获取用户操作日志 ---
@admin_bp.route('/account/log', methods=['GET'])
@admin_required
def get_account_logs(current_admin):
    """获取指定用户的操作日志"""
    user_id = request.args.get('id', type=int)
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 50, type=int)
    
    if not user_id:
        return jsonify({"message": "缺少用户ID"}), 400
    
    query = UserLog.query.filter_by(user_id=user_id).order_by(UserLog.timestamp.desc())
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    logs = pagination.items
    
    return jsonify({
        "items": [{
            "id": log.id,
            "userId": log.user_id,
            "action": log.action,
            "detail": log.detail,
            "timestamp": log.timestamp.isoformat() + 'Z',
            "ip": log.ip,
            "userAgent": log.user_agent
        } for log in logs],
        "total": pagination.total,
        "page": page,
        "pageSize": page_size
    })


# --- 内容审核 (已重构) ---
# --- 1. 重构：内容审核列表 (GET /content/reviews) ---
@admin_bp.route('/content/reviews', methods=['GET'])
@admin_required
def get_content_reviews(current_admin):
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    status = request.args.get('status')
    content_type = request.args.get('type')
    keyword = request.args.get('keyword')

    items = []
    total = 0
    
    if content_type == 'review':
        query = Review.query
        if status: query = query.filter(Review.status == status)
        if keyword: query = query.filter(Review.comment.contains(keyword))
        
        pagination = query.order_by(Review.id.desc()).paginate(page=page, per_page=page_size, error_out=False)
        items = [{
            "id": r.id,
            "author": {"nickname": r.author.nickname, "id": r.author.id},
            "location": {"name": r.location.name, "id": r.location.id},
            "rating": r.rating,
            "comment": r.comment,
            "images": r.images or [],
            "status": r.status,
            "createdAt": r.created_at.isoformat() + 'Z',
            "reviewerNote": r.reviewer_note or ""
        } for r in pagination.items]
        total = pagination.total

    elif content_type == 'suggestion':
        # --- 核心重构：Wiki 建议列表 ---
        query = WikiSuggestion.query.options(
            db.joinedload(WikiSuggestion.author),
            db.joinedload(WikiSuggestion.location)
        )
        if status: query = query.filter(WikiSuggestion.status == status)
        if keyword: query = query.filter(WikiSuggestion.content.contains(keyword))

        pagination = query.order_by(WikiSuggestion.id.desc()).paginate(page=page, per_page=page_size, error_out=False)
        
        items = []
        for s in pagination.items:
            # 安全地处理 author 和 location 可能为空的情况
            author_info = {"nickname": s.author.nickname, "id": s.author.id} if s.author else None
            location_info = {"name": s.location.name, "id": s.location.id} if s.location else None
            
            items.append({
                "id": s.id,
                "author": author_info,
                "location": location_info,
                "content": s.content,
                "reason": s.reason or "", # 确保返回空字符串而不是 None
                "status": s.status,
                "createdAt": s.created_at.isoformat() + 'Z',
                "reviewerNote": s.reviewer_note or "" # 确保返回空字符串而不是 None
            })
        total = pagination.total

    elif content_type == 'report':
        # 文档中举报列表有单独路由，这里暂时保留以防万一，但建议使用新路由
        query = ReviewReport.query
        if status: query = query.filter(ReviewReport.status == status)
        pagination = query.order_by(ReviewReport.id.desc()).paginate(page=page, per_page=page_size, error_out=False)
        items = [{
            "id": r.id, "reason": r.reason, "status": r.status,
            "review": {"id": r.review.id, "comment": r.review.comment[:50] + '...', "author": {"nickname": r.review.author.nickname, "id": r.review.author.id}},
            "reporter": {"nickname": r.reporter.nickname, "id": r.reporter.id},
            "createdAt": r.created_at.isoformat() + 'Z'
        } for r in pagination.items]
        total = pagination.total

    return jsonify({"items": items, "total": total, "page": page, "pageSize": page_size})

# --- 2. 重构：内容详情内部逻辑 (_get_content_detail_logic) ---
def _get_content_detail_logic(content_type, content_id):
    if content_type == 'review':
        review = Review.query.get_or_404(content_id)
        return jsonify({
            "id": review.id,
            "author": {"nickname": review.author.nickname, "id": review.author.id},
            "location": {"name": review.location.name, "id": review.location.id},
            "rating": review.rating,
            "comment": review.comment,
            "images": review.images or [],
            "status": review.status,
            "createdAt": review.created_at.isoformat() + 'Z',
            "reviewerNote": review.reviewer_note or ""
        })
    elif content_type == 'suggestion':
        # --- 核心重构：Wiki 建议详情 ---
        suggestion = WikiSuggestion.query.get_or_404(content_id)
        
        author_info = {"nickname": suggestion.author.nickname, "id": suggestion.author.id} if suggestion.author else None
        location_info = {"name": suggestion.location.name, "id": suggestion.location.id} if suggestion.location else None
        
        return jsonify({
            "id": suggestion.id,
            "author": author_info,
            "location": location_info,
            "content": suggestion.content,
            "reason": suggestion.reason or "",
            "status": suggestion.status,
            "createdAt": suggestion.created_at.isoformat() + 'Z',
            "reviewerNote": suggestion.reviewer_note or ""
        })
    
# --- 路由1：适配 /reviews/38?type=review ---
@admin_bp.route('/content/reviews/<int:content_id>', methods=['GET'])
@admin_required
def get_content_review_detail_by_query_param(current_admin, content_id):
    content_type = request.args.get('type')
    if not content_type:
        return jsonify({"message": "Query parameter 'type' is missing"}), 400
    # 直接调用内部逻辑函数
    return _get_content_detail_logic(content_type, content_id)

# --- 路由2：适配 /reviews/review/38 ---
@admin_bp.route('/content/reviews/<string:content_type>/<int:content_id>', methods=['GET'])
@admin_required
def get_content_review_detail(current_admin, content_type, content_id):
    # 直接调用内部逻辑函数
    return _get_content_detail_logic(content_type, content_id)

# --- 3. 重构：通过审核 (approve) ---
@admin_bp.route('/content/reviews/<int:content_id>/approve', methods=['POST'])
@admin_required
def approve_content_review(current_admin, content_id):
    content_type = request.args.get('type')
    data = request.get_json() or {}
    note = data.get('note')

    if not content_type: return jsonify({"message": "Query parameter 'type' is missing"}), 400
    
    model = {'review': Review, 'suggestion': WikiSuggestion}.get(content_type)
    if not model: return jsonify({"message": "Invalid content type"}), 400
    
    item = model.query.get_or_404(content_id)
    item.status = 'approved'
    if note: item.reviewer_note = note
    
    # --- 核心修改：当通过 Wiki 建议时，应用其内容到地点 ---
    if content_type == 'suggestion' and item.location and item.content:
        # 只有当建议关联了地点且有内容时才更新
        item.location.rich_content = item.content

    db.session.commit()
    # 返回前端期望的、包含更新后状态的响应
    return jsonify({"message": "审核通过", "id": item.id, "status": "approved"}), 200

# --- 4. 重构：拒绝审核 (reject) ---
@admin_bp.route('/content/reviews/<int:content_id>/reject', methods=['POST'])
@admin_required
def reject_content_review(current_admin, content_id):
    content_type = request.args.get('type')
    data = request.get_json() or {}
    note = data.get('note')

    if not content_type: return jsonify({"message": "Query parameter 'type' is missing"}), 400

    model = {'review': Review, 'suggestion': WikiSuggestion}.get(content_type)
    if not model: return jsonify({"message": "Invalid content type"}), 400

    item = model.query.get_or_404(content_id)

    if content_type == 'review':
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "评论已删除"}), 200
    else: # suggestion
        item.status = 'rejected'
        if note: item.reviewer_note = note
        db.session.commit()
        # 返回前端期望的、包含更新后状态的响应
        return jsonify({"message": "已拒绝", "id": item.id, "status": "rejected"}), 200

# --- 5. 新增/重构：评论举报相关路由 ---

@admin_bp.route('/content/review-reports', methods=['GET'])
@admin_required
def get_review_reports(current_admin):
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    status = request.args.get('status')
    
    query = ReviewReport.query
    if status: query = query.filter(ReviewReport.status == status)
    
    pagination = query.order_by(ReviewReport.id.desc()).paginate(page=page, per_page=page_size, error_out=False)
    items = [{
        "id": r.id,
        "reason": r.reason,
        "status": r.status,
        "review": {
            "id": r.review.id,
            "comment": r.review.comment[:50] + ('...' if len(r.review.comment) > 50 else ''),
            "author": {"nickname": r.review.author.nickname, "id": r.review.author.id}
        },
        "reporter": {"nickname": r.reporter.nickname, "id": r.reporter.id},
        "createdAt": r.created_at.isoformat() + 'Z'
    } for r in pagination.items]
    
    return jsonify({"items": items, "total": pagination.total, "page": page, "pageSize": page_size})

@admin_bp.route('/content/review-reports/<int:report_id>', methods=['GET'])
@admin_required
def get_review_report_detail(current_admin, report_id):
    report = ReviewReport.query.get_or_404(report_id)
    review = report.review
    return jsonify({
        "id": report.id,
        "reason": report.reason,
        "status": report.status,
        "review": {
            "id": review.id,
            "comment": review.comment,
            "rating": review.rating,
            "images": review.images or [],
            "author": {"nickname": review.author.nickname, "id": review.author.id},
            "location": {"name": review.location.name, "id": review.location.id},
            "createdAt": review.created_at.isoformat() + 'Z'
        },
        "reporter": {"nickname": report.reporter.nickname, "id": report.reporter.id},
        "createdAt": report.created_at.isoformat() + 'Z'
    })

@admin_bp.route('/content/review-reports/<int:report_id>/resolve', methods=['POST'])
@admin_required
def resolve_review_report(current_admin, report_id):
    report = ReviewReport.query.get_or_404(report_id)
    data = request.get_json()
    action = data.get('action')
    note = data.get('note')

    if action == 'reject_review':
        db.session.delete(report.review) # 级联删除会处理评论相关数据
        report.status = 'resolved'
        message = "举报已处理，相关评论已删除"
    elif action == 'ban_review':
        review_author = report.review.author
        review_author.status = 'banned'
        db.session.delete(report.review)
        report.status = 'resolved'
        message = "举报已处理，评论已删除且作者已被封禁"
    else: # 默认 'resolve'
        report.status = 'resolved'
        message = "举报已处理"
    
    if note: report.reviewer_note = note
    db.session.commit()
    return jsonify({"message": message, "id": report.id, "status": report.status})

@admin_bp.route('/content/review-reports/<int:report_id>/dismiss', methods=['POST'])
@admin_required
def dismiss_review_report(current_admin, report_id):
    report = ReviewReport.query.get_or_404(report_id)
    data = request.get_json() or {}
    reason = data.get('reason')
    
    report.status = 'dismissed'
    if reason: report.reviewer_note = reason
    
    db.session.commit()
    return jsonify({"message": "举报已驳回"})

# --- 新增：删除单个 Wiki 建议 (根据文档) ---
@admin_bp.route('/content/reviews/<int:suggestion_id>', methods=['DELETE'])
@admin_required
def delete_wiki_suggestion(current_admin, suggestion_id):
    """删除单个 Wiki 建议"""
    # 1. 权限检查
    if current_admin.role not in ['admin', 'wiki_admin']:
        return jsonify({"success": False, "message": "权限不足"}), 403

    # 2. 验证请求类型
    content_type = request.args.get('type')
    if content_type != 'suggestion':
        return jsonify({'success': False, 'message': '此接口只能用于删除 Wiki 建议 (type=suggestion)'}), 400

    try:
        # 3. 查找并删除建议
        suggestion = WikiSuggestion.query.get(suggestion_id)
        if not suggestion:
            return jsonify({'success': False, 'message': 'Wiki 建议不存在或已被删除'}), 404
        
        db.session.delete(suggestion)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500

# --- 新增：批量删除 Wiki 建议 (根据文档) ---
@admin_bp.route('/content/reviews/batch-delete', methods=['POST'])
@admin_required
def batch_delete_wiki_suggestions(current_admin):
    """批量删除 Wiki 建议"""
    # 1. 权限检查
    if current_admin.role not in ['admin', 'wiki_admin']:
        return jsonify({"success": False, "message": "权限不足"}), 403

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求体不能为空'}), 400

    ids = data.get('ids', [])
    content_type = data.get('type')

    # 2. 验证请求类型和参数
    if content_type != 'suggestion':
        return jsonify({'success': False, 'message': '此接口只能用于删除 Wiki 建议 (type=suggestion)'}), 400
    if not ids or not isinstance(ids, list):
        return jsonify({'success': False, 'message': 'ids 必须是一个非空数组'}), 400

    # 3. 执行批量删除
    # 使用 in_() 一次性查询所有相关对象，提高效率
    suggestions_to_delete = WikiSuggestion.query.filter(WikiSuggestion.id.in_(ids)).all()
    found_ids = {s.id for s in suggestions_to_delete}

    try:
        for suggestion in suggestions_to_delete:
            db.session.delete(suggestion)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'数据库提交失败: {str(e)}'}), 500

    # 4. 构建详细的响应报告
    success_count = len(found_ids)
    fail_count = len(ids) - success_count
    details = []
    for sid in ids:
        # 将 id 转为整数进行比较
        int_sid = int(sid)
        if int_sid in found_ids:
            details.append({'id': sid, 'success': True})
        else:
            details.append({'id': sid, 'success': False, 'error': '不存在或已被删除'})

    return jsonify({
        'success': True,
        'message': '批量删除完成',
        'successCount': success_count,
        'failCount': fail_count,
        'details': details
    }), 200

# --- 新增：批量审核 Wiki 建议 ---
@admin_bp.route('/content/reviews/batch', methods=['POST'])
@admin_required
def batch_process_suggestions(current_admin):
    data = request.get_json()
    ids = data.get('ids', [])
    action = data.get('action')
    reason = data.get('reason', '')

    if not all([ids, action]):
        return jsonify({"message": "ids and action are required"}), 400
    if action not in ['approve', 'reject', 'delete']:
        return jsonify({"message": "Invalid action"}), 400

    success = []
    failed = []
    
    suggestions = WikiSuggestion.query.filter(WikiSuggestion.id.in_(ids)).all()
    suggestion_map = {s.id: s for s in suggestions}

    for sid in ids:
        suggestion = suggestion_map.get(sid)
        if not suggestion:
            failed.append({"id": sid, "error": "Suggestion not found"})
            continue
        
        try:
            if action == 'approve':
                suggestion.status = 'approved'
                # 应用 Wiki 更新到地点
                if suggestion.location:
                    suggestion.location.rich_content = suggestion.content
            elif action == 'reject':
                suggestion.status = 'rejected'
                suggestion.reject_reason = reason
            elif action == 'delete':
                db.session.delete(suggestion)
            
            success.append(sid)
        except Exception as e:
            failed.append({"id": sid, "error": str(e)})

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Batch operation failed during commit: {e}"}), 500

    return jsonify({"success": success, "failed": failed})

# --- 2. 地点信息管理 (已更新) ---

# --- 修复/增强：地点查询接口 ---
@admin_bp.route('/locations', methods=['GET'])
@admin_required
def get_locations(current_admin):
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    q = request.args.get('keyword', '')
    status = request.args.get('status', '')
    category_name = request.args.get('category', '')

    # 查询未被软删除的地点
    query = Location.query.filter(Location.deleted_at.is_(None))
    
    if q:
        search_term = f'%{q}%'
        query = query.filter(
            or_(
                Location.name.ilike(search_term),
                Location.address.ilike(search_term)
            )
        )
    
    if status:
        query = query.filter_by(status=status)
    
    if category_name:
        query = query.join(Location.category).filter(Category.name == category_name)
        
    pagination = query.order_by(Location.id.desc()).paginate(page=page, per_page=page_size, error_out=False)
    locations = pagination.items
    
    items = [{
        "id": str(loc.id),
        "name": loc.name,
        "address": loc.address,
        "status": loc.status,
        "category": loc.category.name if loc.category else None,
        "description": loc.rich_content,
        "longitude": loc.longitude,
        "latitude": loc.latitude,
        "tags": [t.name for t in loc.tags] if hasattr(loc, 'tags') else [],
        "updatedAt": loc.updated_at.isoformat() if loc.updated_at else None
    } for loc in locations]
    
    return jsonify({
        "items": items,
        "total": pagination.total,
        "page": page,
        "pageSize": page_size
    })

@admin_bp.route('/locations', methods=['POST'])
@admin_required
def create_location(current_admin):
    data = request.get_json()
    new_loc = Location(**data)
    db.session.add(new_loc)
    db.session.commit()
    return jsonify({"id": new_loc.id, "name": new_loc.name}), 201

@admin_bp.route('/locations/<int:loc_id>', methods=['PUT'])
@admin_required
def update_location(current_admin, loc_id):
    loc = Location.query.get_or_404(loc_id)
    data = request.get_json()
    for key, value in data.items():
        if hasattr(loc, key):
            setattr(loc, key, value)
    db.session.commit()
    return jsonify({"message": "Location updated"})

@admin_bp.route('/locations/<int:loc_id>', methods=['DELETE'])
@admin_required
def delete_location_record(current_admin, loc_id):
    loc = Location.query.get_or_404(loc_id)
    db.session.delete(loc)
    db.session.commit()
    return "", 204

# --- 新增：批量删除地点 (使用软删除) ---
@admin_bp.route('/locations/batch-delete', methods=['POST'])
@admin_required
def batch_delete_locations(current_admin):
    if current_admin.role not in ['admin', 'wiki_admin']:
        return jsonify({"message": "Forbidden"}), 403
        
    data = request.get_json()
    ids = data.get('ids', [])
    
    if not ids or not isinstance(ids, list):
        return jsonify({"message": "无效的ID列表"}), 400
    
    # 使用 in_() 进行批量更新，效率更高
    try:
        deleted_count = Location.query.filter(Location.id.in_(ids)).update(
            {'deleted_at': datetime.datetime.utcnow()}, 
            synchronize_session=False
        )
        db.session.commit()
        return jsonify({
            "message": f"成功删除 {deleted_count} 个地点",
            "deleted": deleted_count,
            "failed": []
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"批量删除失败: {str(e)}"}), 500


# --- 修复/增强：导入地点接口 ---
@admin_bp.route('/locations/import', methods=['POST'])
@admin_required
def import_locations(current_admin):
    if current_admin.role not in ['admin', 'wiki_admin']:
        return jsonify({"message": "Forbidden"}), 403

    data = request.get_json()
    items = data.get('items', [])
    if not isinstance(items, list):
        return jsonify({"message": "items必须是数组"}), 400
    
    imported_count, updated_count = 0, 0
    failed_items = []
    
    for idx, item_data in enumerate(items):
        try:
            # --- 核心修改：增加对 building_id 唯一性的预检查 ---
            building_id = item_data.get('building_id')
            item_id = item_data.get('id')

            if building_id is not None:
                # 检查是否有其他地点占用了这个 building_id
                conflict_location = Location.query.filter_by(building_id=building_id).first()
                if conflict_location and (not item_id or conflict_location.id != int(item_id)):
                    raise ValueError(f"Building ID '{building_id}' 已被地点 ID {conflict_location.id} 占用")

            # 尝试通过主键ID查找现有地点
            existing_loc = Location.query.get(item_id) if item_id else None
            
            if existing_loc:
                # 更新逻辑
                for key, value in item_data.items():
                    if hasattr(existing_loc, key) and key != 'id':
                        setattr(existing_loc, key, value)
                updated_count += 1
            else:
                # 创建逻辑
                # 移除 id 以防止主键冲突
                item_data.pop('id', None)
                new_loc = Location(**item_data)
                db.session.add(new_loc)
                imported_count += 1
                
        except (ValueError, IntegrityError) as e:
            # 捕获我们自己抛出的 ValueError 或数据库的 IntegrityError
            db.session.rollback() # 回滚当前失败的条目
            failed_items.append({"index": idx, "name": item_data.get('name', 'unknown'), "error": str(e)})
        except Exception as e:
            db.session.rollback()
            failed_items.append({"index": idx, "name": item_data.get('name', 'unknown'), "error": f"未知错误: {str(e)}"})

    # 统一提交所有成功的操作
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"在最后提交时发生错误: {str(e)}"}), 500
    
    return jsonify({
        "message": f"成功导入 {imported_count} 个新地点, 更新 {updated_count} 个已有地点",
        "imported": imported_count,
        "updated": updated_count,
        "failed": failed_items
    }), 200

# --- 新增：根据 "Wiki批量导入功能-后端实现指南.md" 实现批量导入接口 ---
@admin_bp.route('/wikis/batch-import', methods=['POST'])
@wiki_editor_required
def batch_import_wikis(current_admin, is_admin=False):
    """
    通过上传 JSON 或 CSV 文件批量导入/更新 Wiki (地点) 信息。
    严格遵循前端实现指南。
    """
    # 1. 权限检查
    if current_admin.role not in ['admin', 'wiki_admin']:
        return jsonify({"message": "权限不足"}), 403

    # 2. 文件验证
    if 'file' not in request.files:
        return jsonify({'message': '未上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': '文件名为空'}), 400
    
    filename = secure_filename(file.filename)
    
    # 3. 文件内容读取与解析
    wikis_data = []
    try:
        # 使用 utf-8-sig 兼容带 BOM 的文件
        content = file.read().decode('utf-8-sig') 
        if filename.endswith('.json'):
            wikis_data = json.loads(content)
            if not isinstance(wikis_data, list):
                return jsonify({'message': 'JSON 文件根结构必须是数组'}), 400
        elif filename.endswith('.csv'):
            # 使用 io.StringIO 将字符串内容转换为文件流
            csv_reader = csv.DictReader(io.StringIO(content))
            wikis_data = list(csv_reader)
        else:
            return jsonify({'message': '文件格式不支持，仅接受 .json 或 .csv 文件'}), 415
    except json.JSONDecodeError:
        return jsonify({'message': 'JSON 文件格式错误，无法解析'}), 400
    except Exception as e:
        return jsonify({'message': f'文件读取或解析失败: {str(e)}'}), 400

    # 4. 逐条处理数据
    success_count = 0
    failed_count = 0
    errors = []
    
    for index, item_data in enumerate(wikis_data, start=1):
        name = item_data.get('name', '未知名称').strip()
        try:
            # a. 字段验证
            if not name:
                raise ValueError("name 字段不能为空")
            
            building_id_str = item_data.get('buildingId') or item_data.get('building_id')
            if not building_id_str:
                raise ValueError("buildingId 字段不能为空")
            
            address = item_data.get('address', '').strip()
            if not address:
                raise ValueError("address 字段不能为空")

            latitude_str = item_data.get('latitude')
            longitude_str = item_data.get('longitude')
            if latitude_str is None or longitude_str is None:
                raise ValueError("latitude 和 longitude 字段不能为空")

            # b. 类型转换与范围校验
            try:
                building_id = int(building_id_str)
                latitude = float(latitude_str)
                longitude = float(longitude_str)
                if not (-90 <= latitude <= 90):
                    raise ValueError('纬度必须在 -90 到 90 之间')
                if not (-180 <= longitude <= 180):
                    raise ValueError('经度必须在 -180 到 180 之间')
            except (ValueError, TypeError) as e:
                raise ValueError(f"数字格式错误: {e}")

            # c. 查找或创建 Location
            loc = Location.query.filter_by(building_id=building_id).first()
            if not loc:
                loc = Location(building_id=building_id)
                db.session.add(loc)

            # d. 更新字段
            loc.name = name
            loc.address = address
            loc.latitude = latitude
            loc.longitude = longitude
            loc.main_image = item_data.get('mainImage') or item_data.get('main_image')
            loc.rich_content = item_data.get('richContent') or item_data.get('rich_content')
            
            # 处理 structuredInfo (必须是 JSON 对象)
            s_info = item_data.get('structuredInfo') or item_data.get('structured_info')
            if s_info:
                if isinstance(s_info, str):
                    try:
                        loc.structured_info = json.loads(s_info)
                    except json.JSONDecodeError:
                        raise ValueError("structuredInfo 字段必须是有效的 JSON 格式")
                elif isinstance(s_info, dict):
                    loc.structured_info = s_info
                else:
                    raise ValueError("structuredInfo 字段必须是 JSON 对象或字符串")

            # e. 处理分类
            category_name = item_data.get('category')
            if category_name:
                category = Category.query.filter_by(name=category_name).first()
                if not category:
                    category = Category(name=category_name)
                    db.session.add(category)
                loc.category = category

            # f. 处理标签
            tags_data = item_data.get('tags', [])
            if isinstance(tags_data, str):
                tags_data = [t.strip() for t in tags_data.split(',') if t.strip()]
            
            if isinstance(tags_data, list):
                loc.tags.clear()
                for tag_name in tags_data:
                    tag = Tag.query.filter_by(name=tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name)
                        db.session.add(tag)
                    loc.tags.append(tag)

            success_count += 1

        except Exception as e:
            failed_count += 1
            errors.append(f'第 {index} 行 ({name}) 失败: {str(e)}')
            # 单条失败，继续处理下一条，不需要回滚
            continue
    
    # 5. 统一提交事务
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # 如果在最后提交时失败，所有操作都将失败
        return jsonify({'message': f'数据库最终提交失败: {str(e)}'}), 500

    return jsonify({
        'success': success_count,
        'failed': failed_count,
        'errors': errors,
        'message': f'成功处理 {success_count} 条，失败 {failed_count} 条'
    }), 200

# --- 修复：导出地点接口 ---
@admin_bp.route('/locations/export', methods=['GET'])
@admin_required
def export_locations(current_admin):
    if current_admin.role not in ['admin', 'wiki_admin']:
        return jsonify({"message": "Forbidden"}), 403

    locations = Location.query.filter(Location.deleted_at.is_(None)).all()
    items = [{
        "id": str(loc.id), "name": loc.name, "address": loc.address,
        "category": loc.category.name if loc.category else None,
        "status": loc.status, "description": loc.description,
        "longitude": loc.longitude, "latitude": loc.latitude,
        "tags": [t.name for t in loc.tags] if hasattr(loc, 'tags') else [],
        "main_image": loc.main_image, "rich_content": loc.rich_content,
        "structured_info": loc.structured_info, "building_id": loc.building_id,
        "updated_at": loc.updated_at.isoformat() if loc.updated_at else None
    } for loc in locations]
    return jsonify({"items": items, "total": len(items)})

# --- 系统设置 (已更新) ---
@admin_bp.route('/settings/system', methods=['GET'])
@admin_required
def get_system_settings(current_admin):
    settings = SystemSetting.query.all()
    settings_dict = {s.key: s.value for s in settings}
    return jsonify(settings_dict)

@admin_bp.route('/settings/system', methods=['PUT'])
@admin_required
def update_system_settings(current_admin):
    payload = request.get_json()
    for key, value in payload.items():
        setting = SystemSetting.query.filter_by(key=key).first()
        if setting:
            setting.value = json.dumps(value)
        else:
            setting = SystemSetting(key=key, value=json.dumps(value))
            db.session.add(setting)
    db.session.commit()
    return jsonify({"message": "Settings updated successfully"})

# --- 增强：数据总览接口 ---
@admin_bp.route('/analytics/overview', methods=['GET'])
@admin_required
def get_analytics_overview(current_admin):
    if current_admin.role != 'admin': return jsonify({"message": "Forbidden"}), 403
    
    today = datetime.datetime.now().date()
    
    # 日活 (最近14天)
    daily_active = db.session.query(
        func.date(UserLoginLog.login_time).label('date'),
        func.count(distinct(UserLoginLog.user_id)).label('value')
    ).filter(
        UserLoginLog.login_time >= today - datetime.timedelta(days=13)
    ).group_by('date').order_by('date').all()
    daily_active_data = [{"date": d.strftime('%m-%d'), "value": v} for d, v in daily_active]

    # 周活/月活
    weekly_active = db.session.query(func.count(distinct(UserLoginLog.user_id))).filter(UserLoginLog.login_time >= today - datetime.timedelta(days=7)).scalar() or 0
    monthly_active = db.session.query(func.count(distinct(UserLoginLog.user_id))).filter(UserLoginLog.login_time >= today - datetime.timedelta(days=30)).scalar() or 0

    # 热点区域
    hotspot_query = db.session.query(Location.name, func.count(LocationView.id).label('visits')).join(LocationView).group_by(Location.id).order_by(func.count(LocationView.id).desc()).limit(10).all()
    hotspot_areas = [{"name": name, "visits": visits} for name, visits in hotspot_query]

    # --- 核心修复：根据文档要求，精确计算审核统计 ---
    pending_reviews = Review.query.filter_by(status='pending').count()
    pending_suggestions = WikiSuggestion.query.filter_by(status='pending').count()
    
    approved_reviews = Review.query.filter_by(status='approved').count()
    approved_suggestions = WikiSuggestion.query.filter_by(status='approved').count()
    
    # 评论被拒绝时直接删除，所以只统计被拒绝的 Wiki 建议
    rejected_suggestions = WikiSuggestion.query.filter_by(status='rejected').count()

    review_stats = {
        "pending": pending_reviews + pending_suggestions,
        "approved": approved_reviews + approved_suggestions,
        "rejected": rejected_suggestions
    }

    return jsonify({
        "dailyActive": daily_active_data, "weeklyActive": weekly_active, "monthlyActive": monthly_active,
        "hotspotAreas": hotspot_areas, "reviewStats": review_stats
    })

# --- 新增：用户活跃度接口 ---
@admin_bp.route('/analytics/user-activity', methods=['GET'])
@admin_required
def get_user_activity(current_admin):
    """用户活跃度分析 - 日活、周活、月活、活跃率、分时段统计"""
    if current_admin.role != 'admin':
        return jsonify({"message": "Forbidden"}), 403

    today = datetime.datetime.now().date()
    
    # 1. 日活数据 (最近14天)
    daily_active_query = db.session.query(
        func.date(UserLoginLog.login_time).label('date'),
        func.count(distinct(UserLoginLog.user_id)).label('value')
    ).filter(
        UserLoginLog.login_time >= today - datetime.timedelta(days=13)
    ).group_by('date').order_by('date').all()
    
    # 将查询结果转换为字典以便快速查找
    daily_active_map = {d.strftime('%Y-%m-%d'): v for d, v in daily_active_query}
    daily_active_data = []
    for i in range(14):
        date = today - datetime.timedelta(days=13 - i)
        date_str = date.strftime('%Y-%m-%d')
        daily_active_data.append({
            "date": date_str,
            "value": daily_active_map.get(date_str, 0)
        })

    # 2. 周活/月活
    weekly_active = db.session.query(func.count(distinct(UserLoginLog.user_id))).filter(UserLoginLog.login_time >= today - datetime.timedelta(days=7)).scalar() or 0
    monthly_active = db.session.query(func.count(distinct(UserLoginLog.user_id))).filter(UserLoginLog.login_time >= today - datetime.timedelta(days=30)).scalar() or 0

    # 3. 活跃率 (月活/总用户数)
    total_users = User.query.filter_by(status='active').count()
    active_rate = round(monthly_active / total_users, 2) if total_users > 0 else 0

    # 4. 分时段活跃度 (最近24小时)
    hourly_distribution_query = db.session.query(
        func.hour(UserLoginLog.login_time).label('hour'),
        func.count(distinct(UserLoginLog.user_id)).label('count')
    ).filter(
        UserLoginLog.login_time >= datetime.datetime.now() - datetime.timedelta(hours=24)
    ).group_by('hour').all()
    
    hourly_map = {h: c for h, c in hourly_distribution_query}
    hourly_distribution = [{"hour": h, "count": hourly_map.get(h, 0)} for h in range(24)]

    return jsonify({
        "dailyActive": daily_active_data,
        "weeklyActive": weekly_active,
        "monthlyActive": monthly_active,
        "activeRate": active_rate,
        "hourlyDistribution": hourly_distribution
    })

# --- 新增：高分地点排行 ---
@admin_bp.route('/analytics/top-locations', methods=['GET'])
@admin_required
def get_top_locations(current_admin):
    limit = request.args.get('limit', 10, type=int)
    query = db.session.query(
        Location.id, Location.name,
        func.avg(Review.rating).label('avg_rating'),
        func.count(Review.id).label('review_count'),
        Category.name.label('category_name')
    ).join(Review).outerjoin(Category).group_by(Location.id, Category.name).having(func.count(Review.id) >= 1).order_by(func.avg(Review.rating).desc(), func.count(Review.id).desc()).limit(limit)
    
    items = [{"id": loc_id, "name": name, "averageRating": round(float(avg_rating), 1), "reviewCount": review_count, "category": category or "未分类"} for loc_id, name, avg_rating, review_count, category in query.all()]
    return jsonify({"items": items})

# --- 新增：评论量趋势 ---
@admin_bp.route('/analytics/review-trends', methods=['GET'])
@admin_required
def get_review_trends(current_admin):
    days = request.args.get('days', 30, type=int)
    today = datetime.datetime.now().date()
    
    query = db.session.query(
        func.date(Review.created_at).label('date'),
        func.count(Review.id).label('count')
    ).filter(
        Review.created_at >= today - datetime.timedelta(days=days-1)
    ).group_by('date').order_by('date').all()

    trends = [{"date": d.strftime('%Y-%m-%d'), "count": c} for d, c in query]
    total = sum(item['count'] for item in trends)
    average = round(total / days, 1) if days > 0 else 0
    
    return jsonify({"trends": trends, "total": total, "average": average})

# --- 核心重构：根据文档要求，完整重写搜索热词接口 ---
@admin_bp.route('/analytics/search-keywords', methods=['GET'])
@admin_required
def get_search_keywords(current_admin):
    """
    获取搜索热词统计，并根据时间周期对比计算趋势。
    严格遵循 "搜索热词统计接口-后端实现指南.md" 文档。
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        
        # 1. 定义时间范围
        now = datetime.datetime.utcnow()
        thirty_days_ago = now - datetime.timedelta(days=30)
        seven_days_ago = now - datetime.timedelta(days=7)

        # 2. 查询最近30天内 TOP 10 的热词及其总数
        keyword_stats = db.session.query(
            SearchLog.keyword,
            func.count(SearchLog.id).label('total_count')
        ).filter(
            SearchLog.created_at >= thirty_days_ago,
            SearchLog.keyword.isnot(None),
            SearchLog.keyword != ''
        ).group_by(
            SearchLog.keyword
        ).order_by(
            func.count(SearchLog.id).desc()
        ).limit(limit).all()
        
        # 如果没有任何搜索记录，返回空列表
        if not keyword_stats:
            return jsonify({'keywords': []})

        # 3. 为每个热词计算趋势
        keywords_with_trend = []
        for keyword, total_count in keyword_stats:
            # a. 查询最近7天的搜索次数
            recent_count = db.session.query(func.count(SearchLog.id)).filter(
                SearchLog.keyword == keyword,
                SearchLog.created_at >= seven_days_ago
            ).scalar() or 0
            
            # b. 查询 7-30 天前的搜索次数
            # 注意：这里的时间范围是 [30天前, 7天前)
            old_count = total_count - recent_count
            
            # c. 根据文档逻辑计算趋势
            trend = 'stable'
            if old_count == 0 and recent_count > 0:
                # 如果以前没有，现在有了，就是上升
                trend = 'up'
            elif old_count > 0:
                # 将周期标准化，避免天数不同导致的不公平比较
                # old_period_days = (seven_days_ago - thirty_days_ago).days  # 23天
                # recent_period_days = (now - seven_days_ago).days # 7天
                # old_daily_avg = old_count / old_period_days
                # recent_daily_avg = recent_count / recent_period_days
                
                # 简化逻辑：直接比较两个周期的总数，如果近期比之前多20%则为上升
                if recent_count > old_count * 1.2:
                    trend = 'up'
                elif recent_count < old_count * 0.8:
                    trend = 'down'

            keywords_with_trend.append({
                'keyword': keyword,
                'count': total_count,
                'trend': trend
            })
            
        return jsonify({'keywords': keywords_with_trend})

    except Exception as e:
        # 记录错误日志，并按文档要求返回空列表
        current_app.logger.error(f"获取搜索热词失败: {e}")
        return jsonify({
            'keywords': [],
            'error': str(e)
        }), 500

