#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试仓库加入统计和移出统计功能
验证仓库跟踪管理是否正常工作
"""

import requests
import json
import time
from datetime import datetime

class TrackingFunctionalityTest:
    def __init__(self):
        self.base_url = 'http://localhost:5000'
        self.access_token = None
        self.test_repo_id = None
        
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
    
    def get_repositories(self):
        """获取用户仓库列表"""
        if not self.access_token:
            return []
            
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        
        try:
            response = requests.get(f'{self.base_url}/api/repositories/', headers=headers)
            if response.status_code == 200:
                data = response.json()
                repositories = data.get('data', [])
                print(f"📋 获取到 {len(repositories)} 个仓库")
                print(f"📋 仓库数据类型: {type(repositories)}")
                if isinstance(repositories, dict):
                    repositories = repositories.get('items', [])
                return repositories
            else:
                print(f"❌ 获取仓库列表失败: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ 获取仓库列表异常: {str(e)}")
            return []
    
    def add_to_tracking(self, repo_id):
        """将仓库加入统计"""
        if not self.access_token:
            return False
            
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            print(f"\n🔄 正在将仓库 {repo_id} 加入统计...")
            response = requests.post(
                f'{self.base_url}/api/repositories/{repo_id}/track',
                headers=headers
            )
            
            print(f"📊 响应状态码: {response.status_code}")
            print(f"📊 响应内容: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                repo_data = data.get('data', {})
                print(f"✅ 仓库 {repo_id} 已成功加入统计")
                print(f"   仓库名称: {repo_data.get('name')}")
                print(f"   是否加入统计: {repo_data.get('is_tracked')}")
                return True
            else:
                print(f"❌ 加入统计失败: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   错误信息: {error_data.get('message', 'Unknown error')}")
                except:
                    print(f"   原始响应: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 加入统计异常: {str(e)}")
            return False
    
    def remove_from_tracking(self, repo_id):
        """将仓库移出统计"""
        if not self.access_token:
            return False
            
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            print(f"\n🔄 正在将仓库 {repo_id} 移出统计...")
            response = requests.post(
                f'{self.base_url}/api/repositories/{repo_id}/untrack',
                headers=headers
            )
            
            print(f"📊 响应状态码: {response.status_code}")
            print(f"📊 响应内容: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                repo_data = data.get('data', {})
                print(f"✅ 仓库 {repo_id} 已成功移出统计")
                print(f"   仓库名称: {repo_data.get('name')}")
                print(f"   是否加入统计: {repo_data.get('is_tracked')}")
                return True
            else:
                print(f"❌ 移出统计失败: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   错误信息: {error_data.get('message', 'Unknown error')}")
                except:
                    print(f"   原始响应: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 移出统计异常: {str(e)}")
            return False
    
    def run_test(self):
        """运行完整测试"""
        print("=== 仓库统计管理功能测试 ===")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"目标: 验证仓库加入统计和移出统计功能")
        
        # 1. 登录
        if not self.login():
            return False
            
        # 2. 获取仓库列表
        repositories = self.get_repositories()
        if not repositories:
            print("❌ 没有找到可测试的仓库")
            return False
        
        # 3. 选择一个仓库进行测试
        test_repo = repositories[0]
        repo_id = test_repo.get('id')
        repo_name = test_repo.get('name')
        is_tracked = test_repo.get('is_tracked')
        
        print(f"\n📋 选择测试仓库:")
        print(f"   ID: {repo_id}")
        print(f"   名称: {repo_name}")
        print(f"   当前是否加入统计: {is_tracked}")
        
        success_count = 0
        total_tests = 0
        
        # 4. 测试加入统计功能
        if not is_tracked:
            total_tests += 1
            if self.add_to_tracking(repo_id):
                success_count += 1
                
                # 验证状态是否更新
                updated_repos = self.get_repositories()
                updated_repo = next((r for r in updated_repos if r['id'] == repo_id), None)
                if updated_repo and updated_repo.get('is_tracked'):
                    print("✅ 仓库状态已正确更新为加入统计")
                else:
                    print("❌ 仓库状态未正确更新")
        
        # 5. 测试移出统计功能
        total_tests += 1
        if self.remove_from_tracking(repo_id):
            success_count += 1
            
            # 验证状态是否更新
            updated_repos = self.get_repositories()
            updated_repo = next((r for r in updated_repos if r['id'] == repo_id), None)
            if updated_repo and not updated_repo.get('is_tracked'):
                print("✅ 仓库状态已正确更新为移出统计")
            else:
                print("❌ 仓库状态未正确更新")
        
        # 6. 再次测试加入统计功能
        total_tests += 1
        if self.add_to_tracking(repo_id):
            success_count += 1
            
            # 验证状态是否更新
            updated_repos = self.get_repositories()
            updated_repo = next((r for r in updated_repos if r['id'] == repo_id), None)
            if updated_repo and updated_repo.get('is_tracked'):
                print("✅ 仓库状态已正确更新为加入统计")
            else:
                print("❌ 仓库状态未正确更新")
        
        print(f"\n=== 测试结果 ===")
        print(f"总测试数: {total_tests}")
        print(f"成功测试数: {success_count}")
        print(f"成功率: {success_count/total_tests*100:.1f}%")
        
        if success_count == total_tests:
            print("✅ 所有测试通过! 仓库统计管理功能正常")
            return True
        else:
            print("❌ 部分测试失败! 仓库统计管理功能存在问题")
            return False

if __name__ == '__main__':
    tester = TrackingFunctionalityTest()
    tester.run_test()