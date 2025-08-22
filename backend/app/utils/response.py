# -*- coding: utf-8 -*-
"""
响应格式化工具函数
用于统一API响应格式和状态码处理
"""

from flask import jsonify, request
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import math

def success_response(
    data: Any = None,
    message: str = "操作成功",
    code: int = 200,
    extra: Optional[Dict] = None
) -> tuple:
    """
    成功响应格式
    
    Args:
        data: 响应数据
        message (str): 响应消息
        code (int): HTTP状态码
        extra (dict): 额外的响应字段
    
    Returns:
        tuple: (响应数据, HTTP状态码)
    """
    response_data = {
        'success': True,
        'code': code,
        'message': message,
        'data': data,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    if extra:
        response_data.update(extra)
    
    return jsonify(response_data), code

def error_response(
    message: str = "操作失败",
    code: int = 400,
    error_code: Optional[str] = None,
    details: Optional[Dict] = None
) -> tuple:
    """
    错误响应格式
    
    Args:
        message (str): 错误消息
        code (int): HTTP状态码
        error_code (str): 业务错误码
        details (dict): 错误详情
    
    Returns:
        tuple: (响应数据, HTTP状态码)
    """
    response_data = {
        'success': False,
        'code': code,
        'message': message,
        'data': None,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    if error_code:
        response_data['error_code'] = error_code
    
    if details:
        response_data['details'] = details
    
    return jsonify(response_data), code

def validation_error_response(
    errors: Union[Dict, List, str],
    message: str = "数据验证失败"
) -> tuple:
    """
    数据验证错误响应
    
    Args:
        errors: 验证错误信息
        message (str): 错误消息
    
    Returns:
        tuple: (响应数据, HTTP状态码)
    """
    return error_response(
        message=message,
        code=422,
        error_code="VALIDATION_ERROR",
        details={'validation_errors': errors}
    )

def unauthorized_response(message: str = "未授权访问") -> tuple:
    """
    未授权响应
    
    Args:
        message (str): 错误消息
    
    Returns:
        tuple: (响应数据, HTTP状态码)
    """
    return error_response(
        message=message,
        code=401,
        error_code="UNAUTHORIZED"
    )

def forbidden_response(message: str = "权限不足") -> tuple:
    """
    权限不足响应
    
    Args:
        message (str): 错误消息
    
    Returns:
        tuple: (响应数据, HTTP状态码)
    """
    return error_response(
        message=message,
        code=403,
        error_code="FORBIDDEN"
    )

def not_found_response(message: str = "资源不存在") -> tuple:
    """
    资源不存在响应
    
    Args:
        message (str): 错误消息
    
    Returns:
        tuple: (响应数据, HTTP状态码)
    """
    return error_response(
        message=message,
        code=404,
        error_code="NOT_FOUND"
    )

def conflict_response(message: str = "资源冲突") -> tuple:
    """
    资源冲突响应
    
    Args:
        message (str): 错误消息
    
    Returns:
        tuple: (响应数据, HTTP状态码)
    """
    return error_response(
        message=message,
        code=409,
        error_code="CONFLICT"
    )

def server_error_response(message: str = "服务器内部错误") -> tuple:
    """
    服务器错误响应
    
    Args:
        message (str): 错误消息
    
    Returns:
        tuple: (响应数据, HTTP状态码)
    """
    return error_response(
        message=message,
        code=500,
        error_code="INTERNAL_SERVER_ERROR"
    )

def rate_limit_response(message: str = "请求频率过高") -> tuple:
    """
    请求频率限制响应
    
    Args:
        message (str): 错误消息
    
    Returns:
        tuple: (响应数据, HTTP状态码)
    """
    return error_response(
        message=message,
        code=429,
        error_code="RATE_LIMIT_EXCEEDED"
    )

def paginated_response(
    items: List[Any],
    page: int,
    per_page: int,
    total: int,
    message: str = "获取成功"
) -> tuple:
    """
    分页响应格式
    
    Args:
        items (list): 数据列表
        page (int): 当前页码
        per_page (int): 每页数量
        total (int): 总数量
        message (str): 响应消息
    
    Returns:
        tuple: (响应数据, HTTP状态码)
    """
    total_pages = math.ceil(total / per_page) if per_page > 0 else 0
    has_next = page < total_pages
    has_prev = page > 1
    
    pagination_info = {
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages,
        'has_next': has_next,
        'has_prev': has_prev,
        'next_page': page + 1 if has_next else None,
        'prev_page': page - 1 if has_prev else None
    }
    
    return success_response(
        data={
            'items': items,
            'pagination': pagination_info
        },
        message=message
    )

def created_response(
    data: Any = None,
    message: str = "创建成功",
    location: Optional[str] = None
) -> tuple:
    """
    创建成功响应
    
    Args:
        data: 响应数据
        message (str): 响应消息
        location (str): 资源位置
    
    Returns:
        tuple: (响应数据, HTTP状态码)
    """
    extra = {}
    if location:
        extra['location'] = location
    
    return success_response(
        data=data,
        message=message,
        code=201,
        extra=extra
    )

def updated_response(
    data: Any = None,
    message: str = "更新成功"
) -> tuple:
    """
    更新成功响应
    
    Args:
        data: 响应数据
        message (str): 响应消息
    
    Returns:
        tuple: (响应数据, HTTP状态码)
    """
    return success_response(
        data=data,
        message=message,
        code=200
    )

def deleted_response(message: str = "删除成功") -> tuple:
    """
    删除成功响应
    
    Args:
        message (str): 响应消息
    
    Returns:
        tuple: (响应数据, HTTP状态码)
    """
    return success_response(
        data=None,
        message=message,
        code=200
    )

def no_content_response() -> tuple:
    """
    无内容响应
    
    Returns:
        tuple: (空响应, HTTP状态码)
    """
    return '', 204

def accepted_response(
    data: Any = None,
    message: str = "请求已接受",
    task_id: Optional[str] = None
) -> tuple:
    """
    请求已接受响应（异步处理）
    
    Args:
        data: 响应数据
        message (str): 响应消息
        task_id (str): 任务ID
    
    Returns:
        tuple: (响应数据, HTTP状态码)
    """
    extra = {}
    if task_id:
        extra['task_id'] = task_id
    
    return success_response(
        data=data,
        message=message,
        code=202,
        extra=extra
    )

def partial_content_response(
    data: Any,
    message: str = "部分内容",
    range_info: Optional[Dict] = None
) -> tuple:
    """
    部分内容响应
    
    Args:
        data: 响应数据
        message (str): 响应消息
        range_info (dict): 范围信息
    
    Returns:
        tuple: (响应数据, HTTP状态码)
    """
    extra = {}
    if range_info:
        extra['range'] = range_info
    
    return success_response(
        data=data,
        message=message,
        code=206,
        extra=extra
    )

class ResponseBuilder:
    """
    响应构建器类
    用于链式构建复杂的响应
    """
    
    def __init__(self):
        """
        初始化响应构建器
        """
        self._data = None
        self._message = "操作成功"
        self._code = 200
        self._success = True
        self._error_code = None
        self._details = None
        self._extra = {}
    
    def data(self, data: Any) -> 'ResponseBuilder':
        """
        设置响应数据
        
        Args:
            data: 响应数据
        
        Returns:
            ResponseBuilder: 当前实例
        """
        self._data = data
        return self
    
    def message(self, message: str) -> 'ResponseBuilder':
        """
        设置响应消息
        
        Args:
            message (str): 响应消息
        
        Returns:
            ResponseBuilder: 当前实例
        """
        self._message = message
        return self
    
    def code(self, code: int) -> 'ResponseBuilder':
        """
        设置HTTP状态码
        
        Args:
            code (int): HTTP状态码
        
        Returns:
            ResponseBuilder: 当前实例
        """
        self._code = code
        return self
    
    def success(self, success: bool = True) -> 'ResponseBuilder':
        """
        设置成功状态
        
        Args:
            success (bool): 是否成功
        
        Returns:
            ResponseBuilder: 当前实例
        """
        self._success = success
        return self
    
    def error_code(self, error_code: str) -> 'ResponseBuilder':
        """
        设置错误码
        
        Args:
            error_code (str): 错误码
        
        Returns:
            ResponseBuilder: 当前实例
        """
        self._error_code = error_code
        return self
    
    def details(self, details: Dict) -> 'ResponseBuilder':
        """
        设置详细信息
        
        Args:
            details (dict): 详细信息
        
        Returns:
            ResponseBuilder: 当前实例
        """
        self._details = details
        return self
    
    def extra(self, key: str, value: Any) -> 'ResponseBuilder':
        """
        添加额外字段
        
        Args:
            key (str): 字段名
            value: 字段值
        
        Returns:
            ResponseBuilder: 当前实例
        """
        self._extra[key] = value
        return self
    
    def build(self) -> tuple:
        """
        构建响应
        
        Returns:
            tuple: (响应数据, HTTP状态码)
        """
        response_data = {
            'success': self._success,
            'code': self._code,
            'message': self._message,
            'data': self._data,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        if self._error_code:
            response_data['error_code'] = self._error_code
        
        if self._details:
            response_data['details'] = self._details
        
        response_data.update(self._extra)
        
        return jsonify(response_data), self._code

def build_response() -> ResponseBuilder:
    """
    创建响应构建器
    
    Returns:
        ResponseBuilder: 响应构建器实例
    """
    return ResponseBuilder()

def handle_api_exception(e: Exception) -> tuple:
    """
    处理API异常
    
    Args:
        e (Exception): 异常对象
    
    Returns:
        tuple: (响应数据, HTTP状态码)
    """
    from flask import current_app
    
    # 记录异常日志
    current_app.logger.error(f"API异常: {str(e)}", exc_info=True)
    
    # 根据异常类型返回不同的响应
    if isinstance(e, ValueError):
        return validation_error_response(str(e))
    elif isinstance(e, PermissionError):
        return forbidden_response(str(e))
    elif isinstance(e, FileNotFoundError):
        return not_found_response(str(e))
    else:
        return server_error_response("服务器内部错误")

def format_field_errors(errors: Dict) -> Dict:
    """
    格式化字段验证错误
    
    Args:
        errors (dict): 原始错误信息
    
    Returns:
        dict: 格式化后的错误信息
    """
    formatted_errors = {}
    
    for field, messages in errors.items():
        if isinstance(messages, list):
            formatted_errors[field] = messages[0] if messages else "字段验证失败"
        else:
            formatted_errors[field] = str(messages)
    
    return formatted_errors

def get_request_info() -> Dict:
    """
    获取请求信息
    
    Returns:
        dict: 请求信息
    """
    return {
        'method': request.method,
        'url': request.url,
        'remote_addr': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', ''),
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }

def add_cors_headers(response):
    """
    添加CORS头部
    
    Args:
        response: Flask响应对象
    
    Returns:
        response: 添加了CORS头部的响应对象
    """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

def cache_response(response, max_age: int = 300):
    """
    添加缓存头部
    
    Args:
        response: Flask响应对象
        max_age (int): 缓存时间（秒）
    
    Returns:
        response: 添加了缓存头部的响应对象
    """
    response.headers['Cache-Control'] = f'public, max-age={max_age}'
    return response

def no_cache_response(response):
    """
    添加禁用缓存头部
    
    Args:
        response: Flask响应对象
    
    Returns:
        response: 添加了禁用缓存头部的响应对象
    """
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response