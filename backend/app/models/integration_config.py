# -*- coding: utf-8 -*-
"""
集成配置数据模型
定义集成配置表结构和相关方法
"""

from datetime import datetime
from app import db
from cryptography.fernet import Fernet
from flask import current_app

class IntegrationConfig(db.Model):
    """
    集成配置模型类
    
    Attributes:
        id (int): 配置唯一标识
        user_id (int): 所属用户ID
        platform (str): 平台类型 (yunxiao, github, gitlab)
        config_name (str): 配置名称
        api_url (str): API地址
        access_token_encrypted (str): 加密的访问令牌
        organization (str): 组织/命名空间
        is_active (bool): 是否启用
        last_test_at (datetime): 最后测试时间
        test_status (str): 测试状态 (success, failed, pending)
        test_message (str): 测试结果消息
        created_at (datetime): 创建时间
        updated_at (datetime): 更新时间
    """
    
    __tablename__ = 'integration_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    platform = db.Column(db.String(50), nullable=False, index=True)  # yunxiao, github, gitlab
    config_name = db.Column(db.String(255), nullable=False)
    api_url = db.Column(db.String(500), nullable=False)
    access_token_encrypted = db.Column(db.Text, nullable=False)
    organization = db.Column(db.String(255), nullable=True)  # 组织或命名空间
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_test_at = db.Column(db.DateTime, nullable=True)
    test_status = db.Column(db.String(20), default='pending')  # success, failed, pending
    test_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 复合索引
    __table_args__ = (
        db.Index('idx_user_platform', 'user_id', 'platform'),
        db.UniqueConstraint('user_id', 'platform', 'config_name', name='uq_user_platform_config'),
    )
    
    def __init__(self, user_id, platform, config_name, api_url, access_token, organization=None):
        """
        初始化集成配置实例
        
        Args:
            user_id (int): 用户ID
            platform (str): 平台类型
            config_name (str): 配置名称
            api_url (str): API地址
            access_token (str): 访问令牌（明文）
            organization (str): 组织名称
        """
        self.user_id = user_id
        self.platform = platform
        self.config_name = config_name
        self.api_url = api_url
        self.organization = organization
        self.set_access_token(access_token)
    
    def set_access_token(self, access_token):
        """
        设置加密的访问令牌
        
        Args:
            access_token (str): 明文访问令牌
        """
        if access_token:
            key = current_app.config.get('ENCRYPTION_KEY')
            if not key:
                # 如果没有配置加密密钥，使用默认密钥
                key = 'HmzbMbCbkQDsdFxtlMO00BfOzIWYx3oSmysTOqSsYIQ='
            
            # 确保密钥是bytes格式
            if isinstance(key, str):
                key = key.encode()
            
            cipher_suite = Fernet(key)
            self.access_token_encrypted = cipher_suite.encrypt(access_token.encode()).decode()
    
    def get_access_token(self):
        """
        获取解密的访问令牌
        
        Returns:
            str: 明文访问令牌
        """
        if self.access_token_encrypted:
            try:
                key = current_app.config.get('ENCRYPTION_KEY')
                if not key:
                    # 如果没有配置加密密钥，使用默认密钥
                    key = 'HmzbMbCbkQDsdFxtlMO00BfOzIWYx3oSmysTOqSsYIQ='
                
                # 确保密钥是bytes格式
                if isinstance(key, str):
                    key = key.encode()
                
                cipher_suite = Fernet(key)
                return cipher_suite.decrypt(self.access_token_encrypted.encode()).decode()
            except Exception:
                return None
        return None
    
    def update_test_result(self, status, message=None):
        """
        更新测试结果
        
        Args:
            status (str): 测试状态 (success, failed)
            message (str): 测试消息
        """
        self.test_status = status
        self.test_message = message
        self.last_test_at = datetime.utcnow()
    
    def to_dict(self, include_token=False):
        """
        转换为字典格式
        
        Args:
            include_token (bool): 是否包含访问令牌
        
        Returns:
            dict: 配置信息字典
        """
        result = {
            'id': self.id,
            'platform': self.platform,
            'config_name': self.config_name,
            'api_url': self.api_url,
            'organization': self.organization,
            'is_active': self.is_active,
            'last_test_at': self.last_test_at.isoformat() if self.last_test_at else None,
            'test_status': self.test_status,
            'test_message': self.test_message,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_token:
            result['access_token'] = self.get_access_token()
        
        return result
    
    @classmethod
    def get_by_user_and_platform(cls, user_id, platform):
        """
        根据用户ID和平台获取配置
        
        Args:
            user_id (int): 用户ID
            platform (str): 平台类型
        
        Returns:
            IntegrationConfig: 配置实例或None
        """
        return cls.query.filter_by(user_id=user_id, platform=platform, is_active=True).first()
    
    @classmethod
    def get_user_configs(cls, user_id):
        """
        获取用户的所有集成配置
        
        Args:
            user_id (int): 用户ID
        
        Returns:
            list: 配置列表
        """
        return cls.query.filter_by(user_id=user_id).order_by(cls.platform, cls.config_name).all()
    
    def __repr__(self):
        return f'<IntegrationConfig {self.platform}:{self.config_name}>'