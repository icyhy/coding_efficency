# -*- coding: utf-8 -*-
"""
Flask应用主文件
整合所有组件，配置应用和路由
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta
import os
import logging
from logging.handlers import RotatingFileHandler

from app.models import db, User
from app.api import api_bp
from app.utils.response import error_response, validation_error_response
from app.utils.crypto import hash_password

def create_app(config_name='development'):
    """
    创建Flask应用实例
    
    Args:
        config_name (str): 配置名称
    
    Returns:
        Flask: Flask应用实例
    """
    app = Flask(__name__)
    
    # 加载配置
    load_config(app, config_name)
    
    # 初始化扩展
    init_extensions(app)
    
    # 注册蓝图
    register_blueprints(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 配置日志
    configure_logging(app)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        create_default_admin(app)
    
    return app

def load_config(app, config_name):
    """
    加载应用配置
    
    Args:
        app (Flask): Flask应用实例
        config_name (str): 配置名称
    """
    # 基础配置
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False
    
    # JWT配置
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    app.config['JWT_ALGORITHM'] = 'HS256'
    
    # 数据库配置
    if config_name == 'production':
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
            'DATABASE_URL',
            'sqlite:///production.db'
        )
        app.config['DEBUG'] = False
    elif config_name == 'testing':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
    else:  # development
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
            'DATABASE_URL',
            'sqlite:///development.db'
        )
        app.config['DEBUG'] = True
    
    # 加密配置
    app.config['ENCRYPTION_KEY'] = os.environ.get('ENCRYPTION_KEY', 'default-encryption-key')
    
    # API限流配置
    app.config['RATELIMIT_STORAGE_URL'] = 'memory://'
    app.config['RATELIMIT_DEFAULT'] = '1000 per hour'
    
    # CORS配置
    app.config['CORS_ORIGINS'] = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # 文件上传配置
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
    
    # 日志配置
    app.config['LOG_LEVEL'] = os.environ.get('LOG_LEVEL', 'INFO')
    app.config['LOG_FILE'] = os.environ.get('LOG_FILE', 'logs/app.log')

def init_extensions(app):
    """
    初始化Flask扩展
    
    Args:
        app (Flask): Flask应用实例
    """
    # 初始化数据库
    db.init_app(app)
    
    # 初始化JWT
    jwt = JWTManager(app)
    
    # JWT错误处理
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return error_response("访问令牌已过期", status_code=401)
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return error_response("无效的访问令牌", status_code=401)
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return error_response("缺少访问令牌", status_code=401)
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return error_response("访问令牌已被撤销", status_code=401)
    
    # 初始化CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # 初始化限流器
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=[app.config['RATELIMIT_DEFAULT']]
    )
    
    # 限流错误处理
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return error_response(
            "请求频率过高，请稍后再试",
            status_code=429,
            details={'retry_after': str(e.retry_after)}
        )

def register_blueprints(app):
    """
    注册蓝图
    
    Args:
        app (Flask): Flask应用实例
    """
    # 注册API蓝图
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # 健康检查端点
    @app.route('/health')
    def health_check():
        """健康检查端点"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'version': '1.0.0'
        })
    
    # API信息端点
    @app.route('/api/info')
    def api_info():
        """API信息端点"""
        return jsonify({
            'name': 'Coding Efficiency Analytics API',
            'version': '1.0.0',
            'description': '软件开发团队效率统计分析工具API',
            'endpoints': {
                'auth': '/api/v1/auth',
                'repositories': '/api/v1/repositories',
                'analytics': '/api/v1/analytics'
            },
            'documentation': '/api/docs'
        })

def register_error_handlers(app):
    """
    注册错误处理器
    
    Args:
        app (Flask): Flask应用实例
    """
    @app.errorhandler(400)
    def bad_request(error):
        """处理400错误"""
        return validation_error_response("请求参数错误")
    
    @app.errorhandler(401)
    def unauthorized(error):
        """处理401错误"""
        return error_response("未授权访问", status_code=401)
    
    @app.errorhandler(403)
    def forbidden(error):
        """处理403错误"""
        return error_response("权限不足", status_code=403)
    
    @app.errorhandler(404)
    def not_found(error):
        """处理404错误"""
        return error_response("资源不存在", status_code=404)
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """处理405错误"""
        return error_response("请求方法不允许", status_code=405)
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        """处理413错误"""
        return error_response("请求实体过大", status_code=413)
    
    @app.errorhandler(500)
    def internal_error(error):
        """处理500错误"""
        app.logger.error(f"服务器内部错误: {str(error)}")
        db.session.rollback()
        return error_response("服务器内部错误", status_code=500)
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """处理未捕获的异常"""
        app.logger.error(f"未处理的异常: {str(error)}", exc_info=True)
        db.session.rollback()
        return error_response("服务器内部错误", status_code=500)

def configure_logging(app):
    """
    配置日志
    
    Args:
        app (Flask): Flask应用实例
    """
    if not app.debug and not app.testing:
        # 创建日志目录
        log_dir = os.path.dirname(app.config['LOG_FILE'])
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 配置文件日志处理器
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        # 设置日志级别
        log_level = getattr(logging, app.config['LOG_LEVEL'].upper())
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(log_level)
        
        app.logger.info('应用启动')

def create_default_admin(app):
    """
    创建默认管理员账户
    
    Args:
        app (Flask): Flask应用实例
    """
    try:
        # 检查是否已存在管理员账户
        admin_user = User.query.filter_by(email='admin@example.com').first()
        
        if not admin_user:
            # 创建默认管理员账户
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password_hash=hash_password('admin123'),
                is_admin=True,
                is_active=True
            )
            
            db.session.add(admin_user)
            db.session.commit()
            
            app.logger.info('默认管理员账户创建成功')
            print("默认管理员账户已创建:")
            print("邮箱: admin@example.com")
            print("密码: admin123")
            print("请在生产环境中修改默认密码！")
        
    except Exception as e:
        app.logger.error(f"创建默认管理员账户失败: {str(e)}")
        db.session.rollback()

# 请求前处理
@api_bp.before_request
def before_request():
    """
    请求前处理
    记录请求信息，验证内容类型等
    """
    # 记录请求信息
    if request.method in ['POST', 'PUT', 'PATCH']:
        if request.content_type and 'application/json' not in request.content_type:
            return validation_error_response("请求内容类型必须为application/json")

# 请求后处理
@api_bp.after_request
def after_request(response):
    """
    请求后处理
    添加安全头部，记录响应信息等
    
    Args:
        response: Flask响应对象
    
    Returns:
        Flask响应对象
    """
    # 添加安全头部
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # 添加API版本头部
    response.headers['X-API-Version'] = '1.0.0'
    
    return response

if __name__ == '__main__':
    from datetime import datetime
    
    # 创建应用
    app = create_app()
    
    # 运行应用
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    
    print(f"启动开发服务器: http://{host}:{port}")
    print("API文档: http://127.0.0.1:5000/api/info")
    print("健康检查: http://127.0.0.1:5000/health")
    
    app.run(
        host=host,
        port=port,
        debug=app.config.get('DEBUG', False)
    )