from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB # 使用 PostgreSQL 的 JSONB 类型效率更高
from sqlalchemy.types import JSON # 通用 JSON 类型
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import json

db = SQLAlchemy()

# --- 辅助关联表 ---
location_tags = db.Table('location_tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
    db.Column('location_id', db.Integer, db.ForeignKey('locations.id'), primary_key=True)
)

# --- 新增：评论-标签 关联表 ---
review_tags = db.Table('review_tags',
    db.Column('review_id', db.Integer, db.ForeignKey('reviews.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(1024), nullable=False)
    nickname = db.Column(db.String(80), nullable=True)
    avatar_url = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.String(255), nullable=True) # 个人简介
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # 新增字段
    status = db.Column(db.String(20), default='active', nullable=False) # active, banned, deleted
    role = db.Column(db.String(50), default='user', nullable=False)
    ban_reason = db.Column(db.String(255))
    ban_until = db.Column(db.DateTime)

    # ... (之前的 relationships 和 methods) ...
    favorites = db.relationship('Favorite', backref='user', lazy=True, cascade="all, delete-orphan")
    history = db.relationship('History', backref='user', lazy=True, cascade="all, delete-orphan")
    messages = db.relationship('Message', backref='user', lazy=True, cascade="all, delete-orphan")
    reviews = db.relationship('Review', backref='author', lazy='dynamic', cascade="all, delete-orphan")
    # --- 核心修复：将 backref 修改为 back_populates ---
    wiki_suggestions = db.relationship('WikiSuggestion', back_populates='author', lazy='dynamic')
    # 新增：用户发表的评论回复
    review_replies = db.relationship('ReviewReply', backref='author', lazy='dynamic', cascade="all, delete-orphan")
    # 新增：用户提交的回复举报
    reported_replies = db.relationship('ReviewReplyReport', backref='reporter', lazy='dynamic', cascade="all, delete-orphan")
    # 新增：用户提交的评论举报
    reported_reviews = db.relationship('ReviewReport', backref='reporter', lazy='dynamic', cascade="all, delete-orphan")
    # --- 新增：用户收藏的路线 ---
    favorite_routes = db.relationship('FavoriteRoute', backref='user', lazy='dynamic', cascade="all, delete-orphan")
    # --- 新增：与操作日志的反向关系 ---
    action_logs = db.relationship('ActionLog', backref='user', lazy='dynamic', cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    
class Location(db.Model):
    # ... (之前的字段) ...
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    # 新增 building_id 字段
    building_id = db.Column(db.Integer, unique=True, index=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    # --- 新增：软删除字段 ---
    deleted_at = db.Column(db.DateTime, nullable=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255))
    main_image = db.Column(db.String(255))
    rich_content = db.Column(db.Text)
    structured_info = db.Column(JSON)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    # --- 新增：地点描述字段 ---
    description = db.Column(db.Text, nullable=True)
    # 新增字段
    status = db.Column(db.String(20), default='published', nullable=False) # draft, published, archived

    # --- 新增：经纬度字段 ---
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    # ... (之前的 relationships) ...
    category = db.relationship('Category', backref='locations')
    reviews = db.relationship('Review', backref='location', lazy=True, cascade="all, delete-orphan")
    # --- 核心修复：将 backref 修改为 back_populates ---
    wiki_suggestions = db.relationship('WikiSuggestion', back_populates='location', lazy='dynamic', cascade="all, delete-orphan")

    tags = db.relationship('Tag', secondary=location_tags, lazy='subquery', backref=db.backref('locations', lazy=True))

    # tags = db.relationship('Tag', secondary=db.Table('location_tags', db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True), db.Column('location_id', db.Integer, db.ForeignKey('locations.id'), primary_key=True)), lazy='subquery', backref=db.backref('locations', lazy=True))
    # # 新增：评论的回复列表
    # replies = db.relationship('ReviewReply', back_populates='review', lazy='dynamic', cascade='all, delete-orphan')
    # suggestions = db.relationship('WikiSuggestion', backref='location', lazy=True, cascade="all, delete-orphan")

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    parent = db.relationship('Category', remote_side=[id], backref='children')

class Review(db.Model):
    # ... (之前的字段) ...
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    images = db.Column(JSON)
    # likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)

    # 新增字段
    status = db.Column(db.String(20), default='pending', nullable=False) # pending, approved, rejected
    # --- 核心修复：统一使用 back_populates 定义双向关系 ---
    likes = db.relationship('ReviewLike', back_populates='review', lazy='dynamic', cascade="all, delete-orphan")
    replies = db.relationship('ReviewReply', back_populates='review', lazy='dynamic', cascade="all, delete-orphan")
    reports = db.relationship('ReviewReport', back_populates='review', lazy='dynamic', cascade="all, delete-orphan")
    
    # --- 新增：与 Tag 的多对多关系 ---
    tags = db.relationship('Tag', secondary=review_tags, lazy='subquery', backref=db.backref('reviews', lazy=True))
    # --- 新增：审核备注 ---
    reviewer_note = db.Column(db.Text, nullable=True)

    # tags = db.relationship('Tag', secondary=db.Table('review_tags', db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True), db.Column('review_id', db.Integer, db.ForeignKey('reviews.id'), primary_key=True)), lazy='subquery', backref=db.backref('reviews', lazy=True))
    # # --- 新增：评论的回复列表 ---
    # replies = db.relationship('ReviewReply', back_populates='review', lazy='dynamic', cascade='all, delete-orphan')
    # # 新增：评论收到的举报列表
    # reports = db.relationship('ReviewReport', back_populates='review', lazy='dynamic', cascade='all, delete-orphan')

# --- 新增：标签模型 ---
class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# --- 新增：评论点赞的关联模型 ---
class ReviewLike(db.Model):
    __tablename__ = 'review_likes'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'), primary_key=True)
    # --- 核心修复：添加反向关系 ---
    user = db.relationship('User')
    review = db.relationship('Review', back_populates='likes')
# --- 新增：评论举报模型 ---
class ReviewReport(db.Model):
    __tablename__ = 'review_reports'
    id = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False) # pending, resolved, dismissed
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # 外键
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id', ondelete='CASCADE'), nullable=False)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # 关系
    review = db.relationship('Review', back_populates='reports')
    # --- 新增：审核备注 ---
    reviewer_note = db.Column(db.Text, nullable=True)
    # 唯一约束：防止同一用户重复举报同一条评论
    __table_args__ = (db.UniqueConstraint('reporter_id', 'review_id', name='_reporter_review_uc'),)


# --- 新增：评论回复模型 ---
class ReviewReply(db.Model):
    __tablename__ = 'review_replies'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # 外键
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # 关系
    review = db.relationship('Review', back_populates='replies')
    # 新增：回复收到的举报列表
    reports = db.relationship('ReviewReplyReport', back_populates='reply', lazy='dynamic', cascade='all, delete-orphan')

# --- 新增：评论回复举报模型 ---
class ReviewReplyReport(db.Model):
    __tablename__ = 'review_reply_reports'
    id = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.String(255), nullable=False) # 举报原因
    status = db.Column(db.String(20), default='pending', nullable=False) # 状态: pending, resolved, dismissed
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # 外键
    reply_id = db.Column(db.Integer, db.ForeignKey('review_replies.id', ondelete='CASCADE'), nullable=False)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # 关系
    reply = db.relationship('ReviewReply', back_populates='reports')

    # 唯一约束：防止同一用户重复举报同一条回复
    __table_args__ = (db.UniqueConstraint('reporter_id', 'reply_id', name='_reporter_reply_uc'),)


class WikiSuggestion(db.Model):
    __tablename__ = 'wiki_suggestions'
    
    id = db.Column(db.Integer, primary_key=True)
    # --- 核心修改：移除旧的 title 字段，添加 type 字段 ---
    # title = db.Column(db.String(200)) 
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False, default='general') # 新增 type 字段
    
    reason = db.Column(db.Text) # 保留 reason 字段，可用于管理员备注或未来扩展
    status = db.Column(db.String(20), default='pending', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    reviewer_note = db.Column(db.Text, nullable=True)
    
    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # 确保 user_id 可选
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=True)
    
    # --- 核心修复：确保 back_populates 的名称与 User 模型中的关系名匹配 ---
    author = db.relationship('User', back_populates='wiki_suggestions')
    location = db.relationship('Location', back_populates='wiki_suggestions')

    
class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    building_id = db.Column(db.Integer, nullable=True) # 假设与地点/建筑关联
    wiki_id = db.Column(db.Integer, nullable=True) # 假设与百科/文章关联
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # 可以添加一个唯一约束确保一个用户对一个项目只能收藏一次
    __table_args__ = (db.UniqueConstraint('user_id', 'building_id', name='_user_building_uc'),)

# --- 新增后台管理模型 ---

class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(1024), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='editor') # e.g., 'admin', 'editor'
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # --- 新增：与操作日志的反向关系 ---
    action_logs = db.relationship('ActionLog', backref='admin', lazy='dynamic', cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class ActionLog(db.Model):
    __tablename__ = 'action_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'), index=True)
    action = db.Column(db.String(255), nullable=False) # e.g., 'login', 'update_profile', 'ban_account'
    details = db.Column(JSON) # 存储操作相关的附加上下文
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, index=True)

class SystemSetting(db.Model):
    __tablename__ = 'system_settings'
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(JSON, nullable=False)

class History(db.Model):
    __tablename__ = 'history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    building_id = db.Column(db.Integer, nullable=True)
    wiki_id = db.Column(db.Integer, nullable=True)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255))
    address = db.Column(db.String(255))
    last_visited = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    type = db.Column(db.String(50), nullable=False, default='system') # 'system', 'reply', 'like', 'report'
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    link = db.Column(db.String(255), nullable=True) # e.g., /locations/123?reviewId=45
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # --- 新增字段以符合文档要求 ---
    related_review_id = db.Column(db.Integer, db.ForeignKey('reviews.id', ondelete='SET NULL'), nullable=True)
    related_comment = db.Column(db.Text, nullable=True) # 评论内容快照

    # --- 关系 ---
    review = db.relationship('Review')

# --- 新增：路线收藏模型 ---
class FavoriteRoute(db.Model):
    __tablename__ = 'favorite_routes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100))
    start_id = db.Column(db.Integer, nullable=True) # 假设 building_id 存储在 locations 表
    end_id = db.Column(db.Integer, nullable=True)   # 假设 building_id 存储在 locations 表
    start_name = db.Column(db.String(100), nullable=False)
    end_name = db.Column(db.String(100), nullable=False)
    start_position = db.Column(db.Text)  # JSON string: [lng, lat]
    end_position = db.Column(db.Text)    # JSON string: [lng, lat]
    distance = db.Column(db.String(50), nullable=False)
    walk_time = db.Column(db.String(50), nullable=False)
    bike_time = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

# --- 新增：用于数据统计的日志模型 ---

class UserLoginLog(db.Model):
    """用户登录日志表"""
    __tablename__ = 'user_login_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    login_time = db.Column(db.DateTime, default=datetime.datetime.utcnow, index=True)
    ip_address = db.Column(db.String(45))

class LocationView(db.Model):
    """地点浏览记录表"""
    __tablename__ = 'location_views'
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    viewed_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, index=True)

class SearchLog(db.Model):
    """用户搜索日志表"""
    __tablename__ = 'search_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    keyword = db.Column(db.String(255), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# --- 新增：用户操作日志模型 ---
class UserLog(db.Model):
    __tablename__ = 'user_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    action = db.Column(db.String(50), nullable=False, index=True)
    detail = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, index=True)
    ip = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    
    user = db.relationship('User', backref=db.backref('logs', lazy='dynamic'))
