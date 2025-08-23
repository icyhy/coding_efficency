# -*- coding: utf-8 -*-
"""
通用辅助函数
包含随机字符串生成、时间格式化、分页等功能
"""

import string
import secrets
import hashlib
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from urllib.parse import urlparse
from flask import request
try:
    from dateutil import parser as date_parser
except ImportError:
    date_parser = None

def generate_random_string(length: int = 32, include_symbols: bool = False) -> str:
    """
    生成随机字符串
    
    Args:
        length (int): 字符串长度
        include_symbols (bool): 是否包含特殊符号
    
    Returns:
        str: 随机字符串
    """
    if include_symbols:
        characters = string.ascii_letters + string.digits + string.punctuation
    else:
        characters = string.ascii_letters + string.digits
    
    return ''.join(secrets.choice(characters) for _ in range(length))

def generate_secure_token(length: int = 32) -> str:
    """
    生成安全令牌
    
    Args:
        length (int): 令牌长度
    
    Returns:
        str: 安全令牌
    """
    return secrets.token_urlsafe(length)

def generate_hash(data: str, algorithm: str = 'sha256') -> str:
    """
    生成数据哈希值
    
    Args:
        data (str): 要哈希的数据
        algorithm (str): 哈希算法
    
    Returns:
        str: 哈希值
    """
    if algorithm == 'md5':
        return hashlib.md5(data.encode()).hexdigest()
    elif algorithm == 'sha1':
        return hashlib.sha1(data.encode()).hexdigest()
    elif algorithm == 'sha256':
        return hashlib.sha256(data.encode()).hexdigest()
    elif algorithm == 'sha512':
        return hashlib.sha512(data.encode()).hexdigest()
    else:
        raise ValueError(f"不支持的哈希算法: {algorithm}")

def format_datetime(dt: datetime, format_type: str = 'default') -> str:
    """
    格式化日期时间
    
    Args:
        dt (datetime): 日期时间对象
        format_type (str): 格式类型
    
    Returns:
        str: 格式化后的日期时间字符串
    """
    if not dt:
        return ''
    
    formats = {
        'default': '%Y-%m-%d %H:%M:%S',
        'date': '%Y-%m-%d',
        'time': '%H:%M:%S',
        'datetime': '%Y-%m-%d %H:%M:%S',
        'iso': '%Y-%m-%dT%H:%M:%S',
        'chinese': '%Y年%m月%d日 %H:%M:%S',
        'short': '%m/%d %H:%M',
        'long': '%Y年%m月%d日 %H时%M分%S秒'
    }
    
    format_str = formats.get(format_type, formats['default'])
    return dt.strftime(format_str)

def calculate_time_ago(dt: datetime) -> str:
    """
    计算时间差，返回友好的时间描述
    
    Args:
        dt (datetime): 目标时间
    
    Returns:
        str: 时间差描述
    """
    if not dt:
        return '未知时间'
    
    now = datetime.utcnow()
    diff = now - dt
    
    # 未来时间
    if diff.total_seconds() < 0:
        future_diff = dt - now
        if future_diff.days > 0:
            return f"{future_diff.days}天后"
        elif future_diff.seconds > 3600:
            hours = future_diff.seconds // 3600
            return f"{hours}小时后"
        elif future_diff.seconds > 60:
            minutes = future_diff.seconds // 60
            return f"{minutes}分钟后"
        else:
            return "即将"
    
    # 过去时间
    if diff.days > 365:
        years = diff.days // 365
        return f"{years}年前"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months}个月前"
    elif diff.days > 0:
        return f"{diff.days}天前"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours}小时前"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes}分钟前"
    else:
        return "刚刚"

def parse_datetime(date_str: str, format_str: str = '%Y-%m-%d %H:%M:%S') -> Optional[datetime]:
    """
    解析日期时间字符串
    
    Args:
        date_str (str): 日期时间字符串
        format_str (str): 格式字符串
    
    Returns:
        datetime: 解析后的日期时间对象
    """
    if not date_str:
        return None
    
    try:
        return datetime.strptime(date_str, format_str)
    except ValueError:
        # 尝试其他常见格式
        common_formats = [
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%d %H:%M',
            '%m/%d/%Y %H:%M:%S',
            '%m/%d/%Y'
        ]
        
        for fmt in common_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None

def get_date_range(period: str) -> Dict[str, datetime]:
    """
    根据周期获取日期范围
    
    Args:
        period (str): 周期类型 (today, week, month, quarter, year)
    
    Returns:
        dict: 包含start_date和end_date的字典
    """
    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    if period == 'today':
        return {
            'start_date': today,
            'end_date': today + timedelta(days=1)
        }
    elif period == 'week':
        # 本周（周一到周日）
        days_since_monday = today.weekday()
        start_of_week = today - timedelta(days=days_since_monday)
        return {
            'start_date': start_of_week,
            'end_date': start_of_week + timedelta(days=7)
        }
    elif period == 'month':
        # 本月
        start_of_month = today.replace(day=1)
        if start_of_month.month == 12:
            end_of_month = start_of_month.replace(year=start_of_month.year + 1, month=1)
        else:
            end_of_month = start_of_month.replace(month=start_of_month.month + 1)
        return {
            'start_date': start_of_month,
            'end_date': end_of_month
        }
    elif period == 'quarter':
        # 本季度
        quarter = (today.month - 1) // 3 + 1
        start_month = (quarter - 1) * 3 + 1
        start_of_quarter = today.replace(month=start_month, day=1)
        
        if start_month + 3 > 12:
            end_of_quarter = start_of_quarter.replace(year=start_of_quarter.year + 1, month=1)
        else:
            end_of_quarter = start_of_quarter.replace(month=start_month + 3)
        
        return {
            'start_date': start_of_quarter,
            'end_date': end_of_quarter
        }
    elif period == 'year':
        # 本年
        start_of_year = today.replace(month=1, day=1)
        end_of_year = start_of_year.replace(year=start_of_year.year + 1)
        return {
            'start_date': start_of_year,
            'end_date': end_of_year
        }
    else:
        # 默认返回最近30天
        return {
            'start_date': today - timedelta(days=30),
            'end_date': today + timedelta(days=1)
        }

def paginate_query(query, page: int = 1, per_page: int = 20, max_per_page: int = 100) -> Dict[str, Any]:
    """
    分页查询
    
    Args:
        query: SQLAlchemy查询对象
        page (int): 页码
        per_page (int): 每页数量
        max_per_page (int): 最大每页数量
    
    Returns:
        dict: 分页结果
    """
    # 参数验证
    page = max(1, page)
    per_page = min(max(1, per_page), max_per_page)
    
    # 执行分页查询
    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return {
        'items': pagination.items,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page,
        'per_page': pagination.per_page,
        'has_prev': pagination.has_prev,
        'has_next': pagination.has_next,
        'prev_num': pagination.prev_num,
        'next_num': pagination.next_num
    }

def parse_datetime_string(date_string: str) -> Optional[datetime]:
    """
    解析日期时间字符串
    
    Args:
        date_string (str): 日期时间字符串
    
    Returns:
        datetime: 解析后的日期时间对象，解析失败返回None
    """
    if not date_string:
        return None
    
    try:
        # 尝试使用dateutil解析
        if date_parser:
            return date_parser.parse(date_string)
        
        # 备用解析方法
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S.%fZ'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue
        
        return None
    except Exception:
        return None

def get_date_range_by_params(start_date: Optional[str] = None, end_date: Optional[str] = None, 
                  days: Optional[int] = None, strict: bool = False) -> Tuple[datetime, datetime]:
    """
    获取日期范围
    
    Args:
        start_date (str, optional): 开始日期字符串
        end_date (str, optional): 结束日期字符串
        days (int, optional): 天数（从今天往前推）
        strict (bool): 严格模式，无效日期时抛出异常
    
    Returns:
        tuple: (开始日期, 结束日期)
        
    Raises:
        ValueError: 当strict=True且日期格式无效时
    """
    now = datetime.utcnow()
    
    # 如果指定了天数，从今天往前推
    if days:
        end_dt = now
        start_dt = now - timedelta(days=days)
        return start_dt, end_dt
    
    # 解析开始日期
    if start_date:
        start_dt = parse_datetime_string(start_date)
        if not start_dt:
            if strict:
                raise ValueError(f"无效的开始日期格式: {start_date}")
            start_dt = now - timedelta(days=30)  # 默认30天前
    else:
        start_dt = now - timedelta(days=30)  # 默认30天前
    
    # 解析结束日期
    if end_date:
        end_dt = parse_datetime_string(end_date)
        if not end_dt:
            if strict:
                raise ValueError(f"无效的结束日期格式: {end_date}")
            end_dt = now
    else:
        end_dt = now
    
    # 确保开始日期不晚于结束日期
    if start_dt > end_dt:
        if strict:
            raise ValueError("开始日期不能晚于结束日期")
        start_dt, end_dt = end_dt, start_dt
    
    return start_dt, end_dt

def get_pagination_params() -> Dict[str, int]:
    """
    从请求参数中获取分页参数
    
    Returns:
        dict: 分页参数
    """
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
    except (ValueError, TypeError):
        page = 1
        per_page = 20
    
    # 参数范围限制
    page = max(1, page)
    per_page = min(max(1, per_page), 100)
    
    return {'page': page, 'per_page': per_page}

def safe_int(value: Any, default: int = 0) -> int:
    """
    安全转换为整数
    
    Args:
        value: 要转换的值
        default (int): 默认值
    
    Returns:
        int: 转换后的整数
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value: Any, default: float = 0.0) -> float:
    """
    安全转换为浮点数
    
    Args:
        value: 要转换的值
        default (float): 默认值
    
    Returns:
        float: 转换后的浮点数
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def truncate_string(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    截断字符串
    
    Args:
        text (str): 原始字符串
        max_length (int): 最大长度
        suffix (str): 后缀
    
    Returns:
        str: 截断后的字符串
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def clean_filename(filename: str) -> str:
    """
    清理文件名，移除非法字符
    
    Args:
        filename (str): 原始文件名
    
    Returns:
        str: 清理后的文件名
    """
    import re
    
    # 移除非法字符
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # 移除连续的下划线
    cleaned = re.sub(r'_+', '_', cleaned)
    
    # 移除首尾的下划线和空格
    cleaned = cleaned.strip('_ ')
    
    # 如果文件名为空，使用默认名称
    if not cleaned:
        cleaned = 'untitled'
    
    return cleaned

def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes (int): 字节数
    
    Returns:
        str: 格式化后的文件大小
    """
    if size_bytes == 0:
        return '0 B'
    
    size_names = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def calculate_percentage(part: float, total: float, decimal_places: int = 1) -> float:
    """
    计算百分比
    
    Args:
        part (float): 部分值
        total (float): 总值
        decimal_places (int): 小数位数
    
    Returns:
        float: 百分比
    """
    if total == 0:
        return 0.0
    
    percentage = (part / total) * 100
    return round(percentage, decimal_places)

def group_by_key(items: List[Dict], key: str) -> Dict[str, List[Dict]]:
    """
    按指定键对字典列表进行分组
    
    Args:
        items (list): 字典列表
        key (str): 分组键
    
    Returns:
        dict: 分组后的字典
    """
    groups = {}
    
    for item in items:
        group_key = item.get(key)
        if group_key not in groups:
            groups[group_key] = []
        groups[group_key].append(item)
    
    return groups

def sort_dict_by_value(data: Dict, reverse: bool = True) -> Dict:
    """
    按值对字典进行排序
    
    Args:
        data (dict): 要排序的字典
        reverse (bool): 是否降序
    
    Returns:
        dict: 排序后的字典
    """
    return dict(sorted(data.items(), key=lambda x: x[1], reverse=reverse))

def merge_dicts(*dicts) -> Dict:
    """
    合并多个字典
    
    Args:
        *dicts: 要合并的字典
    
    Returns:
        dict: 合并后的字典
    """
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result