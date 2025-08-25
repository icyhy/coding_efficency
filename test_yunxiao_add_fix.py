#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试云效仓库添加功能修复
验证 Fernet 密钥问题是否已解决
"""

import requests
import json
import time
from datetime import datetime

class YunxiaoAddTest:
    def __init__(self):
        self.base_url = 'http://localhost:5000'
        self.access_token = None
        
    def login(self):
        """登录获取访问令牌"""
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        try:
            response = requests.post(f'{self.base_url}/api/auth/login', json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('data', {}).get('access_token')
                print(f"✅ 登录成功，获取到访问令牌")
                return True
            else:
                print(f"❌ 登录失败: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ 登录异常: {str(e)}")
            return False
    
    def test_add_yunxiao_repository(self):
        """测试添加云效仓库"""
        if not self.access_token:
            print("❌ 未登录，无法测试")
            return False
            
        # 测试数据
        test_repo_data = {
            'repository_id': int(time.time()),  # 使用时间戳确保唯一性
            'name': f'test-repo-{int(time.time())}',
            'clone_url': f'https://codeup.aliyun.com/test/test-repo-{int(time.time())}.git',
            'web_url': f'https://codeup.aliyun.com/test/test-repo-{int(time.time())}',
            'description': 'Test repository for Fernet key fix validation'
        }
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            print(f"\n🔄 正在测试添加云效仓库...")
            print(f"测试数据: {json.dumps(test_repo_data, indent=2, ensure_ascii=False)}")
            
            response = requests.post(
                f'{self.base_url}/api/repositories/yunxiao/add',
                json=test_repo_data,
                headers=headers
            )
            
            print(f"\n📊 响应状态码: {response.status_code}")
            print(f"📊 响应内容: {response.text}")
            
            if response.status_code == 201:
                data = response.json()
                repo_data = data.get('data', {})
                print(f"\n✅ 云效仓库添加成功!")
                print(f"   仓库ID: {repo_data.get('id')}")
                print(f"   仓库名称: {repo_data.get('name')}")
                print(f"   平台: {repo_data.get('platform')}")
                print(f"   是否加入统计: {repo_data.get('is_tracked')}")
                return True
            elif response.status_code == 409:
                print(f"⚠️  仓库已存在（这是正常情况）")
                return True
            else:
                print(f"❌ 添加失败: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   错误信息: {error_data.get('message', 'Unknown error')}")
                except:
                    print(f"   原始响应: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
            return False
    
    def run_test(self):
        """运行完整测试"""
        print("=== 云效仓库添加功能修复测试 ===")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"目标: 验证 Fernet 密钥错误是否已修复")
        
        # 1. 登录
        if not self.login():
            return False
            
        # 2. 测试添加云效仓库
        success = self.test_add_yunxiao_repository()
        
        print(f"\n=== 测试结果 ===")
        if success:
            print("✅ 测试通过! Fernet 密钥问题已修复")
            print("✅ 云效仓库可以正常添加到数据库")
        else:
            print("❌ 测试失败! 仍存在问题")
            
        return success

if __name__ == '__main__':
    tester = YunxiaoAddTest()
    tester.run_test()