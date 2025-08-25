# -*- coding: utf-8 -*-
"""
认证相关工具函数
包含JWT令牌验证、用户权限检查等功能
"""

from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from app.models.user import User

def token_required(f):
    """
    JWT令牌验证装饰器
    验证请求中的JWT令牌是否有效
    
    Args:
        f: 被装饰的函数
    
    Returns:
        装饰器函数
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # 验证JWT令牌
            verify_jwt_in_request()
            
            # 获取当前用户ID
            current_user_id = get_jwt_identity()
            
            if not current_user_id:
                return jsonify({
                    'success': False,
                    'message': '无效的令牌',
                    'error_code': 'INVALID_TOKEN'
                }), 401
            
            # 将字符串ID转换为整数
            try:
                user_id = int(current_user_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': '无效的用户ID格式',
                    'error_code': 'INVALID_USER_ID'
                }), 401
            
            # 检查用户是否存在且活跃
            user = User.find_by_id(user_id)
            if not user or not user.is_active:
                return jsonify({
                    'success': False,
                    'message': '用户不存在或已被禁用',
                    'error_code': 'USER_NOT_FOUND'
                }), 401
            
            # 将用户对象传递给被装饰的函数
            return f(current_user=user, *args, **kwargs)
            
        except Exception as e:
            current_app.logger.error(f"Token验证失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': '令牌验证失败',
                'error_code': 'TOKEN_VERIFICATION_FAILED'
            }), 401
    
    return decorated_function

def admin_required(f):
    """
    管理员权限验证装饰器
    验证当前用户是否具有管理员权限
    
    Args:
        f: 被装饰的函数
    
    Returns:
        装饰器函数
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # 先验证JWT令牌
            verify_jwt_in_request()
            
            # 获取当前用户
            current_user_id = get_jwt_identity()
            user = User.find_by_id(current_user_id)
            
            if not user or not user.is_active:
                return jsonify({
                    'success': False,
                    'message': '用户不存在或已被禁用',
                    'error_code': 'USER_NOT_FOUND'
                }), 401
            
            # 检查管理员权限（这里可以根据实际需求扩展权限系统）
            # 暂时使用用户名判断，实际项目中应该有专门的权限字段
            if user.username != 'admin':
                return jsonify({
                    'success': False,
                    'message': '需要管理员权限',
                    'error_code': 'ADMIN_REQUIRED'
                }), 403
            
            return f(current_user=user, *args, **kwargs)
            
        except Exception as e:
            current_app.logger.error(f"管理员权限验证失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': '权限验证失败',
                'error_code': 'PERMISSION_VERIFICATION_FAILED'
            }), 403
    
    return decorated_function

def get_current_user():
    """
    获取当前登录用户
    
    Returns:
        User: 当前用户对象，如果未登录则返回None
    """
    try:
        # 验证JWT令牌
        verify_jwt_in_request(optional=True)
        
        # 获取用户ID
        current_user_id = get_jwt_identity()
        
        if current_user_id:
            try:
                user_id = int(current_user_id)
                user = User.find_by_id(user_id)
            except (ValueError, TypeError):
                return None
            if user and user.is_active:
                return user
        
        return None
        
    except Exception as e:
        current_app.logger.debug(f"获取当前用户失败: {str(e)}")
        return None

def get_jwt_claims():
    """
    获取JWT中的自定义声明
    
    Returns:
        dict: JWT声明字典
    """
    try:
        verify_jwt_in_request()
        return get_jwt()
    except Exception:
        return {}

def check_user_permission(user, permission):
    """
    检查用户是否具有指定权限
    
    Args:
        user (User): 用户对象
        permission (str): 权限名称
    
    Returns:
        bool: 是否具有权限
    """
    if not user or not user.is_active:
        return False
    
    # 管理员拥有所有权限
    if user.username == 'admin':
        return True
    
    # 这里可以扩展更复杂的权限系统
    # 例如基于角色的权限控制(RBAC)
    
    # 基础权限检查
    basic_permissions = [
        'read_own_data',
        'manage_own_repositories',
        'view_own_analytics'
    ]
    
    if permission in basic_permissions:
        return True
    
    return False

def permission_required(permission):
    """
    权限验证装饰器
    
    Args:
        permission (str): 所需权限
    
    Returns:
        装饰器函数
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # 验证JWT令牌
                verify_jwt_in_request()
                
                # 获取当前用户
                current_user_id = get_jwt_identity()
                user = User.find_by_id(current_user_id)
                
                if not user or not user.is_active:
                    return jsonify({
                        'success': False,
                        'message': '用户不存在或已被禁用',
                        'error_code': 'USER_NOT_FOUND'
                    }), 401
                
                # 检查权限
                if not check_user_permission(user, permission):
                    return jsonify({
                        'success': False,
                        'message': f'缺少权限: {permission}',
                        'error_code': 'PERMISSION_DENIED'
                    }), 403
                
                return f(current_user=user, *args, **kwargs)
                
            except Exception as e:
                current_app.logger.error(f"权限验证失败: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': '权限验证失败',
                    'error_code': 'PERMISSION_VERIFICATION_FAILED'
                }), 403
        
        return decorated_function
    return decorator

def validate_api_key(api_key):
    """
    验证API密钥格式
    
    Args:
        api_key (str): API密钥
    
    Returns:
        bool: 是否有效
    """
    if not api_key or not isinstance(api_key, str):
        return False
    
    # 基本长度检查
    if len(api_key) < 10 or len(api_key) > 200:
        return False
    
    # 检查是否包含非法字符
    import re
    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', api_key):
        return False
    
    return True

def generate_user_context(user):
    """
    生成用户上下文信息
    
    Args:
        user (User): 用户对象
    
    Returns:
        dict: 用户上下文
    """
    if not user:
        return {}
    
    return {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'is_admin': user.username == 'admin',
        'permissions': get_user_permissions(user)
    }

def get_user_permissions(user):
    """
    获取用户权限列表
    
    Args:
        user (User): 用户对象
    
    Returns:
        list: 权限列表
    """
    if not user or not user.is_active:
        return []
    
    permissions = [
        'read_own_data',
        'manage_own_repositories',
        'view_own_analytics'
    ]
    
    # 管理员权限
    if user.username == 'admin':
        permissions.extend([
            'manage_all_users',
            'view_all_repositories',
            'manage_system_settings',
            'view_system_analytics'
        ])
    
    return permissions