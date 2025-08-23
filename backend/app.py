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
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from app import db
from app.models import User
from app.api import api_bp
from app.utils.response import error_response, validation_error_response
from app.utils.crypto import hash_password
from config import config

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
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
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
        key_func=get_remote_address,
        default_limits=[app.config['RATELIMIT_DEFAULT']]
    )
    limiter.init_app(app)
    
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
    try:
        # 导入所有蓝图
        from app.api import auth_bp, repository_bp, analytics_bp
        
        # 注册各个功能模块的蓝图
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(repository_bp, url_prefix='/api/repositories')
        app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
        
        print(f"蓝图注册成功: auth_bp, repository_bp, analytics_bp")
        
        # 打印所有注册的路由
        print("已注册的路由:")
        for rule in app.url_map.iter_rules():
            print(f"  {rule.rule} -> {rule.endpoint} [{', '.join(rule.methods)}]")
        
    except Exception as e:
        print(f"蓝图注册失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
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
        return jsonify({"error": "Resource not found", "path": request.path}), 404
    
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

# 移除全局的before_request和after_request装饰器
# 这些功能现在由各个蓝图自己处理

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