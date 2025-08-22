# -*- coding: utf-8 -*-
"""
Git服务集成模块
实现各种Git平台的API集成
"""

import requests
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
import time

from flask import current_app
from ..utils.crypto import decrypt_data, is_data_encrypted
from ..utils.helpers import parse_datetime_string

class GitService:
    """
    Git服务基类
    定义通用的Git服务接口
    """
    
    def __init__(self, api_key: str, base_url: str = None):
        """
        初始化Git服务
        
        Args:
            api_key (str): API密钥
            base_url (str): API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30
        
        # 设置通用请求头
        self.session.headers.update({
            'User-Agent': 'CodingEfficiencyAnalytics/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        测试API连接
        
        Returns:
            Tuple[bool, str]: (是否成功, 错误信息)
        """
        raise NotImplementedError("子类必须实现test_connection方法")
    
    def get_repositories(self) -> List[Dict]:
        """
        获取仓库列表
        
        Returns:
            List[Dict]: 仓库列表
        """
        raise NotImplementedError("子类必须实现get_repositories方法")
    
    def get_repository_info(self, repo_id: str) -> Optional[Dict]:
        """
        获取仓库详细信息
        
        Args:
            repo_id (str): 仓库ID
        
        Returns:
            Optional[Dict]: 仓库信息
        """
        raise NotImplementedError("子类必须实现get_repository_info方法")
    
    def get_commits(self, repo_id: str, since: datetime = None, until: datetime = None, 
                   page: int = 1, per_page: int = 100) -> List[Dict]:
        """
        获取提交记录
        
        Args:
            repo_id (str): 仓库ID
            since (datetime): 开始时间
            until (datetime): 结束时间
            page (int): 页码
            per_page (int): 每页数量
        
        Returns:
            List[Dict]: 提交记录列表
        """
        raise NotImplementedError("子类必须实现get_commits方法")
    
    def get_merge_requests(self, repo_id: str, state: str = 'all', 
                          since: datetime = None, until: datetime = None,
                          page: int = 1, per_page: int = 100) -> List[Dict]:
        """
        获取合并请求
        
        Args:
            repo_id (str): 仓库ID
            state (str): 状态筛选
            since (datetime): 开始时间
            until (datetime): 结束时间
            page (int): 页码
            per_page (int): 每页数量
        
        Returns:
            List[Dict]: 合并请求列表
        """
        raise NotImplementedError("子类必须实现get_merge_requests方法")
    
    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        发起HTTP请求
        
        Args:
            method (str): HTTP方法
            url (str): 请求URL
            **kwargs: 其他请求参数
        
        Returns:
            requests.Response: 响应对象
        
        Raises:
            requests.RequestException: 请求异常
        """
        try:
            response = self.session.request(method, url, **kwargs)
            
            # 记录请求日志
            current_app.logger.debug(
                f"Git API请求: {method} {url} -> {response.status_code}"
            )
            
            # 检查响应状态
            if response.status_code == 401:
                raise requests.RequestException("API密钥无效或已过期")
            elif response.status_code == 403:
                raise requests.RequestException("权限不足，无法访问该资源")
            elif response.status_code == 404:
                raise requests.RequestException("请求的资源不存在")
            elif response.status_code == 429:
                raise requests.RequestException("API请求频率过高，请稍后重试")
            elif response.status_code >= 500:
                raise requests.RequestException("Git服务器内部错误")
            
            response.raise_for_status()
            return response
            
        except requests.Timeout:
            raise requests.RequestException("请求超时")
        except requests.ConnectionError:
            raise requests.RequestException("网络连接错误")
        except Exception as e:
            current_app.logger.error(f"Git API请求失败: {str(e)}")
            raise

class AliYunXiaoService(GitService):
    """
    阿里云效Git服务集成
    实现阿里云效API的具体调用逻辑
    """
    
    def __init__(self, api_key: str, organization_id: str = None):
        """
        初始化阿里云效服务
        
        Args:
            api_key (str): API密钥
            organization_id (str): 组织ID
        """
        # 阿里云效API基础URL
        base_url = 'https://devops.aliyun.com/api/v4'
        super().__init__(api_key, base_url)
        
        self.organization_id = organization_id
        
        # 设置阿里云效特定的请求头
        self.session.headers.update({
            'PRIVATE-TOKEN': self.api_key
        })
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        测试阿里云效API连接
        
        Returns:
            Tuple[bool, str]: (是否成功, 错误信息)
        """
        try:
            url = urljoin(self.base_url, '/user')
            response = self._make_request('GET', url)
            
            if response.status_code == 200:
                user_data = response.json()
                current_app.logger.info(
                    f"阿里云效API连接成功，用户: {user_data.get('name', 'Unknown')}"
                )
                return True, "连接成功"
            else:
                return False, f"连接失败，状态码: {response.status_code}"
                
        except requests.RequestException as e:
            current_app.logger.error(f"阿里云效API连接测试失败: {str(e)}")
            return False, str(e)
        except Exception as e:
            current_app.logger.error(f"阿里云效API连接测试异常: {str(e)}")
            return False, "连接测试异常"
    
    def get_repositories(self) -> List[Dict]:
        """
        获取阿里云效仓库列表
        
        Returns:
            List[Dict]: 仓库列表
        """
        repositories = []
        page = 1
        per_page = 100
        
        try:
            while True:
                url = urljoin(self.base_url, '/projects')
                params = {
                    'page': page,
                    'per_page': per_page,
                    'membership': True,  # 只获取用户有权限的项目
                    'archived': False,   # 排除已归档的项目
                    'simple': False      # 获取详细信息
                }
                
                if self.organization_id:
                    params['owned'] = True
                
                response = self._make_request('GET', url, params=params)
                data = response.json()
                
                if not data:
                    break
                
                for repo in data:
                    repositories.append(self._format_repository(repo))
                
                # 检查是否还有更多页面
                if len(data) < per_page:
                    break
                
                page += 1
                time.sleep(0.1)  # 避免请求过于频繁
            
            current_app.logger.info(f"获取到 {len(repositories)} 个阿里云效仓库")
            return repositories
            
        except requests.RequestException as e:
            current_app.logger.error(f"获取阿里云效仓库列表失败: {str(e)}")
            raise
        except Exception as e:
            current_app.logger.error(f"获取阿里云效仓库列表异常: {str(e)}")
            raise
    
    def get_repository_info(self, repo_id: str) -> Optional[Dict]:
        """
        获取阿里云效仓库详细信息
        
        Args:
            repo_id (str): 仓库ID
        
        Returns:
            Optional[Dict]: 仓库信息
        """
        try:
            url = urljoin(self.base_url, f'/projects/{repo_id}')
            response = self._make_request('GET', url)
            
            if response.status_code == 200:
                repo_data = response.json()
                return self._format_repository(repo_data)
            else:
                return None
                
        except requests.RequestException as e:
            current_app.logger.error(f"获取阿里云效仓库信息失败: {str(e)}")
            return None
        except Exception as e:
            current_app.logger.error(f"获取阿里云效仓库信息异常: {str(e)}")
            return None
    
    def get_commits(self, repo_id: str, since: datetime = None, until: datetime = None,
                   page: int = 1, per_page: int = 100) -> List[Dict]:
        """
        获取阿里云效提交记录
        
        Args:
            repo_id (str): 仓库ID
            since (datetime): 开始时间
            until (datetime): 结束时间
            page (int): 页码
            per_page (int): 每页数量
        
        Returns:
            List[Dict]: 提交记录列表
        """
        try:
            url = urljoin(self.base_url, f'/projects/{repo_id}/repository/commits')
            params = {
                'page': page,
                'per_page': min(per_page, 100),  # 阿里云效限制每页最多100条
                'ref_name': 'master'  # 默认获取master分支
            }
            
            # 添加时间筛选
            if since:
                params['since'] = since.isoformat()
            if until:
                params['until'] = until.isoformat()
            
            response = self._make_request('GET', url, params=params)
            commits_data = response.json()
            
            commits = []
            for commit in commits_data:
                formatted_commit = self._format_commit(commit, repo_id)
                if formatted_commit:
                    commits.append(formatted_commit)
            
            current_app.logger.debug(
                f"获取到 {len(commits)} 条阿里云效提交记录 (仓库: {repo_id}, 页码: {page})"
            )
            return commits
            
        except requests.RequestException as e:
            current_app.logger.error(f"获取阿里云效提交记录失败: {str(e)}")
            raise
        except Exception as e:
            current_app.logger.error(f"获取阿里云效提交记录异常: {str(e)}")
            raise
    
    def get_merge_requests(self, repo_id: str, state: str = 'all',
                          since: datetime = None, until: datetime = None,
                          page: int = 1, per_page: int = 100) -> List[Dict]:
        """
        获取阿里云效合并请求
        
        Args:
            repo_id (str): 仓库ID
            state (str): 状态筛选 (opened, closed, merged, all)
            since (datetime): 开始时间
            until (datetime): 结束时间
            page (int): 页码
            per_page (int): 每页数量
        
        Returns:
            List[Dict]: 合并请求列表
        """
        try:
            url = urljoin(self.base_url, f'/projects/{repo_id}/merge_requests')
            params = {
                'page': page,
                'per_page': min(per_page, 100),
                'order_by': 'created_at',
                'sort': 'desc'
            }
            
            # 状态筛选
            if state != 'all':
                params['state'] = state
            
            # 时间筛选（阿里云效可能不直接支持，需要在结果中过滤）
            response = self._make_request('GET', url, params=params)
            mrs_data = response.json()
            
            merge_requests = []
            for mr in mrs_data:
                formatted_mr = self._format_merge_request(mr, repo_id)
                if formatted_mr:
                    # 应用时间筛选
                    created_at = parse_datetime_string(formatted_mr['created_at_remote'])
                    if since and created_at < since:
                        continue
                    if until and created_at > until:
                        continue
                    
                    merge_requests.append(formatted_mr)
            
            current_app.logger.debug(
                f"获取到 {len(merge_requests)} 个阿里云效合并请求 (仓库: {repo_id}, 页码: {page})"
            )
            return merge_requests
            
        except requests.RequestException as e:
            current_app.logger.error(f"获取阿里云效合并请求失败: {str(e)}")
            raise
        except Exception as e:
            current_app.logger.error(f"获取阿里云效合并请求异常: {str(e)}")
            raise
    
    def get_commit_diff(self, repo_id: str, commit_sha: str) -> Optional[Dict]:
        """
        获取提交的差异信息
        
        Args:
            repo_id (str): 仓库ID
            commit_sha (str): 提交SHA
        
        Returns:
            Optional[Dict]: 差异信息
        """
        try:
            url = urljoin(self.base_url, f'/projects/{repo_id}/repository/commits/{commit_sha}/diff')
            response = self._make_request('GET', url)
            
            if response.status_code == 200:
                diff_data = response.json()
                return self._parse_diff_stats(diff_data)
            else:
                return None
                
        except requests.RequestException as e:
            current_app.logger.error(f"获取提交差异信息失败: {str(e)}")
            return None
        except Exception as e:
            current_app.logger.error(f"获取提交差异信息异常: {str(e)}")
            return None
    
    def _format_repository(self, repo_data: Dict) -> Dict:
        """
        格式化仓库数据
        
        Args:
            repo_data (Dict): 原始仓库数据
        
        Returns:
            Dict: 格式化后的仓库数据
        """
        return {
            'id': str(repo_data.get('id', '')),
            'name': repo_data.get('name', ''),
            'full_name': repo_data.get('path_with_namespace', ''),
            'description': repo_data.get('description', ''),
            'url': repo_data.get('web_url', ''),
            'clone_url': repo_data.get('http_url_to_repo', ''),
            'ssh_url': repo_data.get('ssh_url_to_repo', ''),
            'default_branch': repo_data.get('default_branch', 'master'),
            'visibility': repo_data.get('visibility', 'private'),
            'created_at': repo_data.get('created_at', ''),
            'updated_at': repo_data.get('last_activity_at', ''),
            'stars_count': repo_data.get('star_count', 0),
            'forks_count': repo_data.get('forks_count', 0),
            'open_issues_count': repo_data.get('open_issues_count', 0),
            'platform': 'aliyunxiao'
        }
    
    def _format_commit(self, commit_data: Dict, repo_id: str) -> Optional[Dict]:
        """
        格式化提交数据
        
        Args:
            commit_data (Dict): 原始提交数据
            repo_id (str): 仓库ID
        
        Returns:
            Optional[Dict]: 格式化后的提交数据
        """
        try:
            # 获取提交的详细差异信息
            diff_stats = self.get_commit_diff(repo_id, commit_data.get('id', ''))
            
            return {
                'id': commit_data.get('id', ''),
                'short_id': commit_data.get('short_id', ''),
                'title': commit_data.get('title', ''),
                'message': commit_data.get('message', ''),
                'author_name': commit_data.get('author_name', ''),
                'author_email': commit_data.get('author_email', ''),
                'authored_date': commit_data.get('authored_date', ''),
                'committed_date': commit_data.get('committed_date', ''),
                'committer_name': commit_data.get('committer_name', ''),
                'committer_email': commit_data.get('committer_email', ''),
                'parent_ids': commit_data.get('parent_ids', []),
                'stats': diff_stats or {
                    'additions': 0,
                    'deletions': 0,
                    'total': 0,
                    'files_changed': 0
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"格式化提交数据失败: {str(e)}")
            return None
    
    def _format_merge_request(self, mr_data: Dict, repo_id: str) -> Optional[Dict]:
        """
        格式化合并请求数据
        
        Args:
            mr_data (Dict): 原始合并请求数据
            repo_id (str): 仓库ID
        
        Returns:
            Optional[Dict]: 格式化后的合并请求数据
        """
        try:
            return {
                'id': str(mr_data.get('id', '')),
                'iid': mr_data.get('iid', 0),
                'title': mr_data.get('title', ''),
                'description': mr_data.get('description', ''),
                'state': mr_data.get('state', ''),
                'created_at': mr_data.get('created_at', ''),
                'updated_at': mr_data.get('updated_at', ''),
                'merged_at': mr_data.get('merged_at', ''),
                'closed_at': mr_data.get('closed_at', ''),
                'author': {
                    'name': mr_data.get('author', {}).get('name', ''),
                    'email': mr_data.get('author', {}).get('email', ''),
                    'username': mr_data.get('author', {}).get('username', '')
                },
                'assignee': mr_data.get('assignee'),
                'source_branch': mr_data.get('source_branch', ''),
                'target_branch': mr_data.get('target_branch', ''),
                'merge_status': mr_data.get('merge_status', ''),
                'web_url': mr_data.get('web_url', ''),
                'changes_count': mr_data.get('changes_count', 0),
                'user_notes_count': mr_data.get('user_notes_count', 0),
                'upvotes': mr_data.get('upvotes', 0),
                'downvotes': mr_data.get('downvotes', 0),
                'work_in_progress': mr_data.get('work_in_progress', False)
            }
            
        except Exception as e:
            current_app.logger.error(f"格式化合并请求数据失败: {str(e)}")
            return None
    
    def _parse_diff_stats(self, diff_data: List[Dict]) -> Dict:
        """
        解析差异统计信息
        
        Args:
            diff_data (List[Dict]): 差异数据
        
        Returns:
            Dict: 统计信息
        """
        stats = {
            'additions': 0,
            'deletions': 0,
            'total': 0,
            'files_changed': len(diff_data)
        }
        
        try:
            for file_diff in diff_data:
                # 解析每个文件的变更统计
                diff_content = file_diff.get('diff', '')
                additions = diff_content.count('\n+')
                deletions = diff_content.count('\n-')
                
                stats['additions'] += additions
                stats['deletions'] += deletions
            
            stats['total'] = stats['additions'] + stats['deletions']
            
        except Exception as e:
            current_app.logger.error(f"解析差异统计失败: {str(e)}")
        
        return stats

def create_git_service(platform: str, api_key: str, **kwargs) -> GitService:
    """
    创建Git服务实例
    
    Args:
        platform (str): 平台名称
        api_key (str): API密钥
        **kwargs: 其他参数
    
    Returns:
        GitService: Git服务实例
    
    Raises:
        ValueError: 不支持的平台
    """
    # 解密API密钥（如果已加密）
    if is_data_encrypted(api_key):
        try:
            api_key = decrypt_data(api_key)
        except Exception as e:
            current_app.logger.error(f"解密API密钥失败: {str(e)}")
            raise ValueError("API密钥解密失败")
    
    if platform.lower() == 'aliyunxiao':
        return AliYunXiaoService(
            api_key=api_key,
            organization_id=kwargs.get('organization_id')
        )
    else:
        raise ValueError(f"不支持的Git平台: {platform}")

def get_supported_platforms() -> List[Dict]:
    """
    获取支持的Git平台列表
    
    Returns:
        List[Dict]: 支持的平台列表
    """
    return [
        {
            'key': 'aliyunxiao',
            'name': '阿里云效',
            'description': '阿里云效代码管理平台',
            'api_doc_url': 'https://help.aliyun.com/zh/yunxiao/developer-reference/api-reference-standard-proprietary/',
            'required_fields': ['api_key'],
            'optional_fields': ['organization_id']
        }
    ]