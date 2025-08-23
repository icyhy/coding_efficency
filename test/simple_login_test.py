#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的登录测试脚本
用于验证后端登录接口是否正常工作
"""

import requests
import json

def test_login():
    """
    测试登录接口
    """
    url = "http://localhost:3000/api/auth/login"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        print(f"正在请求: {url}")
        print(f"请求数据: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.content:
            try:
                response_data = response.json()
                print(f"响应数据: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            except json.JSONDecodeError:
                print(f"响应文本: {response.text}")
        else:
            print("响应为空")
            
        return response.status_code == 200
        
    except requests.exceptions.ConnectionError as e:
        print(f"连接错误: {e}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"请求超时: {e}")
        return False
    except Exception as e:
        print(f"其他错误: {e}")
        return False

if __name__ == '__main__':
    print("开始测试登录接口...")
    success = test_login()
    print(f"\n测试结果: {'成功' if success else '失败'}")