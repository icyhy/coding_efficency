# -*- coding: utf-8 -*-
"""
数据分析服务模块
实现编程效率评分和统计分析算法
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy import func, and_, or_, desc, asc
from collections import defaultdict, Counter
import statistics

from ..models import Repository, Commit, MergeRequest, User
from .. import db
from ..utils.helpers import get_date_range, group_by_key, calculate_percentage

class AnalyticsService:
    """
    数据分析服务
    提供编程效率评分和各种统计分析功能
    """
    
    def __init__(self):
        """
        初始化分析服务
        """
        # 效率评分权重配置
        self.score_weights = {
            'commit_frequency': 0.25,    # 提交频率
            'code_quality': 0.20,       # 代码质量（基于提交大小）
            'merge_request_ratio': 0.15, # 合并请求比率
            'consistency': 0.20,        # 编程一致性
            'collaboration': 0.20       # 协作能力
        }
        
        # 评分标准
        self.score_standards = {
            'excellent': 90,
            'good': 75,
            'average': 60,
            'below_average': 40
        }
    
    def calculate_efficiency_score(self, user_id: int, 
                                 repository_ids: List[int] = None,
                                 start_date: datetime = None,
                                 end_date: datetime = None) -> Dict:
        """
        计算用户编程效率评分
        
        Args:
            user_id (int): 用户ID
            repository_ids (List[int]): 仓库ID列表，如果为空则分析所有仓库
            start_date (datetime): 开始日期
            end_date (datetime): 结束日期
        
        Returns:
            Dict: 效率评分结果
        """
        try:
            # 设置默认时间范围（最近30天）
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # 获取用户信息
            user = User.query.get(user_id)
            if not user:
                return {
                    'success': False,
                    'error': '用户不存在'
                }
            
            # 构建查询条件
            repo_filter = self._build_repository_filter(user_id, repository_ids)
            
            # 获取基础数据
            commits_data = self._get_commits_data(
                repo_filter, start_date, end_date, user.email
            )
            mrs_data = self._get_merge_requests_data(
                repo_filter, start_date, end_date, user.email
            )
            
            if not commits_data['commits']:
                return {
                    'success': True,
                    'score': 0,
                    'level': 'inactive',
                    'message': '在指定时间范围内没有提交记录',
                    'details': {},
                    'recommendations': ['增加代码提交频率', '参与更多项目开发']
                }
            
            # 计算各项评分
            commit_frequency_score = self._calculate_commit_frequency_score(
                commits_data, start_date, end_date
            )
            
            code_quality_score = self._calculate_code_quality_score(
                commits_data
            )
            
            mr_ratio_score = self._calculate_merge_request_ratio_score(
                commits_data, mrs_data
            )
            
            consistency_score = self._calculate_consistency_score(
                commits_data, start_date, end_date
            )
            
            collaboration_score = self._calculate_collaboration_score(
                commits_data, mrs_data
            )
            
            # 计算加权总分
            total_score = (
                commit_frequency_score * self.score_weights['commit_frequency'] +
                code_quality_score * self.score_weights['code_quality'] +
                mr_ratio_score * self.score_weights['merge_request_ratio'] +
                consistency_score * self.score_weights['consistency'] +
                collaboration_score * self.score_weights['collaboration']
            )
            
            # 确定等级
            level = self._get_score_level(total_score)
            
            # 生成建议
            recommendations = self._generate_recommendations({
                'commit_frequency': commit_frequency_score,
                'code_quality': code_quality_score,
                'merge_request_ratio': mr_ratio_score,
                'consistency': consistency_score,
                'collaboration': collaboration_score
            })
            
            return {
                'success': True,
                'score': round(total_score, 1),
                'level': level,
                'period': {
                    'start_date': start_date.isoformat() + 'Z',
                    'end_date': end_date.isoformat() + 'Z',
                    'days': (end_date - start_date).days
                },
                'details': {
                    'commit_frequency': {
                        'score': round(commit_frequency_score, 1),
                        'weight': self.score_weights['commit_frequency'],
                        'weighted_score': round(commit_frequency_score * self.score_weights['commit_frequency'], 1)
                    },
                    'code_quality': {
                        'score': round(code_quality_score, 1),
                        'weight': self.score_weights['code_quality'],
                        'weighted_score': round(code_quality_score * self.score_weights['code_quality'], 1)
                    },
                    'merge_request_ratio': {
                        'score': round(mr_ratio_score, 1),
                        'weight': self.score_weights['merge_request_ratio'],
                        'weighted_score': round(mr_ratio_score * self.score_weights['merge_request_ratio'], 1)
                    },
                    'consistency': {
                        'score': round(consistency_score, 1),
                        'weight': self.score_weights['consistency'],
                        'weighted_score': round(consistency_score * self.score_weights['consistency'], 1)
                    },
                    'collaboration': {
                        'score': round(collaboration_score, 1),
                        'weight': self.score_weights['collaboration'],
                        'weighted_score': round(collaboration_score * self.score_weights['collaboration'], 1)
                    }
                },
                'statistics': {
                    'total_commits': commits_data['total_commits'],
                    'total_additions': commits_data['total_additions'],
                    'total_deletions': commits_data['total_deletions'],
                    'total_files_changed': commits_data['total_files_changed'],
                    'total_merge_requests': mrs_data['total_mrs'],
                    'avg_commit_size': commits_data['avg_commit_size'],
                    'repositories_count': len(commits_data['repositories'])
                },
                'recommendations': recommendations
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_commits_analysis(self, user_id: int = None,
                           repository_ids: List[int] = None,
                           start_date: datetime = None,
                           end_date: datetime = None,
                           group_by: str = 'day') -> Dict:
        """
        获取提交统计分析
        
        Args:
            user_id (int): 用户ID
            repository_ids (List[int]): 仓库ID列表
            start_date (datetime): 开始日期
            end_date (datetime): 结束日期
            group_by (str): 分组方式 ('day', 'week', 'month', 'author')
        
        Returns:
            Dict: 提交分析结果
        """
        try:
            # 设置默认时间范围
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # 构建查询
            query = db.session.query(Commit).join(Repository)
            
            # 添加过滤条件
            if user_id:
                query = query.filter(Repository.user_id == user_id)
            
            if repository_ids:
                query = query.filter(Repository.id.in_(repository_ids))
            
            query = query.filter(
                and_(
                    Commit.commit_date >= start_date,
                    Commit.commit_date <= end_date
                )
            )
            
            commits = query.all()
            
            if not commits:
                return {
                    'success': True,
                    'data': [],
                    'summary': {
                        'total_commits': 0,
                        'total_additions': 0,
                        'total_deletions': 0,
                        'total_files_changed': 0,
                        'unique_authors': 0
                    }
                }
            
            # 根据分组方式处理数据
            if group_by == 'author':
                grouped_data = self._group_commits_by_author(commits)
            elif group_by == 'repository':
                grouped_data = self._group_commits_by_repository(commits)
            else:
                grouped_data = self._group_commits_by_time(commits, group_by, start_date, end_date)
            
            # 计算汇总统计
            summary = {
                'total_commits': len(commits),
                'total_additions': sum(c.additions for c in commits),
                'total_deletions': sum(c.deletions for c in commits),
                'total_files_changed': sum(c.files_changed for c in commits),
                'unique_authors': len(set(c.author_email for c in commits)),
                'avg_commit_size': round(sum(c.additions + c.deletions for c in commits) / len(commits), 1),
                'period_days': (end_date - start_date).days
            }
            
            return {
                'success': True,
                'data': grouped_data,
                'summary': summary,
                'period': {
                    'start_date': start_date.isoformat() + 'Z',
                    'end_date': end_date.isoformat() + 'Z'
                },
                'group_by': group_by
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_merge_requests_analysis(self, user_id: int = None,
                                  repository_ids: List[int] = None,
                                  start_date: datetime = None,
                                  end_date: datetime = None) -> Dict:
        """
        获取合并请求统计分析
        
        Args:
            user_id (int): 用户ID
            repository_ids (List[int]): 仓库ID列表
            start_date (datetime): 开始日期
            end_date (datetime): 结束日期
        
        Returns:
            Dict: 合并请求分析结果
        """
        try:
            # 设置默认时间范围
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # 构建查询
            query = db.session.query(MergeRequest).join(Repository)
            
            # 添加过滤条件
            if user_id:
                query = query.filter(Repository.user_id == user_id)
            
            if repository_ids:
                query = query.filter(Repository.id.in_(repository_ids))
            
            query = query.filter(
                and_(
                    MergeRequest.created_at_remote >= start_date,
                    MergeRequest.created_at_remote <= end_date
                )
            )
            
            merge_requests = query.all()
            
            # 按状态分组统计
            status_stats = Counter(mr.state for mr in merge_requests)
            
            # 按作者分组统计
            author_stats = defaultdict(lambda: {
                'count': 0,
                'merged': 0,
                'closed': 0,
                'open': 0
            })
            
            # 计算合并时间统计
            merge_times = []
            
            for mr in merge_requests:
                author_stats[mr.author_email]['count'] += 1
                author_stats[mr.author_email][mr.state] += 1
                
                # 计算合并时间（如果已合并）
                if mr.state == 'merged' and mr.merged_at:
                    merge_time = (mr.merged_at - mr.created_at_remote).total_seconds() / 3600  # 小时
                    merge_times.append(merge_time)
            
            # 计算合并时间统计
            merge_time_stats = {}
            if merge_times:
                merge_time_stats = {
                    'avg_hours': round(statistics.mean(merge_times), 1),
                    'median_hours': round(statistics.median(merge_times), 1),
                    'min_hours': round(min(merge_times), 1),
                    'max_hours': round(max(merge_times), 1)
                }
            
            # 转换作者统计为列表格式
            author_list = []
            for email, stats in author_stats.items():
                author_list.append({
                    'author_email': email,
                    'total_count': stats['count'],
                    'merged_count': stats['merged'],
                    'closed_count': stats['closed'],
                    'open_count': stats['open'],
                    'merge_rate': calculate_percentage(stats['merged'], stats['count'])
                })
            
            # 按总数排序
            author_list.sort(key=lambda x: x['total_count'], reverse=True)
            
            return {
                'success': True,
                'summary': {
                    'total_merge_requests': len(merge_requests),
                    'merged_count': status_stats.get('merged', 0),
                    'closed_count': status_stats.get('closed', 0),
                    'open_count': status_stats.get('opened', 0),
                    'merge_rate': calculate_percentage(status_stats.get('merged', 0), len(merge_requests)),
                    'unique_authors': len(author_stats)
                },
                'status_distribution': dict(status_stats),
                'author_statistics': author_list,
                'merge_time_statistics': merge_time_stats,
                'period': {
                    'start_date': start_date.isoformat() + 'Z',
                    'end_date': end_date.isoformat() + 'Z',
                    'days': (end_date - start_date).days
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_time_distribution_analysis(self, user_id: int = None,
                                     repository_ids: List[int] = None,
                                     start_date: datetime = None,
                                     end_date: datetime = None) -> Dict:
        """
        获取时间分布分析
        
        Args:
            user_id (int): 用户ID
            repository_ids (List[int]): 仓库ID列表
            start_date (datetime): 开始日期
            end_date (datetime): 结束日期
        
        Returns:
            Dict: 时间分布分析结果
        """
        try:
            # 设置默认时间范围
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # 构建查询
            query = db.session.query(Commit).join(Repository)
            
            # 添加过滤条件
            if user_id:
                query = query.filter(Repository.user_id == user_id)
            
            if repository_ids:
                query = query.filter(Repository.id.in_(repository_ids))
            
            query = query.filter(
                and_(
                    Commit.commit_date >= start_date,
                    Commit.commit_date <= end_date
                )
            )
            
            commits = query.all()
            
            if not commits:
                return {
                    'success': True,
                    'hourly_distribution': [],
                    'daily_distribution': [],
                    'weekly_distribution': []
                }
            
            # 按小时分布统计
            hourly_stats = defaultdict(int)
            daily_stats = defaultdict(int)
            weekly_stats = defaultdict(int)
            
            weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            for commit in commits:
                commit_time = commit.commit_date
                
                # 小时分布 (0-23)
                hourly_stats[commit_time.hour] += 1
                
                # 星期分布 (0=Monday, 6=Sunday)
                weekday = commit_time.weekday()
                weekly_stats[weekday_names[weekday]] += 1
                
                # 日期分布
                date_key = commit_time.strftime('%Y-%m-%d')
                daily_stats[date_key] += 1
            
            # 格式化小时分布数据
            hourly_distribution = []
            for hour in range(24):
                hourly_distribution.append({
                    'hour': hour,
                    'count': hourly_stats[hour],
                    'label': f"{hour:02d}:00"
                })
            
            # 格式化星期分布数据
            weekly_distribution = []
            for day_name in weekday_names:
                weekly_distribution.append({
                    'day': day_name,
                    'count': weekly_stats[day_name]
                })
            
            # 格式化日期分布数据
            daily_distribution = []
            for date_str, count in sorted(daily_stats.items()):
                daily_distribution.append({
                    'date': date_str,
                    'count': count
                })
            
            # 计算活跃时间段
            peak_hour = max(hourly_stats.items(), key=lambda x: x[1])[0] if hourly_stats else 0
            peak_day = max(weekly_stats.items(), key=lambda x: x[1])[0] if weekly_stats else 'Monday'
            
            return {
                'success': True,
                'hourly_distribution': hourly_distribution,
                'daily_distribution': daily_distribution,
                'weekly_distribution': weekly_distribution,
                'insights': {
                    'peak_hour': peak_hour,
                    'peak_day': peak_day,
                    'total_commits': len(commits),
                    'active_days': len(daily_stats),
                    'avg_commits_per_day': round(len(commits) / max(len(daily_stats), 1), 1)
                },
                'period': {
                    'start_date': start_date.isoformat() + 'Z',
                    'end_date': end_date.isoformat() + 'Z',
                    'days': (end_date - start_date).days
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    # 私有辅助方法
    
    def _build_repository_filter(self, user_id: int, repository_ids: List[int] = None):
        """
        构建仓库过滤条件
        """
        if repository_ids:
            return Repository.id.in_(repository_ids)
        else:
            return Repository.user_id == user_id
    
    def _get_commits_data(self, repo_filter, start_date: datetime, 
                         end_date: datetime, user_email: str) -> Dict:
        """
        获取提交数据
        """
        commits = db.session.query(Commit).join(Repository).filter(
            and_(
                repo_filter,
                Commit.commit_date >= start_date,
                Commit.commit_date <= end_date,
                Commit.author_email == user_email
            )
        ).all()
        
        if not commits:
            return {
                'commits': [],
                'total_commits': 0,
                'total_additions': 0,
                'total_deletions': 0,
                'total_files_changed': 0,
                'avg_commit_size': 0,
                'repositories': set()
            }
        
        total_additions = sum(c.additions for c in commits)
        total_deletions = sum(c.deletions for c in commits)
        total_files_changed = sum(c.files_changed for c in commits)
        
        return {
            'commits': commits,
            'total_commits': len(commits),
            'total_additions': total_additions,
            'total_deletions': total_deletions,
            'total_files_changed': total_files_changed,
            'avg_commit_size': (total_additions + total_deletions) / len(commits),
            'repositories': set(c.repository_id for c in commits)
        }
    
    def _get_merge_requests_data(self, repo_filter, start_date: datetime,
                               end_date: datetime, user_email: str) -> Dict:
        """
        获取合并请求数据
        """
        mrs = db.session.query(MergeRequest).join(Repository).filter(
            and_(
                repo_filter,
                MergeRequest.created_at_remote >= start_date,
                MergeRequest.created_at_remote <= end_date,
                MergeRequest.author_email == user_email
            )
        ).all()
        
        return {
            'merge_requests': mrs,
            'total_mrs': len(mrs),
            'merged_mrs': len([mr for mr in mrs if mr.state == 'merged'])
        }
    
    def _calculate_commit_frequency_score(self, commits_data: Dict, 
                                        start_date: datetime, end_date: datetime) -> float:
        """
        计算提交频率评分
        """
        days = max((end_date - start_date).days, 1)
        commits_per_day = commits_data['total_commits'] / days
        
        # 评分标准：每天1次提交为满分
        if commits_per_day >= 1.0:
            return 100.0
        elif commits_per_day >= 0.5:
            return 80.0 + (commits_per_day - 0.5) * 40
        elif commits_per_day >= 0.2:
            return 60.0 + (commits_per_day - 0.2) * 66.7
        else:
            return commits_per_day * 300  # 最低分
    
    def _calculate_code_quality_score(self, commits_data: Dict) -> float:
        """
        计算代码质量评分（基于提交大小）
        """
        if commits_data['total_commits'] == 0:
            return 0.0
        
        avg_size = commits_data['avg_commit_size']
        
        # 理想的提交大小：50-200行变更
        if 50 <= avg_size <= 200:
            return 100.0
        elif 20 <= avg_size < 50 or 200 < avg_size <= 500:
            return 80.0
        elif 10 <= avg_size < 20 or 500 < avg_size <= 1000:
            return 60.0
        else:
            return 40.0
    
    def _calculate_merge_request_ratio_score(self, commits_data: Dict, mrs_data: Dict) -> float:
        """
        计算合并请求比率评分
        """
        if commits_data['total_commits'] == 0:
            return 0.0
        
        # 理想比率：每5-10次提交有1个合并请求
        ratio = mrs_data['total_mrs'] / commits_data['total_commits']
        
        if 0.1 <= ratio <= 0.2:  # 1/10 到 1/5
            return 100.0
        elif 0.05 <= ratio < 0.1 or 0.2 < ratio <= 0.3:
            return 80.0
        elif ratio > 0.3:
            return 60.0
        else:
            return ratio * 500  # 比率过低
    
    def _calculate_consistency_score(self, commits_data: Dict, 
                                   start_date: datetime, end_date: datetime) -> float:
        """
        计算编程一致性评分
        """
        if not commits_data['commits']:
            return 0.0
        
        # 按日期分组提交
        daily_commits = defaultdict(int)
        for commit in commits_data['commits']:
            date_key = commit.commit_date.date()
            daily_commits[date_key] += 1
        
        # 计算活跃天数
        total_days = (end_date - start_date).days
        active_days = len(daily_commits)
        
        # 一致性评分：活跃天数比例
        consistency_ratio = active_days / max(total_days, 1)
        
        if consistency_ratio >= 0.8:
            return 100.0
        elif consistency_ratio >= 0.6:
            return 80.0 + (consistency_ratio - 0.6) * 100
        elif consistency_ratio >= 0.3:
            return 60.0 + (consistency_ratio - 0.3) * 66.7
        else:
            return consistency_ratio * 200
    
    def _calculate_collaboration_score(self, commits_data: Dict, mrs_data: Dict) -> float:
        """
        计算协作能力评分
        """
        # 基于合并请求的合并率
        if mrs_data['total_mrs'] == 0:
            return 50.0  # 没有合并请求时给中等分
        
        merge_rate = mrs_data['merged_mrs'] / mrs_data['total_mrs']
        
        if merge_rate >= 0.8:
            return 100.0
        elif merge_rate >= 0.6:
            return 80.0 + (merge_rate - 0.6) * 100
        elif merge_rate >= 0.4:
            return 60.0 + (merge_rate - 0.4) * 100
        else:
            return merge_rate * 150
    
    def _get_score_level(self, score: float) -> str:
        """
        根据分数获取等级
        """
        if score >= self.score_standards['excellent']:
            return 'excellent'
        elif score >= self.score_standards['good']:
            return 'good'
        elif score >= self.score_standards['average']:
            return 'average'
        elif score >= self.score_standards['below_average']:
            return 'below_average'
        else:
            return 'poor'
    
    def _generate_recommendations(self, scores: Dict) -> List[str]:
        """
        根据各项评分生成改进建议
        """
        recommendations = []
        
        if scores['commit_frequency'] < 70:
            recommendations.append('增加代码提交频率，建议每天至少提交一次')
        
        if scores['code_quality'] < 70:
            recommendations.append('优化提交粒度，每次提交包含50-200行代码变更为佳')
        
        if scores['merge_request_ratio'] < 70:
            recommendations.append('增加合并请求的使用，建议每5-10次提交创建一个合并请求')
        
        if scores['consistency'] < 70:
            recommendations.append('保持编程的一致性，尽量每天都有代码活动')
        
        if scores['collaboration'] < 70:
            recommendations.append('提高合并请求的质量，确保更多的请求能够被成功合并')
        
        if not recommendations:
            recommendations.append('继续保持良好的编程习惯！')
        
        return recommendations
    
    def _group_commits_by_time(self, commits: List, group_by: str, 
                             start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        按时间分组提交记录
        """
        if group_by == 'day':
            date_format = '%Y-%m-%d'
            date_range = get_date_range(start_date, end_date, 'day')
        elif group_by == 'week':
            date_format = '%Y-W%U'
            date_range = get_date_range(start_date, end_date, 'week')
        elif group_by == 'month':
            date_format = '%Y-%m'
            date_range = get_date_range(start_date, end_date, 'month')
        else:
            date_format = '%Y-%m-%d'
            date_range = get_date_range(start_date, end_date, 'day')
        
        # 按时间分组
        grouped = defaultdict(lambda: {
            'commits': 0,
            'additions': 0,
            'deletions': 0,
            'files_changed': 0
        })
        
        for commit in commits:
            key = commit.commit_date.strftime(date_format)
            grouped[key]['commits'] += 1
            grouped[key]['additions'] += commit.additions
            grouped[key]['deletions'] += commit.deletions
            grouped[key]['files_changed'] += commit.files_changed
        
        # 格式化结果
        result = []
        for date_key in date_range:
            formatted_key = date_key.strftime(date_format)
            data = grouped[formatted_key]
            result.append({
                'date': formatted_key,
                'commits': data['commits'],
                'additions': data['additions'],
                'deletions': data['deletions'],
                'files_changed': data['files_changed'],
                'total_changes': data['additions'] + data['deletions']
            })
        
        return result
    
    def _group_commits_by_author(self, commits: List) -> List[Dict]:
        """
        按作者分组提交记录
        """
        grouped = defaultdict(lambda: {
            'commits': 0,
            'additions': 0,
            'deletions': 0,
            'files_changed': 0,
            'author_name': ''
        })
        
        for commit in commits:
            key = commit.author_email
            grouped[key]['commits'] += 1
            grouped[key]['additions'] += commit.additions
            grouped[key]['deletions'] += commit.deletions
            grouped[key]['files_changed'] += commit.files_changed
            grouped[key]['author_name'] = commit.author_name
        
        # 转换为列表并排序
        result = []
        for email, data in grouped.items():
            result.append({
                'author_email': email,
                'author_name': data['author_name'],
                'commits': data['commits'],
                'additions': data['additions'],
                'deletions': data['deletions'],
                'files_changed': data['files_changed'],
                'total_changes': data['additions'] + data['deletions']
            })
        
        # 按提交数排序
        result.sort(key=lambda x: x['commits'], reverse=True)
        return result
    
    def _group_commits_by_repository(self, commits: List) -> List[Dict]:
        """
        按仓库分组提交记录
        """
        grouped = defaultdict(lambda: {
            'commits': 0,
            'additions': 0,
            'deletions': 0,
            'files_changed': 0,
            'repository_name': ''
        })
        
        for commit in commits:
            key = commit.repository_id
            grouped[key]['commits'] += 1
            grouped[key]['additions'] += commit.additions
            grouped[key]['deletions'] += commit.deletions
            grouped[key]['files_changed'] += commit.files_changed
            grouped[key]['repository_name'] = commit.repository.name
        
        # 转换为列表并排序
        result = []
        for repo_id, data in grouped.items():
            result.append({
                'repository_id': repo_id,
                'repository_name': data['repository_name'],
                'commits': data['commits'],
                'additions': data['additions'],
                'deletions': data['deletions'],
                'files_changed': data['files_changed'],
                'total_changes': data['additions'] + data['deletions']
            })
        
        # 按提交数排序
        result.sort(key=lambda x: x['commits'], reverse=True)
        return result