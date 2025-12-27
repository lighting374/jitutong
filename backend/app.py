import os
from flask import Flask, jsonify, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix # 1. 导入 ProxyFix
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os
from datetime import datetime
# 从 .models 模块导入 db 实例
# 导入模型类是为了让 Flask-Migrate 能够识别它们
from .models.models import db, User, Admin, Location, Review, Category, Tag

# 从 .routers 模块导入所有蓝图
from .routers.users import user_bp
from .routers.locations import location_bp
from .routers.reviews import reviews_bp
from .routers.admin_routes import admin_bp
from .routers.routes import routes_bp # --- 新增导入 ---
# --- 新增：导入 search_bp ---
from .routers.search import search_bp

def create_app():
    # --- 新增的调试日志 ---
    print(f"--- Jitutong App Reloaded at {datetime.utcnow().isoformat()} ---")
    """
    应用工厂函数，用于创建和配置 Flask 应用实例。
    """
    # 修改 Flask 实例的创建，指定静态文件路径
    app = Flask(__name__, static_folder='static', static_url_path='')
    
    # --- 新增：配置上传文件夹 ---
    # 路径相对于项目根目录
    app.config['UPLOAD_FOLDER'] = 'backend/static/uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 限制上传大小为 16MB

    # 确保上传文件夹存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # # --- 配置 ---
    # # 从环境变量获取密钥，如果不存在则使用一个默认的开发密钥
    # app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-secure-default-secret-key-for-development')
    
    # # 数据库配置 (使用 SQLite 作为默认)
    # # 生产环境建议使用 PostgreSQL: 'postgresql://user:password@host:port/dbname'
    # db_path = os.path.join(os.path.dirname(__file__), 'jitutong.db')
    # # 默认使用开发环境的 MySQL 连接
    # default_db_uri = 'mysql+pymysql://jitutong_user:Your_New_ASCII_Password_123@localhost/jitutong'
    try:
        app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
    except KeyError:
        raise RuntimeError("FATAL: SECRET_KEY environment variable is not set.")

    # 数据库配置
    # 同样，对 DATABASE_URL 也使用更严格的检查
    try:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    except KeyError:
        raise RuntimeError("FATAL: DATABASE_URL environment variable is not set.")
  
    # app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', default_db_uri)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_AS_ASCII'] = False # 支持中文字符正常显示

    # --- 初始化扩展 ---
    # 启用跨域资源共享 (CORS)，允许前端访问 API
    # 生产环境中应将 "*" 替换为你的前端域名
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # =====================================================
    # 关键修复：添加 ProxyFix 中间件
    # =====================================================
    # 告诉 ProxyFix 我们信任来自反向代理（Nginx）的一个 'X-Forwarded-For' 和一个 'X-Forwarded-Host' 头。
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )
    # =====================================================

    # 初始化数据库 ORM
    db.init_app(app)
    
    # 初始化数据库迁移工具
    Migrate(app, db)

    # --- 注册蓝图 ---
    app.register_blueprint(user_bp)
    app.register_blueprint(location_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(routes_bp) # --- 新增注册 ---
    app.register_blueprint(search_bp)

    # --- 定义根路由/健康检查路由 ---
    @app.route('/')
    def index():
        return jsonify({"status": "ok", "message": "Jitutong API is running."})

    return app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 运行 Flask 应用
    # debug=True 会在代码更改后自动重载，并提供详细的错误页面
    # 生产环境中应使用 Gunicorn 或 uWSGI 等 WSGI 服务器运行
    app.run(debug=True, host='0.0.0.0', port=5000)

# # 在 PowerShell 中
# $env:FLASK_APP="backend.app:app"
# $env:FLASK_ENV="development"
# $env:SECRET_KEY="your-own-strong-secret-key"

# flask run --host=0.0.0.0 --port=5000


# export FLASK_APP="backend.app:app"
# export DATABASE_URL="mysql+pymysql://jitutong_user:Your_New_ASCII_Password_123@localhost/jitutong"
# export SECRET_KEY="MY_SECRET_KEY"

# source /home/jcy/backend/backend/bin/activate

# flask db init
# flask db migrate -m "Initial migration."
# flask db upgrade


# sudo systemctl start jitutong
# sudo systemctl enable jitutong

# # 检查服务状态，确保没有错误
# sudo systemctl status jitutong

# journalctl -u jitutong.service -n 50 --no-pager
# sudo systemctl restart jitutong

# sudo nano /etc/nginx/sites-available/jitutong
# sudo nginx -t
# sudo systemctl restart nginx

# sudo cp -r dist/* /var/www/jitutong/
# sudo chown -R www-data:www-data /var/www/jitutong
# sudo find /var/www/jitutong -type d -exec chmod 755 {} \;
# sudo find /var/www/jitutong -type f -exec chmod 644 {} \;
# sudo systemctl restart nginx

#sudo cp -r dist/* /var/www/jitutong/ && sudo chown -R www-data:www-data /var/www/jitutong && sudo find /var/www/jitutong -type d -exec chmod 755 {} \; && sudo find /var/www/jitutong -type f -exec chmod 644 {} \; && sudo systemctl restart nginx