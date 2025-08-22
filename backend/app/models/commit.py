# -*- coding: utf-8 -*-
"""
提交记录数据模型
定义Git提交记录表结构和相关方法
"""

from datetime import datetime
from app import db
from sqlalchemy import func

class Commit(db.Model):
    """
    提交记录模型类
    
    Attributes:
        id (int): 记录唯一标识
        repository_id (int): 所属仓库ID
        commit_hash (str): 提交哈希值
        author_name (str): 提交作者姓名
        author_email (str): 提交作者邮箱
        message (str): 提交信息
        additions (int): 新增行数
        deletions (int): 删除行数
        files_changed (int): 修改文件数
        commit_date (datetime): 提交时间
        created_at (datetime): 记录创建时间
    """
    
    __tablename__ = 'commits'
    
    id = db.Column(db.Integer, primary_key=True)
    repository_id = db.Column(db.Integer, db.ForeignKey('repositories.id'), nullable=False, index=True)
    commit_hash = db.Column(db.String(40), nullable=False, index=True)
    author_name = db.Column(db.String(255), nullable=False, index=True)
    author_email = db.Column(db.String(255), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    additions = db.Column(db.Integer, default=0, nullable=False)
    deletions = db.Column(db.Integer, default=0, nullable=False)
    files_changed = db.Column(db.Integer, default=0, nullable=False)
    commit_date = db.Column(db.DateTime, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # 复合索引
    __table_args__ = (
        db.Index('idx_repo_commit_hash', 'repository_id', 'commit_hash'),
        db.Index('idx_repo_author_date', 'repository_id', 'author_email', 'commit_date'),
    )
    
    def __init__(self, repository_id, commit_hash, author_name, author_email, 
                 message, commit_date, additions=0, deletions=0, files_changed=0):
        """
        初始化提交记录实例
        
        Args:
            repository_id (int): 仓库ID
            commit_hash (str): 提交哈希
            author_name (str): 作者姓名
            author_email (str): 作者邮箱
            message (str): 提交信息
            commit_date (datetime): 提交时间
            additions (int): 新增行数
            deletions (int): 删除行数
            files_changed (int): 修改文件数
        """
        self.repository_id = repository_id
        self.commit_hash = commit_hash
        self.author_name = author_name
        self.author_email = author_email
        self.message = message
        self.commit_date = commit_date
        self.additions = additions
        self.deletions = deletions
        self.files_changed = files_changed
    
    def to_dict(self):
        """
        将提交记录对象转换为字典
        
        Returns:
            dict: 提交记录信息字典
        """
        return {
            'id': self.id,
            'repository_id': self.repository_id,
            'commit_hash': self.commit_hash,
            'author_name': self.author_name,
            'author_email': self.author_email,
            'message': self.message,
            'additions': self.additions,
            'deletions': self.deletions,
            'files_changed': self.files_changed,
            'total_changes': self.additions + self.deletions,
            'commit_date': self.commit_date.isoformat(),
            'created_at': self.created_at.isoformat()
        }
    
    def calculate_score(self, add_weight=1.0, del_weight=0.5, file_weight=0.1):
        """
        计算提交贡献分数
        
        Args:
            add_weight (float): 新增代码权重
            del_weight (float): 删除代码权重
            file_weight (float): 文件数权重
        
        Returns:
            float: 贡献分数
        """
        return (
            self.additions * add_weight + 
            self.deletions * del_weight + 
            self.files_changed * file_weight
        )
    
    @staticmethod
    def find_by_repository(repository_id, start_date=None, end_date=None, limit=None):
        """
        根据仓库ID查找提交记录
        
        Args:
            repository_id (int): 仓库ID
            start_date (datetime): 开始时间
            end_date (datetime): 结束时间
            limit (int): 限制数量
        
        Returns:
            list: 提交记录列表
        """
        query = Commit.query.filter_by(repository_id=repository_id)
        
        if start_date:
            query = query.filter(Commit.commit_date >= start_date)
        if end_date:
            query = query.filter(Commit.commit_date <= end_date)
        
        query = query.order_by(Commit.commit_date.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def find_by_author(repository_id, author_email, start_date=None, end_date=None):
        """
        根据作者查找提交记录
        
        Args:
            repository_id (int): 仓库ID
            author_email (str): 作者邮箱
            start_date (datetime): 开始时间
            end_date (datetime): 结束时间
        
        Returns:
            list: 提交记录列表
        """
        query = Commit.query.filter_by(
            repository_id=repository_id,
            author_email=author_email
        )
        
        if start_date:
            query = query.filter(Commit.commit_date >= start_date)
        if end_date:
            query = query.filter(Commit.commit_date <= end_date)
        
        return query.order_by(Commit.commit_date.desc()).all()
    
    @staticmethod
    def get_author_statistics(repository_id, start_date=None, end_date=None):
        """
        获取作者统计信息
        
        Args:
            repository_id (int): 仓库ID
            start_date (datetime): 开始时间
            end_date (datetime): 结束时间
        
        Returns:
            list: 作者统计列表
        """
        query = db.session.query(
            Commit.author_name,
            Commit.author_email,
            func.count(Commit.id).label('commit_count'),
            func.sum(Commit.additions).label('total_additions'),
            func.sum(Commit.deletions).label('total_deletions'),
            func.sum(Commit.files_changed).label('total_files')
        ).filter_by(repository_id=repository_id)
        
        if start_date:
            query = query.filter(Commit.commit_date >= start_date)
        if end_date:
            query = query.filter(Commit.commit_date <= end_date)
        
        return query.group_by(
            Commit.author_name, 
            Commit.author_email
        ).order_by(
            func.count(Commit.id).desc()
        ).all()
    
    @staticmethod
    def get_time_distribution(repository_id, start_date=None, end_date=None, group_by='day'):
        """
        获取时间分布统计
        
        Args:
            repository_id (int): 仓库ID
            start_date (datetime): 开始时间
            end_date (datetime): 结束时间
            group_by (str): 分组方式 ('hour', 'day', 'week', 'month')
        
        Returns:
            list: 时间分布统计
        """
        # 根据分组方式选择不同的时间格式
        if group_by == 'hour':
            time_format = func.strftime('%Y-%m-%d %H:00:00', Commit.commit_date)
        elif group_by == 'day':
            time_format = func.date(Commit.commit_date)
        elif group_by == 'week':
            time_format = func.strftime('%Y-W%W', Commit.commit_date)
        elif group_by == 'month':
            time_format = func.strftime('%Y-%m', Commit.commit_date)
        else:
            time_format = func.date(Commit.commit_date)
        
        query = db.session.query(
            time_format.label('time_period'),
            func.count(Commit.id).label('commit_count'),
            func.sum(Commit.additions).label('total_additions'),
            func.sum(Commit.deletions).label('total_deletions')
        ).filter_by(repository_id=repository_id)
        
        if start_date:
            query = query.filter(Commit.commit_date >= start_date)
        if end_date:
            query = query.filter(Commit.commit_date <= end_date)
        
        return query.group_by(time_format).order_by(time_format).all()
    
    @staticmethod
    def exists_by_hash(repository_id, commit_hash):
        """
        检查提交是否已存在
        
        Args:
            repository_id (int): 仓库ID
            commit_hash (str): 提交哈希
        
        Returns:
            bool: 是否存在
        """
        return Commit.query.filter_by(
            repository_id=repository_id,
            commit_hash=commit_hash
        ).first() is not None
    
    def __repr__(self):
        """
        提交记录对象的字符串表示
        
        Returns:
            str: 提交记录对象描述
        """
        return f'<Commit {self.commit_hash[:8]} by {self.author_name}>'