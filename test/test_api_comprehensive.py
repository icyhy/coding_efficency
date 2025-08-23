#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
后端API综合测试脚本
测试所有API接口的功能和响应
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import sys
import os

class APITester:
    """
    API测试类
    提供完整的API接口测试功能
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        """
        初始化API测试器
        
        Args:
            base_url (str): API基础URL
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        self.test_user_id = None
        self.test_repo_id = None
        
        # 测试结果统计
        self.test_results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        
        print(f"🚀 API测试器初始化完成，基础URL: {self.base_url}")
    
    def log_test(self, test_name: str, success: bool, message: str = "", response_data: Any = None):
        """
        记录测试结果
        
        Args:
            test_name (str): 测试名称
            success (bool): 是否成功
            message (str): 消息
            response_data (Any): 响应数据
        """
        self.test_results['total'] += 1
        
        if success:
            self.test_results['passed'] += 1
            print(f"✅ {test_name}: {message}")
        else:
            self.test_results['failed'] += 1
            error_info = f"❌ {test_name}: {message}"
            if response_data:
                error_info += f" | 响应: {response_data}"
            print(error_info)
            self.test_results['errors'].append(error_info)
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, 
                    params: Dict = None, headers: Dict = None, 
                    use_auth: bool = True) -> requests.Response:
        """
        发送HTTP请求
        
        Args:
            method (str): HTTP方法
            endpoint (str): API端点
            data (Dict): 请求数据
            params (Dict): 查询参数
            headers (Dict): 请求头
            use_auth (bool): 是否使用认证
        
        Returns:
            requests.Response: 响应对象
        """
        url = f"{self.base_url}{endpoint}"
        
        # 设置默认请求头
        request_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # 添加认证头
        if use_auth and self.access_token:
            request_headers['Authorization'] = f'Bearer {self.access_token}'
        
        # 合并自定义请求头
        if headers:
            request_headers.update(headers)
        
        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                json=data,
                params=params,
                headers=request_headers,
                timeout=30
            )
            return response
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {e}")
            raise
    
    def test_health_check(self):
        """
        测试健康检查接口
        """
        print("\n=== 健康检查测试 ===")
        
        try:
            response = self.make_request('GET', '/health', use_auth=False)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "健康检查", 
                    True, 
                    f"服务正常运行 - 状态: {data.get('status', 'unknown')}"
                )
            else:
                self.log_test(
                    "健康检查", 
                    False, 
                    f"状态码: {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_test("健康检查", False, f"异常: {str(e)}")
    
    def test_api_info(self):
        """
        测试API信息接口
        """
        print("\n=== API信息测试 ===")
        
        try:
            response = self.make_request('GET', '/api/info', use_auth=False)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "API信息", 
                    True, 
                    f"API名称: {data.get('name', 'unknown')}, 版本: {data.get('version', 'unknown')}"
                )
            else:
                self.log_test(
                    "API信息", 
                    False, 
                    f"状态码: {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_test("API信息", False, f"异常: {str(e)}")
    
    def test_auth_register(self):
        """
        测试用户注册接口
        """
        print("\n=== 用户注册测试 ===")
        
        # 生成唯一的测试用户数据
        timestamp = int(time.time())
        test_data = {
            'username': f'testuser_{timestamp}',
            'email': f'test_{timestamp}@example.com',
            'password': 'TestPass123!'
        }
        
        try:
            response = self.make_request('POST', '/api/auth/register', data=test_data, use_auth=False)
            
            if response.status_code == 201:
                data = response.json()
                self.access_token = data.get('data', {}).get('access_token')
                self.refresh_token = data.get('data', {}).get('refresh_token')
                self.test_user_id = data.get('data', {}).get('user', {}).get('id')
                
                self.log_test(
                    "用户注册", 
                    True, 
                    f"用户创建成功 - ID: {self.test_user_id}, 用户名: {test_data['username']}"
                )
            else:
                self.log_test(
                    "用户注册", 
                    False, 
                    f"状态码: {response.status_code}",
                    response.json() if response.content else response.text
                )
        except Exception as e:
            self.log_test("用户注册", False, f"异常: {str(e)}")
    
    def test_auth_login(self):
        """
        测试用户登录接口
        """
        print("\n=== 用户登录测试 ===")
        
        # 如果没有access_token，说明注册失败，跳过登录测试
        if not self.access_token:
            self.log_test("用户登录", False, "跳过测试 - 用户注册失败")
            return
        
        # 使用注册时的用户名和密码
        timestamp = int(time.time())
        login_data = {
            'username': f'testuser_{timestamp}',
            'password': 'TestPass123!'
        }
        
        try:
            response = self.make_request('POST', '/api/auth/login', data=login_data, use_auth=False)
            
            if response.status_code == 200:
                data = response.json()
                # 更新token（可能与注册时不同）
                self.access_token = data.get('data', {}).get('access_token')
                self.refresh_token = data.get('data', {}).get('refresh_token')
                
                self.log_test(
                    "用户登录", 
                    True, 
                    f"登录成功 - 用户: {login_data['username']}"
                )
            else:
                self.log_test(
                    "用户登录", 
                    False, 
                    f"状态码: {response.status_code}",
                    response.json() if response.content else response.text
                )
        except Exception as e:
            self.log_test("用户登录", False, f"异常: {str(e)}")
    
    def test_auth_profile(self):
        """
        测试获取用户资料接口
        """
        print("\n=== 用户资料测试 ===")
        
        if not self.access_token:
            self.log_test("获取用户资料", False, "跳过测试 - 未登录")
            return
        
        try:
            response = self.make_request('GET', '/api/auth/profile')
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get('data', {})
                self.log_test(
                    "获取用户资料", 
                    True, 
                    f"用户ID: {user_data.get('id')}, 用户名: {user_data.get('username')}"
                )
            else:
                self.log_test(
                    "获取用户资料", 
                    False, 
                    f"状态码: {response.status_code}",
                    response.json() if response.content else response.text
                )
        except Exception as e:
            self.log_test("获取用户资料", False, f"异常: {str(e)}")
    
    def test_auth_refresh_token(self):
        """
        测试刷新Token接口
        """
        print("\n=== Token刷新测试 ===")
        
        if not self.refresh_token:
            self.log_test("Token刷新", False, "跳过测试 - 无刷新Token")
            return
        
        try:
            # 使用refresh token
            headers = {'Authorization': f'Bearer {self.refresh_token}'}
            response = self.make_request('POST', '/api/auth/refresh', headers=headers, use_auth=False)
            
            if response.status_code == 200:
                data = response.json()
                new_access_token = data.get('data', {}).get('access_token')
                if new_access_token:
                    self.access_token = new_access_token
                
                self.log_test(
                    "Token刷新", 
                    True, 
                    "新的访问Token获取成功"
                )
            else:
                self.log_test(
                    "Token刷新", 
                    False, 
                    f"状态码: {response.status_code}",
                    response.json() if response.content else response.text
                )
        except Exception as e:
            self.log_test("Token刷新", False, f"异常: {str(e)}")
    
    def test_repositories_list(self):
        """
        测试获取仓库列表接口
        """
        print("\n=== 仓库列表测试 ===")
        
        if not self.access_token:
            self.log_test("获取仓库列表", False, "跳过测试 - 未登录")
            return
        
        try:
            response = self.make_request('GET', '/api/repositories/')
            
            if response.status_code == 200:
                data = response.json()
                repositories = data.get('data', {}).get('repositories', [])
                self.log_test(
                    "获取仓库列表", 
                    True, 
                    f"成功获取 {len(repositories)} 个仓库"
                )
            else:
                self.log_test(
                    "获取仓库列表", 
                    False, 
                    f"状态码: {response.status_code}",
                    response.json() if response.content else response.text
                )
        except Exception as e:
            self.log_test("获取仓库列表", False, f"异常: {str(e)}")
    
    def test_yunxiao_search(self):
        """
        测试云效仓库搜索接口
        """
        print("\n=== 云效仓库搜索测试 ===")
        
        if not self.access_token:
            self.log_test("云效仓库搜索", False, "跳过测试 - 未登录")
            return
        
        try:
            params = {
                'page': 1,
                'per_page': 10,
                'search': 'test'
            }
            response = self.make_request('GET', '/api/repositories/yunxiao/search', params=params)
            
            if response.status_code == 200:
                data = response.json()
                repositories = data.get('data', [])
                self.log_test(
                    "云效仓库搜索", 
                    True, 
                    f"搜索到 {len(repositories)} 个仓库"
                )
            else:
                self.log_test(
                    "云效仓库搜索", 
                    False, 
                    f"状态码: {response.status_code}",
                    response.json() if response.content else response.text
                )
        except Exception as e:
            self.log_test("云效仓库搜索", False, f"异常: {str(e)}")
    
    def test_yunxiao_add_repository(self):
        """
        测试添加云效仓库接口
        """
        print("\n=== 添加云效仓库测试 ===")
        
        if not self.access_token:
            self.log_test("添加云效仓库", False, "跳过测试 - 未登录")
            return
        
        # 测试数据
        test_repo_data = {
            'repository_id': 12345,
            'name': 'test-repo',
            'clone_url': 'https://codeup.aliyun.com/test/test-repo.git',
            'web_url': 'https://codeup.aliyun.com/test/test-repo',
            'description': 'Test repository for API testing'
        }
        
        try:
            response = self.make_request('POST', '/api/repositories/yunxiao/add', data=test_repo_data)
            
            if response.status_code == 201:
                data = response.json()
                repo_data = data.get('data', {})
                self.test_repo_id = repo_data.get('id')
                self.log_test(
                    "添加云效仓库", 
                    True, 
                    f"仓库添加成功 - ID: {self.test_repo_id}, 名称: {repo_data.get('name')}"
                )
            elif response.status_code == 409:
                # 仓库已存在，这也算是正常情况
                self.log_test(
                    "添加云效仓库", 
                    True, 
                    "仓库已存在（正常情况）"
                )
            else:
                self.log_test(
                    "添加云效仓库", 
                    False, 
                    f"状态码: {response.status_code}",
                    response.json() if response.content else response.text
                )
        except Exception as e:
            self.log_test("添加云效仓库", False, f"异常: {str(e)}")
    
    def test_repository_tracking(self):
        """
        测试仓库跟踪功能（加入/移出统计）
        """
        print("\n=== 仓库跟踪测试 ===")
        
        if not self.access_token or not self.test_repo_id:
            self.log_test("仓库跟踪", False, "跳过测试 - 未登录或无测试仓库")
            return
        
        try:
            # 测试加入统计
            response = self.make_request('POST', f'/api/repositories/{self.test_repo_id}/track')
            
            if response.status_code == 200:
                self.log_test(
                    "加入统计", 
                    True, 
                    "仓库成功加入统计"
                )
                
                # 测试移出统计
                response = self.make_request('POST', f'/api/repositories/{self.test_repo_id}/untrack')
                
                if response.status_code == 200:
                    self.log_test(
                        "移出统计", 
                        True, 
                        "仓库成功移出统计"
                    )
                else:
                    self.log_test(
                        "移出统计", 
                        False, 
                        f"状态码: {response.status_code}",
                        response.json() if response.content else response.text
                    )
            else:
                self.log_test(
                    "加入统计", 
                    False, 
                    f"状态码: {response.status_code}",
                    response.json() if response.content else response.text
                )
        except Exception as e:
            self.log_test("仓库跟踪", False, f"异常: {str(e)}")
    
    def test_analytics_dashboard(self):
        """
        测试分析统计仪表盘接口
        """
        print("\n=== 分析统计测试 ===")
        
        if not self.access_token:
            self.log_test("分析统计", False, "跳过测试 - 未登录")
            return
        
        try:
            response = self.make_request('GET', '/api/analytics/dashboard')
            
            if response.status_code == 200:
                data = response.json()
                dashboard_data = data.get('data', {})
                self.log_test(
                    "分析统计", 
                    True, 
                    f"获取仪表盘数据成功 - 仓库数: {dashboard_data.get('total_repositories', 0)}"
                )
            else:
                self.log_test(
                    "分析统计", 
                    False, 
                    f"状态码: {response.status_code}",
                    response.json() if response.content else response.text
                )
        except Exception as e:
            self.log_test("分析统计", False, f"异常: {str(e)}")
    
    def run_auth_tests(self):
        """
        运行所有认证相关测试
        """
        print("\n🔐 开始认证模块测试...")
        
        self.test_health_check()
        self.test_api_info()
        self.test_auth_register()
        self.test_auth_login()
        self.test_auth_profile()
        self.test_auth_refresh_token()
    
    def run_repository_tests(self):
        """
        运行所有仓库管理相关测试
        """
        print("\n📁 开始仓库管理模块测试...")
        
        self.test_repositories_list()
        self.test_yunxiao_search()
        self.test_yunxiao_add_repository()
        self.test_repository_tracking()
    
    def run_analytics_tests(self):
        """
        运行所有分析统计相关测试
        """
        print("\n📊 开始分析统计模块测试...")
        
        self.test_analytics_dashboard()
    
    def run_all_tests(self):
        """
        运行所有测试
        """
        self.run_auth_tests()
        self.run_repository_tests()
        self.run_analytics_tests()
    
    def print_summary(self):
        """
        打印测试结果摘要
        """
        print("\n" + "="*50)
        print("📊 测试结果摘要")
        print("="*50)
        print(f"总测试数: {self.test_results['total']}")
        print(f"通过: {self.test_results['passed']}")
        print(f"失败: {self.test_results['failed']}")
        
        if self.test_results['failed'] > 0:
            print("\n❌ 失败的测试:")
            for error in self.test_results['errors']:
                print(f"  {error}")
        
        success_rate = (self.test_results['passed'] / self.test_results['total'] * 100) if self.test_results['total'] > 0 else 0
        print(f"\n成功率: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("🎉 所有测试通过！")
        elif success_rate >= 80:
            print("⚠️  大部分测试通过，但有一些问题需要修复")
        else:
            print("🚨 多个测试失败，需要重点关注")

def main():
    """
    主函数
    """
    print("🧪 后端API综合测试开始")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建测试器实例
    tester = APITester()
    
    try:
        # 运行所有测试模块
        tester.run_all_tests()
        
        # 打印测试摘要
        tester.print_summary()
        
    except KeyboardInterrupt:
        print("\n⏹️  测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🏁 测试完成")

if __name__ == '__main__':
    main()