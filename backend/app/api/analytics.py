# -*- coding: utf-8 -*-
"""
数据分析API模块
包含统计分析、效率评分、报表生成等功能
"""

from flask import request, current_app, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
import json
from collections import defaultdict

from . import analytics_bp as api_bp
from ..models import Repository, User, Commit, MergeRequest, AnalyticsCache
from .. import db
from ..services.analytics import analytics_service
from ..utils.response import (
    success_response, error_response, validation_error_response,
    not_found_response
)
from ..utils.validators import validate_date_range
from ..utils.auth import token_required, get_current_user
from ..utils.decorators import require_permission
from ..utils.helpers import parse_datetime_string, get_date_range_by_params

@api_bp.route('/overview', methods=['GET'])
@token_required
def get_analytics_overview(current_user):
    """
    获取分析概览
    
    Headers:
        Authorization: Bearer <access_token>
    
    Query Parameters:
        start_date (str): 开始日期 (YYYY-MM-DD)
        end_date (str): 结束日期 (YYYY-MM-DD)
        repository_ids (str): 仓库ID列表，逗号分隔
    
    Returns:
        JSON响应包含分析概览数据
    """
    try:
        # 获取查询参数
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        repository_ids_str = request.args.get('repository_ids')
        
        # 解析日期范围
        start_date, end_date = get_date_range_by_params(
            start_date_str,
            end_date_str,
            30
        )
        
        # 解析仓库ID列表
        repository_ids = None
        if repository_ids_str:
            try:
                repository_ids = [int(id.strip()) for id in repository_ids_str.split(',') if id.strip()]
            except ValueError:
                return validation_error_response("仓库ID格式不正确")
        
        # 获取用户的仓库
        repositories_query = Repository.query.filter_by(
            user_id=current_user.id,
            is_active=True
        )
        
        if repository_ids:
            repositories_query = repositories_query.filter(
                Repository.id.in_(repository_ids)
            )
        
        repositories = repositories_query.all()
        repo_ids = [repo.id for repo in repositories]
        
        if not repo_ids:
            return success_response(
                data={
                    'repositories_count': 0,
                    'commits_count': 0,
                    'merge_requests_count': 0,
                    'active_contributors': 0,
                    'code_changes': {
                        'additions': 0,
                        'deletions': 0,
                        'net_changes': 0
                    },
                    'period': {
                        'start_date': start_date.isoformat() + 'Z',
                        'end_date': end_date.isoformat() + 'Z'
                    }
                },
                message="获取分析概览成功"
            )
        
        # 统计提交数据
        commits_stats = db.session.query(
            func.count(Commit.id).label('count'),
            func.sum(Commit.additions).label('additions'),
            func.sum(Commit.deletions).label('deletions'),
            func.count(func.distinct(Commit.author_email)).label('contributors')
        ).filter(
            Commit.repository_id.in_(repo_ids),
            Commit.commit_date >= start_date,
            Commit.commit_date <= end_date
        ).first()
        
        # 统计合并请求数据
        mrs_stats = db.session.query(
            func.count(MergeRequest.id).label('count'),
            func.sum(MergeRequest.additions).label('additions'),
            func.sum(MergeRequest.deletions).label('deletions')
        ).filter(
            MergeRequest.repository_id.in_(repo_ids),
            MergeRequest.created_at_remote >= start_date,
            MergeRequest.created_at_remote <= end_date
        ).first()
        
        # 构建响应数据
        overview_data = {
            'repositories_count': len(repositories),
            'commits_count': commits_stats.count or 0,
            'merge_requests_count': mrs_stats.count or 0,
            'active_contributors': commits_stats.contributors or 0,
            'code_changes': {
                'additions': (commits_stats.additions or 0) + (mrs_stats.additions or 0),
                'deletions': (commits_stats.deletions or 0) + (mrs_stats.deletions or 0),
                'net_changes': ((commits_stats.additions or 0) + (mrs_stats.additions or 0)) - 
                              ((commits_stats.deletions or 0) + (mrs_stats.deletions or 0))
            },
            'period': {
                'start_date': start_date.isoformat() + 'Z',
                'end_date': end_date.isoformat() + 'Z'
            }
        }
        
        return success_response(
            data=overview_data,
            message="获取分析概览成功"
        )
        
    except Exception as e:
        current_app.logger.error(f"获取分析概览失败: {str(e)}")
        return error_response("获取分析概览失败")

@api_bp.route('/commits', methods=['GET'])
@token_required
def get_commits_analytics(current_user):
    """
    获取提交统计分析
    
    Headers:
        Authorization: Bearer <access_token>
    
    Query Parameters:
        start_date (str): 开始日期
        end_date (str): 结束日期
        repository_ids (str): 仓库ID列表
        group_by (str): 分组方式 (hour, day, week, month, author)
        author_email (str): 作者邮箱筛选
    
    Returns:
        JSON响应包含提交统计数据
    """
    try:
        # 获取查询参数
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        repository_ids_str = request.args.get('repository_ids')
        group_by = request.args.get('group_by', 'day')
        author_email = request.args.get('author_email')
        
        # 解析日期范围
        start_date, end_date = get_date_range_by_params(
            start_date_str,
            end_date_str,
            30
        )
        
        # 解析仓库ID列表
        repository_ids = None
        if repository_ids_str:
            try:
                repository_ids = [int(id.strip()) for id in repository_ids_str.split(',') if id.strip()]
            except ValueError:
                return validation_error_response("仓库ID格式不正确")
        
        # 获取用户的仓库
        repositories_query = Repository.query.filter_by(
            user_id=current_user.id,
            is_active=True
        )
        
        if repository_ids:
            repositories_query = repositories_query.filter(
                Repository.id.in_(repository_ids)
            )
        
        repositories = repositories_query.all()
        repo_ids = [repo.id for repo in repositories]
        
        if not repo_ids:
            return success_response(
                data={'items': [], 'summary': {}},
                message="获取提交统计成功"
            )
        
        # 构建查询
        query = Commit.query.filter(
            Commit.repository_id.in_(repo_ids),
            Commit.commit_date >= start_date,
            Commit.commit_date <= end_date
        )
        
        if author_email:
            query = query.filter(Commit.author_email == author_email)
        
        # 根据分组方式获取数据
        if group_by == 'author':
            analytics_data = get_commits_by_author(query)
        else:
            analytics_data = get_commits_by_time(query, group_by, start_date, end_date)
        
        return success_response(
            data=analytics_data,
            message="获取提交统计成功"
        )
        
    except Exception as e:
        current_app.logger.error(f"获取提交统计失败: {str(e)}")
        return error_response("获取提交统计失败")

@api_bp.route('/merge-requests', methods=['GET'])
@token_required
def get_merge_requests_analytics(current_user):
    """
    获取合并请求统计分析
    
    Headers:
        Authorization: Bearer <access_token>
    
    Query Parameters:
        start_date (str): 开始日期
        end_date (str): 结束日期
        repository_ids (str): 仓库ID列表
        group_by (str): 分组方式 (day, week, month, author, state)
        state (str): 状态筛选 (opened, merged, closed)
        author_email (str): 作者邮箱筛选
    
    Returns:
        JSON响应包含合并请求统计数据
    """
    try:
        # 获取查询参数
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        repository_ids_str = request.args.get('repository_ids')
        group_by = request.args.get('group_by', 'day')
        state = request.args.get('state')
        author_email = request.args.get('author_email')
        
        # 解析日期范围
        start_date, end_date = get_date_range_by_params(
            start_date_str,
            end_date_str,
            30
        )
        
        # 解析仓库ID列表
        repository_ids = None
        if repository_ids_str:
            try:
                repository_ids = [int(id.strip()) for id in repository_ids_str.split(',') if id.strip()]
            except ValueError:
                return validation_error_response("仓库ID格式不正确")
        
        # 获取用户的仓库
        repositories_query = Repository.query.filter_by(
            user_id=current_user.id,
            is_active=True
        )
        
        if repository_ids:
            repositories_query = repositories_query.filter(
                Repository.id.in_(repository_ids)
            )
        
        repositories = repositories_query.all()
        repo_ids = [repo.id for repo in repositories]
        
        if not repo_ids:
            return success_response(
                data={'items': [], 'summary': {}},
                message="获取合并请求统计成功"
            )
        
        # 构建查询
        query = MergeRequest.query.filter(
            MergeRequest.repository_id.in_(repo_ids),
            MergeRequest.created_at_remote >= start_date,
            MergeRequest.created_at_remote <= end_date
        )
        
        if state:
            query = query.filter(MergeRequest.state == state)
        
        if author_email:
            query = query.filter(MergeRequest.author_email == author_email)
        
        # 根据分组方式获取数据
        if group_by == 'author':
            analytics_data = get_merge_requests_by_author(query)
        elif group_by == 'state':
            analytics_data = get_merge_requests_by_state(query)
        else:
            analytics_data = get_merge_requests_by_time(query, group_by, start_date, end_date)
        
        return success_response(
            data=analytics_data,
            message="获取合并请求统计成功"
        )
        
    except Exception as e:
        current_app.logger.error(f"获取合并请求统计失败: {str(e)}")
        return error_response("获取合并请求统计失败")

@api_bp.route('/efficiency-score', methods=['GET'])
@token_required
def get_efficiency_score(current_user):
    """
    获取效率评分
    
    Headers:
        Authorization: Bearer <access_token>
    
    Query Parameters:
        start_date (str): 开始日期
        end_date (str): 结束日期
        repository_ids (str): 仓库ID列表
        group_by (str): 分组方式 (author, repository)
        score_config (str): 评分配置JSON字符串
    
    Returns:
        JSON响应包含效率评分数据
    """
    try:
        # 获取查询参数
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        repository_ids_str = request.args.get('repository_ids')
        group_by = request.args.get('group_by', 'author')
        score_config_str = request.args.get('score_config')
        
        # 解析评分配置
        score_config = {
            'commit_weight': 1.0,
            'merge_request_weight': 2.0,
            'addition_weight': 0.1,
            'deletion_weight': 0.05,
            'file_change_weight': 0.2
        }
        
        if score_config_str:
            try:
                custom_config = json.loads(score_config_str)
                score_config.update(custom_config)
            except json.JSONDecodeError:
                return validation_error_response("评分配置格式不正确")
        
        # 解析日期范围
        start_date, end_date = get_date_range_by_params(
            start_date_str,
            end_date_str,
            30
        )
        
        # 解析仓库ID列表
        repository_ids = None
        if repository_ids_str:
            try:
                repository_ids = [int(id.strip()) for id in repository_ids_str.split(',') if id.strip()]
            except ValueError:
                return validation_error_response("仓库ID格式不正确")
        
        # 获取用户的仓库
        repositories_query = Repository.query.filter_by(
            user_id=current_user.id,
            is_active=True
        )
        
        if repository_ids:
            repositories_query = repositories_query.filter(
                Repository.id.in_(repository_ids)
            )
        
        repositories = repositories_query.all()
        repo_ids = [repo.id for repo in repositories]
        
        if not repo_ids:
            return success_response(
                data={'items': [], 'config': score_config},
                message="获取效率评分成功"
            )
        
        # 计算效率评分
        if group_by == 'author':
            score_data = calculate_efficiency_score_by_author(
                repo_ids, start_date, end_date, score_config
            )
        else:
            score_data = calculate_efficiency_score_by_repository(
                repo_ids, start_date, end_date, score_config
            )
        
        return success_response(
            data={
                'items': score_data,
                'config': score_config,
                'period': {
                    'start_date': start_date.isoformat() + 'Z',
                    'end_date': end_date.isoformat() + 'Z'
                }
            },
            message="获取效率评分成功"
        )
        
    except Exception as e:
        current_app.logger.error(f"获取效率评分失败: {str(e)}")
        return error_response("获取效率评分失败")

@api_bp.route('/repository/<int:repo_id>', methods=['GET'])
@jwt_required()
@require_permission('read')
def get_repository_analytics(repo_id):
    """获取仓库分析数据"""
    try:
        # 获取时间范围参数
        days = request.args.get('days', 30, type=int)
        
        # 验证仓库存在
        repository = Repository.query.get_or_404(repo_id)
        
        # 使用分析服务获取统计数据
        stats = analytics_service.get_repository_stats(repo_id, days)
        
        return jsonify({
            'repository': {
                'id': repository.id,
                'name': repository.name,
                'url': repository.url
            },
            'statistics': stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
@require_permission('read')
def get_user_analytics(user_id):
    """获取用户分析数据"""
    try:
        # 获取时间范围参数
        days = request.args.get('days', 30, type=int)
        
        # 验证用户存在
        user = User.query.get_or_404(user_id)
        
        # 使用分析服务获取统计数据
        stats = analytics_service.get_user_stats(user_id, days)
        
        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'statistics': stats
        })
        
    except Exception as e:
         return jsonify({'error': str(e)}), 500

@api_bp.route('/team/productivity', methods=['GET'])
@jwt_required()
@require_permission('read')
def get_team_productivity():
    """获取团队生产力分析数据"""
    try:
        # 获取参数
        days = request.args.get('days', 30, type=int)
        repo_ids_str = request.args.get('repo_ids', '')
        
        # 解析仓库ID列表
        if repo_ids_str:
            repo_ids = [int(id.strip()) for id in repo_ids_str.split(',') if id.strip().isdigit()]
        else:
            # 如果没有指定仓库，获取用户有权限的所有仓库
            current_user_id = get_jwt_identity()
            user_repos = Repository.query.filter_by(user_id=current_user_id).all()
            repo_ids = [repo.id for repo in user_repos]
        
        if not repo_ids:
            return jsonify({'error': '没有找到可分析的仓库'}), 400
        
        # 使用分析服务获取团队生产力数据
        stats = analytics_service.get_team_productivity(repo_ids, days)
        
        return jsonify({
            'team_productivity': stats,
            'analyzed_repositories': repo_ids
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@require_permission('read')
def get_dashboard_data():
    """获取仪表板数据"""
    try:
        current_user_id = get_jwt_identity()
        days = request.args.get('days', 30, type=int)
        
        # 获取用户统计
        user_stats = analytics_service.get_user_stats(current_user_id, days)
        
        # 获取用户仓库列表
        user_repos = Repository.query.filter_by(user_id=current_user_id).all()
        repo_ids = [repo.id for repo in user_repos]
        
        # 获取团队生产力数据
        team_stats = analytics_service.get_team_productivity(repo_ids, days) if repo_ids else {}
        
        # 获取最近活跃的仓库统计
        recent_repo_stats = []
        for repo in user_repos[:5]:  # 限制最多5个仓库
            repo_stat = analytics_service.get_repository_stats(repo.id, 7)  # 最近7天
            recent_repo_stats.append({
                'repository': {
                    'id': repo.id,
                    'name': repo.name,
                    'url': repo.url
                },
                'stats': repo_stat
            })
        
        return jsonify({
            'user_statistics': user_stats,
            'team_productivity': team_stats,
            'recent_repositories': recent_repo_stats,
            'summary': {
                'total_repositories': len(user_repos),
                'analysis_period_days': days
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/time-distribution', methods=['GET'])
@token_required
def get_time_distribution(current_user):
    """
    获取时间分布分析
    
    Headers:
        Authorization: Bearer <access_token>
    
    Query Parameters:
        start_date (str): 开始日期
        end_date (str): 结束日期
        repository_ids (str): 仓库ID列表
        type (str): 分析类型 (commits, merge_requests)
        dimension (str): 时间维度 (hour, weekday, month)
    
    Returns:
        JSON响应包含时间分布数据
    """
    try:
        # 获取查询参数
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        repository_ids_str = request.args.get('repository_ids')
        analysis_type = request.args.get('type', 'commits')
        dimension = request.args.get('dimension', 'hour')
        
        # 解析日期范围
        start_date, end_date = get_date_range_by_params(
            start_date_str,
            end_date_str,
            30
        )
        
        # 解析仓库ID列表
        repository_ids = None
        if repository_ids_str:
            try:
                repository_ids = [int(id.strip()) for id in repository_ids_str.split(',') if id.strip()]
            except ValueError:
                return validation_error_response("仓库ID格式不正确")
        
        # 获取用户的仓库
        repositories_query = Repository.query.filter_by(
            user_id=current_user.id,
            is_active=True
        )
        
        if repository_ids:
            repositories_query = repositories_query.filter(
                Repository.id.in_(repository_ids)
            )
        
        repositories = repositories_query.all()
        repo_ids = [repo.id for repo in repositories]
        
        if not repo_ids:
            return success_response(
                data={'distribution': [], 'summary': {}},
                message="获取时间分布成功"
            )
        
        # 获取时间分布数据
        if analysis_type == 'commits':
            distribution_data = get_commits_time_distribution(
                repo_ids, start_date, end_date, dimension
            )
        else:
            distribution_data = get_merge_requests_time_distribution(
                repo_ids, start_date, end_date, dimension
            )
        
        return success_response(
            data=distribution_data,
            message="获取时间分布成功"
        )
        
    except Exception as e:
        current_app.logger.error(f"获取时间分布失败: {str(e)}")
        return error_response("获取时间分布失败")

# 辅助函数

def get_commits_by_author(query):
    """
    按作者分组获取提交统计
    
    Args:
        query: SQLAlchemy查询对象
    
    Returns:
        dict: 统计数据
    """
    results = query.with_entities(
        Commit.author_name,
        Commit.author_email,
        func.count(Commit.id).label('commits_count'),
        func.sum(Commit.additions).label('additions'),
        func.sum(Commit.deletions).label('deletions'),
        func.sum(Commit.files_changed).label('files_changed')
    ).group_by(
        Commit.author_name,
        Commit.author_email
    ).order_by(
        func.count(Commit.id).desc()
    ).all()
    
    items = []
    total_commits = 0
    total_additions = 0
    total_deletions = 0
    
    for result in results:
        item = {
            'author_name': result.author_name,
            'author_email': result.author_email,
            'commits_count': result.commits_count,
            'additions': result.additions or 0,
            'deletions': result.deletions or 0,
            'files_changed': result.files_changed or 0,
            'net_changes': (result.additions or 0) - (result.deletions or 0)
        }
        items.append(item)
        
        total_commits += result.commits_count
        total_additions += result.additions or 0
        total_deletions += result.deletions or 0
    
    return {
        'items': items,
        'summary': {
            'total_commits': total_commits,
            'total_additions': total_additions,
            'total_deletions': total_deletions,
            'total_contributors': len(items)
        }
    }

def get_commits_by_time(query, group_by, start_date, end_date):
    """
    按时间分组获取提交统计
    
    Args:
        query: SQLAlchemy查询对象
        group_by (str): 分组方式
        start_date (datetime): 开始日期
        end_date (datetime): 结束日期
    
    Returns:
        dict: 统计数据
    """
    # 根据分组方式选择时间格式（SQLite使用strftime）
    if group_by == 'hour':
        time_format = func.strftime('%Y-%m-%d %H:00:00', Commit.commit_date)
    elif group_by == 'day':
        time_format = func.strftime('%Y-%m-%d', Commit.commit_date)
    elif group_by == 'week':
        time_format = func.strftime('%Y-%W', Commit.commit_date)
    else:  # month
        time_format = func.strftime('%Y-%m', Commit.commit_date)
    
    results = query.with_entities(
        time_format.label('time_period'),
        func.count(Commit.id).label('commits_count'),
        func.sum(Commit.additions).label('additions'),
        func.sum(Commit.deletions).label('deletions')
    ).group_by(
        time_format
    ).order_by(
        time_format
    ).all()
    
    items = []
    for result in results:
        item = {
            'time_period': result.time_period,
            'commits_count': result.commits_count,
            'additions': result.additions or 0,
            'deletions': result.deletions or 0,
            'net_changes': (result.additions or 0) - (result.deletions or 0)
        }
        items.append(item)
    
    return {
        'items': items,
        'group_by': group_by
    }

def get_merge_requests_by_author(query):
    """
    按作者分组获取合并请求统计
    
    Args:
        query: SQLAlchemy查询对象
    
    Returns:
        dict: 统计数据
    """
    results = query.with_entities(
        MergeRequest.author_name,
        MergeRequest.author_email,
        func.count(MergeRequest.id).label('mrs_count'),
        func.sum(MergeRequest.additions).label('additions'),
        func.sum(MergeRequest.deletions).label('deletions'),
        func.sum(MergeRequest.commits_count).label('commits_count')
    ).group_by(
        MergeRequest.author_name,
        MergeRequest.author_email
    ).order_by(
        func.count(MergeRequest.id).desc()
    ).all()
    
    items = []
    for result in results:
        item = {
            'author_name': result.author_name,
            'author_email': result.author_email,
            'merge_requests_count': result.mrs_count,
            'additions': result.additions or 0,
            'deletions': result.deletions or 0,
            'commits_count': result.commits_count or 0,
            'net_changes': (result.additions or 0) - (result.deletions or 0)
        }
        items.append(item)
    
    return {'items': items}

def get_merge_requests_by_state(query):
    """
    按状态分组获取合并请求统计
    
    Args:
        query: SQLAlchemy查询对象
    
    Returns:
        dict: 统计数据
    """
    results = query.with_entities(
        MergeRequest.state,
        func.count(MergeRequest.id).label('count')
    ).group_by(
        MergeRequest.state
    ).all()
    
    items = []
    for result in results:
        item = {
            'state': result.state,
            'count': result.count
        }
        items.append(item)
    
    return {'items': items}

def get_merge_requests_by_time(query, group_by, start_date, end_date):
    """
    按时间分组获取合并请求统计
    
    Args:
        query: SQLAlchemy查询对象
        group_by (str): 分组方式
        start_date (datetime): 开始日期
        end_date (datetime): 结束日期
    
    Returns:
        dict: 统计数据
    """
    # 根据分组方式选择时间格式（SQLite使用strftime）
    if group_by == 'day':
        time_format = func.strftime('%Y-%m-%d', MergeRequest.created_at_remote)
    elif group_by == 'week':
        time_format = func.strftime('%Y-%W', MergeRequest.created_at_remote)
    else:  # month
        time_format = func.strftime('%Y-%m', MergeRequest.created_at_remote)
    
    results = query.with_entities(
        time_format.label('time_period'),
        func.count(MergeRequest.id).label('mrs_count'),
        func.sum(MergeRequest.additions).label('additions'),
        func.sum(MergeRequest.deletions).label('deletions')
    ).group_by(
        time_format
    ).order_by(
        time_format
    ).all()
    
    items = []
    for result in results:
        item = {
            'time_period': result.time_period,
            'merge_requests_count': result.mrs_count,
            'additions': result.additions or 0,
            'deletions': result.deletions or 0,
            'net_changes': (result.additions or 0) - (result.deletions or 0)
        }
        items.append(item)
    
    return {
        'items': items,
        'group_by': group_by
    }

def calculate_efficiency_score_by_author(repo_ids, start_date, end_date, config):
    """
    按作者计算效率评分
    
    Args:
        repo_ids (list): 仓库ID列表
        start_date (datetime): 开始日期
        end_date (datetime): 结束日期
        config (dict): 评分配置
    
    Returns:
        list: 评分数据
    """
    # 获取提交统计
    commits_stats = db.session.query(
        Commit.author_name,
        Commit.author_email,
        func.count(Commit.id).label('commits_count'),
        func.sum(Commit.additions).label('additions'),
        func.sum(Commit.deletions).label('deletions'),
        func.sum(Commit.files_changed).label('files_changed')
    ).filter(
        Commit.repository_id.in_(repo_ids),
        Commit.commit_date >= start_date,
        Commit.commit_date <= end_date
    ).group_by(
        Commit.author_name,
        Commit.author_email
    ).all()
    
    # 获取合并请求统计
    mrs_stats = db.session.query(
        MergeRequest.author_name,
        MergeRequest.author_email,
        func.count(MergeRequest.id).label('mrs_count'),
        func.sum(MergeRequest.additions).label('additions'),
        func.sum(MergeRequest.deletions).label('deletions')
    ).filter(
        MergeRequest.repository_id.in_(repo_ids),
        MergeRequest.created_at_remote >= start_date,
        MergeRequest.created_at_remote <= end_date
    ).group_by(
        MergeRequest.author_name,
        MergeRequest.author_email
    ).all()
    
    # 合并统计数据
    author_stats = defaultdict(lambda: {
        'commits_count': 0,
        'mrs_count': 0,
        'additions': 0,
        'deletions': 0,
        'files_changed': 0
    })
    
    for stat in commits_stats:
        key = (stat.author_name, stat.author_email)
        author_stats[key]['commits_count'] = stat.commits_count
        author_stats[key]['additions'] += stat.additions or 0
        author_stats[key]['deletions'] += stat.deletions or 0
        author_stats[key]['files_changed'] += stat.files_changed or 0
    
    for stat in mrs_stats:
        key = (stat.author_name, stat.author_email)
        author_stats[key]['mrs_count'] = stat.mrs_count
        author_stats[key]['additions'] += stat.additions or 0
        author_stats[key]['deletions'] += stat.deletions or 0
    
    # 计算效率评分
    score_items = []
    for (author_name, author_email), stats in author_stats.items():
        score = (
            stats['commits_count'] * config['commit_weight'] +
            stats['mrs_count'] * config['merge_request_weight'] +
            stats['additions'] * config['addition_weight'] +
            stats['deletions'] * config['deletion_weight'] +
            stats['files_changed'] * config['file_change_weight']
        )
        
        score_items.append({
            'author_name': author_name,
            'author_email': author_email,
            'score': round(score, 2),
            'stats': stats
        })
    
    # 按评分排序
    score_items.sort(key=lambda x: x['score'], reverse=True)
    
    return score_items

def calculate_efficiency_score_by_repository(repo_ids, start_date, end_date, config):
    """
    按仓库计算效率评分
    
    Args:
        repo_ids (list): 仓库ID列表
        start_date (datetime): 开始日期
        end_date (datetime): 结束日期
        config (dict): 评分配置
    
    Returns:
        list: 评分数据
    """
    score_items = []
    
    for repo_id in repo_ids:
        # 获取仓库信息
        repository = Repository.query.get(repo_id)
        if not repository:
            continue
        
        # 获取提交统计
        commits_stats = db.session.query(
            func.count(Commit.id).label('commits_count'),
            func.sum(Commit.additions).label('additions'),
            func.sum(Commit.deletions).label('deletions'),
            func.sum(Commit.files_changed).label('files_changed')
        ).filter(
            Commit.repository_id == repo_id,
            Commit.commit_date >= start_date,
            Commit.commit_date <= end_date
        ).first()
        
        # 获取合并请求统计
        mrs_stats = db.session.query(
            func.count(MergeRequest.id).label('mrs_count'),
            func.sum(MergeRequest.additions).label('additions'),
            func.sum(MergeRequest.deletions).label('deletions')
        ).filter(
            MergeRequest.repository_id == repo_id,
            MergeRequest.created_at_remote >= start_date,
            MergeRequest.created_at_remote <= end_date
        ).first()
        
        # 计算评分
        stats = {
            'commits_count': commits_stats.commits_count or 0,
            'mrs_count': mrs_stats.mrs_count or 0,
            'additions': (commits_stats.additions or 0) + (mrs_stats.additions or 0),
            'deletions': (commits_stats.deletions or 0) + (mrs_stats.deletions or 0),
            'files_changed': commits_stats.files_changed or 0
        }
        
        score = (
            stats['commits_count'] * config['commit_weight'] +
            stats['mrs_count'] * config['merge_request_weight'] +
            stats['additions'] * config['addition_weight'] +
            stats['deletions'] * config['deletion_weight'] +
            stats['files_changed'] * config['file_change_weight']
        )
        
        score_items.append({
            'repository_id': repo_id,
            'repository_name': repository.name,
            'score': round(score, 2),
            'stats': stats
        })
    
    # 按评分排序
    score_items.sort(key=lambda x: x['score'], reverse=True)
    
    return score_items

def get_commits_time_distribution(repo_ids, start_date, end_date, dimension):
    """
    获取提交时间分布
    
    Args:
        repo_ids (list): 仓库ID列表
        start_date (datetime): 开始日期
        end_date (datetime): 结束日期
        dimension (str): 时间维度
    
    Returns:
        dict: 时间分布数据
    """
    if dimension == 'hour':
        time_extract = func.strftime('%H', Commit.commit_date)
        labels = [f"{i:02d}:00" for i in range(24)]
    elif dimension == 'weekday':
        time_extract = func.strftime('%w', Commit.commit_date)
        labels = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    else:  # month
        time_extract = func.strftime('%m', Commit.commit_date)
        labels = [f"{i}月" for i in range(1, 13)]
    
    results = db.session.query(
        time_extract.label('time_unit'),
        func.count(Commit.id).label('count')
    ).filter(
        Commit.repository_id.in_(repo_ids),
        Commit.commit_date >= start_date,
        Commit.commit_date <= end_date
    ).group_by(
        time_extract
    ).all()
    
    # 构建分布数据
    distribution = [0] * len(labels)
    for result in results:
        time_unit = result.time_unit
        if dimension == 'hour':
            index = int(time_unit)
            distribution[index] = result.count
        elif dimension == 'weekday':
            # SQLite的strftime('%w')返回0-6，对应周日-周六
            index = int(time_unit)
            distribution[index] = result.count
        else:  # month
            index = int(time_unit) - 1
            distribution[index] = result.count
    
    return {
        'distribution': [
            {'label': labels[i], 'value': distribution[i]}
            for i in range(len(labels))
        ],
        'dimension': dimension,
        'summary': {
            'total_commits': sum(distribution),
            'peak_time': labels[distribution.index(max(distribution))] if distribution else None
        }
    }

def get_merge_requests_time_distribution(repo_ids, start_date, end_date, dimension):
    """
    获取合并请求时间分布
    
    Args:
        repo_ids (list): 仓库ID列表
        start_date (datetime): 开始日期
        end_date (datetime): 结束日期
        dimension (str): 时间维度
    
    Returns:
        dict: 时间分布数据
    """
    if dimension == 'hour':
        time_extract = func.strftime('%H', MergeRequest.created_at_remote)
        labels = [f"{i:02d}:00" for i in range(24)]
    elif dimension == 'weekday':
        time_extract = func.strftime('%w', MergeRequest.created_at_remote)
        labels = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    else:  # month
        time_extract = func.strftime('%m', MergeRequest.created_at_remote)
        labels = [f"{i}月" for i in range(1, 13)]
    
    results = db.session.query(
        time_extract.label('time_unit'),
        func.count(MergeRequest.id).label('count')
    ).filter(
        MergeRequest.repository_id.in_(repo_ids),
        MergeRequest.created_at_remote >= start_date,
        MergeRequest.created_at_remote <= end_date
    ).group_by(
        time_extract
    ).all()
    
    # 构建分布数据
    distribution = [0] * len(labels)
    for result in results:
        time_unit = result.time_unit
        if dimension == 'hour':
            index = int(time_unit)
            distribution[index] = result.count
        elif dimension == 'weekday':
            # SQLite的strftime('%w')返回0-6，对应周日-周六
            index = int(time_unit)
            distribution[index] = result.count
        else:  # month
            index = int(time_unit) - 1
            distribution[index] = result.count
    
    return {
        'distribution': [
            {'label': labels[i], 'value': distribution[i]}
            for i in range(len(labels))
        ],
        'dimension': dimension,
        'summary': {
            'total_merge_requests': sum(distribution),
            'peak_time': labels[distribution.index(max(distribution))] if distribution else None
        }
    }