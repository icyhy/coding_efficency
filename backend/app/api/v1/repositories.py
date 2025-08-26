from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.core.database import get_async_session
from app.core.deps import get_current_active_user
from app.models.user import User
from app.models.repository import Repository
from app.models.commit import Commit
from app.models.merge_request import MergeRequest
from app.schemas.repository import (
    RepositoryCreate,
    RepositoryUpdate,
    RepositoryResponse,
    RepositoryListResponse,
    CommitResponse,
    MergeRequestResponse
)
from app.utils.validators import validate_git_url
import re

router = APIRouter()


@router.get("", response_model=RepositoryListResponse)
@router.get("/", response_model=RepositoryListResponse)
async def get_repositories(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(10, ge=1, le=100, description="每页数量"),
    platform: Optional[str] = Query(None, description="平台筛选"),
    is_active: Optional[bool] = Query(None, description="是否激活筛选"),
    search: Optional[str] = Query(None, description="搜索关键词")
) -> Any:
    """
    获取用户的仓库列表
    """
    # 构建查询
    query = select(Repository).where(Repository.user_id == current_user.id)
    
    # 平台筛选
    if platform:
        query = query.where(Repository.platform == platform)
    
    # 激活状态筛选
    if is_active is not None:
        query = query.where(Repository.is_active == is_active)
    
    # 搜索筛选
    if search:
        search_term = f"%{search.strip()}%"
        query = query.where(
            or_(
                Repository.name.ilike(search_term),
                Repository.url.ilike(search_term)
            )
        )
    
    # 排序
    query = query.order_by(Repository.created_at.desc())
    
    # 计算总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # 分页
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    
    result = await db.execute(query)
    repositories = result.scalars().all()
    
    # 获取统计信息
    repositories_data = []
    for repo in repositories:
        # 获取提交数量
        commits_count_query = select(func.count(Commit.id)).where(Commit.repository_id == repo.id)
        commits_result = await db.execute(commits_count_query)
        commits_count = commits_result.scalar() or 0
        
        # 获取合并请求数量
        mrs_count_query = select(func.count(MergeRequest.id)).where(MergeRequest.repository_id == repo.id)
        mrs_result = await db.execute(mrs_count_query)
        mrs_count = mrs_result.scalar() or 0
        
        repo_dict = repo.to_dict()
        repo_dict['stats'] = {
            'commits_count': commits_count,
            'merge_requests_count': mrs_count,
            'last_sync_at': repo.last_sync_at
        }
        repositories_data.append(RepositoryResponse(**repo_dict))
    
    pages = (total + per_page - 1) // per_page
    
    return RepositoryListResponse(
        items=repositories_data,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages
    )


@router.post("/", response_model=RepositoryResponse, status_code=status.HTTP_201_CREATED)
async def create_repository(
    repository_data: RepositoryCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    添加新仓库
    """
    # 验证URL格式
    url_validation = validate_git_url(repository_data.url)
    if not url_validation['valid']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=url_validation['message']
        )
    
    # 检查仓库是否已存在
    existing_repo_query = select(Repository).where(
        and_(
            Repository.user_id == current_user.id,
            Repository.url == repository_data.url
        )
    )
    result = await db.execute(existing_repo_query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该仓库已存在"
        )
    
    # 创建新仓库
    repository = Repository(
        user_id=current_user.id,
        name=repository_data.name,
        url=repository_data.url,
        platform=repository_data.platform,
        project_id=repository_data.project_id,
        api_key_encrypted=repository_data.api_key  # 暂时不加密存储
    )
    
    db.add(repository)
    await db.commit()
    await db.refresh(repository)
    
    # 返回仓库信息
    repo_dict = repository.to_dict()
    repo_dict['stats'] = {
        'commits_count': 0,
        'merge_requests_count': 0,
        'last_sync_at': None
    }
    
    return RepositoryResponse(**repo_dict)


@router.get("/{repo_id}", response_model=RepositoryResponse)
async def get_repository(
    repo_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    获取仓库详情
    """
    # 查找仓库
    query = select(Repository).where(
        and_(
            Repository.user_id == current_user.id,
            Repository.id == repo_id
        )
    )
    result = await db.execute(query)
    repository = result.scalar_one_or_none()
    
    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="仓库不存在"
        )
    
    # 获取统计信息
    commits_count_query = select(func.count(Commit.id)).where(Commit.repository_id == repo_id)
    commits_result = await db.execute(commits_count_query)
    commits_count = commits_result.scalar() or 0
    
    mrs_count_query = select(func.count(MergeRequest.id)).where(MergeRequest.repository_id == repo_id)
    mrs_result = await db.execute(mrs_count_query)
    mrs_count = mrs_result.scalar() or 0
    
    repo_dict = repository.to_dict()
    repo_dict['stats'] = {
        'commits_count': commits_count,
        'merge_requests_count': mrs_count,
        'last_sync_at': repository.last_sync_at
    }
    
    return RepositoryResponse(**repo_dict)


@router.put("/{repo_id}", response_model=RepositoryResponse)
async def update_repository(
    repo_id: int,
    repository_data: RepositoryUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    更新仓库信息
    """
    # 查找仓库
    query = select(Repository).where(
        and_(
            Repository.user_id == current_user.id,
            Repository.id == repo_id
        )
    )
    result = await db.execute(query)
    repository = result.scalar_one_or_none()
    
    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="仓库不存在"
        )
    
    # 更新字段
    update_data = repository_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "api_key":
            repository.api_key_encrypted = value  # 暂时不加密存储
        else:
            setattr(repository, field, value)
    
    await db.commit()
    await db.refresh(repository)
    
    # 获取统计信息
    commits_count_query = select(func.count(Commit.id)).where(Commit.repository_id == repo_id)
    commits_result = await db.execute(commits_count_query)
    commits_count = commits_result.scalar() or 0
    
    mrs_count_query = select(func.count(MergeRequest.id)).where(MergeRequest.repository_id == repo_id)
    mrs_result = await db.execute(mrs_count_query)
    mrs_count = mrs_result.scalar() or 0
    
    repo_dict = repository.to_dict()
    repo_dict['stats'] = {
        'commits_count': commits_count,
        'merge_requests_count': mrs_count,
        'last_sync_at': repository.last_sync_at
    }
    
    return RepositoryResponse(**repo_dict)


@router.delete("/{repo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_repository(
    repo_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user)
) -> None:
    """
    删除仓库
    """
    # 查找仓库
    query = select(Repository).where(
        and_(
            Repository.user_id == current_user.id,
            Repository.id == repo_id
        )
    )
    result = await db.execute(query)
    repository = result.scalar_one_or_none()
    
    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="仓库不存在"
        )
    
    await db.delete(repository)
    await db.commit()


@router.get("/{repo_id}/commits", response_model=list[CommitResponse])
async def get_repository_commits(
    repo_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(20, ge=1, le=100, description="每页数量")
) -> Any:
    """
    获取仓库的提交记录
    """
    # 验证仓库权限
    repo_query = select(Repository).where(
        and_(
            Repository.user_id == current_user.id,
            Repository.id == repo_id
        )
    )
    repo_result = await db.execute(repo_query)
    if not repo_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="仓库不存在"
        )
    
    # 获取提交记录
    offset = (page - 1) * per_page
    commits_query = select(Commit).where(
        Commit.repository_id == repo_id
    ).order_by(Commit.commit_date.desc()).offset(offset).limit(per_page)
    
    result = await db.execute(commits_query)
    commits = result.scalars().all()
    
    return [CommitResponse(**commit.to_dict()) for commit in commits]


@router.get("/{repo_id}/merge-requests", response_model=list[MergeRequestResponse])
async def get_repository_merge_requests(
    repo_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(20, ge=1, le=100, description="每页数量"),
    status_filter: Optional[str] = Query(None, description="状态筛选")
) -> Any:
    """
    获取仓库的合并请求
    """
    # 验证仓库权限
    repo_query = select(Repository).where(
        and_(
            Repository.user_id == current_user.id,
            Repository.id == repo_id
        )
    )
    repo_result = await db.execute(repo_query)
    if not repo_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="仓库不存在"
        )
    
    # 构建查询
    query = select(MergeRequest).where(MergeRequest.repository_id == repo_id)
    
    if status_filter:
        query = query.where(MergeRequest.status == status_filter)
    
    # 分页
    offset = (page - 1) * per_page
    query = query.order_by(MergeRequest.created_date.desc()).offset(offset).limit(per_page)
    
    result = await db.execute(query)
    merge_requests = result.scalars().all()
    
    return [MergeRequestResponse(**mr.to_dict()) for mr in merge_requests]