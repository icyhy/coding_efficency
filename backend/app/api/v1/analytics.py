from typing import Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, distinct
from datetime import datetime, timedelta

from app.core.database import get_async_session
from app.core.deps import get_current_active_user
from app.models.user import User
from app.models.repository import Repository
from app.models.commit import Commit
from app.models.merge_request import MergeRequest
from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    CommitsAnalyticsResponse,
    MergeRequestsAnalyticsResponse,
    EfficiencyScoreResponse,
    ContributorStatsResponse
)

router = APIRouter()


def parse_date_range(start_date: Optional[str], end_date: Optional[str], days: int = 30) -> tuple[datetime, datetime]:
    """
    解析日期范围
    """
    if start_date and end_date:
        try:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            return start, end
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="日期格式不正确，请使用 YYYY-MM-DD 格式"
            )
    else:
        # 默认使用最近30天
        end = datetime.utcnow()
        start = end - timedelta(days=days)
        return start, end


@router.get("/overview", response_model=AnalyticsOverviewResponse)
async def get_analytics_overview(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    repository_ids: Optional[str] = Query(None, description="仓库ID列表，逗号分隔")
) -> Any:
    """
    获取分析概览
    """
    # 解析日期范围
    start_dt, end_dt = parse_date_range(start_date, end_date)
    
    # 解析仓库ID列表
    repo_ids = None
    if repository_ids:
        try:
            repo_ids = [int(id.strip()) for id in repository_ids.split(',') if id.strip()]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="仓库ID格式不正确"
            )
    
    # 获取用户的仓库
    repositories_query = select(Repository).where(
        and_(
            Repository.user_id == current_user.id,
            Repository.is_active == True
        )
    )
    
    if repo_ids:
        repositories_query = repositories_query.where(Repository.id.in_(repo_ids))
    
    result = await db.execute(repositories_query)
    repositories = result.scalars().all()
    repo_ids_list = [repo.id for repo in repositories]
    
    if not repo_ids_list:
        return AnalyticsOverviewResponse(
            repositories_count=0,
            commits_count=0,
            merge_requests_count=0,
            active_contributors=0,
            code_changes={
                'additions': 0,
                'deletions': 0,
                'net_changes': 0
            },
            period={
                'start_date': start_dt.isoformat() + 'Z',
                'end_date': end_dt.isoformat() + 'Z'
            }
        )
    
    # 统计提交数据
    commits_stats_query = select(
        func.count(Commit.id).label('count'),
        func.count(distinct(Commit.author_email)).label('contributors')
    ).where(
        and_(
            Commit.repository_id.in_(repo_ids_list),
            Commit.commit_date >= start_dt,
            Commit.commit_date <= end_dt
        )
    )
    
    commits_result = await db.execute(commits_stats_query)
    commits_stats = commits_result.first()
    
    # 统计合并请求数据
    mrs_stats_query = select(
        func.count(MergeRequest.id).label('count')
    ).where(
        and_(
            MergeRequest.repository_id.in_(repo_ids_list),
            MergeRequest.created_date >= start_dt,
            MergeRequest.created_date <= end_dt
        )
    )
    
    mrs_result = await db.execute(mrs_stats_query)
    mrs_stats = mrs_result.first()
    
    # 构建响应数据
    overview_data = AnalyticsOverviewResponse(
        repositories_count=len(repositories),
        commits_count=commits_stats.count or 0,
        merge_requests_count=mrs_stats.count or 0,
        active_contributors=commits_stats.contributors or 0,
        code_changes={
            'additions': 0,  # 需要添加字段到模型中
            'deletions': 0,  # 需要添加字段到模型中
            'net_changes': 0
        },
        period={
            'start_date': start_dt.isoformat() + 'Z',
            'end_date': end_dt.isoformat() + 'Z'
        }
    )
    
    return overview_data


@router.get("/commits", response_model=CommitsAnalyticsResponse)
async def get_commits_analytics(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    repository_ids: Optional[str] = Query(None, description="仓库ID列表"),
    group_by: str = Query("day", description="分组方式 (hour, day, week, month, author)"),
    author_email: Optional[str] = Query(None, description="作者邮箱筛选")
) -> Any:
    """
    获取提交统计分析
    """
    # 解析日期范围
    start_dt, end_dt = parse_date_range(start_date, end_date)
    
    # 解析仓库ID列表
    repo_ids = None
    if repository_ids:
        try:
            repo_ids = [int(id.strip()) for id in repository_ids.split(',') if id.strip()]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="仓库ID格式不正确"
            )
    
    # 获取用户的仓库
    repositories_query = select(Repository).where(
        and_(
            Repository.user_id == current_user.id,
            Repository.is_active == True
        )
    )
    
    if repo_ids:
        repositories_query = repositories_query.where(Repository.id.in_(repo_ids))
    
    result = await db.execute(repositories_query)
    repositories = result.scalars().all()
    repo_ids_list = [repo.id for repo in repositories]
    
    if not repo_ids_list:
        return CommitsAnalyticsResponse(
            total_commits=0,
            period={
                'start_date': start_dt.isoformat() + 'Z',
                'end_date': end_dt.isoformat() + 'Z'
            },
            group_by=group_by,
            data=[]
        )
    
    # 构建查询条件
    query_conditions = [
        Commit.repository_id.in_(repo_ids_list),
        Commit.commit_date >= start_dt,
        Commit.commit_date <= end_dt
    ]
    
    if author_email:
        query_conditions.append(Commit.author_email == author_email)
    
    # 获取提交数据
    commits_query = select(Commit).where(and_(*query_conditions)).order_by(Commit.commit_date.desc())
    
    commits_result = await db.execute(commits_query)
    commits = commits_result.scalars().all()
    
    # 根据group_by参数处理数据
    grouped_data = {}
    
    for commit in commits:
        if group_by == "author":
            key = commit.author_email
        elif group_by == "day":
            key = commit.commit_date.strftime("%Y-%m-%d")
        elif group_by == "week":
            key = commit.commit_date.strftime("%Y-W%U")
        elif group_by == "month":
            key = commit.commit_date.strftime("%Y-%m")
        elif group_by == "hour":
            key = commit.commit_date.strftime("%Y-%m-%d %H:00")
        else:
            key = commit.commit_date.strftime("%Y-%m-%d")
        
        if key not in grouped_data:
            grouped_data[key] = {
                'key': key,
                'commits_count': 0,
                'authors': set()
            }
        
        grouped_data[key]['commits_count'] += 1
        grouped_data[key]['authors'].add(commit.author_email)
    
    # 转换为列表格式
    data_list = []
    for key, data in grouped_data.items():
        data_list.append({
            'key': key,
            'commits_count': data['commits_count'],
            'authors_count': len(data['authors'])
        })
    
    # 按key排序
    data_list.sort(key=lambda x: x['key'])
    
    return CommitsAnalyticsResponse(
        total_commits=len(commits),
        period={
            'start_date': start_dt.isoformat() + 'Z',
            'end_date': end_dt.isoformat() + 'Z'
        },
        group_by=group_by,
        data=data_list
    )


@router.get("/merge-requests", response_model=MergeRequestsAnalyticsResponse)
async def get_merge_requests_analytics(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    repository_ids: Optional[str] = Query(None, description="仓库ID列表"),
    status_filter: Optional[str] = Query(None, description="状态筛选")
) -> Any:
    """
    获取合并请求统计分析
    """
    # 解析日期范围
    start_dt, end_dt = parse_date_range(start_date, end_date)
    
    # 解析仓库ID列表
    repo_ids = None
    if repository_ids:
        try:
            repo_ids = [int(id.strip()) for id in repository_ids.split(',') if id.strip()]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="仓库ID格式不正确"
            )
    
    # 获取用户的仓库
    repositories_query = select(Repository).where(
        and_(
            Repository.user_id == current_user.id,
            Repository.is_active == True
        )
    )
    
    if repo_ids:
        repositories_query = repositories_query.where(Repository.id.in_(repo_ids))
    
    result = await db.execute(repositories_query)
    repositories = result.scalars().all()
    repo_ids_list = [repo.id for repo in repositories]
    
    if not repo_ids_list:
        return MergeRequestsAnalyticsResponse(
            total_merge_requests=0,
            period={
                'start_date': start_dt.isoformat() + 'Z',
                'end_date': end_dt.isoformat() + 'Z'
            },
            status_breakdown={},
            data=[]
        )
    
    # 构建查询条件
    query_conditions = [
        MergeRequest.repository_id.in_(repo_ids_list),
        MergeRequest.created_date >= start_dt,
        MergeRequest.created_date <= end_dt
    ]
    
    if status_filter:
        query_conditions.append(MergeRequest.status == status_filter)
    
    # 获取合并请求数据
    mrs_query = select(MergeRequest).where(and_(*query_conditions)).order_by(MergeRequest.created_date.desc())
    
    mrs_result = await db.execute(mrs_query)
    merge_requests = mrs_result.scalars().all()
    
    # 统计状态分布
    status_breakdown = {}
    daily_data = {}
    
    for mr in merge_requests:
        # 状态统计
        status = mr.status or 'unknown'
        status_breakdown[status] = status_breakdown.get(status, 0) + 1
        
        # 按日期分组
        date_key = mr.created_date.strftime("%Y-%m-%d")
        if date_key not in daily_data:
            daily_data[date_key] = {
                'date': date_key,
                'count': 0,
                'opened': 0,
                'merged': 0,
                'closed': 0
            }
        
        daily_data[date_key]['count'] += 1
        if status == 'opened':
            daily_data[date_key]['opened'] += 1
        elif status == 'merged':
            daily_data[date_key]['merged'] += 1
        elif status == 'closed':
            daily_data[date_key]['closed'] += 1
    
    # 转换为列表格式并排序
    data_list = list(daily_data.values())
    data_list.sort(key=lambda x: x['date'])
    
    return MergeRequestsAnalyticsResponse(
        total_merge_requests=len(merge_requests),
        period={
            'start_date': start_dt.isoformat() + 'Z',
            'end_date': end_dt.isoformat() + 'Z'
        },
        status_breakdown=status_breakdown,
        data=data_list
    )


@router.get("/contributors", response_model=List[ContributorStatsResponse])
async def get_contributors_stats(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    repository_ids: Optional[str] = Query(None, description="仓库ID列表"),
    limit: int = Query(10, ge=1, le=100, description="返回数量限制")
) -> Any:
    """
    获取贡献者统计
    """
    # 解析日期范围
    start_dt, end_dt = parse_date_range(start_date, end_date)
    
    # 解析仓库ID列表
    repo_ids = None
    if repository_ids:
        try:
            repo_ids = [int(id.strip()) for id in repository_ids.split(',') if id.strip()]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="仓库ID格式不正确"
            )
    
    # 获取用户的仓库
    repositories_query = select(Repository).where(
        and_(
            Repository.user_id == current_user.id,
            Repository.is_active == True
        )
    )
    
    if repo_ids:
        repositories_query = repositories_query.where(Repository.id.in_(repo_ids))
    
    result = await db.execute(repositories_query)
    repositories = result.scalars().all()
    repo_ids_list = [repo.id for repo in repositories]
    
    if not repo_ids_list:
        return []
    
    # 获取提交统计
    commits_query = select(
        Commit.author_email,
        Commit.author_name,
        func.count(Commit.id).label('commits_count')
    ).where(
        and_(
            Commit.repository_id.in_(repo_ids_list),
            Commit.commit_date >= start_dt,
            Commit.commit_date <= end_dt
        )
    ).group_by(Commit.author_email, Commit.author_name).order_by(
        func.count(Commit.id).desc()
    ).limit(limit)
    
    commits_result = await db.execute(commits_query)
    contributors_data = commits_result.all()
    
    # 构建响应数据
    contributors_list = []
    for contributor in contributors_data:
        contributors_list.append(ContributorStatsResponse(
            author_email=contributor.author_email,
            author_name=contributor.author_name or contributor.author_email,
            commits_count=contributor.commits_count,
            merge_requests_count=0  # 可以添加MR统计
        ))
    
    return contributors_list