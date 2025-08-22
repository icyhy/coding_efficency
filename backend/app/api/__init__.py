# -*- coding: utf-8 -*-
"""
API蓝图包初始化文件
"""

from flask import Blueprint

# 创建各个功能模块的蓝图
auth_bp = Blueprint('auth', __name__)
repository_bp = Blueprint('repositories', __name__)
analytics_bp = Blueprint('analytics', __name__)

# 为了兼容现有代码，保留api_bp
api_bp = auth_bp

# 导入所有API模块
from . import auth, repositories, analytics