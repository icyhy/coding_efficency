# -*- coding: utf-8 -*-
"""
数据验证工具函数
包含邮箱、密码、URL等格式验证功能
"""

import re
from urllib.parse import urlparse
from typing import Optional, Dict, Any

def validate_email(email: str) -> Dict[str, Any]:
    """
    验证邮箱格式
    
    Args:
        email (str): 邮箱地址
    
    Returns:
        dict: 验证结果 {'valid': bool, 'message': str}
    """
    if not email or not isinstance(email, str):
        return {'valid': False, 'message': '邮箱不能为空'}
    
    # 去除首尾空格
    email = email.strip()
    
    # 长度检查
    if len(email) < 5 or len(email) > 254:
        return {'valid': False, 'message': '邮箱长度必须在5-254个字符之间'}
    
    # 正则表达式验证
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return {'valid': False, 'message': '邮箱格式不正确'}
    
    # 检查是否有连续的点
    if '..' in email:
        return {'valid': False, 'message': '邮箱格式不正确'}
    
    # 检查@符号数量
    if email.count('@') != 1:
        return {'valid': False, 'message': '邮箱格式不正确'}
    
    return {'valid': True, 'message': '邮箱格式正确'}

def validate_password(password: str) -> Dict[str, Any]:
    """
    验证密码强度
    
    Args:
        password (str): 密码
    
    Returns:
        dict: 验证结果 {'valid': bool, 'message': str, 'strength': str}
    """
    if not password or not isinstance(password, str):
        return {'valid': False, 'message': '密码不能为空', 'strength': 'none'}
    
    # 长度检查
    if len(password) < 6:
        return {'valid': False, 'message': '密码长度至少6个字符', 'strength': 'weak'}
    
    if len(password) > 128:
        return {'valid': False, 'message': '密码长度不能超过128个字符', 'strength': 'none'}
    
    # 强度评估
    strength_score = 0
    strength_messages = []
    
    # 检查长度
    if len(password) >= 8:
        strength_score += 1
    else:
        strength_messages.append('建议密码长度至少8个字符')
    
    # 检查是否包含小写字母
    if re.search(r'[a-z]', password):
        strength_score += 1
    else:
        strength_messages.append('建议包含小写字母')
    
    # 检查是否包含大写字母
    if re.search(r'[A-Z]', password):
        strength_score += 1
    else:
        strength_messages.append('建议包含大写字母')
    
    # 检查是否包含数字
    if re.search(r'\d', password):
        strength_score += 1
    else:
        strength_messages.append('建议包含数字')
    
    # 检查是否包含特殊字符
    if re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'"\\|,.<>\/?]', password):
        strength_score += 1
    else:
        strength_messages.append('建议包含特殊字符')
    
    # 检查是否包含常见弱密码模式
    weak_patterns = [
        r'123456',
        r'password',
        r'admin',
        r'qwerty',
        r'abc123',
        r'111111',
        r'000000'
    ]
    
    for pattern in weak_patterns:
        if re.search(pattern, password.lower()):
            strength_score -= 2
            strength_messages.append('避免使用常见密码模式')
            break
    
    # 确定强度等级
    if strength_score >= 4:
        strength = 'strong'
        message = '密码强度良好'
    elif strength_score >= 2:
        strength = 'medium'
        message = '密码强度中等，' + '，'.join(strength_messages[:2])
    else:
        strength = 'weak'
        message = '密码强度较弱，' + '，'.join(strength_messages[:3])
    
    return {
        'valid': True,
        'message': message,
        'strength': strength,
        'score': max(0, strength_score),
        'suggestions': strength_messages
    }

def validate_username(username: str) -> Dict[str, Any]:
    """
    验证用户名格式
    
    Args:
        username (str): 用户名
    
    Returns:
        dict: 验证结果 {'valid': bool, 'message': str}
    """
    if not username or not isinstance(username, str):
        return {'valid': False, 'message': '用户名不能为空'}
    
    # 去除首尾空格
    username = username.strip()
    
    # 长度检查
    if len(username) < 3:
        return {'valid': False, 'message': '用户名长度至少3个字符'}
    
    if len(username) > 50:
        return {'valid': False, 'message': '用户名长度不能超过50个字符'}
    
    # 格式检查：只允许字母、数字、下划线、连字符
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return {'valid': False, 'message': '用户名只能包含字母、数字、下划线和连字符'}
    
    # 不能以数字开头
    if username[0].isdigit():
        return {'valid': False, 'message': '用户名不能以数字开头'}
    
    # 不能全是数字
    if username.isdigit():
        return {'valid': False, 'message': '用户名不能全是数字'}
    
    # 保留用户名检查
    reserved_usernames = [
        'admin', 'root', 'system', 'api', 'www', 'mail', 'ftp',
        'test', 'guest', 'anonymous', 'null', 'undefined'
    ]
    
    if username.lower() in reserved_usernames:
        return {'valid': False, 'message': '该用户名为系统保留，请选择其他用户名'}
    
    return {'valid': True, 'message': '用户名格式正确'}

def validate_url(url: str) -> Dict[str, Any]:
    """
    验证URL格式
    
    Args:
        url (str): URL地址
    
    Returns:
        dict: 验证结果 {'valid': bool, 'message': str, 'parsed': dict}
    """
    if not url or not isinstance(url, str):
        return {'valid': False, 'message': 'URL不能为空', 'parsed': None}
    
    # 去除首尾空格
    url = url.strip()
    
    # 长度检查
    if len(url) > 2048:
        return {'valid': False, 'message': 'URL长度不能超过2048个字符', 'parsed': None}
    
    try:
        # 解析URL
        parsed = urlparse(url)
        
        # 检查协议
        if not parsed.scheme:
            return {'valid': False, 'message': 'URL必须包含协议(http/https)', 'parsed': None}
        
        if parsed.scheme.lower() not in ['http', 'https']:
            return {'valid': False, 'message': 'URL协议必须是http或https', 'parsed': None}
        
        # 检查域名
        if not parsed.netloc:
            return {'valid': False, 'message': 'URL必须包含有效的域名', 'parsed': None}
        
        # 域名格式检查
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        
        # 提取域名部分（去除端口）
        domain = parsed.netloc.split(':')[0]
        
        if not re.match(domain_pattern, domain):
            return {'valid': False, 'message': 'URL域名格式不正确', 'parsed': None}
        
        return {
            'valid': True,
            'message': 'URL格式正确',
            'parsed': {
                'scheme': parsed.scheme,
                'domain': domain,
                'port': parsed.port,
                'path': parsed.path,
                'query': parsed.query,
                'fragment': parsed.fragment
            }
        }
        
    except Exception as e:
        return {'valid': False, 'message': f'URL格式错误: {str(e)}', 'parsed': None}

def validate_git_url(url: str) -> Dict[str, Any]:
    """
    验证Git仓库URL格式
    
    Args:
        url (str): Git仓库URL
    
    Returns:
        dict: 验证结果 {'valid': bool, 'message': str, 'type': str}
    """
    if not url or not isinstance(url, str):
        return {'valid': False, 'message': 'Git URL不能为空', 'type': None}
    
    url = url.strip()
    
    # 检查是否是HTTPS Git URL
    if url.startswith('https://'):
        # 验证基本URL格式
        url_result = validate_url(url)
        if not url_result['valid']:
            return {'valid': False, 'message': url_result['message'], 'type': None}
        
        # 检查是否以.git结尾
        if not url.endswith('.git'):
            return {'valid': False, 'message': 'Git URL应该以.git结尾', 'type': 'https'}
        
        # 检查是否是支持的Git平台
        supported_platforms = [
            'github.com',
            'gitlab.com',
            'codeup.aliyun.com',
            'gitee.com',
            'bitbucket.org'
        ]
        
        domain = urlparse(url).netloc.lower()
        platform_type = None
        
        for platform in supported_platforms:
            if platform in domain:
                platform_type = platform
                break
        
        return {
            'valid': True,
            'message': 'Git URL格式正确',
            'type': 'https',
            'platform': platform_type
        }
    
    # 检查是否是SSH Git URL
    elif url.startswith('git@'):
        # SSH格式: git@hostname:username/repository.git
        ssh_pattern = r'^git@([a-zA-Z0-9.-]+):([a-zA-Z0-9._/-]+)\.git$'
        
        if not re.match(ssh_pattern, url):
            return {'valid': False, 'message': 'SSH Git URL格式不正确', 'type': None}
        
        return {
            'valid': True,
            'message': 'SSH Git URL格式正确',
            'type': 'ssh'
        }
    
    else:
        return {'valid': False, 'message': 'Git URL必须以https://或git@开头', 'type': None}

def validate_project_name(name: str) -> Dict[str, Any]:
    """
    验证项目名称格式
    
    Args:
        name (str): 项目名称
    
    Returns:
        dict: 验证结果 {'valid': bool, 'message': str}
    """
    if not name or not isinstance(name, str):
        return {'valid': False, 'message': '项目名称不能为空'}
    
    name = name.strip()
    
    # 长度检查
    if len(name) < 2:
        return {'valid': False, 'message': '项目名称长度至少2个字符'}
    
    if len(name) > 100:
        return {'valid': False, 'message': '项目名称长度不能超过100个字符'}
    
    # 格式检查：允许字母、数字、中文、下划线、连字符、空格
    if not re.match(r'^[a-zA-Z0-9\u4e00-\u9fa5_\s-]+$', name):
        return {'valid': False, 'message': '项目名称只能包含字母、数字、中文、下划线、连字符和空格'}
    
    # 不能全是空格
    if not name.strip():
        return {'valid': False, 'message': '项目名称不能全是空格'}
    
    return {'valid': True, 'message': '项目名称格式正确'}

def validate_date_range(start_date: Optional[str], end_date: Optional[str]) -> Dict[str, Any]:
    """
    验证日期范围
    
    Args:
        start_date (str): 开始日期 (YYYY-MM-DD)
        end_date (str): 结束日期 (YYYY-MM-DD)
    
    Returns:
        dict: 验证结果 {'valid': bool, 'message': str}
    """
    from datetime import datetime
    
    try:
        # 如果都为空，则有效
        if not start_date and not end_date:
            return {'valid': True, 'message': '日期范围有效'}
        
        # 日期格式验证
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        
        if start_date and not re.match(date_pattern, start_date):
            return {'valid': False, 'message': '开始日期格式不正确，应为YYYY-MM-DD'}
        
        if end_date and not re.match(date_pattern, end_date):
            return {'valid': False, 'message': '结束日期格式不正确，应为YYYY-MM-DD'}
        
        # 解析日期
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        
        if end_date:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # 检查日期范围
        if start_dt and end_dt:
            if start_dt > end_dt:
                return {'valid': False, 'message': '开始日期不能晚于结束日期'}
            
            # 检查范围是否过大（例如不超过1年）
            if (end_dt - start_dt).days > 365:
                return {'valid': False, 'message': '日期范围不能超过1年'}
        
        # 检查日期是否在合理范围内
        current_date = datetime.now()
        min_date = datetime(2000, 1, 1)
        
        if start_dt and (start_dt < min_date or start_dt > current_date):
            return {'valid': False, 'message': '开始日期超出有效范围'}
        
        if end_dt and (end_dt < min_date or end_dt > current_date):
            return {'valid': False, 'message': '结束日期超出有效范围'}
        
        return {'valid': True, 'message': '日期范围有效'}
        
    except ValueError as e:
        return {'valid': False, 'message': f'日期格式错误: {str(e)}'}
    except Exception as e:
        return {'valid': False, 'message': f'日期验证失败: {str(e)}'}