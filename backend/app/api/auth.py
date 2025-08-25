# -*- coding: utf-8 -*-
"""
用户认证API模块
包含用户注册、登录、个人资料管理等功能
"""

from flask import request, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity, get_jwt
)
from datetime import timedelta
from sqlalchemy.exc import IntegrityError

from . import auth_bp as api_bp
from ..models import User
from .. import db
from ..utils.response import (
    success_response, error_response, validation_error_response,
    unauthorized_response, conflict_response, created_response,
    updated_response
)
from ..utils.validators import (
    validate_email, validate_password, validate_username
)
from ..utils.auth import token_required, get_current_user
from ..utils.helpers import generate_random_string

@api_bp.route('/register', methods=['POST'])
def register():
    """
    用户注册
    
    Request Body:
        {
            "username": "用户名",
            "email": "邮箱地址",
            "password": "密码"
        }
    
    Returns:
        JSON响应包含用户信息和访问令牌
    """
    try:
        data = request.get_json()
        
        if not data:
            return validation_error_response("请求数据不能为空")
        
        # 获取请求参数
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # 验证必填字段
        if not all([username, email, password]):
            return validation_error_response("用户名、邮箱和密码不能为空")
        
        # 验证用户名格式
        if not validate_username(username):
            return validation_error_response(
                "用户名格式不正确，只能包含字母、数字、下划线和连字符，长度3-20个字符"
            )
        
        # 验证邮箱格式
        if not validate_email(email):
            return validation_error_response("邮箱格式不正确")
        
        # 验证密码强度
        password_validation = validate_password(password)
        if not password_validation['valid']:
            return validation_error_response(
                f"密码不符合要求: {', '.join(password_validation['errors'])}"
            )
        
        # 检查用户名是否已存在
        if User.find_by_username(username):
            return conflict_response("用户名已存在")
        
        # 检查邮箱是否已存在
        if User.find_by_email(email):
            return conflict_response("邮箱已被注册")
        
        # 创建新用户
        user = User(
            username=username,
            email=email,
            password=password  # 直接传递password参数
        )
        
        db.session.add(user)
        db.session.commit()
        
        # 生成访问令牌
        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(hours=24)
        )
        refresh_token = create_refresh_token(
            identity=str(user.id),
            expires_delta=timedelta(days=30)
        )
        
        # 返回用户信息和令牌
        user_data = user.to_dict()
        user_data.update({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer'
        })
        
        return created_response(
            data=user_data,
            message="用户注册成功"
        )
        
    except IntegrityError:
        db.session.rollback()
        return conflict_response("用户名或邮箱已存在")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"用户注册失败: {str(e)}")
        return error_response("注册失败，请稍后重试")

@api_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录
    
    Request Body:
        {
            "username": "用户名或邮箱",
            "password": "密码"
        }
    
    Returns:
        JSON响应包含用户信息和访问令牌
    """
    try:
        data = request.get_json()
        
        if not data:
            return validation_error_response("请求数据不能为空")
        
        # 获取请求参数
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # 验证必填字段
        if not all([username, password]):
            return validation_error_response("用户名和密码不能为空")
        
        # 查找用户（支持用户名或邮箱登录）
        if '@' in username:
            user = User.find_by_email(username.lower())
            current_app.logger.info(f"通过邮箱查找用户: {username.lower()}, 结果: {user}")
        else:
            user = User.find_by_username(username)
            current_app.logger.info(f"通过用户名查找用户: {username}, 结果: {user}")
        
        # 验证用户存在性和密码正确性
        if not user:
            current_app.logger.info(f"用户不存在: {username}")
            return unauthorized_response("用户名或密码错误")
        
        current_app.logger.info(f"找到用户: {user.username}, 开始验证密码")
        if not user.check_password(password):
            current_app.logger.info(f"密码验证失败: {username}")
            return unauthorized_response("用户名或密码错误")
        
        current_app.logger.info(f"用户验证成功: {user.username}")
        
        # 检查用户是否被禁用
        if not user.is_active:
            return unauthorized_response("账户已被禁用，请联系管理员")
        
        # 生成访问令牌
        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(hours=24)
        )
        refresh_token = create_refresh_token(
            identity=str(user.id),
            expires_delta=timedelta(days=30)
        )
        
        # 更新最后登录时间
        user.updated_at = db.func.now()
        db.session.commit()
        
        # 返回用户信息和令牌
        user_data = user.to_dict()
        user_data.update({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer'
        })
        
        return success_response(
            data=user_data,
            message="登录成功"
        )
        
    except Exception as e:
        current_app.logger.error(f"用户登录失败: {str(e)}")
        return error_response("登录失败，请稍后重试")

@api_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    刷新访问令牌
    
    Headers:
        Authorization: Bearer <refresh_token>
    
    Returns:
        JSON响应包含新的访问令牌
    """
    try:
        current_user_id = get_jwt_identity()
        
        # 将字符串ID转换为整数
        try:
            user_id = int(current_user_id)
        except (ValueError, TypeError):
            return unauthorized_response("无效的用户ID格式")
        
        # 查找用户
        user = User.find_by_id(user_id)
        if not user:
            return unauthorized_response("用户不存在")
        
        # 检查用户是否被禁用
        if not user.is_active:
            return unauthorized_response("账户已被禁用")
        
        # 生成新的访问令牌
        new_access_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(hours=24)
        )
        
        return success_response(
            data={
                'access_token': new_access_token,
                'token_type': 'Bearer'
            },
            message="令牌刷新成功"
        )
        
    except Exception as e:
        current_app.logger.error(f"令牌刷新失败: {str(e)}")
        return error_response("令牌刷新失败")

@api_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    用户登出
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
        JSON响应确认登出成功
    """
    try:
        # 获取当前JWT令牌
        jti = get_jwt()['jti']
        
        # 在实际应用中，这里应该将令牌加入黑名单
        # 由于这是一个简化版本，我们只返回成功响应
        
        return success_response(
            message="登出成功"
        )
        
    except Exception as e:
        current_app.logger.error(f"用户登出失败: {str(e)}")
        return error_response("登出失败")

@api_bp.route('/debug/users', methods=['GET'])
def debug_users():
    """
    调试端点：查看所有用户
    
    Returns:
        JSON响应包含用户列表
    """
    try:
        users = User.query.all()
        user_list = [{
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_active': user.is_active
        } for user in users]
        
        return success_response(
            data={
                'users': user_list,
                'count': len(user_list)
            },
            message="获取用户列表成功"
        )
        
    except Exception as e:
        current_app.logger.error(f"调试查询失败: {str(e)}")
        return error_response(f"调试查询失败: {str(e)}")

@api_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """
    获取用户个人资料
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
        JSON响应包含用户个人资料
    """
    try:
        
        return success_response(
            data=current_user.to_dict(),
            message="获取个人资料成功"
        )
        
    except Exception as e:
        current_app.logger.error(f"获取个人资料失败: {str(e)}")
        return error_response("获取个人资料失败")

@api_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """
    更新用户个人资料
    
    Headers:
        Authorization: Bearer <access_token>
    
    Request Body:
        {
            "username": "新用户名",
            "email": "新邮箱地址"
        }
    
    Returns:
        JSON响应包含更新后的用户信息
    """
    try:
        data = request.get_json()
        
        if not data:
            return validation_error_response("请求数据不能为空")
        
        # 获取更新字段
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        
        # 验证用户名
        if username and username != current_user.username:
            if not validate_username(username):
                return validation_error_response(
                    "用户名格式不正确，只能包含字母、数字、下划线和连字符，长度3-20个字符"
                )
            
            # 检查用户名是否已被其他用户使用
            existing_user = User.find_by_username(username)
            if existing_user and existing_user.id != current_user.id:
                return conflict_response("用户名已存在")
        
        # 验证邮箱
        if email and email != current_user.email:
            if not validate_email(email):
                return validation_error_response("邮箱格式不正确")
            
            # 检查邮箱是否已被其他用户使用
            existing_user = User.find_by_email(email)
            if existing_user and existing_user.id != current_user.id:
                return conflict_response("邮箱已被注册")
        
        # 更新用户信息
        update_data = {}
        if username and username != current_user.username:
            update_data['username'] = username
        if email and email != current_user.email:
            update_data['email'] = email
        
        if update_data:
            current_user.update_profile(**update_data)
            db.session.commit()
        
        return updated_response(
            data=current_user.to_dict(),
            message="个人资料更新成功"
        )
        
    except IntegrityError:
        db.session.rollback()
        return conflict_response("用户名或邮箱已存在")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新个人资料失败: {str(e)}")
        return error_response("更新个人资料失败")

@api_bp.route('/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    """
    修改密码
    
    Headers:
        Authorization: Bearer <access_token>
    
    Request Body:
        {
            "current_password": "当前密码",
            "new_password": "新密码"
        }
    
    Returns:
        JSON响应确认密码修改成功
    """
    try:
        data = request.get_json()
        
        if not data:
            return validation_error_response("请求数据不能为空")
        
        # 获取请求参数
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        # 验证必填字段
        if not all([current_password, new_password]):
            return validation_error_response("当前密码和新密码不能为空")
        
        # 验证当前密码
        if not current_user.check_password(current_password):
            return unauthorized_response("当前密码错误")
        
        # 验证新密码强度
        password_validation = validate_password(new_password)
        if not password_validation['valid']:
            return validation_error_response(
                f"新密码不符合要求: {', '.join(password_validation['errors'])}"
            )
        
        # 检查新密码是否与当前密码相同
        if current_user.check_password(new_password):
            return validation_error_response("新密码不能与当前密码相同")
        
        # 更新密码
        current_user.set_password(new_password)
        current_user.updated_at = db.func.now()
        db.session.commit()
        
        return success_response(
            message="密码修改成功"
        )
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"修改密码失败: {str(e)}")
        return error_response("修改密码失败")

@api_bp.route('/deactivate', methods=['POST'])
@token_required
def deactivate_account(current_user):
    """
    停用账户
    
    Headers:
        Authorization: Bearer <access_token>
    
    Request Body:
        {
            "password": "当前密码"
        }
    
    Returns:
        JSON响应确认账户停用成功
    """
    try:
        data = request.get_json()
        
        if not data:
            return validation_error_response("请求数据不能为空")
        
        # 获取密码确认
        password = data.get('password', '')
        
        if not password:
            return validation_error_response("请输入密码确认")
        
        # 验证密码
        if not current_user.check_password(password):
            return unauthorized_response("密码错误")
        
        # 停用账户
        current_user.is_active = False
        current_user.updated_at = db.func.now()
        db.session.commit()
        
        return success_response(
            message="账户已停用"
        )
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"停用账户失败: {str(e)}")
        return error_response("停用账户失败")

@api_bp.route('/check-username', methods=['POST'])
def check_username():
    """
    检查用户名是否可用
    
    Request Body:
        {
            "username": "要检查的用户名"
        }
    
    Returns:
        JSON响应包含用户名可用性信息
    """
    try:
        data = request.get_json()
        
        if not data:
            return validation_error_response("请求数据不能为空")
        
        username = data.get('username', '').strip()
        
        if not username:
            return validation_error_response("用户名不能为空")
        
        # 验证用户名格式
        if not validate_username(username):
            return success_response(
                data={
                    'available': False,
                    'reason': '用户名格式不正确，只能包含字母、数字、下划线和连字符，长度3-20个字符'
                },
                message="用户名不可用"
            )
        
        # 检查用户名是否已存在
        existing_user = User.find_by_username(username)
        available = existing_user is None
        
        return success_response(
            data={
                'available': available,
                'reason': '用户名已存在' if not available else None
            },
            message="用户名可用" if available else "用户名不可用"
        )
        
    except Exception as e:
        current_app.logger.error(f"检查用户名失败: {str(e)}")
        return error_response("检查用户名失败")

@api_bp.route('/check-email', methods=['POST'])
def check_email():
    """
    检查邮箱是否可用
    
    Request Body:
        {
            "email": "要检查的邮箱"
        }
    
    Returns:
        JSON响应包含邮箱可用性信息
    """
    try:
        data = request.get_json()
        
        if not data:
            return validation_error_response("请求数据不能为空")
        
        email = data.get('email', '').strip().lower()
        
        if not email:
            return validation_error_response("邮箱不能为空")
        
        # 验证邮箱格式
        if not validate_email(email):
            return success_response(
                data={
                    'available': False,
                    'reason': '邮箱格式不正确'
                },
                message="邮箱不可用"
            )
        
        # 检查邮箱是否已存在
        existing_user = User.find_by_email(email)
        available = existing_user is None
        
        return success_response(
            data={
                'available': available,
                'reason': '邮箱已被注册' if not available else None
            },
            message="邮箱可用" if available else "邮箱不可用"
        )
        
    except Exception as e:
        current_app.logger.error(f"检查邮箱失败: {str(e)}")
        return error_response("检查邮箱失败")