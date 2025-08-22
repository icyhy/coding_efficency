# -*- coding: utf-8 -*-
"""
Pytest配置文件
提供测试夹具和配置
"""

import os
import sys
import pytest
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Repository, Commit, MergeRequest
from werkzeug.security import generate_password_hash

@pytest.fixture(scope='session')
def app():
    """
    创建测试应用实例
    """
    app = create_app('testing')
    
    with app.app_context():
        yield app

@pytest.fixture(scope='session')
def client(app):
    """
    创建测试客户端
    """
    return app.test_client()

@pytest.fixture(scope='session')
def runner(app):
    """
    创建CLI测试运行器
    """
    return app.test_cli_runner()

@pytest.fixture(scope='function')
def database(app):
    """
    创建测试数据库
    每个测试函数都会重新创建数据库
    """
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture
def admin_user(database):
    """
    创建管理员用户
    """
    user = User(
        username='admin',
        email='admin@test.com',
        password_hash=generate_password_hash('admin123'),
        is_active=True,
        created_at=datetime.utcnow()
    )
    database.session.add(user)
    database.session.commit()
    return user

@pytest.fixture
def test_user(database):
    """
    创建测试用户
    """
    user = User(
        username='testuser',
        email='test@test.com',
        password_hash=generate_password_hash('test123'),
        is_active=True,
        created_at=datetime.utcnow()
    )
    database.session.add(user)
    database.session.commit()
    return user

@pytest.fixture
def test_repository(database, admin_user):
    """
    创建测试仓库
    """
    repo = Repository(
        name='test-repo',
        url='https://codeup.aliyun.com/test/test-repo.git',
        platform='aliyunxiao',
        owner_id=admin_user.id,
        description='测试仓库',
        is_active=True,
        created_at=datetime.utcnow()
    )
    database.session.add(repo)
    database.session.commit()
    return repo

@pytest.fixture
def auth_headers(client, admin_user):
    """
    获取认证头信息
    """
    response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    access_token = data['access_token']
    
    return {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

@pytest.fixture
def sample_commits(database, test_repository, admin_user):
    """
    创建示例提交记录
    """
    commits = []
    for i in range(5):
        commit = Commit(
            repository_id=test_repository.id,
            commit_id=f'commit_{i}',
            author_name=admin_user.username,
            author_email=admin_user.email,
            message=f'Test commit {i}',
            additions=10 + i,
            deletions=5 + i,
            files_changed=2 + i,
            committed_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        commits.append(commit)
        database.session.add(commit)
    
    database.session.commit()
    return commits

@pytest.fixture
def sample_merge_requests(database, test_repository, admin_user):
    """
    创建示例合并请求
    """
    merge_requests = []
    for i in range(3):
        mr = MergeRequest(
            repository_id=test_repository.id,
            merge_request_id=f'mr_{i}',
            title=f'Test MR {i}',
            description=f'Test merge request {i}',
            author_name=admin_user.username,
            author_email=admin_user.email,
            source_branch=f'feature_{i}',
            target_branch='main',
            state='merged' if i % 2 == 0 else 'open',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            merged_at=datetime.utcnow() if i % 2 == 0 else None
        )
        merge_requests.append(mr)
        database.session.add(mr)
    
    database.session.commit()
    return merge_requests

class AuthActions:
    """
    认证操作辅助类
    """
    
    def __init__(self, client):
        self._client = client
    
    def login(self, username='admin', password='admin123'):
        """
        用户登录
        """
        return self._client.post('/api/auth/login', json={
            'username': username,
            'password': password
        })
    
    def logout(self, headers=None):
        """
        用户登出
        """
        return self._client.post('/api/auth/logout', headers=headers)
    
    def register(self, username, email, password):
        """
        用户注册
        """
        return self._client.post('/api/auth/register', json={
            'username': username,
            'email': email,
            'password': password
        })

@pytest.fixture
def auth(client):
    """
    认证操作夹具
    """
    return AuthActions(client)