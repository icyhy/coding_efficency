#!/usr/bin/env python3

import sys
sys.path.append('backend')

from datetime import datetime, timedelta
from typing import Optional

try:
    from dateutil import parser as date_parser
except ImportError:
    date_parser = None

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
                  days: Optional[int] = None, strict: bool = False):
    """
    获取日期范围
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

# 测试
if __name__ == '__main__':
    print("测试日期解析:")
    
    # 测试有效日期
    print(f"有效日期 '2024-01-01': {parse_datetime_string('2024-01-01')}")
    
    # 测试无效日期
    print(f"无效日期 'invalid-date': {parse_datetime_string('invalid-date')}")
    
    # 测试严格模式
    print("\n测试严格模式:")
    try:
        result = get_date_range_by_params('invalid-date', '2024-12-31', strict=True)
        print(f"严格模式结果: {result}")
    except ValueError as e:
        print(f"严格模式异常: {e}")
    
    # 测试非严格模式
    print("\n测试非严格模式:")
    result = get_date_range_by_params('invalid-date', '2024-12-31', strict=False)
    print(f"非严格模式结果: {result}")