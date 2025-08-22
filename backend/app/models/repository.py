# -*- coding: utf-8 -*-
"""
仓库数据模型
定义Git仓库表结构和相关方法
"""

from datetime import datetime
from app import db
from cryptography.fernet import Fernet
from flask import current_app

class Repository(db.Model):
    """
    仓库模型类
    
    Attributes:
        id (int): 仓库唯一标识
        user_id (int): 所属用户ID
        name (str): 仓库名称
        url (str): 仓库URL
        api_key_encrypted (str): 加密的API密钥
        platform (str): Git平台类型
        project_id (str): 项目ID（云效专用）
        is_active (bool): 是否激活监控
        last_sync_at (datetime): 最后同步时间
        sync_status (str): 同步状态
        created_at (datetime): 创建时间
        updated_at (datetime): 更新时间
    """
    
    __tablename__ = 'repositories'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    api_key_encrypted = db.Column(db.Text, nullable=False)
    platform = db.Column(db.String(50), nullable=False, default='yunxiao')
    project_id = db.Column(db.String(100), nullable=True)  # 云效项目ID
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_sync_at = db.Column(db.DateTime, nullable=True)
    sync_status = db.Column(db.String(50), default='pending')  # pending, syncing, success, error
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关联关系
    commits = db.relationship('Commit', backref='repository', lazy='dynamic', cascade='all, delete-orphan')
    merge_requests = db.relationship('MergeRequest', backref='repository', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, user_id, name, url, api_key, platform='yunxiao', project_id=None):
        """
        初始化仓库实例
        
        Args:
            user_id (int): 用户ID
            name (str): 仓库名称
            url (str): 仓库URL
            api_key (str): API密钥
            platform (str): 平台类型
            project_id (str): 项目ID
        """
        self.user_id = user_id
        self.name = name
        self.url = url
        self.platform = platform
        self.project_id = project_id
        self.set_api_key(api_key)
    
    def set_api_key(self, api_key):
        """
        设置并加密API密钥
        
        Args:
            api_key (str): 明文API密钥
        """
        if api_key:
            key = current_app.config['ENCRYPTION_KEY'].encode()
            f = Fernet(key)
            self.api_key_encrypted = f.encrypt(api_key.encode()).decode()
    
    def get_api_key(self):
        """
        获取解密后的API密钥
        
        Returns:
            str: 解密后的API密钥
        """
        if self.api_key_encrypted:
            try:
                key = current_app.config['ENCRYPTION_KEY'].encode()
                f = Fernet(key)
                return f.decrypt(self.api_key_encrypted.encode()).decode()
            except Exception:
                return None
        return None
    
    def update_sync_status(self, status, sync_time=None):
        """
        更新同步状态
        
        Args:
            status (str): 同步状态
            sync_time (datetime): 同步时间
        """
        self.sync_status = status
        if sync_time:
            self.last_sync_at = sync_time
        else:
            self.last_sync_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self, include_api_key=False):
        """
        将仓库对象转换为字典
        
        Args:
            include_api_key (bool): 是否包含API密钥
        
        Returns:
            dict: 仓库信息字典
        """
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'url': self.url,
            'platform': self.platform,
            'project_id': self.project_id,
            'is_active': self.is_active,
            'sync_status': self.sync_status,
            'last_sync_at': self.last_sync_at.isoformat() if self.last_sync_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_api_key:
            data['api_key'] = self.get_api_key()
        
        return data
    
    def update_info(self, **kwargs):
        """
        更新仓库信息
        
        Args:
            **kwargs: 要更新的字段
        """
        allowed_fields = ['name', 'url', 'platform', 'project_id', 'is_active']
        
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(self, field):
                setattr(self, field, value)
            elif field == 'api_key':
                self.set_api_key(value)
        
        self.updated_at = datetime.utcnow()
    
    @staticmethod
    def find_by_user(user_id, active_only=False):
        """
        根据用户ID查找仓库列表
        
        Args:
            user_id (int): 用户ID
            active_only (bool): 是否只返回激活的仓库
        
        Returns:
            list: 仓库列表
        """
        query = Repository.query.filter_by(user_id=user_id)
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        return query.all()
    
    @staticmethod
    def find_by_id(repo_id):
        """
        根据ID查找仓库
        
        Args:
            repo_id (int): 仓库ID
        
        Returns:
            Repository: 仓库对象或None
        """
        return Repository.query.get(repo_id)
    
    @staticmethod
    def find_active_repositories():
        """
        查找所有激活的仓库
        
        Returns:
            list: 激活的仓库列表
        """
        return Repository.query.filter_by(is_active=True).all()
    
    def get_commit_count(self):
        """
        获取仓库的提交数量
        
        Returns:
            int: 提交数量
        """
        return self.commits.count()
    
    def get_merge_request_count(self):
        """
        获取仓库的合并请求数量
        
        Returns:
            int: 合并请求数量
        """
        return self.merge_requests.count()
    
    def __repr__(self):
        """
        仓库对象的字符串表示
        
        Returns:
            str: 仓库对象描述
        """
        return f'<Repository {self.name}>'