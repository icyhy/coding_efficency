# -*- coding: utf-8 -*-
"""
装饰器工具模块
提供权限检查、缓存等装饰器功能
"""

from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models import User


def require_permission(permission_type='read'):
    """
    权限检查装饰器
    
    Args:
        permission_type (str): 权限类型，默认为'read'
        
    Returns:
        装饰器函数
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # 验证JWT令牌
                verify_jwt_in_request()
                
                # 获取当前用户ID
                current_user_id = get_jwt_identity()
                
                # 查询用户信息
                user = User.query.get(current_user_id)
                if not user:
                    return jsonify({'error': '用户不存在'}), 401
                
                # 检查用户是否激活
                if not user.is_active:
                    return jsonify({'error': '用户账户已被禁用'}), 403
                
                # 简单的权限检查（可根据需要扩展）
                # 这里假设所有激活用户都有基本的读权限
                if permission_type == 'read':
                    return f(*args, **kwargs)
                elif permission_type == 'write':
                    # 可以添加更复杂的写权限检查逻辑
                    return f(*args, **kwargs)
                elif permission_type == 'admin':
                    # 检查是否为管理员（可根据用户模型扩展）
                    if hasattr(user, 'is_admin') and user.is_admin:
                        return f(*args, **kwargs)
                    else:
                        return jsonify({'error': '需要管理员权限'}), 403
                else:
                    return jsonify({'error': '未知的权限类型'}), 400
                    
            except Exception as e:
                return jsonify({'error': f'权限验证失败: {str(e)}'}), 401
                
        return decorated_function
    return decorator


def cache_result(cache_key_func=None, expire_seconds=3600):
    """
    结果缓存装饰器
    
    Args:
        cache_key_func (callable): 生成缓存键的函数
        expire_seconds (int): 缓存过期时间（秒）
        
    Returns:
        装饰器函数
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 这里可以实现缓存逻辑
            # 暂时直接调用原函数
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def rate_limit(max_requests=100, per_seconds=3600):
    """
    速率限制装饰器
    
    Args:
        max_requests (int): 最大请求次数
        per_seconds (int): 时间窗口（秒）
        
    Returns:
        装饰器函数
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 这里可以实现速率限制逻辑
            # 暂时直接调用原函数
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_json(*required_fields):
    """
    JSON数据验证装饰器
    
    Args:
        *required_fields: 必需的字段名称
        
    Returns:
        装饰器函数
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # 检查请求是否包含JSON数据
                if not request.is_json:
                    return jsonify({'error': '请求必须包含JSON数据'}), 400
                
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'JSON数据不能为空'}), 400
                
                # 检查必需字段
                missing_fields = []
                for field in required_fields:
                    if field not in data or data[field] is None:
                        missing_fields.append(field)
                
                if missing_fields:
                    return jsonify({
                        'error': f'缺少必需字段: {", ".join(missing_fields)}'
                    }), 400
                
                return f(*args, **kwargs)
                
            except Exception as e:
                return jsonify({'error': f'JSON验证失败: {str(e)}'}), 400
                
        return decorated_function
    return decorator