#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试token认证问题
"""

import requests
import json

def test_token_auth():
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    # 1. 登录获取token
    print("1. 测试登录...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = session.post(f"{base_url}/api/auth/login", json=login_data)
    print(f"登录响应状态码: {response.status_code}")
    print(f"登录响应内容: {response.text}")
    
    if response.status_code != 200:
        print("登录失败，停止测试")
        return
    
    result = response.json()
    # 从嵌套的data字段中获取token
    data = result.get('data', {})
    token = data.get('access_token')
    print(f"获取到的token: {token[:50] if token else 'None'}...")
    
    if not token:
        print("未获取到token，停止测试")
        return
    
    # 2. 设置Authorization头
    session.headers.update({'Authorization': f'Bearer {token}'})
    print(f"设置的Authorization头: {session.headers.get('Authorization')[:70]}...")
    
    # 3. 测试需要认证的API
    print("\n2. 测试认证API...")
    
    # 测试仓库列表API
    print("测试仓库列表API...")
    response = session.get(f"{base_url}/api/repositories/")
    print(f"仓库列表API响应状态码: {response.status_code}")
    print(f"仓库列表API响应内容: {response.text[:200]}...")
    
    # 测试云效搜索API
    print("\n测试云效搜索API...")
    params = {
        'search': 'test',
        'page': 1,
        'per_page': 10
    }
    response = session.get(f"{base_url}/api/repositories/yunxiao/search", params=params)
    print(f"云效搜索API响应状态码: {response.status_code}")
    print(f"云效搜索API响应内容: {response.text[:200]}...")
    
    # 4. 直接使用requests测试（不使用session）
    print("\n3. 直接使用requests测试...")
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{base_url}/api/repositories/yunxiao/search", 
                          params=params, headers=headers)
    print(f"直接请求响应状态码: {response.status_code}")
    print(f"直接请求响应内容: {response.text[:200]}...")

if __name__ == "__main__":
    test_token_auth()