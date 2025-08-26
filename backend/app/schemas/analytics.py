from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime


class PeriodInfo(BaseModel):
    """时间段信息"""
    start_date: str = Field(..., description="开始日期")
    end_date: str = Field(..., description="结束日期")


class CodeChanges(BaseModel):
    """代码变更统计"""
    additions: int = Field(0, description="新增行数")
    deletions: int = Field(0, description="删除行数")
    net_changes: int = Field(0, description="净变更行数")


class AnalyticsOverviewResponse(BaseModel):
    """分析概览响应"""
    repositories_count: int = Field(..., description="仓库数量")
    commits_count: int = Field(..., description="提交数量")
    merge_requests_count: int = Field(..., description="合并请求数量")
    active_contributors: int = Field(..., description="活跃贡献者数量")
    code_changes: CodeChanges = Field(..., description="代码变更统计")
    period: PeriodInfo = Field(..., description="统计时间段")


class CommitDataPoint(BaseModel):
    """提交数据点"""
    key: str = Field(..., description="分组键值")
    commits_count: int = Field(..., description="提交数量")
    authors_count: int = Field(..., description="作者数量")


class CommitsAnalyticsResponse(BaseModel):
    """提交分析响应"""
    total_commits: int = Field(..., description="总提交数")
    period: PeriodInfo = Field(..., description="统计时间段")
    group_by: str = Field(..., description="分组方式")
    data: List[CommitDataPoint] = Field(..., description="分组数据")


class MergeRequestDataPoint(BaseModel):
    """合并请求数据点"""
    date: str = Field(..., description="日期")
    count: int = Field(..., description="总数量")
    opened: int = Field(0, description="打开数量")
    merged: int = Field(0, description="合并数量")
    closed: int = Field(0, description="关闭数量")


class MergeRequestsAnalyticsResponse(BaseModel):
    """合并请求分析响应"""
    total_merge_requests: int = Field(..., description="总合并请求数")
    period: PeriodInfo = Field(..., description="统计时间段")
    status_breakdown: Dict[str, int] = Field(..., description="状态分布")
    data: List[MergeRequestDataPoint] = Field(..., description="按日期分组数据")


class ContributorStatsResponse(BaseModel):
    """贡献者统计响应"""
    author_email: str = Field(..., description="作者邮箱")
    author_name: str = Field(..., description="作者姓名")
    commits_count: int = Field(..., description="提交数量")
    merge_requests_count: int = Field(0, description="合并请求数量")


class EfficiencyMetrics(BaseModel):
    """效率指标"""
    commits_per_day: float = Field(0.0, description="日均提交数")
    lines_per_commit: float = Field(0.0, description="每次提交平均行数")
    merge_request_frequency: float = Field(0.0, description="合并请求频率")
    code_review_time: float = Field(0.0, description="代码审查平均时间(小时)")


class EfficiencyScoreResponse(BaseModel):
    """效率评分响应"""
    overall_score: float = Field(..., description="总体评分 (0-100)")
    metrics: EfficiencyMetrics = Field(..., description="效率指标")
    period: PeriodInfo = Field(..., description="统计时间段")
    recommendations: List[str] = Field([], description="改进建议")


class RepositoryActivityResponse(BaseModel):
    """仓库活跃度响应"""
    repository_id: int = Field(..., description="仓库ID")
    repository_name: str = Field(..., description="仓库名称")
    commits_count: int = Field(..., description="提交数量")
    merge_requests_count: int = Field(..., description="合并请求数量")
    contributors_count: int = Field(..., description="贡献者数量")
    last_activity_date: Optional[datetime] = Field(None, description="最后活跃时间")
    activity_score: float = Field(0.0, description="活跃度评分")


class TrendDataPoint(BaseModel):
    """趋势数据点"""
    date: str = Field(..., description="日期")
    value: float = Field(..., description="数值")
    change_rate: Optional[float] = Field(None, description="变化率")


class TrendAnalysisResponse(BaseModel):
    """趋势分析响应"""
    metric_name: str = Field(..., description="指标名称")
    period: PeriodInfo = Field(..., description="统计时间段")
    trend_direction: str = Field(..., description="趋势方向 (up/down/stable)")
    average_value: float = Field(..., description="平均值")
    data: List[TrendDataPoint] = Field(..., description="趋势数据")


class ComparisonPeriod(BaseModel):
    """对比时间段"""
    label: str = Field(..., description="时间段标签")
    commits_count: int = Field(..., description="提交数量")
    merge_requests_count: int = Field(..., description="合并请求数量")
    contributors_count: int = Field(..., description="贡献者数量")
    code_changes: CodeChanges = Field(..., description="代码变更")


class PeriodComparisonResponse(BaseModel):
    """时间段对比响应"""
    current_period: ComparisonPeriod = Field(..., description="当前时间段")
    previous_period: ComparisonPeriod = Field(..., description="上一时间段")
    growth_rates: Dict[str, float] = Field(..., description="增长率")


class HeatmapDataPoint(BaseModel):
    """热力图数据点"""
    date: str = Field(..., description="日期")
    hour: int = Field(..., description="小时 (0-23)")
    value: int = Field(..., description="数值")


class ActivityHeatmapResponse(BaseModel):
    """活跃度热力图响应"""
    period: PeriodInfo = Field(..., description="统计时间段")
    data: List[HeatmapDataPoint] = Field(..., description="热力图数据")
    max_value: int = Field(..., description="最大值")
    total_activities: int = Field(..., description="总活动数")