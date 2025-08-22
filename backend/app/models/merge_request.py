# -*- coding: utf-8 -*-
"""
合并请求数据模型
定义Git合并请求表结构和相关方法
"""

from datetime import datetime
from app import db
from sqlalchemy import func

class MergeRequest(db.Model):
    """
    合并请求模型类
    
    Attributes:
        id (int): 记录唯一标识
        repository_id (int): 所属仓库ID
        mr_id (str): 合并请求ID
        title (str): 合并请求标题
        description (str): 合并请求描述
        author_name (str): 创建者姓名
        author_email (str): 创建者邮箱
        target_branch (str): 目标分支
        source_branch (str): 源分支
        state (str): 状态 (opened, merged, closed)
        additions (int): 新增行数
        deletions (int): 删除行数
        files_changed (int): 修改文件数
        commits_count (int): 包含提交数
        created_at_remote (datetime): 远程创建时间
        updated_at_remote (datetime): 远程更新时间
        merged_at (datetime): 合并时间
        created_at (datetime): 本地记录创建时间
        updated_at (datetime): 本地记录更新时间
    """
    
    __tablename__ = 'merge_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    repository_id = db.Column(db.Integer, db.ForeignKey('repositories.id'), nullable=False, index=True)
    mr_id = db.Column(db.String(50), nullable=False, index=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    author_name = db.Column(db.String(255), nullable=False, index=True)
    author_email = db.Column(db.String(255), nullable=False, index=True)
    target_branch = db.Column(db.String(255), nullable=False)
    source_branch = db.Column(db.String(255), nullable=False)
    state = db.Column(db.String(20), nullable=False, default='opened', index=True)
    additions = db.Column(db.Integer, default=0, nullable=False)
    deletions = db.Column(db.Integer, default=0, nullable=False)
    files_changed = db.Column(db.Integer, default=0, nullable=False)
    commits_count = db.Column(db.Integer, default=0, nullable=False)
    created_at_remote = db.Column(db.DateTime, nullable=False, index=True)
    updated_at_remote = db.Column(db.DateTime, nullable=False)
    merged_at = db.Column(db.DateTime, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 复合索引
    __table_args__ = (
        db.Index('idx_repo_mr_id', 'repository_id', 'mr_id'),
        db.Index('idx_repo_author_state', 'repository_id', 'author_email', 'state'),
        db.Index('idx_repo_merged_at', 'repository_id', 'merged_at'),
    )
    
    def __init__(self, repository_id, mr_id, title, author_name, author_email,
                 target_branch, source_branch, created_at_remote, updated_at_remote,
                 description=None, state='opened', additions=0, deletions=0, 
                 files_changed=0, commits_count=0, merged_at=None):
        """
        初始化合并请求实例
        
        Args:
            repository_id (int): 仓库ID
            mr_id (str): 合并请求ID
            title (str): 标题
            author_name (str): 作者姓名
            author_email (str): 作者邮箱
            target_branch (str): 目标分支
            source_branch (str): 源分支
            created_at_remote (datetime): 远程创建时间
            updated_at_remote (datetime): 远程更新时间
            description (str): 描述
            state (str): 状态
            additions (int): 新增行数
            deletions (int): 删除行数
            files_changed (int): 修改文件数
            commits_count (int): 提交数
            merged_at (datetime): 合并时间
        """
        self.repository_id = repository_id
        self.mr_id = mr_id
        self.title = title
        self.description = description
        self.author_name = author_name
        self.author_email = author_email
        self.target_branch = target_branch
        self.source_branch = source_branch
        self.state = state
        self.additions = additions
        self.deletions = deletions
        self.files_changed = files_changed
        self.commits_count = commits_count
        self.created_at_remote = created_at_remote
        self.updated_at_remote = updated_at_remote
        self.merged_at = merged_at
    
    def to_dict(self):
        """
        将合并请求对象转换为字典
        
        Returns:
            dict: 合并请求信息字典
        """
        return {
            'id': self.id,
            'repository_id': self.repository_id,
            'mr_id': self.mr_id,
            'title': self.title,
            'description': self.description,
            'author_name': self.author_name,
            'author_email': self.author_email,
            'target_branch': self.target_branch,
            'source_branch': self.source_branch,
            'state': self.state,
            'additions': self.additions,
            'deletions': self.deletions,
            'files_changed': self.files_changed,
            'commits_count': self.commits_count,
            'total_changes': self.additions + self.deletions,
            'created_at_remote': self.created_at_remote.isoformat(),
            'updated_at_remote': self.updated_at_remote.isoformat(),
            'merged_at': self.merged_at.isoformat() if self.merged_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def update_info(self, **kwargs):
        """
        更新合并请求信息
        
        Args:
            **kwargs: 要更新的字段
        """
        allowed_fields = {
            'title', 'description', 'state', 'additions', 'deletions',
            'files_changed', 'commits_count', 'updated_at_remote', 'merged_at'
        }
        
        for key, value in kwargs.items():
            if key in allowed_fields and hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.utcnow()
    
    def calculate_score(self, add_weight=1.0, del_weight=0.5, file_weight=0.1, commit_weight=0.2):
        """
        计算合并请求贡献分数
        
        Args:
            add_weight (float): 新增代码权重
            del_weight (float): 删除代码权重
            file_weight (float): 文件数权重
            commit_weight (float): 提交数权重
        
        Returns:
            float: 贡献分数
        """
        return (
            self.additions * add_weight + 
            self.deletions * del_weight + 
            self.files_changed * file_weight +
            self.commits_count * commit_weight
        )
    
    @property
    def is_merged(self):
        """
        检查是否已合并
        
        Returns:
            bool: 是否已合并
        """
        return self.state == 'merged' and self.merged_at is not None
    
    @staticmethod
    def find_by_repository(repository_id, state=None, start_date=None, end_date=None, limit=None):
        """
        根据仓库ID查找合并请求
        
        Args:
            repository_id (int): 仓库ID
            state (str): 状态过滤
            start_date (datetime): 开始时间
            end_date (datetime): 结束时间
            limit (int): 限制数量
        
        Returns:
            list: 合并请求列表
        """
        query = MergeRequest.query.filter_by(repository_id=repository_id)
        
        if state:
            query = query.filter_by(state=state)
        
        if start_date:
            query = query.filter(MergeRequest.created_at_remote >= start_date)
        if end_date:
            query = query.filter(MergeRequest.created_at_remote <= end_date)
        
        query = query.order_by(MergeRequest.created_at_remote.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def find_by_author(repository_id, author_email, state=None, start_date=None, end_date=None):
        """
        根据作者查找合并请求
        
        Args:
            repository_id (int): 仓库ID
            author_email (str): 作者邮箱
            state (str): 状态过滤
            start_date (datetime): 开始时间
            end_date (datetime): 结束时间
        
        Returns:
            list: 合并请求列表
        """
        query = MergeRequest.query.filter_by(
            repository_id=repository_id,
            author_email=author_email
        )
        
        if state:
            query = query.filter_by(state=state)
        
        if start_date:
            query = query.filter(MergeRequest.created_at_remote >= start_date)
        if end_date:
            query = query.filter(MergeRequest.created_at_remote <= end_date)
        
        return query.order_by(MergeRequest.created_at_remote.desc()).all()
    
    @staticmethod
    def get_author_statistics(repository_id, state=None, start_date=None, end_date=None):
        """
        获取作者统计信息
        
        Args:
            repository_id (int): 仓库ID
            state (str): 状态过滤
            start_date (datetime): 开始时间
            end_date (datetime): 结束时间
        
        Returns:
            list: 作者统计列表
        """
        query = db.session.query(
            MergeRequest.author_name,
            MergeRequest.author_email,
            func.count(MergeRequest.id).label('mr_count'),
            func.sum(MergeRequest.additions).label('total_additions'),
            func.sum(MergeRequest.deletions).label('total_deletions'),
            func.sum(MergeRequest.files_changed).label('total_files'),
            func.sum(MergeRequest.commits_count).label('total_commits')
        ).filter_by(repository_id=repository_id)
        
        if state:
            query = query.filter_by(state=state)
        
        if start_date:
            query = query.filter(MergeRequest.created_at_remote >= start_date)
        if end_date:
            query = query.filter(MergeRequest.created_at_remote <= end_date)
        
        return query.group_by(
            MergeRequest.author_name, 
            MergeRequest.author_email
        ).order_by(
            func.count(MergeRequest.id).desc()
        ).all()
    
    @staticmethod
    def get_merged_statistics(repository_id, start_date=None, end_date=None):
        """
        获取已合并的统计信息
        
        Args:
            repository_id (int): 仓库ID
            start_date (datetime): 开始时间
            end_date (datetime): 结束时间
        
        Returns:
            list: 已合并统计列表
        """
        query = db.session.query(
            MergeRequest.author_name,
            MergeRequest.author_email,
            func.count(MergeRequest.id).label('merged_count'),
            func.sum(MergeRequest.additions).label('total_additions'),
            func.sum(MergeRequest.deletions).label('total_deletions'),
            func.sum(MergeRequest.files_changed).label('total_files')
        ).filter_by(repository_id=repository_id, state='merged')
        
        if start_date:
            query = query.filter(MergeRequest.merged_at >= start_date)
        if end_date:
            query = query.filter(MergeRequest.merged_at <= end_date)
        
        return query.group_by(
            MergeRequest.author_name, 
            MergeRequest.author_email
        ).order_by(
            func.sum(MergeRequest.additions + MergeRequest.deletions).desc()
        ).all()
    
    @staticmethod
    def exists_by_mr_id(repository_id, mr_id):
        """
        检查合并请求是否已存在
        
        Args:
            repository_id (int): 仓库ID
            mr_id (str): 合并请求ID
        
        Returns:
            MergeRequest or None: 合并请求对象或None
        """
        return MergeRequest.query.filter_by(
            repository_id=repository_id,
            mr_id=mr_id
        ).first()
    
    def __repr__(self):
        """
        合并请求对象的字符串表示
        
        Returns:
            str: 合并请求对象描述
        """
        return f'<MergeRequest {self.mr_id} - {self.title[:50]} by {self.author_name}>'