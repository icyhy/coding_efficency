# -*- coding: utf-8 -*-
"""
分析缓存模型
用于缓存分析结果，提高查询性能
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from app import db

class AnalyticsCache(db.Model):
    """
    分析缓存模型
    用于缓存分析结果，避免重复计算
    """
    __tablename__ = 'analytics_cache'
    
    id = Column(Integer, primary_key=True)
    cache_key = Column(String(255), unique=True, nullable=False, index=True, comment='缓存键')
    cache_type = Column(String(50), nullable=False, index=True, comment='缓存类型')
    data = Column(JSON, nullable=False, comment='缓存数据')
    expires_at = Column(DateTime, nullable=False, index=True, comment='过期时间')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment='更新时间')
    is_valid = Column(Boolean, default=True, nullable=False, comment='是否有效')
    
    def __repr__(self):
        return f'<AnalyticsCache {self.cache_key}>'
    
    @classmethod
    def get_cache(cls, cache_key):
        """
        获取缓存数据
        
        Args:
            cache_key (str): 缓存键
        
        Returns:
            dict: 缓存数据，如果不存在或已过期返回None
        """
        cache = cls.query.filter_by(
            cache_key=cache_key,
            is_valid=True
        ).first()
        
        if not cache:
            return None
        
        # 检查是否过期
        if cache.expires_at < datetime.utcnow():
            cache.is_valid = False
            db.session.commit()
            return None
        
        return cache.data
    
    @classmethod
    def set_cache(cls, cache_key, cache_type, data, expires_at):
        """
        设置缓存数据
        
        Args:
            cache_key (str): 缓存键
            cache_type (str): 缓存类型
            data (dict): 缓存数据
            expires_at (datetime): 过期时间
        
        Returns:
            AnalyticsCache: 缓存对象
        """
        # 查找现有缓存
        cache = cls.query.filter_by(cache_key=cache_key).first()
        
        if cache:
            # 更新现有缓存
            cache.cache_type = cache_type
            cache.data = data
            cache.expires_at = expires_at
            cache.updated_at = datetime.utcnow()
            cache.is_valid = True
        else:
            # 创建新缓存
            cache = cls(
                cache_key=cache_key,
                cache_type=cache_type,
                data=data,
                expires_at=expires_at
            )
            db.session.add(cache)
        
        db.session.commit()
        return cache
    
    @classmethod
    def invalidate_cache(cls, cache_key=None, cache_type=None):
        """
        使缓存失效
        
        Args:
            cache_key (str, optional): 特定缓存键
            cache_type (str, optional): 缓存类型
        """
        query = cls.query
        
        if cache_key:
            query = query.filter_by(cache_key=cache_key)
        elif cache_type:
            query = query.filter_by(cache_type=cache_type)
        
        query.update({'is_valid': False})
        db.session.commit()
    
    @classmethod
    def cleanup_expired(cls):
        """
        清理过期缓存
        
        Returns:
            int: 清理的缓存数量
        """
        expired_count = cls.query.filter(
            cls.expires_at < datetime.utcnow()
        ).count()
        
        cls.query.filter(
            cls.expires_at < datetime.utcnow()
        ).delete()
        
        db.session.commit()
        return expired_count
    
    def to_dict(self):
        """
        转换为字典格式
        
        Returns:
            dict: 缓存信息字典
        """
        return {
            'id': self.id,
            'cache_key': self.cache_key,
            'cache_type': self.cache_type,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_valid': self.is_valid
        }