import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app
from ..models.models import User, Admin

def create_token(user_id):
    """为普通用户创建JWT"""
    # 设置过期时间为30天
    expires_delta = datetime.timedelta(days=30)
    expires_in_seconds = int(expires_delta.total_seconds())
    
    payload = {
        'exp': datetime.datetime.utcnow() + expires_delta,
        'iat': datetime.datetime.utcnow(),
        'sub': str(user_id),
        'type': 'user' # --- 核心修复：为普通用户token添加type字段 ---
    }
    token = jwt.encode(
        payload,
        current_app.config.get('SECRET_KEY'),
        algorithm='HS256'
    )
    # 返回令牌和过期秒数
    return token, expires_in_seconds

def token_required(f=None, optional=False): # <-- 核心修改：增加 optional 参数
    if f is None:
        return lambda func: token_required(func, optional=optional)

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]

        if not token:
            if optional: # <-- 核心修改：如果 token 是可选的，直接将 None 作为 current_user 传入
                return f(None, *args, **kwargs)
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            # if data.get('type') == 'admin':
            #     # 如果需要，可以处理管理员token，但这里我们主要关心普通用户
            #     current_user = None
            # else:
            current_user = User.query.get(data['sub'])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        if not current_user and not optional: # 如果找不到用户且认证不是可选的
             return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            payload = jwt.decode(token, current_app.config.get('SECRET_KEY'), algorithms=['HS256'])
            
            # --- 核心修改：检查 type 字段 ---
            if payload.get('type') != 'admin':
                return jsonify({'message': 'Forbidden: Admin access required.'}), 403
                
            current_admin = Admin.query.get(payload['sub'])
            if not current_admin:
                return jsonify({'message': 'Admin user not found.'}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401

        return f(current_admin, *args, **kwargs)
    return decorated

def create_admin_token(admin_id):
    """为管理员生成 JWT"""
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
            'iat': datetime.datetime.utcnow(),
            'sub': str(admin_id),
            'type': 'admin' # 添加类型以区分普通用户 token
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return str(e)
    
# --- 新增：Wiki 编辑权限装饰器 ---
def wiki_editor_required(f):
    """
    装饰器：验证用户是否为 Wiki 编辑者或管理员。
    它会向被装饰的函数传递两个参数：
    1. current_user: User 或 Admin 对象。
    2. is_admin: 布尔值，指示用户是否为管理员级别的编辑者。
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            payload = jwt.decode(token, current_app.config.get('SECRET_KEY'), algorithms=['HS256'])
            
            # 场景1：管理员 Token
            if payload.get('type') == 'admin':
                current_admin = Admin.query.get(payload['sub'])
                if not current_admin:
                    return jsonify({'message': 'Admin user not found.'}), 401
                # 管理员拥有所有权限，调用函数并传入 Admin 对象和 is_admin=True
                return f(current_admin, *args, **kwargs, is_admin=True)

            # 场景2：普通用户 Token
            else:
                current_user = User.query.get(payload['sub'])
                if not current_user:
                    return jsonify({'message': 'User not found.'}), 401
                
                # 检查用户角色是否为 'wiki_editor' 或 'admin'
                if current_user.role in ['wiki_editor', 'admin']:
                    # 角色符合，调用函数并传入 User 对象和 is_admin=True
                    return f(current_user, *args, **kwargs, is_admin=True)
                else:
                    # 角色不符合，权限不足
                    return jsonify({'message': 'Forbidden: Wiki editor access required.'}), 403

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401

    return decorated