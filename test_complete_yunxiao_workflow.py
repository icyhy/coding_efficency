#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的云效仓库管理工作流程测试
测试从查询云效仓库到加入统计的完整流程
"""

import requests
import json
import time

class YunxiaoWorkflowTester:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.session = requests.Session()
        self.token = None
        
    def login(self, username="admin", password="admin123"):
        """用户登录"""
        login_data = {
            "username": username,
            "password": password
        }
        
        response = self.session.post(f"{self.base_url}/api/auth/login", json=login_data)
        if response.status_code == 200:
            result = response.json()
            # 从嵌套的data字段中获取token
            data = result.get('data', {})
            self.token = data.get('access_token')
            self.session.headers.update({'Authorization': f'Bearer {self.token}'})
            print(f"✓ 登录成功: {username}")
            return True
        else:
            print(f"✗ 登录失败: {response.status_code} - {response.text}")
            return False
    
    def search_yunxiao_repositories(self, search_term="test"):
        """搜索云效仓库"""
        # 云效搜索API要求必须提供search参数
        params = {
            'search': search_term or 'test',  # 如果没有提供搜索词，默认使用'test'
            'page': 1,
            'per_page': 10
        }
            
        response = self.session.get(f"{self.base_url}/api/repositories/yunxiao/search", params=params)
        if response.status_code == 200:
            result = response.json()
            print(f"调试 - API响应结构: {type(result)}")
            print(f"调试 - API响应完整内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 处理嵌套的响应结构
            if isinstance(result, dict) and 'data' in result:
                data = result['data']
                if isinstance(data, dict) and 'items' in data:
                    repositories = data['items']
                else:
                    repositories = data if isinstance(data, list) else []
            else:
                repositories = result if isinstance(result, list) else []
            
            print(f"✓ 成功查询到 {len(repositories)} 个云效仓库")
            return repositories
        else:
            print(f"✗ 查询云效仓库失败: {response.status_code} - {response.text}")
            return []
    
    def add_yunxiao_repository(self, repo_data):
        """添加云效仓库到用户仓库管理"""
        response = self.session.post(f"{self.base_url}/api/repositories/yunxiao/add", json=repo_data)
        if response.status_code == 201:
            result = response.json()
            print(f"✓ 成功添加仓库: {repo_data.get('name', 'Unknown')}")
            return result
        else:
            print(f"✗ 添加仓库失败: {response.status_code} - {response.text}")
            return None
            
    def add_to_tracking(self, repo_id):
        """将仓库加入统计"""
        response = self.session.post(f"{self.base_url}/api/repositories/{repo_id}/track")
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 成功将仓库加入统计")
            return result
        else:
            print(f"✗ 加入统计失败: {response.status_code} - {response.text}")
            return None
            
    def get_user_repositories(self):
        """获取用户的所有仓库列表"""
        response = self.session.get(f"{self.base_url}/api/repositories/")
        if response.status_code == 200:
            result = response.json()
            print(f"调试 - 用户仓库API响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 处理嵌套的响应结构
            if isinstance(result, dict) and 'data' in result:
                data = result['data']
                if isinstance(data, dict) and 'items' in data:
                    repositories = data['items']
                else:
                    repositories = data if isinstance(data, list) else []
            else:
                repositories = result if isinstance(result, list) else []
                
            return repositories
        else:
            print(f"✗ 获取用户仓库列表失败: {response.status_code} - {response.text}")
            return []
    
    def get_tracked_repositories(self):
        """获取已加入统计的仓库列表"""
        response = self.session.get(f"{self.base_url}/api/repositories/")
        if response.status_code == 200:
            result = response.json()
            
            # 根据实际API响应结构获取仓库列表
            if isinstance(result, dict) and 'data' in result:
                all_repositories = result['data'].get('items', [])
            elif isinstance(result, dict) and 'items' in result:
                all_repositories = result.get('items', [])
            else:
                all_repositories = result if isinstance(result, list) else []
            
            # 过滤出已加入统计的仓库
            tracked_repositories = [repo for repo in all_repositories if repo.get('is_tracked', False)]
            print(f"✓ 获取到 {len(all_repositories)} 个仓库，其中 {len(tracked_repositories)} 个已加入统计")
            
            return tracked_repositories
        else:
            print(f"✗ 获取仓库列表失败: {response.status_code} - {response.text}")
            return []
    
    def remove_repository_from_tracking(self, repo_id):
        """将仓库从统计中移除"""
        response = self.session.delete(f"{self.base_url}/api/repositories/{repo_id}")
        if response.status_code == 200:
            print(f"✓ 成功将仓库 {repo_id} 从统计中移除")
            return True
        else:
            print(f"✗ 移除仓库失败: {response.status_code} - {response.text}")
            return False
    
    def run_complete_workflow_test(self):
        """运行完整的工作流程测试"""
        print("=== 开始完整的云效仓库管理工作流程测试 ===")
        
        # 1. 用户登录
        print("\n1. 测试用户登录...")
        if not self.login():
            print("登录失败，测试终止")
            return False
        
        # 2. 查询云效仓库
        print("\n2. 测试查询云效仓库...")
        yunxiao_repos = self.search_yunxiao_repositories()
        if not yunxiao_repos:
            print("未找到云效仓库，测试终止")
            return False
        
        # 显示找到的仓库
        print("找到的云效仓库:")
        # 确保yunxiao_repos是列表
        repo_list = yunxiao_repos if isinstance(yunxiao_repos, list) else []
        for i, repo in enumerate(repo_list[:3]):  # 只显示前3个
            print(f"  {i+1}. {repo.get('name', 'Unknown')} - {repo.get('description', 'No description')}")
        
        # 3. 选择一个仓库添加到统计
        print("\n3. 测试添加仓库到统计...")
        if not repo_list:
            print("没有可用的仓库进行测试")
            return False
        test_repo = repo_list[0]  # 选择第一个仓库
        
        # 准备仓库数据
        # 云效API返回的clone_url字段为空，使用url字段作为clone_url
        clone_url = test_repo.get('clone_url') or test_repo.get('url', '')
        if clone_url and not clone_url.endswith('.git'):
            clone_url = clone_url + '.git'  # 确保clone_url以.git结尾
            
        repo_data = {
            "repository_id": test_repo.get('id'),
            "name": test_repo.get('name') or test_repo.get('full_name', 'Unknown'),
            "clone_url": clone_url,
            "web_url": test_repo.get('url', ''),
            "description": test_repo.get('description', '')
        }
        
        print(f"调试 - 准备添加的仓库数据: {repo_data}")
        
        added_repo = self.add_yunxiao_repository(repo_data)
        repo_id = None
        
        if added_repo:
            # 成功添加新仓库
            repo_id = added_repo.get('data', {}).get('id')
        else:
            # 仓库可能已存在，尝试从用户仓库列表中查找
            print("\n仓库可能已存在，正在查找现有仓库...")
            existing_repos = self.get_user_repositories()
            for repo in existing_repos:
                if repo.get('name') == test_repo.get('name'):
                    repo_id = repo.get('id')
                    print(f"✓ 找到现有仓库: {repo.get('name')} (ID: {repo_id})")
                    break
            
            if not repo_id:
                print("\n无法找到仓库，测试终止")
                return False
                
        # 将仓库加入统计
        if repo_id:
            print(f"\n正在将仓库 {repo_id} 加入统计...")
            track_result = self.add_to_tracking(repo_id)
            if not track_result:
                # 检查是否是因为仓库已经在统计中
                print("\n仓库可能已经在统计中，继续验证...")
        else:
            print("\n无法获取仓库ID，跳过加入统计步骤")
            return False
        
        # 4. 验证仓库已加入统计列表
        print("\n4. 测试获取已加入统计的仓库列表...")
        tracked_repos = self.get_tracked_repositories()
        if not tracked_repos:
            print("✗ 获取统计列表失败")
            return False
            
        # 检查仓库是否在统计列表中
        found_in_tracking = False
        for tracked_repo in tracked_repos:
            if tracked_repo.get('id') == repo_id:
                found_in_tracking = True
                print(f"✓ 仓库已在统计列表中: {tracked_repo.get('name')}")
                break
                
        if not found_in_tracking:
            print("✗ 仓库未在统计列表中找到")
            return False
        
        # 5. 测试从统计中移除仓库
        print("\n5. 测试从统计中移除仓库...")
        if self.remove_repository_from_tracking(repo_id):
            # 验证仓库已被移除
            updated_repos = self.get_tracked_repositories()
            still_exists = any(repo.get('id') == repo_id for repo in updated_repos)
            
            if not still_exists:
                print("✓ 确认仓库已成功从统计中移除")
            else:
                print("✗ 仓库仍在统计列表中")
                return False
        else:
            print("移除仓库失败")
            return False
        
        print("\n=== 完整工作流程测试成功完成 ===")
        return True

def main():
    tester = YunxiaoWorkflowTester()
    
    try:
        success = tester.run_complete_workflow_test()
        if success:
            print("\n🎉 所有测试通过！云效仓库管理功能工作正常。")
        else:
            print("\n❌ 测试失败，请检查相关功能。")
    except Exception as e:
        print(f"\n💥 测试过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()