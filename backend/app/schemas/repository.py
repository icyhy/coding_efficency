from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


class RepositoryBase(BaseModel):
    """仓库基础模式"""
    name: str = Field(..., min_length=1, max_length=255, description="仓库名称")
    url: str = Field(..., description="仓库URL")
    platform: str = Field(default="yunxiao", description="平台类型")
    project_id: Optional[str] = Field(None, description="项目ID")


class RepositoryCreate(RepositoryBase):
    """创建仓库模式"""
    api_key: str = Field(..., min_length=1, description="API密钥")


class RepositoryUpdate(BaseModel):
    """更新仓库模式"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="仓库名称")
    api_key: Optional[str] = Field(None, min_length=1, description="API密钥")
    is_active: Optional[bool] = Field(None, description="是否激活")
    is_tracked: Optional[bool] = Field(None, description="是否跟踪")


class RepositoryStats(BaseModel):
    """仓库统计信息模式"""
    commits_count: int = Field(default=0, description="提交数量")
    merge_requests_count: int = Field(default=0, description="合并请求数量")
    last_sync_at: Optional[datetime] = Field(None, description="最后同步时间")


class RepositoryResponse(RepositoryBase):
    """仓库响应模式"""
    id: int
    user_id: int
    is_active: bool
    is_tracked: bool
    sync_status: str
    last_sync_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    stats: Optional[RepositoryStats] = None
    
    class Config:
        from_attributes = True


class RepositoryListResponse(BaseModel):
    """仓库列表响应模式"""
    items: list[RepositoryResponse]
    total: int
    page: int
    per_page: int
    pages: int


class CommitBase(BaseModel):
    """提交基础模式"""
    commit_hash: str = Field(..., description="提交哈希")
    author_name: str = Field(..., description="作者姓名")
    author_email: str = Field(..., description="作者邮箱")
    message: str = Field(..., description="提交消息")
    commit_date: datetime = Field(..., description="提交时间")


class CommitResponse(CommitBase):
    """提交响应模式"""
    id: int
    repository_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class MergeRequestBase(BaseModel):
    """合并请求基础模式"""
    mr_id: str = Field(..., description="合并请求ID")
    title: str = Field(..., description="标题")
    description: Optional[str] = Field(None, description="描述")
    author_name: str = Field(..., description="作者姓名")
    author_email: str = Field(..., description="作者邮箱")
    status: str = Field(..., description="状态")
    created_date: datetime = Field(..., description="创建时间")
    updated_date: Optional[datetime] = Field(None, description="更新时间")
    merged_date: Optional[datetime] = Field(None, description="合并时间")


class MergeRequestResponse(MergeRequestBase):
    """合并请求响应模式"""
    id: int
    repository_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True