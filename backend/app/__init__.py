# -*- coding: utf-8 -*-
"""
Flask应用工厂
创建和配置Flask应用实例
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from config import config
import logging
from logging.handlers import RotatingFileHandler
import os

# 初始化扩展
db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
migrate = Migrate()

def create_app(config_name='default'):
    """
    应用工厂函数
    
    Args:
        config_name (str): 配置名称 ('development', 'production', 'testing')
    
    Returns:
        Flask: 配置好的Flask应用实例
    """
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, origins=app.config['CORS_ORIGINS'])
    migrate.init_app(app, db)
    
    # 导入所有模型以确保Flask-Migrate能够检测到它们
    from app.models import User, Repository, Commit, MergeRequest, AnalyticsCache, IntegrationConfig
    
    # 注册蓝图
    from app.api import auth_bp, repository_bp, analytics_bp
    print(f"注册蓝图: auth_bp = {auth_bp}")
    print(f"注册蓝图: repository_bp = {repository_bp}")
    print(f"注册蓝图: analytics_bp = {analytics_bp}")
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(repository_bp, url_prefix='/api/repositories')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    
    print("蓝图注册完成")
    print("已注册的路由:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint} [{', '.join(rule.methods)}]")
    
    # 添加健康检查端点
    @app.route('/health')
    def health_check():
        """健康检查端点"""
        return {'status': 'healthy', 'message': 'API is running'}, 200
    
    # 添加API信息端点
    @app.route('/api/info')
    def api_info():
        """API信息端点"""
        return {
            'name': 'Coding Efficiency Analytics API',
            'version': '1.0.0',
            'description': '软件开发团队效率统计分析工具API',
            'endpoints': {
                'auth': '/api/auth',
                'repositories': '/api/repositories',
                'analytics': '/api/analytics'
            },
            'documentation': '/api/docs'
        }, 200
    
    # 配置日志
    configure_logging(app)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 注册JWT回调
    register_jwt_callbacks(app)
    
    return app

def configure_logging(app):
    """
    配置应用日志
    
    Args:
        app (Flask): Flask应用实例
    """
    if not app.debug and not app.testing:
        # 生产环境日志配置
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Application startup')

def register_error_handlers(app):
    """
    注册全局错误处理器
    
    Args:
        app (Flask): Flask应用实例
    """
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import request
        return {'error': 'Resource not found', 'path': request.path, 'method': request.method}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(400)
    def bad_request_error(error):
        return {'error': 'Bad request'}, 400
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        return {'error': 'Unauthorized'}, 401
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return {'error': 'Forbidden'}, 403

def register_jwt_callbacks(app):
    """
    注册JWT回调函数
    
    Args:
        app (Flask): Flask应用实例
    """
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {'error': 'Token has expired'}, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {'error': 'Invalid token'}, 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {'error': 'Authorization token is required'}, 401