#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云效仓库接口测试脚本

测试功能：
1. 云效仓库搜索接口
2. 添加云效仓库接口
3. 仓库加入/移出统计接口
4. 冲突处理测试

作者: AI Assistant
创建时间: 2025-01-23
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional


class YunxiaoRepositoryTester:
    """云效仓库接口测试类"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        """
        初始化测试器
        
        Args:
            base_url: 后端API基础URL
        """
        self.base_url = base_url
        self.access_token = None
        self.test_results = []
        self.test_repo_id = None
        
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
        if details:
            print(f"   详细信息: {json.dumps(details, ensure_ascii=False, indent=2)}")
    
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
            requests.Response: 响应对象
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Content-Type': 'application/json'
        }
        
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        
        if method.upper() == 'GET':
            return requests.get(url, headers=headers, params=params)
        elif method.upper() == 'POST':
            return requests.post(url, headers=headers, json=data, params=params)
        elif method.upper() == 'PUT':
            return requests.put(url, headers=headers, json=data)
        elif method.upper() == 'DELETE':
            return requests.delete(url, headers=headers)
        else:
            raise ValueError(f"不支持的HTTP方法: {method}")
    
    def login(self, username: str = "admin", password: str = "admin123") -> bool:
        """
        用户登录获取访问令牌
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            bool: 登录是否成功
        """
        print("\n=== 用户登录 ===")
        
        try:
            response = self.make_request('POST', '/api/auth/login', {
                'username': username,
                'password': password
            })
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('data', {}).get('access_token')
                if self.access_token:
                    self.log_test("用户登录", True, f"登录成功，用户: {username}")
                    return True
                else:
                    self.log_test("用户登录", False, "登录响应中未找到访问令牌")
                    return False
            else:
                self.log_test(
                    "用户登录", 
                    False, 
                    f"登录失败，状态码: {response.status_code}",
                    response.json() if response.content else response.text
                )
                return False
                
        except Exception as e:
            self.log_test("用户登录", False, f"登录异常: {str(e)}")
            return False
    
    def test_yunxiao_search(self):
        """
        测试云效仓库搜索接口
        """
        print("\n=== 云效仓库搜索测试 ===")
        
        if not self.access_token:
            self.log_test("云效仓库搜索", False, "跳过测试 - 未登录")
            return
        
        # 测试用例1: 正常搜索
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
                    "云效仓库搜索 - 正常搜索", 
                    True, 
                    f"搜索到 {len(repositories)} 个仓库",
                    {'search_keyword': 'test', 'result_count': len(repositories)}
                )
            else:
                self.log_test(
                    "云效仓库搜索 - 正常搜索", 
                    False, 
                    f"状态码: {response.status_code}",
                    response.json() if response.content else response.text
                )
        except Exception as e:
            self.log_test("云效仓库搜索 - 正常搜索", False, f"异常: {str(e)}")
        
        # 测试用例2: 空搜索关键词
        try:
            params = {
                'page': 1,
                'per_page': 10,
                'search': ''
            }
            response = self.make_request('GET', '/api/repositories/yunxiao/search', params=params)
            
            if response.status_code == 400:
                self.log_test(
                    "云效仓库搜索 - 空关键词", 
                    True, 
                    "正确返回400错误"
                )
            else:
                self.log_test(
                    "云效仓库搜索 - 空关键词", 
                    False, 
                    f"期望400错误，实际状态码: {response.status_code}"
                )
        except Exception as e:
            self.log_test("云效仓库搜索 - 空关键词", False, f"异常: {str(e)}")
        
        # 测试用例3: 分页测试
        try:
            params = {
                'page': 2,
                'per_page': 5,
                'search': 'repo'
            }
            response = self.make_request('GET', '/api/repositories/yunxiao/search', params=params)
            
            if response.status_code == 200:
                data = response.json()
                pagination = data.get('pagination', {})
                self.log_test(
                    "云效仓库搜索 - 分页测试", 
                    True, 
                    f"分页信息: 第{pagination.get('page', 'N/A')}页，每页{pagination.get('per_page', 'N/A')}条",
                    pagination
                )
            else:
                self.log_test(
                    "云效仓库搜索 - 分页测试", 
                    False, 
                    f"状态码: {response.status_code}"
                )
        except Exception as e:
            self.log_test("云效仓库搜索 - 分页测试", False, f"异常: {str(e)}")
    
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
            'name': 'test-repo-' + str(int(time.time())),
            'clone_url': f'https://codeup.aliyun.com/test/test-repo-{int(time.time())}.git',
            'web_url': f'https://codeup.aliyun.com/test/test-repo-{int(time.time())}',
            'description': 'Test repository for API testing'
        }
        
        # 测试用例1: 正常添加仓库
        try:
            response = self.make_request('POST', '/api/repositories/yunxiao/add', data=test_repo_data)
            
            if response.status_code == 201:
                data = response.json()
                repo_data = data.get('data', {})
                self.test_repo_id = repo_data.get('id')
                self.log_test(
                    "添加云效仓库 - 正常添加", 
                    True, 
                    f"仓库添加成功 - ID: {self.test_repo_id}, 名称: {repo_data.get('name')}",
                    repo_data
                )
            else:
                self.log_test(
                    "添加云效仓库 - 正常添加", 
                    False, 
                    f"状态码: {response.status_code}",
                    response.json() if response.content else response.text
                )
        except Exception as e:
            self.log_test("添加云效仓库 - 正常添加", False, f"异常: {str(e)}")
        
        # 测试用例2: 重复添加（409冲突测试）
        try:
            response = self.make_request('POST', '/api/repositories/yunxiao/add', data=test_repo_data)
            
            if response.status_code == 409:
                self.log_test(
                    "添加云效仓库 - 重复添加", 
                    True, 
                    "正确返回409冲突错误",
                    response.json() if response.content else None
                )
            else:
                self.log_test(
                    "添加云效仓库 - 重复添加", 
                    False, 
                    f"期望409冲突错误，实际状态码: {response.status_code}"
                )
        except Exception as e:
            self.log_test("添加云效仓库 - 重复添加", False, f"异常: {str(e)}")
        
        # 测试用例3: 缺少必需字段
        try:
            invalid_data = {
                'repository_id': 12346,
                'name': 'invalid-repo'
                # 缺少 clone_url
            }
            response = self.make_request('POST', '/api/repositories/yunxiao/add', data=invalid_data)
            
            if response.status_code == 400:
                self.log_test(
                    "添加云效仓库 - 缺少字段", 
                    True, 
                    "正确返回400验证错误"
                )
            else:
                self.log_test(
                    "添加云效仓库 - 缺少字段", 
                    False, 
                    f"期望400验证错误，实际状态码: {response.status_code}"
                )
        except Exception as e:
            self.log_test("添加云效仓库 - 缺少字段", False, f"异常: {str(e)}")
    
    def test_repository_tracking(self):
        """
        测试仓库统计管理接口
        """
        print("\n=== 仓库统计管理测试 ===")
        
        if not self.access_token:
            self.log_test("仓库统计管理", False, "跳过测试 - 未登录")
            return
        
        if not self.test_repo_id:
            self.log_test("仓库统计管理", False, "跳过测试 - 没有测试仓库ID")
            return
        
        # 测试用例1: 加入统计
        try:
            response = self.make_request('POST', f'/api/repositories/{self.test_repo_id}/track')
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "仓库统计管理 - 加入统计", 
                    True, 
                    f"仓库 {self.test_repo_id} 已加入统计",
                    data.get('data', {})
                )
            else:
                self.log_test(
                    "仓库统计管理 - 加入统计", 
                    False, 
                    f"状态码: {response.status_code}",
                    response.json() if response.content else response.text
                )
        except Exception as e:
            self.log_test("仓库统计管理 - 加入统计", False, f"异常: {str(e)}")
        
        # 测试用例2: 重复加入统计
        try:
            response = self.make_request('POST', f'/api/repositories/{self.test_repo_id}/track')
            
            if response.status_code in [200, 409]:  # 可能返回200（已在统计中）或409（冲突）
                self.log_test(
                    "仓库统计管理 - 重复加入", 
                    True, 
                    f"正确处理重复加入，状态码: {response.status_code}"
                )
            else:
                self.log_test(
                    "仓库统计管理 - 重复加入", 
                    False, 
                    f"状态码: {response.status_code}"
                )
        except Exception as e:
            self.log_test("仓库统计管理 - 重复加入", False, f"异常: {str(e)}")
        
        # 测试用例3: 移出统计
        try:
            response = self.make_request('POST', f'/api/repositories/{self.test_repo_id}/untrack')
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "仓库统计管理 - 移出统计", 
                    True, 
                    f"仓库 {self.test_repo_id} 已移出统计",
                    data.get('data', {})
                )
            else:
                self.log_test(
                    "仓库统计管理 - 移出统计", 
                    False, 
                    f"状态码: {response.status_code}",
                    response.json() if response.content else response.text
                )
        except Exception as e:
            self.log_test("仓库统计管理 - 移出统计", False, f"异常: {str(e)}")
        
        # 测试用例4: 不存在的仓库ID
        try:
            fake_repo_id = 999999
            response = self.make_request('POST', f'/api/repositories/{fake_repo_id}/track')
            
            if response.status_code == 404:
                self.log_test(
                    "仓库统计管理 - 不存在仓库", 
                    True, 
                    "正确返回404错误"
                )
            else:
                self.log_test(
                    "仓库统计管理 - 不存在仓库", 
                    False, 
                    f"期望404错误，实际状态码: {response.status_code}"
                )
        except Exception as e:
            self.log_test("仓库统计管理 - 不存在仓库", False, f"异常: {str(e)}")
    
    def test_conflict_handling(self):
        """
        测试冲突处理逻辑
        """
        print("\n=== 冲突处理测试 ===")
        
        if not self.access_token:
            self.log_test("冲突处理测试", False, "跳过测试 - 未登录")
            return
        
        # 创建一个测试仓库用于冲突测试
        conflict_repo_data = {
            'repository_id': 99999,
            'name': 'conflict-test-repo',
            'clone_url': 'https://codeup.aliyun.com/conflict/test-repo.git',
            'web_url': 'https://codeup.aliyun.com/conflict/test-repo',
            'description': 'Repository for conflict testing'
        }
        
        # 第一次添加
        try:
            response1 = self.make_request('POST', '/api/repositories/yunxiao/add', data=conflict_repo_data)
            
            if response1.status_code == 201:
                # 第二次添加相同仓库，应该返回409
                response2 = self.make_request('POST', '/api/repositories/yunxiao/add', data=conflict_repo_data)
                
                if response2.status_code == 409:
                    conflict_data = response2.json()
                    self.log_test(
                        "冲突处理测试 - 409响应", 
                        True, 
                        f"正确返回409冲突错误: {conflict_data.get('message', '')}",
                        conflict_data
                    )
                    
                    # 验证错误消息是否包含中文
                    if '已存在' in conflict_data.get('message', ''):
                        self.log_test(
                            "冲突处理测试 - 中文错误消息", 
                            True, 
                            "错误消息包含中文提示"
                        )
                    else:
                        self.log_test(
                            "冲突处理测试 - 中文错误消息", 
                            False, 
                            "错误消息未包含中文提示"
                        )
                else:
                    self.log_test(
                        "冲突处理测试 - 409响应", 
                        False, 
                        f"期望409冲突错误，实际状态码: {response2.status_code}"
                    )
            else:
                self.log_test(
                    "冲突处理测试 - 初始添加", 
                    False, 
                    f"初始添加失败，状态码: {response1.status_code}"
                )
        except Exception as e:
            self.log_test("冲突处理测试", False, f"异常: {str(e)}")
    
    def run_all_tests(self):
        """
        运行所有测试
        """
        print("\n" + "="*50)
        print("开始云效仓库接口测试")
        print("="*50)
        
        # 登录
        if not self.login():
            print("\n❌ 登录失败，终止测试")
            return
        
        # 运行各项测试
        self.test_yunxiao_search()
        self.test_yunxiao_add_repository()
        self.test_repository_tracking()
        self.test_conflict_handling()
        
        # 输出测试总结
        self.print_test_summary()
    
    def print_test_summary(self):
        """
        打印测试总结
        """
        print("\n" + "="*50)
        print("测试总结")
        print("="*50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "成功率: 0%")
        
        if failed_tests > 0:
            print("\n失败的测试:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  ❌ {result['test_name']}: {result['message']}")
        
        # 保存详细测试结果到文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"yunxiao_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'summary': {
                        'total_tests': total_tests,
                        'passed_tests': passed_tests,
                        'failed_tests': failed_tests,
                        'success_rate': f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
                    },
                    'test_results': self.test_results
                }, f, ensure_ascii=False, indent=2)
            
            print(f"\n详细测试结果已保存到: {filename}")
        except Exception as e:
            print(f"\n保存测试结果失败: {str(e)}")


def main():
    """
    主函数
    """
    tester = YunxiaoRepositoryTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()