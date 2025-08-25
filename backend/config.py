# -*- coding: utf-8 -*-
"""
应用配置文件
定义不同环境下的配置选项
"""

import os
from datetime import timedelta
from pathlib import Path

# 获取项目根目录
BASE_DIR = Path(__file__).parent
PROJECT_ROOT = BASE_DIR.parent

class Config:
    """
    基础配置类
    包含所有环境通用的配置选项
    """
    
    # 应用基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    APP_NAME = 'Coding Efficiency Analytics'
    APP_VERSION = '1.0.0'
    
    # 数据库配置
    # 使用绝对路径确保SQLite可以正确找到数据库文件
    # 确保instance目录存在
    instance_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance')
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir)
    
    # 使用正斜杠替换反斜杠，避免Windows路径问题
    db_path = os.path.join(instance_dir, 'app.db').replace('\\', '/')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{db_path}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {'check_same_thread': False}
    }
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ALGORITHM = 'HS256'
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    
    # CORS配置
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000').split(',')
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    
    # 限流配置
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'memory://'
    RATELIMIT_DEFAULT = '100 per hour'
    RATELIMIT_HEADERS_ENABLED = True
    
    # 分页配置
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    POSTS_PER_PAGE = 20  # 保持向后兼容
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'json'}
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = BASE_DIR / 'logs' / 'app.log'
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # 缓存配置
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = 300  # 5分钟
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    
    # 邮件配置
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Git平台配置
    SUPPORTED_GIT_PLATFORMS = {
        'aliyunxiao': {
            'name': '阿里云效',
            'api_base_url': 'https://devops.aliyun.com/api',
            'auth_type': 'token',
            'rate_limit': '1000 per hour'
        },
        'gitlab': {
            'name': 'GitLab',
            'api_base_url': 'https://gitlab.com/api/v4',
            'auth_type': 'token',
            'rate_limit': '2000 per hour'
        },
        'github': {
            'name': 'GitHub',
            'api_base_url': 'https://api.github.com',
            'auth_type': 'token',
            'rate_limit': '5000 per hour'
        }
    }
    
    # 阿里云效API配置（保持向后兼容）
    YUNXIAO_API_BASE_URL = 'https://devops.aliyun.com/api/v4'
    
    # 阿里云效API配置（从环境变量读取）
    ALIYUNXIAO_API_BASE_URL = os.environ.get('ALIYUNXIAO_API_BASE_URL')
    ALIYUNXIAO_ACCESS_TOKEN = os.environ.get('ALIYUNXIAO_ACCESS_TOKEN')
    ALIYUNXIAO_ORGANIZATION_ID = os.environ.get('ALIYUNXIAO_ORGANIZATION_ID')
    
    # 数据同步配置
    SYNC_BATCH_SIZE = 100
    SYNC_MAX_RETRIES = 3
    SYNC_RETRY_DELAY = 5  # 秒
    SYNC_DEFAULT_DAYS = 30  # 默认同步最近30天的数据
    
    # 分析配置
    ANALYTICS_CACHE_TIMEOUT = 3600  # 1小时
    EFFICIENCY_SCORE_WEIGHTS = {
        'commit_frequency': 0.25,
        'code_quality': 0.20,
        'merge_request_ratio': 0.15,
        'consistency': 0.20,
        'collaboration': 0.20
    }
    
    # 安全配置
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_NUMBERS = True
    PASSWORD_REQUIRE_SPECIAL = False
    
    # API配置
    API_TITLE = 'Coding Efficiency Analytics API'
    API_VERSION = 'v1'
    API_DESCRIPTION = 'API for analyzing coding efficiency and productivity'
    
    # 任务调度配置
    SCHEDULER_API_ENABLED = True
    
    # 加密配置
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or 'bMVjgRWs9rReZ6fzeYeyn6udh0NeLMYRrj-cQAG8bp8='
    
    # 监控配置
    HEALTH_CHECK_ENABLED = True
    METRICS_ENABLED = os.environ.get('METRICS_ENABLED', 'false').lower() in ['true', 'on', '1']
    
    @staticmethod
    def init_app(app):
        """
        初始化应用配置
        
        Args:
            app: Flask应用实例
        """
        # 创建必要的目录
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.LOG_FILE.parent, exist_ok=True)
        
        # 设置日志
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug and not app.testing:
            # 文件日志
            file_handler = RotatingFileHandler(
                Config.LOG_FILE,
                maxBytes=Config.LOG_MAX_BYTES,
                backupCount=Config.LOG_BACKUP_COUNT
            )
            file_handler.setFormatter(logging.Formatter(Config.LOG_FORMAT))
            file_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
            app.logger.addHandler(file_handler)
            
            # 控制台日志
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(Config.LOG_FORMAT))
            console_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
            app.logger.addHandler(console_handler)
            
            app.logger.setLevel(getattr(logging, Config.LOG_LEVEL))
            app.logger.info(f'{Config.APP_NAME} startup')

class DevelopmentConfig(Config):
    """
    开发环境配置
    """
    DEBUG = True
    TESTING = False
    
    # 开发环境使用更宽松的限流
    RATELIMIT_DEFAULT = '1000 per hour'
    
    # 开发环境启用SQL查询日志
    SQLALCHEMY_ECHO = os.environ.get('SQLALCHEMY_ECHO', 'false').lower() in ['true', 'on', '1']
    
    # 开发环境缓存配置
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 60  # 1分钟，便于开发调试
    
    # 开发环境JWT配置（更短的过期时间便于测试）
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    
    # 开发环境加密密钥
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or 'bMVjgRWs9rReZ6fzeYeyn6udh0NeLMYRrj-cQAG8bp8='
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # 开发环境额外配置
        app.logger.info('Development mode enabled')
        
        # 如果使用SQLite，启用外键约束
        if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
            from sqlalchemy import event
            from sqlalchemy.engine import Engine
            
            @event.listens_for(Engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

class TestingConfig(Config):
    """
    测试环境配置
    """
    DEBUG = False
    TESTING = True
    
    # 测试环境使用内存数据库
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # 测试环境禁用CSRF保护
    WTF_CSRF_ENABLED = False
    
    # 测试环境使用简单缓存
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 1
    
    # 测试环境JWT配置（更短的过期时间）
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(hours=1)
    
    # 测试环境禁用限流
    RATELIMIT_ENABLED = False
    
    # 测试环境日志配置
    LOG_LEVEL = 'DEBUG'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # 测试环境额外配置
        app.logger.info('Testing mode enabled')
        
        # 禁用邮件发送
        app.config['MAIL_SUPPRESS_SEND'] = True

class ProductionConfig(Config):
    """
    生产环境配置
    """
    DEBUG = False
    TESTING = False
    
    # 生产环境必须设置的环境变量
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # 生产环境额外配置
        app.logger.info('Production mode enabled')
        
        # 检查必要的环境变量
        required_env_vars = [
            'SECRET_KEY',
            'JWT_SECRET_KEY',
            'DATABASE_URL'
        ]
        
        missing_vars = []
        for var in required_env_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise RuntimeError(
                f'Missing required environment variables: {", ".join(missing_vars)}'
            )
        
        # 生产环境安全检查
        if app.config['SECRET_KEY'] == 'dev-secret-key-change-in-production':
            raise RuntimeError('Must set SECRET_KEY environment variable in production')
        
        # 生产环境使用Redis缓存
        if not app.config.get('CACHE_REDIS_URL'):
            app.logger.warning('REDIS_URL not set, using simple cache in production')
        else:
            app.config['CACHE_TYPE'] = 'redis'
            app.config['CACHE_REDIS_URL'] = app.config['CACHE_REDIS_URL']
        
        # 生产环境错误处理
        import logging
        from logging.handlers import SMTPHandler
        
        # 邮件错误通知（如果配置了邮件）
        if app.config.get('MAIL_SERVER'):
            auth = None
            if app.config.get('MAIL_USERNAME'):
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            
            secure = None
            if app.config.get('MAIL_USE_TLS'):
                secure = ()
            
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr=app.config['MAIL_DEFAULT_SENDER'],
                toaddrs=[app.config['MAIL_DEFAULT_SENDER']],
                subject=f'{Config.APP_NAME} Error',
                credentials=auth,
                secure=secure
            )
            mail_handler.setLevel(logging.ERROR)
            mail_handler.setFormatter(logging.Formatter(
                '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
            ))
            app.logger.addHandler(mail_handler)

class DockerConfig(ProductionConfig):
    """
    Docker容器环境配置
    """
    
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)
        
        # Docker环境额外配置
        app.logger.info('Docker mode enabled')
        
        # Docker环境日志输出到stdout
        import logging
        import sys
        
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s'
        ))
        app.logger.addHandler(stream_handler)

# 配置映射
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'docker': DockerConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """
    获取配置类
    
    Args:
        config_name (str): 配置名称
    
    Returns:
        Config: 配置类
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config.get(config_name, config['default'])