# -*- coding: utf-8 -*-
"""
用户数据模型
定义用户表结构和相关方法
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model):
    """
    用户模型类
    
    Attributes:
        id (int): 用户唯一标识
        username (str): 用户名
        email (str): 邮箱地址
        password_hash (str): 密码哈希值
        is_active (bool): 用户是否激活
        created_at (datetime): 创建时间
        updated_at (datetime): 更新时间
    """
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关联关系
    repositories = db.relationship('Repository', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, username, email, password):
        """
        初始化用户实例
        
        Args:
            username (str): 用户名
            email (str): 邮箱地址
            password (str): 明文密码
        """
        self.username = username
        self.email = email
        self.set_password(password)
    
    def set_password(self, password):
        """
        设置用户密码
        
        Args:
            password (str): 明文密码
        """
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """
        验证用户密码
        
        Args:
            password (str): 待验证的明文密码
        
        Returns:
            bool: 密码是否正确
        """
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_email=True):
        """
        将用户对象转换为字典
        
        Args:
            include_email (bool): 是否包含邮箱信息
        
        Returns:
            dict: 用户信息字典
        """
        data = {
            'id': self.id,
            'username': self.username,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_email:
            data['email'] = self.email
        
        return data
    
    def update_profile(self, **kwargs):
        """
        更新用户资料
        
        Args:
            **kwargs: 要更新的字段
        """
        allowed_fields = ['username', 'email']
        
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(self, field):
                setattr(self, field, value)
        
        self.updated_at = datetime.utcnow()
    
    @staticmethod
    def find_by_username(username):
        """
        根据用户名查找用户
        
        Args:
            username (str): 用户名
        
        Returns:
            User: 用户对象或None
        """
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def find_by_email(email):
        """
        根据邮箱查找用户
        
        Args:
            email (str): 邮箱地址
        
        Returns:
            User: 用户对象或None
        """
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def find_by_id(user_id):
        """
        根据ID查找用户
        
        Args:
            user_id (int): 用户ID
        
        Returns:
            User: 用户对象或None
        """
        return User.query.get(user_id)
    
    def __repr__(self):
        """
        用户对象的字符串表示
        
        Returns:
            str: 用户对象描述
        """
        return f'<User {self.username}>'