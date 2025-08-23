#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析统计API接口测试脚本
测试所有数据分析、报表生成等功能接口
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class AnalyticsAPITester:
    """
    分析统计API测试类
    """
    
    def __init__(self, base_url: str = "http://localhost:5001"):
        """
        初始化测试器
        
        Args:
            base_url: API基础URL
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
        self.test_user_id = None
        self.test_repo_ids = []
        
    def log_test(self, test_name: str, success: bool, message: str, details: Optional[Dict] = None):
        """
        记录测试结果
        
        Args:
            test_name: 测试名称
            success: 是否成功
            message: 测试消息
            details: 详细信息
        """
        result = {
            'test_name': test_name,
            'success': success,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{status} - {test_name}: {message}")
        if details and success:
            print(f"   详细信息: {json.dumps(details, ensure_ascii=False, indent=2)}")
        elif details and not success:
            print(f"   错误详情: {json.dumps(details, ensure_ascii=False, indent=2)}")
    
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    params: Optional[Dict] = None) -> requests.Response:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法
            endpoint: API端点
            data: 请求数据
            params: 查询参数
            
        Returns:
            响应对象
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, headers=headers, params=params, timeout=10)
            elif method.upper() == 'POST':
                response = self.session.post(url, headers=headers, json=data, params=params, timeout=10)
            elif method.upper() == 'PUT':
                response = self.session.put(url, headers=headers, json=data, params=params, timeout=10)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, headers=headers, params=params, timeout=10)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {e}")
            raise
    
    def login(self, username: str = "admin", password: str = "admin123") -> bool:
        """
        用户登录获取访问令牌
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            是否登录成功
        """
        try:
            response = self.make_request('POST', '/api/auth/login', {
                'username': username,
                'password': password
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'access_token' in data.get('data', {}):
                    self.access_token = data['data']['access_token']
                    self.test_user_id = data['data'].get('id')
                    self.log_test("用户登录", True, f"登录成功，用户ID: {self.test_user_id}")
                    return True
                else:
                    self.log_test("用户登录", False, "登录响应格式错误", data)
                    return False
            else:
                self.log_test("用户登录", False, f"登录失败，状态码: {response.status_code}", 
                            response.json() if response.content else response.text)
                return False
        except Exception as e:
            self.log_test("用户登录", False, f"登录异常: {str(e)}")
            return False
    
    def get_test_repositories(self) -> List[int]:
        """
        获取测试用的仓库ID列表
        
        Returns:
            仓库ID列表
        """
        try:
            response = self.make_request('GET', '/api/repositories/')
            if response.status_code == 200:
                data = response.json()
                repositories = data.get('data', [])
                repo_ids = [repo['id'] for repo in repositories if repo.get('is_tracked', False)]
                self.test_repo_ids = repo_ids[:3]  # 取前3个用于测试
                return self.test_repo_ids
            else:
                return []
        except Exception:
            return []
    
    def test_analytics_overview(self):
        """
        测试分析概览接口
        """
        try:
            # 获取默认概览
            response = self.make_request('GET', '/api/analytics/overview')
            
            if response.status_code == 200:
                data = response.json()
                overview_data = data.get('data', {})
                self.log_test(
                    "分析概览 - 默认查询", 
                    True, 
                    f"获取概览成功 - 仓库数: {overview_data.get('repositories_count', 0)}, 提交数: {overview_data.get('commits_count', 0)}",
                    overview_data
                )
            else:
                self.log_test(
                    "分析概览 - 默认查询", 
                    False, 
                    f"状态码: {response.status_code}",
                    response.json() if response.content else response.text
                )
            
            # 测试带参数的查询
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            params = {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            }
            
            if self.test_repo_ids:
                params['repository_ids'] = ','.join(map(str, self.test_repo_ids))
            
            response = self.make_request('GET', '/api/analytics/overview', params=params)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "分析概览 - 参数查询", 
                    True, 
                    "带参数查询成功",
                    data.get('data', {})
                )
            else:
                self.log_test(
                    "分析概览 - 参数查询", 
                    False, 
                    f"状态码: {response.status_code}",
                    response.json() if response.content else response.text
                )
                
        except Exception as e:
            self.log_test("分析概览测试", False, f"异常: {str(e)}")
    
    def test_commits_analytics(self):
        """
        测试提交统计分析接口
        """
        try:
            # 测试默认查询
            response = self.make_request('GET', '/api/analytics/commits')
            
            if response.status_code == 200:
                data = response.json()
                commits_data = data.get('data', {})
                self.log_test(
                    "提交统计 - 默认查询", 
                    True, 
                    f"获取提交统计成功 - 总数: {commits_data.get('total_count', 0)}",
                    commits_data
                )
            else:
                self.log_test(
                    "提交统计 - 默认查询", 
                    False, 
                    f"状态码: {response.status_code}",
                    response.json() if response.content else response.text
                )
            
            # 测试不同分组方式
            for group_by in ['day', 'week', 'month', 'author']:
                params = {'group_by': group_by}
                response = self.make_request('GET', '/api/analytics/commits', params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(
                        f"提交统计 - {group_by}分组", 
                        True, 
                        f"按{group_by}分组查询成功"
                    )
                else:
                    self.log_test(
                        f"提交统计 - {group_by}分组", 
                        False, 
                        f"状态码: {response.status_code}",
                        response.json() if response.content else response.text
                    )
                    
        except Exception as e:
            self.log_test("提交统计测试", False, f"异常: {str(e)}")
    
    def test_merge_requests_analytics(self):
        """
        测试合并请求统计分析接口
        """
        try:
            # 测试默认查询
            response = self.make_request('GET', '/api/analytics/merge-requests')
            
            if response.status_code == 200:
                data = response.json()
                mrs_data = data.get('data', {})
                self.log_test(
                    "合并请求统计 - 默认查询", 
                    True, 
                    f"获取合并请求统计成功 - 总数: {mrs_data.get('total_count', 0)}",
                    mrs_data
                )
            else:
                self.log_test(
                    "合并请求统计 - 默认查询", 
                    False, 
                    f"状态码: {response.status_code}",
                    response.json() if response.content else response.text
                )
            
            # 测试状态筛选
            for state in ['opened', 'merged', 'closed']:
                params = {'state': state}
                response = self.make_request('GET', '/api/analytics/merge-requests', params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(
                        f"合并请求统计 - {state}状态", 
                        True, 
                        f"按{state}状态筛选成功"
                    )
                else:
                    self.log_test(
                        f"合并请求统计 - {state}状态", 
                        False, 
                        f"状态码: {response.status_code}",
                        response.json() if response.content else response.text
                    )
                    
        except Exception as e:
            self.log_test("合并请求统计测试", False, f"异常: {str(e)}")
    
    def test_time_distribution(self):
        """
        测试时间分布分析接口
        """
        try:
            # 测试不同类型和维度的组合
            test_cases = [
                {'type': 'commits', 'dimension': 'hour'},
                {'type': 'commits', 'dimension': 'weekday'},
                {'type': 'commits', 'dimension': 'month'},
                {'type': 'merge_requests', 'dimension': 'hour'},
                {'type': 'merge_requests', 'dimension': 'weekday'}
            ]
            
            for case in test_cases:
                response = self.make_request('GET', '/api/analytics/time-distribution', params=case)
                
                if response.status_code == 200:
                    data = response.json()
                    distribution_data = data.get('data', {})
                    self.log_test(
                        f"时间分布 - {case['type']}按{case['dimension']}", 
                        True, 
                        f"获取时间分布成功 - 数据点数: {len(distribution_data.get('distribution', []))}"
                    )
                else:
                    self.log_test(
                        f"时间分布 - {case['type']}按{case['dimension']}", 
                        False, 
                        f"状态码: {response.status_code}",
                        response.json() if response.content else response.text
                    )
                    
        except Exception as e:
            self.log_test("时间分布测试", False, f"异常: {str(e)}")
    
    def test_user_analytics(self):
        """
        测试用户分析接口
        """
        if not self.test_user_id:
            self.log_test("用户分析测试", False, "跳过测试 - 无用户ID")
            return
            
        try:
            # 测试获取用户分析数据
            response = self.make_request('GET', f'/api/analytics/user/{self.test_user_id}')
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get('user', {})
                stats_data = data.get('statistics', {})
                self.log_test(
                    "用户分析 - 默认查询", 
                    True, 
                    f"获取用户分析成功 - 用户: {user_data.get('username', 'N/A')}",
                    stats_data
                )
            else:
                self.log_test(
                    "用户分析 - 默认查询", 
                    False, 
                    f"状态码: {response.status_code}",
                    response.json() if response.content else response.text
                )
            
            # 测试不同天数参数
            for days in [7, 30, 90]:
                params = {'days': days}
                response = self.make_request('GET', f'/api/analytics/user/{self.test_user_id}', params=params)
                
                if response.status_code == 200:
                    self.log_test(
                        f"用户分析 - {days}天", 
                        True, 
                        f"获取{days}天用户分析成功"
                    )
                else:
                    self.log_test(
                        f"用户分析 - {days}天", 
                        False, 
                        f"状态码: {response.status_code}",
                        response.json() if response.content else response.text
                    )
                    
        except Exception as e:
            self.log_test("用户分析测试", False, f"异常: {str(e)}")
    
    def test_error_handling(self):
        """
        测试错误处理
        """
        try:
            # 测试无效的日期格式
            params = {
                'start_date': 'invalid-date',
                'end_date': '2024-12-31'
            }
            response = self.make_request('GET', '/api/analytics/overview', params=params)
            
            if response.status_code in [400, 422]:
                self.log_test(
                    "错误处理 - 无效日期", 
                    True, 
                    f"正确返回错误状态码: {response.status_code}"
                )
            else:
                self.log_test(
                    "错误处理 - 无效日期", 
                    False, 
                    f"期望400/422错误，实际状态码: {response.status_code}",
                    response.json() if response.content else response.text
                )
            
            # 测试无效的仓库ID
            params = {'repository_ids': 'invalid,ids'}
            response = self.make_request('GET', '/api/analytics/commits', params=params)
            
            if response.status_code in [400, 422]:
                self.log_test(
                    "错误处理 - 无效仓库ID", 
                    True, 
                    f"正确返回错误状态码: {response.status_code}"
                )
            else:
                self.log_test(
                    "错误处理 - 无效仓库ID", 
                    False, 
                    f"期望400/422错误，实际状态码: {response.status_code}",
                    response.json() if response.content else response.text
                )
            
            # 测试不存在的用户
            response = self.make_request('GET', '/api/analytics/user/99999')
            
            if response.status_code == 404:
                self.log_test(
                    "错误处理 - 不存在用户", 
                    True, 
                    "正确返回404错误"
                )
            else:
                self.log_test(
                    "错误处理 - 不存在用户", 
                    False, 
                    f"期望404错误，实际状态码: {response.status_code}",
                    response.json() if response.content else response.text
                )
                
        except Exception as e:
            self.log_test("错误处理测试", False, f"异常: {str(e)}")
    
    def save_test_results(self):
        """
        保存测试结果到文件
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'analytics_test_results_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n详细测试结果已保存到: {filename}")
    
    def run_all_tests(self):
        """
        运行所有分析统计接口测试
        """
        print("=" * 50)
        print("分析统计API接口测试")
        print("=" * 50)
        
        # 登录获取访问令牌
        if not self.login():
            print("❌ 登录失败，跳过所有测试")
            return
        
        # 获取测试用的仓库
        self.get_test_repositories()
        print(f"\n📊 找到 {len(self.test_repo_ids)} 个测试仓库")
        
        # 运行各项测试
        print("\n=== 分析概览测试 ===")
        self.test_analytics_overview()
        
        print("\n=== 提交统计测试 ===")
        self.test_commits_analytics()
        
        print("\n=== 合并请求统计测试 ===")
        self.test_merge_requests_analytics()
        
        print("\n=== 时间分布测试 ===")
        self.test_time_distribution()
        
        print("\n=== 用户分析测试 ===")
        self.test_user_analytics()
        
        print("\n=== 错误处理测试 ===")
        self.test_error_handling()
        
        # 统计测试结果
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 50)
        print("测试总结")
        print("=" * 50)
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"成功率: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\n失败的测试:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  ❌ {result['test_name']}: {result['message']}")
        
        # 保存测试结果
        self.save_test_results()

def main():
    """
    主函数
    """
    tester = AnalyticsAPITester()
    tester.run_all_tests()

if __name__ == '__main__':
    main()