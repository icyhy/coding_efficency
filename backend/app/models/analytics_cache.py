# -*- coding: utf-8 -*-
"""
分析缓存数据模型
定义分析结果缓存表结构和相关方法
"""

from datetime import datetime, timedelta
from app import db
import json

class AnalyticsCache(db.Model):
    """
    分析缓存模型类
    
    Attributes:
        id (int): 记录唯一标识
        cache_key (str): 缓存键
        cache_type (str): 缓存类型 (commit_stats, mr_stats, author_stats, time_distribution)
        repository_id (int): 所属仓库ID (可选)
        user_id (int): 所属用户ID (可选)
        parameters (str): 查询参数JSON
        result_data (str): 结果数据JSON
        expires_at (datetime): 过期时间
        created_at (datetime): 创建时间
        updated_at (datetime): 更新时间
    """
    
    __tablename__ = 'analytics_cache'
    
    id = db.Column(db.Integer, primary_key=True)
    cache_key = db.Column(db.String(255), nullable=False, unique=True, index=True)
    cache_type = db.Column(db.String(50), nullable=False, index=True)
    repository_id = db.Column(db.Integer, db.ForeignKey('repositories.id'), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    parameters = db.Column(db.Text, nullable=False)
    result_data = db.Column(db.Text, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 复合索引
    __table_args__ = (
        db.Index('idx_cache_type_repo', 'cache_type', 'repository_id'),
        db.Index('idx_cache_type_user', 'cache_type', 'user_id'),
        db.Index('idx_expires_at', 'expires_at'),
    )
    
    def __init__(self, cache_key, cache_type, parameters, result_data, 
                 expires_at=None, repository_id=None, user_id=None):
        """
        初始化分析缓存实例
        
        Args:
            cache_key (str): 缓存键
            cache_type (str): 缓存类型
            parameters (dict): 查询参数
            result_data (dict): 结果数据
            expires_at (datetime): 过期时间
            repository_id (int): 仓库ID
            user_id (int): 用户ID
        """
        self.cache_key = cache_key
        self.cache_type = cache_type
        self.repository_id = repository_id
        self.user_id = user_id
        self.parameters = json.dumps(parameters, ensure_ascii=False, default=str)
        self.result_data = json.dumps(result_data, ensure_ascii=False, default=str)
        
        # 默认缓存1小时
        if expires_at is None:
            self.expires_at = datetime.utcnow() + timedelta(hours=1)
        else:
            self.expires_at = expires_at
    
    def to_dict(self):
        """
        将缓存对象转换为字典
        
        Returns:
            dict: 缓存信息字典
        """
        return {
            'id': self.id,
            'cache_key': self.cache_key,
            'cache_type': self.cache_type,
            'repository_id': self.repository_id,
            'user_id': self.user_id,
            'parameters': self.get_parameters(),
            'result_data': self.get_result_data(),
            'expires_at': self.expires_at.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_expired': self.is_expired()
        }
    
    def get_parameters(self):
        """
        获取查询参数
        
        Returns:
            dict: 查询参数字典
        """
        try:
            return json.loads(self.parameters)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def get_result_data(self):
        """
        获取结果数据
        
        Returns:
            dict: 结果数据字典
        """
        try:
            return json.loads(self.result_data)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def update_result(self, result_data, expires_at=None):
        """
        更新缓存结果
        
        Args:
            result_data (dict): 新的结果数据
            expires_at (datetime): 新的过期时间
        """
        self.result_data = json.dumps(result_data, ensure_ascii=False, default=str)
        
        if expires_at:
            self.expires_at = expires_at
        else:
            # 延长1小时
            self.expires_at = datetime.utcnow() + timedelta(hours=1)
        
        self.updated_at = datetime.utcnow()
    
    def is_expired(self):
        """
        检查缓存是否过期
        
        Returns:
            bool: 是否过期
        """
        return datetime.utcnow() > self.expires_at
    
    def extend_expiry(self, hours=1):
        """
        延长缓存过期时间
        
        Args:
            hours (int): 延长小时数
        """
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)
        self.updated_at = datetime.utcnow()
    
    @staticmethod
    def generate_cache_key(cache_type, **kwargs):
        """
        生成缓存键
        
        Args:
            cache_type (str): 缓存类型
            **kwargs: 参数
        
        Returns:
            str: 缓存键
        """
        # 排序参数以确保一致性
        sorted_params = sorted(kwargs.items())
        params_str = '_'.join([f"{k}:{v}" for k, v in sorted_params if v is not None])
        return f"{cache_type}_{params_str}"
    
    @staticmethod
    def get_cache(cache_key):
        """
        获取缓存
        
        Args:
            cache_key (str): 缓存键
        
        Returns:
            AnalyticsCache or None: 缓存对象或None
        """
        cache = AnalyticsCache.query.filter_by(cache_key=cache_key).first()
        
        if cache and not cache.is_expired():
            return cache
        elif cache and cache.is_expired():
            # 删除过期缓存
            db.session.delete(cache)
            db.session.commit()
        
        return None
    
    @staticmethod
    def set_cache(cache_key, cache_type, parameters, result_data, 
                  expires_at=None, repository_id=None, user_id=None):
        """
        设置缓存
        
        Args:
            cache_key (str): 缓存键
            cache_type (str): 缓存类型
            parameters (dict): 查询参数
            result_data (dict): 结果数据
            expires_at (datetime): 过期时间
            repository_id (int): 仓库ID
            user_id (int): 用户ID
        
        Returns:
            AnalyticsCache: 缓存对象
        """
        # 检查是否已存在
        existing_cache = AnalyticsCache.query.filter_by(cache_key=cache_key).first()
        
        if existing_cache:
            # 更新现有缓存
            existing_cache.update_result(result_data, expires_at)
            db.session.commit()
            return existing_cache
        else:
            # 创建新缓存
            cache = AnalyticsCache(
                cache_key=cache_key,
                cache_type=cache_type,
                parameters=parameters,
                result_data=result_data,
                expires_at=expires_at,
                repository_id=repository_id,
                user_id=user_id
            )
            db.session.add(cache)
            db.session.commit()
            return cache
    
    @staticmethod
    def clear_expired_cache():
        """
        清理过期缓存
        
        Returns:
            int: 清理的缓存数量
        """
        expired_count = AnalyticsCache.query.filter(
            AnalyticsCache.expires_at < datetime.utcnow()
        ).count()
        
        AnalyticsCache.query.filter(
            AnalyticsCache.expires_at < datetime.utcnow()
        ).delete()
        
        db.session.commit()
        return expired_count
    
    @staticmethod
    def clear_cache_by_repository(repository_id):
        """
        清理指定仓库的缓存
        
        Args:
            repository_id (int): 仓库ID
        
        Returns:
            int: 清理的缓存数量
        """
        cache_count = AnalyticsCache.query.filter_by(repository_id=repository_id).count()
        
        AnalyticsCache.query.filter_by(repository_id=repository_id).delete()
        db.session.commit()
        
        return cache_count
    
    @staticmethod
    def clear_cache_by_user(user_id):
        """
        清理指定用户的缓存
        
        Args:
            user_id (int): 用户ID
        
        Returns:
            int: 清理的缓存数量
        """
        cache_count = AnalyticsCache.query.filter_by(user_id=user_id).count()
        
        AnalyticsCache.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        
        return cache_count
    
    @staticmethod
    def clear_cache_by_type(cache_type):
        """
        清理指定类型的缓存
        
        Args:
            cache_type (str): 缓存类型
        
        Returns:
            int: 清理的缓存数量
        """
        cache_count = AnalyticsCache.query.filter_by(cache_type=cache_type).count()
        
        AnalyticsCache.query.filter_by(cache_type=cache_type).delete()
        db.session.commit()
        
        return cache_count
    
    @staticmethod
    def get_cache_statistics():
        """
        获取缓存统计信息
        
        Returns:
            dict: 缓存统计信息
        """
        total_count = AnalyticsCache.query.count()
        expired_count = AnalyticsCache.query.filter(
            AnalyticsCache.expires_at < datetime.utcnow()
        ).count()
        
        # 按类型统计
        type_stats = db.session.query(
            AnalyticsCache.cache_type,
            db.func.count(AnalyticsCache.id).label('count')
        ).group_by(AnalyticsCache.cache_type).all()
        
        return {
            'total_count': total_count,
            'expired_count': expired_count,
            'active_count': total_count - expired_count,
            'type_statistics': [{
                'cache_type': stat.cache_type,
                'count': stat.count
            } for stat in type_stats]
        }
    
    def __repr__(self):
        """
        缓存对象的字符串表示
        
        Returns:
            str: 缓存对象描述
        """
        return f'<AnalyticsCache {self.cache_key} - {self.cache_type}>'