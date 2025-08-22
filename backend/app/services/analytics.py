# -*- coding: utf-8 -*-
"""
数据统计和分析核心算法模块
提供代码提交、合并请求等数据的统计分析功能
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy import func, and_, or_
from app.models import Repository, Commit, MergeRequest, User
from app.models.analytics_cache import AnalyticsCache
from app import db
import json


class AnalyticsService:
    """数据分析服务类"""
    
    def __init__(self):
        self.cache_duration = timedelta(hours=1)  # 缓存1小时
    
    def get_repository_stats(self, repo_id: int, days: int = 30) -> Dict:
        """获取仓库统计数据
        
        Args:
            repo_id: 仓库ID
            days: 统计天数，默认30天
            
        Returns:
            包含统计数据的字典
        """
        cache_key = f"repo_stats_{repo_id}_{days}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 基础统计
        total_commits = self._get_commit_count(repo_id, start_date, end_date)
        total_mrs = self._get_mr_count(repo_id, start_date, end_date)
        active_contributors = self._get_active_contributors(repo_id, start_date, end_date)
        
        # 趋势数据
        commit_trend = self._get_commit_trend(repo_id, start_date, end_date, days)
        mr_trend = self._get_mr_trend(repo_id, start_date, end_date, days)
        
        # 贡献者排行
        top_contributors = self._get_top_contributors(repo_id, start_date, end_date)
        
        stats = {
            'total_commits': total_commits,
            'total_merge_requests': total_mrs,
            'active_contributors': active_contributors,
            'commit_trend': commit_trend,
            'mr_trend': mr_trend,
            'top_contributors': top_contributors,
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            }
        }
        
        self._cache_data(cache_key, stats)
        return stats
    
    def get_user_stats(self, user_id: int, days: int = 30) -> Dict:
        """获取用户统计数据
        
        Args:
            user_id: 用户ID
            days: 统计天数，默认30天
            
        Returns:
            包含用户统计数据的字典
        """
        cache_key = f"user_stats_{user_id}_{days}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 用户提交统计
        user = User.query.get(user_id)
        if not user:
            return None
            
        user_commits = db.session.query(Commit).filter(
            and_(
                Commit.author_email == user.email,
                Commit.commit_date >= start_date,
                Commit.commit_date <= end_date
            )
        ).count()
        
        # 用户MR统计
        user_mrs = db.session.query(MergeRequest).filter(
            and_(
                MergeRequest.author_email == user.email,
                MergeRequest.created_at_remote >= start_date,
                MergeRequest.created_at_remote <= end_date
            )
        ).count()
        
        # 用户活跃仓库
        active_repos = db.session.query(
            Repository.id,
            Repository.name,
            func.count(Commit.id).label('commit_count')
        ).join(
            Commit, Repository.id == Commit.repository_id
        ).filter(
            and_(
                Commit.author_email == user.email,
                Commit.commit_date >= start_date,
                Commit.commit_date <= end_date
            )
        ).group_by(Repository.id, Repository.name).all()
        
        stats = {
            'total_commits': user_commits,
            'total_merge_requests': user_mrs,
            'active_repositories': [
                {
                    'id': repo.id,
                    'name': repo.name,
                    'commit_count': repo.commit_count
                }
                for repo in active_repos
            ],
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            }
        }
        
        self._cache_data(cache_key, stats)
        return stats
    
    def get_team_productivity(self, repo_ids: List[int], days: int = 30) -> Dict:
        """获取团队生产力统计
        
        Args:
            repo_ids: 仓库ID列表
            days: 统计天数，默认30天
            
        Returns:
            包含团队生产力数据的字典
        """
        cache_key = f"team_productivity_{'_'.join(map(str, repo_ids))}_{days}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 团队总体统计
        total_commits = db.session.query(Commit).filter(
            and_(
                Commit.repository_id.in_(repo_ids),
                Commit.commit_date >= start_date,
                Commit.commit_date <= end_date
            )
        ).count()
        
        total_mrs = db.session.query(MergeRequest).filter(
            and_(
                MergeRequest.repository_id.in_(repo_ids),
                MergeRequest.created_at_remote >= start_date,
                MergeRequest.created_at_remote <= end_date
            )
        ).count()
        
        # 平均合并时间
        avg_merge_time = self._calculate_avg_merge_time(repo_ids, start_date, end_date)
        
        # 代码质量指标（基于MR状态）
        quality_metrics = self._calculate_quality_metrics(repo_ids, start_date, end_date)
        
        stats = {
            'total_commits': total_commits,
            'total_merge_requests': total_mrs,
            'average_merge_time_hours': avg_merge_time,
            'quality_metrics': quality_metrics,
            'commits_per_day': round(total_commits / days, 2),
            'mrs_per_day': round(total_mrs / days, 2),
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            }
        }
        
        self._cache_data(cache_key, stats)
        return stats
    
    def _get_commit_count(self, repo_id: int, start_date: datetime, end_date: datetime) -> int:
        """获取指定时间段内的提交数量"""
        return db.session.query(Commit).filter(
            and_(
                Commit.repository_id == repo_id,
                Commit.commit_date >= start_date,
                Commit.commit_date <= end_date
            )
        ).count()
    
    def _get_mr_count(self, repo_id: int, start_date: datetime, end_date: datetime) -> int:
        """获取指定时间段内的合并请求数量"""
        return db.session.query(MergeRequest).filter(
            and_(
                MergeRequest.repository_id == repo_id,
                MergeRequest.created_at_remote >= start_date,
                MergeRequest.created_at_remote <= end_date
            )
        ).count()
    
    def _get_active_contributors(self, repo_id: int, start_date: datetime, end_date: datetime) -> int:
        """获取活跃贡献者数量"""
        return db.session.query(Commit.author_email).filter(
            and_(
                Commit.repository_id == repo_id,
                Commit.commit_date >= start_date,
                Commit.commit_date <= end_date
            )
        ).distinct().count()
    
    def _get_commit_trend(self, repo_id: int, start_date: datetime, end_date: datetime, days: int) -> List[Dict]:
        """获取提交趋势数据"""
        # 按天分组统计提交数量
        trend_data = []
        current_date = start_date
        
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            count = db.session.query(Commit).filter(
                and_(
                    Commit.repository_id == repo_id,
                    Commit.commit_date >= current_date,
                    Commit.commit_date < next_date
                )
            ).count()
            
            trend_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'count': count
            })
            
            current_date = next_date
        
        return trend_data
    
    def _get_mr_trend(self, repo_id: int, start_date: datetime, end_date: datetime, days: int) -> List[Dict]:
        """获取合并请求趋势数据"""
        trend_data = []
        current_date = start_date
        
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            count = db.session.query(MergeRequest).filter(
                and_(
                    MergeRequest.repository_id == repo_id,
                    MergeRequest.created_at_remote >= current_date,
                    MergeRequest.created_at_remote < next_date
                )
            ).count()
            
            trend_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'count': count
            })
            
            current_date = next_date
        
        return trend_data
    
    def _get_top_contributors(self, repo_id: int, start_date: datetime, end_date: datetime, limit: int = 10) -> List[Dict]:
        """获取顶级贡献者排行"""
        contributors = db.session.query(
            User.id,
            User.username,
            User.email,
            func.count(Commit.id).label('commit_count')
        ).join(
            Commit, User.email == Commit.author_email
        ).filter(
            and_(
                Commit.repository_id == repo_id,
                Commit.commit_date >= start_date,
                Commit.commit_date <= end_date
            )
        ).group_by(
            User.id, User.username, User.email
        ).order_by(
            func.count(Commit.id).desc()
        ).limit(limit).all()
        
        return [
            {
                'user_id': contrib.id,
                'username': contrib.username,
                'email': contrib.email,
                'commit_count': contrib.commit_count
            }
            for contrib in contributors
        ]
    
    def _calculate_avg_merge_time(self, repo_ids: List[int], start_date: datetime, end_date: datetime) -> float:
        """计算平均合并时间（小时）"""
        merged_mrs = db.session.query(MergeRequest).filter(
            and_(
                MergeRequest.repository_id.in_(repo_ids),
                MergeRequest.created_at_remote >= start_date,
                MergeRequest.created_at_remote <= end_date,
                MergeRequest.state == 'merged',
                MergeRequest.merged_at.isnot(None)
            )
        ).all()
        
        if not merged_mrs:
            return 0.0
        
        total_hours = 0
        for mr in merged_mrs:
            if mr.merged_at and mr.created_at:
                delta = mr.merged_at - mr.created_at
                total_hours += delta.total_seconds() / 3600
        
        return round(total_hours / len(merged_mrs), 2)
    
    def _calculate_quality_metrics(self, repo_ids: List[int], start_date: datetime, end_date: datetime) -> Dict:
        """计算代码质量指标"""
        mrs = db.session.query(MergeRequest).filter(
            and_(
                MergeRequest.repository_id.in_(repo_ids),
                MergeRequest.created_at_remote >= start_date,
                MergeRequest.created_at_remote <= end_date
            )
        ).all()
        
        if not mrs:
            return {
                'merge_rate': 0.0,
                'close_rate': 0.0,
                'open_rate': 0.0
            }
        
        total_count = len(mrs)
        merged_count = sum(1 for mr in mrs if mr.state == 'merged')
        closed_count = sum(1 for mr in mrs if mr.state == 'closed')
        open_count = sum(1 for mr in mrs if mr.state == 'opened')
        
        return {
            'merge_rate': round(merged_count / total_count * 100, 2),
            'close_rate': round(closed_count / total_count * 100, 2),
            'open_rate': round(open_count / total_count * 100, 2)
        }
    
    def _get_cached_data(self, cache_key: str) -> Optional[Dict]:
        """获取缓存数据"""
        cache_entry = AnalyticsCache.query.filter_by(cache_key=cache_key).first()
        if cache_entry and cache_entry.expires_at > datetime.utcnow():
            return cache_entry.get_result_data()
        return None
    
    def _cache_data(self, cache_key: str, data: Dict) -> None:
        """缓存数据"""
        expires_at = datetime.utcnow() + self.cache_duration
        
        # 删除旧缓存
        AnalyticsCache.query.filter_by(cache_key=cache_key).delete()
        
        # 创建新缓存
        cache_entry = AnalyticsCache(
            cache_key=cache_key,
            cache_type='dashboard',
            parameters={},
            result_data=data,
            expires_at=expires_at
        )
        
        db.session.add(cache_entry)
        db.session.commit()


# 创建全局实例
analytics_service = AnalyticsService()