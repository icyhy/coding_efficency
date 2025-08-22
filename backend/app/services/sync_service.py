# -*- coding: utf-8 -*-
"""
数据同步服务模块
实现Git仓库数据的同步和更新逻辑
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy import and_, or_
from flask import current_app

from ..models import Repository, Commit, MergeRequest
from .. import db
from .git_service import create_git_service
from ..utils.helpers import parse_datetime_string

class SyncService:
    """
    数据同步服务
    负责从Git平台同步数据到本地数据库
    """
    
    def __init__(self):
        """
        初始化同步服务
        """
        self.batch_size = 100  # 批量处理大小
        self.max_retries = 3   # 最大重试次数
    
    def sync_repository_data(self, repository_id: int, 
                           sync_commits: bool = True, 
                           sync_merge_requests: bool = True,
                           force_full_sync: bool = False) -> Dict:
        """
        同步仓库数据
        
        Args:
            repository_id (int): 仓库ID
            sync_commits (bool): 是否同步提交记录
            sync_merge_requests (bool): 是否同步合并请求
            force_full_sync (bool): 是否强制全量同步
        
        Returns:
            Dict: 同步结果
        """
        try:
            # 获取仓库信息
            repository = Repository.query.get(repository_id)
            if not repository:
                return {
                    'success': False,
                    'error': '仓库不存在',
                    'stats': {}
                }
            
            if not repository.is_active:
                return {
                    'success': False,
                    'error': '仓库已禁用',
                    'stats': {}
                }
            
            # 创建Git服务实例
            git_service = create_git_service(
                platform=repository.platform,
                api_key=repository.api_key,
                organization_id=repository.organization_id
            )
            
            # 测试连接
            is_connected, error_msg = git_service.test_connection()
            if not is_connected:
                return {
                    'success': False,
                    'error': f'Git服务连接失败: {error_msg}',
                    'stats': {}
                }
            
            sync_stats = {
                'commits_added': 0,
                'commits_updated': 0,
                'merge_requests_added': 0,
                'merge_requests_updated': 0,
                'errors': []
            }
            
            # 同步提交记录
            if sync_commits:
                commits_result = self._sync_commits(
                    git_service, repository, force_full_sync
                )
                sync_stats['commits_added'] = commits_result['added']
                sync_stats['commits_updated'] = commits_result['updated']
                sync_stats['errors'].extend(commits_result['errors'])
            
            # 同步合并请求
            if sync_merge_requests:
                mrs_result = self._sync_merge_requests(
                    git_service, repository, force_full_sync
                )
                sync_stats['merge_requests_added'] = mrs_result['added']
                sync_stats['merge_requests_updated'] = mrs_result['updated']
                sync_stats['errors'].extend(mrs_result['errors'])
            
            # 更新仓库同步时间
            repository.last_sync_at = datetime.utcnow()
            db.session.commit()
            
            current_app.logger.info(
                f"仓库 {repository.name} 同步完成: "
                f"提交 +{sync_stats['commits_added']}/~{sync_stats['commits_updated']}, "
                f"合并请求 +{sync_stats['merge_requests_added']}/~{sync_stats['merge_requests_updated']}"
            )
            
            return {
                'success': True,
                'stats': sync_stats,
                'repository': {
                    'id': repository.id,
                    'name': repository.name,
                    'last_sync_at': repository.last_sync_at.isoformat() + 'Z'
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"同步仓库数据失败: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': str(e),
                'stats': {}
            }
    
    def _sync_commits(self, git_service, repository: Repository, 
                     force_full_sync: bool = False) -> Dict:
        """
        同步提交记录
        
        Args:
            git_service: Git服务实例
            repository (Repository): 仓库对象
            force_full_sync (bool): 是否强制全量同步
        
        Returns:
            Dict: 同步结果统计
        """
        result = {
            'added': 0,
            'updated': 0,
            'errors': []
        }
        
        try:
            # 确定同步时间范围
            since_date = None
            if not force_full_sync and repository.last_sync_at:
                # 增量同步：从上次同步时间开始
                since_date = repository.last_sync_at - timedelta(hours=1)  # 留1小时缓冲
            else:
                # 全量同步：从30天前开始（避免数据量过大）
                since_date = datetime.utcnow() - timedelta(days=30)
            
            current_app.logger.info(
                f"开始同步仓库 {repository.name} 的提交记录 (从 {since_date.isoformat()})"
            )
            
            page = 1
            total_processed = 0
            
            while True:
                try:
                    # 获取提交记录
                    commits = git_service.get_commits(
                        repo_id=repository.remote_id,
                        since=since_date,
                        page=page,
                        per_page=self.batch_size
                    )
                    
                    if not commits:
                        break
                    
                    # 批量处理提交记录
                    batch_result = self._process_commits_batch(
                        commits, repository.id
                    )
                    
                    result['added'] += batch_result['added']
                    result['updated'] += batch_result['updated']
                    result['errors'].extend(batch_result['errors'])
                    
                    total_processed += len(commits)
                    
                    current_app.logger.debug(
                        f"处理第 {page} 页提交记录: {len(commits)} 条 "
                        f"(累计: {total_processed})"
                    )
                    
                    # 如果返回的记录数少于批量大小，说明已经到最后一页
                    if len(commits) < self.batch_size:
                        break
                    
                    page += 1
                    
                except Exception as e:
                    error_msg = f"获取第 {page} 页提交记录失败: {str(e)}"
                    current_app.logger.error(error_msg)
                    result['errors'].append(error_msg)
                    break
            
            current_app.logger.info(
                f"仓库 {repository.name} 提交记录同步完成: "
                f"处理 {total_processed} 条，新增 {result['added']} 条，更新 {result['updated']} 条"
            )
            
        except Exception as e:
            error_msg = f"同步提交记录失败: {str(e)}"
            current_app.logger.error(error_msg)
            result['errors'].append(error_msg)
        
        return result
    
    def _sync_merge_requests(self, git_service, repository: Repository,
                           force_full_sync: bool = False) -> Dict:
        """
        同步合并请求
        
        Args:
            git_service: Git服务实例
            repository (Repository): 仓库对象
            force_full_sync (bool): 是否强制全量同步
        
        Returns:
            Dict: 同步结果统计
        """
        result = {
            'added': 0,
            'updated': 0,
            'errors': []
        }
        
        try:
            # 确定同步时间范围
            since_date = None
            if not force_full_sync and repository.last_sync_at:
                since_date = repository.last_sync_at - timedelta(hours=1)
            else:
                since_date = datetime.utcnow() - timedelta(days=30)
            
            current_app.logger.info(
                f"开始同步仓库 {repository.name} 的合并请求 (从 {since_date.isoformat()})"
            )
            
            page = 1
            total_processed = 0
            
            while True:
                try:
                    # 获取合并请求
                    merge_requests = git_service.get_merge_requests(
                        repo_id=repository.remote_id,
                        state='all',
                        since=since_date,
                        page=page,
                        per_page=self.batch_size
                    )
                    
                    if not merge_requests:
                        break
                    
                    # 批量处理合并请求
                    batch_result = self._process_merge_requests_batch(
                        merge_requests, repository.id
                    )
                    
                    result['added'] += batch_result['added']
                    result['updated'] += batch_result['updated']
                    result['errors'].extend(batch_result['errors'])
                    
                    total_processed += len(merge_requests)
                    
                    current_app.logger.debug(
                        f"处理第 {page} 页合并请求: {len(merge_requests)} 条 "
                        f"(累计: {total_processed})"
                    )
                    
                    if len(merge_requests) < self.batch_size:
                        break
                    
                    page += 1
                    
                except Exception as e:
                    error_msg = f"获取第 {page} 页合并请求失败: {str(e)}"
                    current_app.logger.error(error_msg)
                    result['errors'].append(error_msg)
                    break
            
            current_app.logger.info(
                f"仓库 {repository.name} 合并请求同步完成: "
                f"处理 {total_processed} 条，新增 {result['added']} 条，更新 {result['updated']} 条"
            )
            
        except Exception as e:
            error_msg = f"同步合并请求失败: {str(e)}"
            current_app.logger.error(error_msg)
            result['errors'].append(error_msg)
        
        return result
    
    def _process_commits_batch(self, commits: List[Dict], repository_id: int) -> Dict:
        """
        批量处理提交记录
        
        Args:
            commits (List[Dict]): 提交记录列表
            repository_id (int): 仓库ID
        
        Returns:
            Dict: 处理结果统计
        """
        result = {
            'added': 0,
            'updated': 0,
            'errors': []
        }
        
        try:
            for commit_data in commits:
                try:
                    # 检查提交是否已存在
                    existing_commit = Commit.query.filter_by(
                        repository_id=repository_id,
                        commit_hash=commit_data['id']
                    ).first()
                    
                    if existing_commit:
                        # 更新现有提交（可能有新的统计信息）
                        self._update_commit(existing_commit, commit_data)
                        result['updated'] += 1
                    else:
                        # 创建新提交
                        self._create_commit(commit_data, repository_id)
                        result['added'] += 1
                        
                except Exception as e:
                    error_msg = f"处理提交 {commit_data.get('id', 'unknown')} 失败: {str(e)}"
                    current_app.logger.error(error_msg)
                    result['errors'].append(error_msg)
                    continue
            
            # 批量提交数据库更改
            db.session.commit()
            
        except Exception as e:
            current_app.logger.error(f"批量处理提交记录失败: {str(e)}")
            db.session.rollback()
            result['errors'].append(str(e))
        
        return result
    
    def _process_merge_requests_batch(self, merge_requests: List[Dict], 
                                    repository_id: int) -> Dict:
        """
        批量处理合并请求
        
        Args:
            merge_requests (List[Dict]): 合并请求列表
            repository_id (int): 仓库ID
        
        Returns:
            Dict: 处理结果统计
        """
        result = {
            'added': 0,
            'updated': 0,
            'errors': []
        }
        
        try:
            for mr_data in merge_requests:
                try:
                    # 检查合并请求是否已存在
                    existing_mr = MergeRequest.query.filter_by(
                        repository_id=repository_id,
                        mr_id=mr_data['iid']
                    ).first()
                    
                    if existing_mr:
                        # 更新现有合并请求
                        self._update_merge_request(existing_mr, mr_data)
                        result['updated'] += 1
                    else:
                        # 创建新合并请求
                        self._create_merge_request(mr_data, repository_id)
                        result['added'] += 1
                        
                except Exception as e:
                    error_msg = f"处理合并请求 {mr_data.get('iid', 'unknown')} 失败: {str(e)}"
                    current_app.logger.error(error_msg)
                    result['errors'].append(error_msg)
                    continue
            
            # 批量提交数据库更改
            db.session.commit()
            
        except Exception as e:
            current_app.logger.error(f"批量处理合并请求失败: {str(e)}")
            db.session.rollback()
            result['errors'].append(str(e))
        
        return result
    
    def _create_commit(self, commit_data: Dict, repository_id: int) -> Commit:
        """
        创建新的提交记录
        
        Args:
            commit_data (Dict): 提交数据
            repository_id (int): 仓库ID
        
        Returns:
            Commit: 创建的提交对象
        """
        stats = commit_data.get('stats', {})
        
        commit = Commit(
            repository_id=repository_id,
            commit_hash=commit_data['id'],
            author_name=commit_data.get('author_name', ''),
            author_email=commit_data.get('author_email', ''),
            message=commit_data.get('message', ''),
            additions=stats.get('additions', 0),
            deletions=stats.get('deletions', 0),
            files_changed=stats.get('files_changed', 0),
            commit_date=parse_datetime_string(
                commit_data.get('authored_date') or 
                commit_data.get('committed_date') or 
                datetime.utcnow().isoformat()
            )
        )
        
        db.session.add(commit)
        return commit
    
    def _update_commit(self, commit: Commit, commit_data: Dict):
        """
        更新现有提交记录
        
        Args:
            commit (Commit): 现有提交对象
            commit_data (Dict): 新的提交数据
        """
        stats = commit_data.get('stats', {})
        
        # 更新可能变化的字段
        commit.message = commit_data.get('message', commit.message)
        commit.additions = stats.get('additions', commit.additions)
        commit.deletions = stats.get('deletions', commit.deletions)
        commit.files_changed = stats.get('files_changed', commit.files_changed)
        commit.updated_at = datetime.utcnow()
    
    def _create_merge_request(self, mr_data: Dict, repository_id: int) -> MergeRequest:
        """
        创建新的合并请求
        
        Args:
            mr_data (Dict): 合并请求数据
            repository_id (int): 仓库ID
        
        Returns:
            MergeRequest: 创建的合并请求对象
        """
        author = mr_data.get('author', {})
        
        merge_request = MergeRequest(
            repository_id=repository_id,
            mr_id=mr_data['iid'],
            title=mr_data.get('title', ''),
            author_name=author.get('name', ''),
            author_email=author.get('email', ''),
            state=mr_data.get('state', ''),
            additions=0,  # 需要额外API调用获取
            deletions=0,  # 需要额外API调用获取
            files_changed=mr_data.get('changes_count', 0),
            commits_count=0,  # 需要额外API调用获取
            created_at_remote=parse_datetime_string(
                mr_data.get('created_at') or datetime.utcnow().isoformat()
            ),
            merged_at=parse_datetime_string(mr_data.get('merged_at')) if mr_data.get('merged_at') else None
        )
        
        db.session.add(merge_request)
        return merge_request
    
    def _update_merge_request(self, merge_request: MergeRequest, mr_data: Dict):
        """
        更新现有合并请求
        
        Args:
            merge_request (MergeRequest): 现有合并请求对象
            mr_data (Dict): 新的合并请求数据
        """
        author = mr_data.get('author', {})
        
        # 更新可能变化的字段
        merge_request.title = mr_data.get('title', merge_request.title)
        merge_request.state = mr_data.get('state', merge_request.state)
        merge_request.files_changed = mr_data.get('changes_count', merge_request.files_changed)
        
        # 更新合并时间（如果状态变为已合并）
        if mr_data.get('merged_at') and not merge_request.merged_at:
            merge_request.merged_at = parse_datetime_string(mr_data['merged_at'])
        
        merge_request.updated_at = datetime.utcnow()
    
    def sync_all_repositories(self, user_id: int = None, 
                            active_only: bool = True) -> Dict:
        """
        同步所有仓库数据
        
        Args:
            user_id (int): 用户ID，如果指定则只同步该用户的仓库
            active_only (bool): 是否只同步活跃仓库
        
        Returns:
            Dict: 同步结果汇总
        """
        try:
            # 获取需要同步的仓库列表
            query = Repository.query
            
            if user_id:
                query = query.filter_by(user_id=user_id)
            
            if active_only:
                query = query.filter_by(is_active=True)
            
            repositories = query.all()
            
            if not repositories:
                return {
                    'success': True,
                    'message': '没有需要同步的仓库',
                    'total_repositories': 0,
                    'results': []
                }
            
            current_app.logger.info(f"开始同步 {len(repositories)} 个仓库")
            
            results = []
            success_count = 0
            
            for repository in repositories:
                current_app.logger.info(f"同步仓库: {repository.name}")
                
                result = self.sync_repository_data(
                    repository_id=repository.id,
                    sync_commits=True,
                    sync_merge_requests=True,
                    force_full_sync=False
                )
                
                result['repository_name'] = repository.name
                results.append(result)
                
                if result['success']:
                    success_count += 1
                else:
                    current_app.logger.error(
                        f"仓库 {repository.name} 同步失败: {result.get('error', 'Unknown error')}"
                    )
            
            current_app.logger.info(
                f"批量同步完成: {success_count}/{len(repositories)} 个仓库同步成功"
            )
            
            return {
                'success': True,
                'total_repositories': len(repositories),
                'success_count': success_count,
                'failed_count': len(repositories) - success_count,
                'results': results
            }
            
        except Exception as e:
            current_app.logger.error(f"批量同步仓库失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'total_repositories': 0,
                'results': []
            }
    
    def get_sync_status(self, repository_id: int) -> Dict:
        """
        获取仓库同步状态
        
        Args:
            repository_id (int): 仓库ID
        
        Returns:
            Dict: 同步状态信息
        """
        try:
            repository = Repository.query.get(repository_id)
            if not repository:
                return {
                    'success': False,
                    'error': '仓库不存在'
                }
            
            # 统计数据
            commits_count = Commit.query.filter_by(repository_id=repository_id).count()
            mrs_count = MergeRequest.query.filter_by(repository_id=repository_id).count()
            
            # 最新数据时间
            latest_commit = Commit.query.filter_by(
                repository_id=repository_id
            ).order_by(Commit.commit_date.desc()).first()
            
            latest_mr = MergeRequest.query.filter_by(
                repository_id=repository_id
            ).order_by(MergeRequest.created_at_remote.desc()).first()
            
            return {
                'success': True,
                'repository': {
                    'id': repository.id,
                    'name': repository.name,
                    'platform': repository.platform,
                    'is_active': repository.is_active,
                    'last_sync_at': repository.last_sync_at.isoformat() + 'Z' if repository.last_sync_at else None,
                    'created_at': repository.created_at.isoformat() + 'Z'
                },
                'stats': {
                    'commits_count': commits_count,
                    'merge_requests_count': mrs_count,
                    'latest_commit_date': latest_commit.commit_date.isoformat() + 'Z' if latest_commit else None,
                    'latest_mr_date': latest_mr.created_at_remote.isoformat() + 'Z' if latest_mr else None
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"获取同步状态失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }