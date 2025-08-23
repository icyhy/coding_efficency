#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云效API测试脚本
用于验证云效代码管理API的连接和仓库列表获取功能

参考文档：
- ListRepositories API: https://help.aliyun.com/zh/yunxiao/developer-reference/listrepositories-query-code-base-list
- GetRepository API: https://help.aliyun.com/zh/yunxiao/developer-reference/api-devops-2021-06-25-getrepository
"""

import requests
import json
import os
from typing import Dict, List, Optional

class YunxiaoAPITester:
    """云效API测试类"""
    
    def __init__(self, domain: str, organization_id: str, access_token: str):
        """
        初始化云效API测试器
        
        Args:
            domain: 云效服务接入点域名（可以包含或不包含https://协议）
            organization_id: 组织ID
            access_token: 个人访问令牌
        """
        self.domain = domain
        self.organization_id = organization_id
        self.access_token = access_token
        # 确保base_url格式正确，不重复添加协议
        if domain.startswith('http'):
            self.base_url = domain
        else:
            self.base_url = f"https://{domain}"
        self.headers = {
            'Content-Type': 'application/json',
            'x-yunxiao-token': access_token
        }
    
    def test_connection(self) -> bool:
        """
        测试API连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            # 使用获取仓库列表API测试连接
            url = f"{self.base_url}/oapi/v1/codeup/organizations/{self.organization_id}/repositories"
            params = {
                'page': 1,
                'perPage': 1  # 只获取1个仓库用于测试连接
            }
            
            print(f"测试连接到: {url}")
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            print(f"响应状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("✅ API连接成功")
                return True
            else:
                print(f"❌ API连接失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 连接异常: {e}")
            return False
    
    def list_repositories(self, page: int = 1, per_page: int = 20, 
                         search: Optional[str] = None, 
                         archived: bool = False) -> Optional[List[Dict]]:
        """
        获取仓库列表
        
        Args:
            page: 页码，默认从1开始
            per_page: 每页大小，默认20，取值范围[1,100]
            search: 搜索关键字，用于模糊匹配代码库路径
            archived: 是否归档
            
        Returns:
            Optional[List[Dict]]: 仓库列表，失败时返回None
        """
        try:
            url = f"{self.base_url}/oapi/v1/codeup/organizations/{self.organization_id}/repositories"
            params = {
                'page': page,
                'perPage': per_page,
                'orderBy': 'created_at',
                'sort': 'desc',
                'archived': str(archived).lower()
            }
            
            if search:
                params['search'] = search
            
            print(f"\n获取仓库列表: {url}")
            print(f"请求参数: {params}")
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                print(f"响应内容: {response.text[:500]}...")  # 打印前500个字符
                try:
                    repositories = response.json()
                    print(f"✅ 成功获取 {len(repositories)} 个仓库")
                    return repositories
                except json.JSONDecodeError as e:
                    print(f"❌ JSON解析失败: {e}")
                    print(f"响应可能不是JSON格式，内容类型: {response.headers.get('Content-Type')}")
                    return None
            else:
                print(f"❌ 获取仓库列表失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析异常: {e}")
            return None
    
    def get_repository_details(self, repo_id: str) -> Optional[Dict]:
        """
        获取单个仓库详情（使用云效Codeup API）
        
        Args:
            repo_id: 仓库ID
            
        Returns:
            Optional[Dict]: 仓库详情，失败时返回None
        """
        try:
            # 使用云效Codeup API获取仓库详情
            url = f"{self.base_url}/oapi/v1/codeup/organizations/{self.organization_id}/repositories/{repo_id}"
            
            print(f"\n获取仓库详情: {url}")
            
            response = requests.get(url, headers=self.headers, timeout=30)
            
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print("✅ 成功获取仓库详情")
                    return result
                except json.JSONDecodeError as e:
                    print(f"❌ JSON解析失败: {e}")
                    print(f"响应内容: {response.text[:500]}...")
                    return None
            else:
                print(f"❌ 获取仓库详情失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return None
    
    def print_repository_info(self, repositories: List[Dict]):
        """
        打印仓库信息
        
        Args:
            repositories: 仓库列表
        """
        print("\n=== 仓库列表 ===")
        for i, repo in enumerate(repositories, 1):
            print(f"{i}. {repo.get('name', 'N/A')}")
            print(f"   ID: {repo.get('id', 'N/A')}")
            print(f"   路径: {repo.get('pathWithNamespace', 'N/A')}")
            print(f"   描述: {repo.get('description', 'N/A')}")
            print(f"   可见性: {repo.get('visibility', 'N/A')}")
            print(f"   创建时间: {repo.get('createdAt', 'N/A')}")
            print(f"   最后活跃: {repo.get('lastActivityAt', 'N/A')}")
            print(f"   Web URL: {repo.get('webUrl', 'N/A')}")
            print()

def load_env_config():
    """
    从.env文件加载配置
    
    Returns:
        tuple: (domain, organization_id, access_token)
    """
    import os
    from pathlib import Path
    
    # 查找.env文件
    env_file = Path(__file__).parent / "backend" / ".env"
    if not env_file.exists():
        print(f"❌ 找不到.env文件: {env_file}")
        return None, None, None
    
    # 读取.env文件
    config = {}
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    
    # 提取云效配置
    api_base_url = config.get('ALIYUNXIAO_API_BASE_URL', '')
    organization_id = config.get('ALIYUNXIAO_ORGANIZATION_ID', '')
    access_token = config.get('ALIYUNXIAO_ACCESS_TOKEN', '')
    
    # 使用配置中的API基础URL
    if not api_base_url:
        print("❌ 缺少ALIYUNXIAO_API_BASE_URL配置")
        return None, None, None
    
    # 构建完整的域名URL，确保不重复添加协议
    if api_base_url.startswith('http'):
        domain = api_base_url
    else:
        domain = f"https://{api_base_url}"
    
    return domain, organization_id, access_token

def main():
    """
    主函数 - 运行云效API测试
    """
    print("=== 云效API测试脚本 ===")
    
    # 从.env文件加载配置
    print("\n正在加载配置...")
    domain, organization_id, access_token = load_env_config()
    
    # 检查配置
    if not domain or not organization_id or not access_token:
        print("❌ 配置加载失败或配置不完整")
        print("\n请检查backend/.env文件中的以下配置:")
        print("- ALIYUNXIAO_API_BASE_URL")
        print("- ALIYUNXIAO_ORGANIZATION_ID")
        print("- ALIYUNXIAO_ACCESS_TOKEN")
        return
    
    print(f"✅ 配置加载成功:")
    print(f"   域名: {domain}")
    print(f"   组织ID: {organization_id}")
    print(f"   访问令牌: {access_token[:20]}...")
    
    # 创建测试器
    tester = YunxiaoAPITester(domain, organization_id, access_token)
    
    # 测试连接
    print("\n1. 测试API连接...")
    if not tester.test_connection():
        print("❌ API连接失败，请检查配置")
        return
    
    # 获取仓库列表
    print("\n2. 获取仓库列表...")
    repositories = tester.list_repositories(page=1, per_page=10)
    
    if repositories:
        tester.print_repository_info(repositories)
        
        # 如果有仓库，测试获取单个仓库详情
        if repositories:
            print("\n3. 测试获取单个仓库详情...")
            first_repo = repositories[0]
            repo_id = first_repo.get('id')
            if repo_id:
                details = tester.get_repository_details(str(repo_id))
                if details:
                    print(f"仓库详情获取成功: {details.get('name')}")
    else:
        print("❌ 无法获取仓库列表")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()