from flask import Blueprint, request, jsonify, current_app
from sqlalchemy.exc import IntegrityError
from ..models.models import db, Review, Location, ReviewLike, ReviewReply, ReviewReport, Message, Tag, review_tags, UserLog, ReviewReplyReport
from .auth import token_required
import os
import uuid
from werkzeug.utils import secure_filename
# --- 新增：导入 timezone ---
from datetime import timezone

# --- 导入 users.py 中的日志函数 ---
from .users import log_user_action

reviews_bp = Blueprint('reviews_api', __name__, url_prefix='/api/reviews')

@reviews_bp.route('', methods=['GET'])
def get_location_comments():
    """获取评论列表（支持标签筛选）"""
    location_id = request.args.get('locationId', type=int)
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    tag_filter = request.args.get('tag') # 标签筛选
    
    if not location_id:
        return jsonify({"message": "locationId is required"}), 400
        
    query = Review.query.filter_by(location_id=location_id)

    # 如果有标签筛选
    if tag_filter:
        query = query.join(review_tags).join(Tag).filter(Tag.name == tag_filter)
    
    query = query.order_by(Review.created_at.desc())
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    reviews = pagination.items
    
    base_url = request.url_root.rstrip('/')

    items = []
    for r in reviews:
        image_urls = []
        if isinstance(r.images, list):
            # image_urls = [f"{base_url}{img}" if img.startswith('/') else img for img in r.images]
            image_urls = [f"{img}" if img.startswith('/') else img for img in r.images]
        # 获取该评论的回复
        replies = r.replies.order_by(ReviewReply.created_at.asc()).all()
        reply_list = []
        for reply in replies:
            reply_list.append({
                "id": reply.id,
                "userId": reply.author.id,
                "userName": reply.author.nickname,
                "userAvatar": reply.author.avatar_url,
                "content": reply.content,
                "createdAt": reply.created_at.isoformat() + 'Z'
            })

        items.append({
            "id": r.id,
            "userId": r.author.id,
            "userName": r.author.nickname,
            "userAvatar": r.author.avatar_url,
            "locationId": r.location_id,
            "rating": r.rating,
            "comment": r.comment,
            "images": image_urls,
            "createdAt": r.created_at.isoformat() + 'Z',
            "updatedAt": r.updated_at.isoformat() + 'Z',
            "likes": r.likes.count(),
            "tags": [t.name for t in r.tags], # 添加标签
            "replyCount": len(replies),
            "replies": reply_list
        })

    return jsonify({
        "items": items,
        "total": pagination.total,
        "page": pagination.page,
        "pageSize": pagination.per_page,
        "pages": pagination.pages
    }), 200

# --- 允许的图片扩展名 ---
REVIEWS_SUBFOLDER = 'reviews'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@reviews_bp.route('', methods=['POST'])
@token_required
def submit_review(current_user):
    # --- 核心修改：从 request.form 和 request.files 获取数据 ---
    # data = request.get_json()  <-- 不再使用这个
    
    # 从表单获取文本数据
    location_id = request.form.get('locationId', type=int)
    rating = request.form.get('rating', type=float)
    comment = request.form.get('comment', type=str)
    # 获取标签列表
    tags = request.form.getlist('tags[]')

    # 从文件部分获取图片
    uploaded_files = request.files.getlist('images')
    
    if not location_id or rating is None:
        return jsonify({"message": "locationId and rating are required"}), 400

    # 检查地点是否存在
    if not Location.query.get(location_id):
        return jsonify({"message": "Location not found"}), 404
        
    image_paths = []
    for file in uploaded_files:
        if file and allowed_file(file.filename):
            # 生成安全且唯一的文件名
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4()}.{ext}"
            
            # --- 核心修改：构建正确的保存路径 ---
            # 确保子文件夹存在
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], REVIEWS_SUBFOLDER)
            os.makedirs(upload_path, exist_ok=True)
            save_path = os.path.join(upload_path, unique_filename)
            
            # 保存文件
            file.save(save_path)
            
            # --- 核心修改：存储可供 Web 访问的相对路径 ---
            web_path = f"/uploads/{REVIEWS_SUBFOLDER}/{unique_filename}".replace('\\', '/')
            image_paths.append(web_path)
    new_review = Review(
        user_id=current_user.id,
        location_id=location_id,
        rating=rating,
        comment=comment,
        # 存储图片路径列表
        images=image_paths
    )

    # --- 处理标签 ---
    if tags:
        for tag_name in set(tags): # 使用 set 去重
            tag_name = tag_name.strip()
            if not tag_name or len(tag_name) > 10:
                continue
            
            # 查找或创建标签
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            
            # 添加关联
            new_review.tags.append(tag)

    db.session.add(new_review)
    log_user_action(current_user, 'SUBMIT_REVIEW', detail={"review_id": new_review.id, "location_id": location_id})
    db.session.commit()
    
    return jsonify({
        "success": True,
        "message": "Review submitted successfully",
        "reviewId": new_review.id
    }), 201

# --- 新增：举报评论的路由 ---
@reviews_bp.route('/<int:review_id>/report', methods=['POST'])
@token_required
def report_review(current_user, review_id):
    """
    举报一条评论
    """
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"message": "被举报的评论不存在"}), 404

    if review.user_id == current_user.id:
        return jsonify({"message": "你不能举报自己的评论"}), 403

    data = request.get_json()
    reason = data.get('description', '').strip()
    
    if len(reason) > 255:
        return jsonify({"message": "举报原因不能超过255个字符"}), 400

    try:
        new_report = ReviewReport(
            review_id=review_id,
            reporter_id=current_user.id,
            reason=reason
        )
        db.session.add(new_report)

        # --- 新增：发送被举报通知给评论作者 ---
        notification = Message(
            user_id=review.user_id,
            type='report', # 或 'report'
            content="你的一条评论被举报，我们将会尽快审核。",
            link=f"/locations/{review.location_id}?reviewId={review.id}",
            related_review_id=review.id,
            related_comment=review.comment[:100]
        )
        db.session.add(notification)
        log_user_action(current_user, 'REPORT_REVIEW', detail={"review_id": review_id})
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "你已经举报过这条评论"}), 409

    return jsonify({
        "success": True,
        "message": "举报成功，我们将会尽快处理"
    }), 201

# --- 新增：提交回复的路由 ---
@reviews_bp.route('/<int:review_id>/replies', methods=['POST'])
@token_required
def add_reply(current_user, review_id):
    """
    为指定评论添加回复
    """
    # 检查评论是否存在
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"message": "评论不存在"}), 404
    
    data = request.get_json()
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({"message": "回复内容不能为空"}), 400
    
    if len(content) > 500:
        return jsonify({"message": "回复内容不能超过500字"}), 400
    
    # 创建回复
    new_reply = ReviewReply(
        review_id=review_id,
        user_id=current_user.id,
        content=content
    )
    
    db.session.add(new_reply)

    # --- 新增：发送消息通知 ---
    # 只有当回复者不是评论作者本人时才发送通知
    if review.user_id != current_user.id:
        notification_content = f"你的评论收到了来自 {current_user.nickname} 的一条新回复"
        # 创建一个链接，前端可以点击跳转到对应的评论区
        notification_link = f"/locations/{review.location_id}?reviewId={review.id}"
        
        notification = Message(
            user_id=review.user_id,
            type='reply',
            content=notification_content,
            link=notification_link,
            related_review_id=review.id,
            related_comment=review.comment[:100]
        )
        db.session.add(notification)
    log_user_action(current_user, 'ADD_REVIEW_REPLY', detail={"review_id": review_id, "reply_id": new_reply.id})
    db.session.commit()
    
    # --- 核心修复：正确处理 UTC 时间转换 ---
    # 1. 假设从数据库获取的 created_at 是一个 naive datetime (代表UTC时间)
    # 2. 使用 .replace(tzinfo=timezone.utc) 告诉 Python "这个时间是UTC时区的"
    # 3. 然后调用 isoformat()，它会自动包含 'Z' 或 '+00:00'
    utc_created_at = new_reply.created_at.replace(tzinfo=timezone.utc)

    return jsonify({
        "success": True,
        "message": "回复成功",
        "reply": {
            "id": new_reply.id,
            "userId": current_user.id,
            "userName": current_user.nickname,
            "userAvatar": current_user.avatar_url,
            "content": new_reply.content,
            "createdAt": utc_created_at.isoformat() # 直接调用 isoformat()
        }
    }), 201

# --- 新增：举报评论回复的路由 ---
@reviews_bp.route('/replies/<int:reply_id>/report', methods=['POST'])
@token_required
def report_review_reply(current_user, reply_id):
    """
    举报一条评论回复
    """
    reply = ReviewReply.query.get(reply_id)
    if not reply:
        return jsonify({"message": "被举报的回复不存在"}), 404

    # 不能举报自己的回复
    if reply.user_id == current_user.id:
        return jsonify({"message": "你不能举报自己的回复"}), 403

    data = request.get_json()
    reason = data.get('description', '').strip()
    
    if len(reason) > 255:
        return jsonify({"message": "举报原因不能超过255个字符"}), 400

    try:
        new_report = ReviewReplyReport(
            reply_id=reply_id,
            reporter_id=current_user.id,
            reason=reason
        )
        db.session.add(new_report)
        log_user_action(current_user, 'REPORT_REVIEW_REPLY', detail={"reply_id": reply_id})
        db.session.commit()
    except IntegrityError:
        # 捕获唯一约束冲突，说明用户已经举报过
        db.session.rollback()
        return jsonify({"message": "你已经举报过这条回复"}), 409

    return jsonify({
        "success": True,
        "message": "举报成功，我们将会尽快处理"
    }), 201

# --- 新增：点赞评论的路由 ---
@reviews_bp.route('/<int:review_id>/like', methods=['POST'])
@token_required
def toggle_like_review(current_user, review_id):
    """
    为指定 ID 的评论点赞或取消点赞。
    """
    review = Review.query.get(review_id)
    
    if not review:
        return jsonify({"message": "Review not found"}), 404
        
    # 查找用户是否已经点过赞
    existing_like = ReviewLike.query.filter_by(
        user_id=current_user.id,
        review_id=review.id
    ).first()
    
    if existing_like:
        # --- 如果已点赞，则取消点赞 ---
        db.session.delete(existing_like)
        message = "Review unliked successfully"
        liked = False
    else:
        # --- 如果未点赞，则添加点赞 ---
        new_like = ReviewLike(user_id=current_user.id, review_id=review.id)
        db.session.add(new_like)
        message = "Review liked successfully"
        liked = True

        # --- 新增：发送点赞通知 ---
        # 仅当点赞者不是评论作者本人时发送
        if review.user_id != current_user.id:
            notification = Message(
                user_id=review.user_id,
                type='like',
                content=f"你的评论收到了来自 {current_user.nickname} 的一个赞",
                link=f"/locations/{review.location_id}?reviewId={review.id}",
                related_review_id=review.id,
                related_comment=review.comment[:100] # 截取前100字作为快照
            )
            db.session.add(notification)
        
    log_user_action(current_user, 'TOGGLE_LIKE_REVIEW', detail={"review_id": review_id, "liked": liked})
    db.session.commit()
    
    # --- 核心修复：在 commit 后，通过关系查询最新的点赞总数 ---
    current_likes_count = review.likes.count()
    
    return jsonify({
        "success": True,
        "message": message,
        "liked": liked,
        "likes": current_likes_count # 返回最新的计数值
    }), 200
