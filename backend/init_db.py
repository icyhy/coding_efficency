#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
创建数据库表结构和初始数据
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Repository, Commit, MergeRequest, AnalyticsCache
from werkzeug.security import generate_password_hash

def init_database(drop_existing=False):
    """
    初始化数据库
    创建所有表结构
    
    Args:
        drop_existing (bool): 是否删除现有表
    """
    print("正在初始化数据库...")
    
    if drop_existing:
        print("删除现有数据库表...")
        db.drop_all()
    
    # 创建所有表
    db.create_all()
    
    print("数据库表创建完成！")
    
    # 检查表是否创建成功
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"已创建的表: {', '.join(tables)}")
    except Exception as e:
        print(f"检查表结构时出错: {e}")
    
    return True

def create_sample_data():
    """
    创建示例数据
    用于开发和测试
    """
    print("正在创建示例数据...")
    
    try:
        # 创建管理员用户
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            admin_user.is_active = True
            admin_user.created_at = datetime.utcnow()
            db.session.add(admin_user)
            print("创建管理员用户: admin / admin123")
        
        # 创建测试用户
        if not User.query.filter_by(username='testuser').first():
            test_user = User(
                username='testuser',
                email='test@example.com',
                password='test123'
            )
            test_user.is_active = True
            test_user.created_at = datetime.utcnow()
            db.session.add(test_user)
            print("创建测试用户: testuser / test123")
        
        if not User.find_by_username('developer'):
            dev_user = User(
                username='developer',
                email='developer@example.com',
                password='dev123'
            )
            dev_user.is_active = True
            dev_user.created_at = datetime.utcnow()
            db.session.add(dev_user)
            print("创建开发者用户: developer / dev123")
        
        # 提交用户数据
        db.session.commit()
        
        # 获取用户ID
        admin = User.find_by_username('admin')
        developer = User.find_by_username('developer')
        
        # 创建示例仓库
        if admin:
            existing_repo = Repository.query.filter_by(user_id=admin.id, name='sample-project').first()
            if not existing_repo:
                sample_repo = Repository(
                    user_id=admin.id,
                    name='sample-project',
                    url='https://codeup.aliyun.com/sample/sample-project.git',
                    api_key='sample_api_key_123',
                    platform='aliyun_codeup',
                    project_id='sample_project_123'
                )
                db.session.add(sample_repo)
                print("创建示例仓库: sample-project")
        
        if developer:
            existing_repo = Repository.query.filter_by(user_id=developer.id, name='my-app').first()
            if not existing_repo:
                dev_repo = Repository(
                    user_id=developer.id,
                    name='my-app',
                    url='https://codeup.aliyun.com/dev/my-app.git',
                    api_key='dev_api_key_456',
                    platform='aliyun_codeup',
                    project_id='my_app_456'
                )
                db.session.add(dev_repo)
                print("创建开发仓库: my-app")
        
        # 提交仓库数据
        db.session.commit()
        
        print("示例数据创建完成！")
        return True
        
    except Exception as e:
        print(f"创建示例数据时出错: {str(e)}")
        db.session.rollback()
        return False

def drop_all_tables():
    """
    删除所有表
    谨慎使用！
    """
    print("警告：即将删除所有数据库表！")
    confirm = input("请输入 'YES' 确认删除: ")
    
    if confirm == 'YES':
        db.drop_all()
        print("所有表已删除！")
        return True
    else:
        print("操作已取消")
        return False

def reset_database():
    """
    重置数据库
    删除所有表并重新创建
    """
    print("正在重置数据库...")
    
    # 删除所有表
    db.drop_all()
    print("已删除所有表")
    
    # 重新创建表
    init_database()
    
    # 创建示例数据
    create_sample_data()
    
    print("数据库重置完成！")
    return True

def check_database_status():
    """
    检查数据库状态
    """
    print("正在检查数据库状态...")
    
    try:
        # 检查表是否存在
        tables = db.engine.table_names()
        print(f"数据库中的表: {', '.join(tables) if tables else '无'}")
        
        if not tables:
            print("数据库为空，需要初始化")
            return False
        
        # 检查数据统计
        user_count = User.query.count()
        repo_count = Repository.query.count()
        commit_count = Commit.query.count()
        mr_count = MergeRequest.query.count()
        cache_count = AnalyticsCache.query.count()
        
        print(f"数据统计:")
        print(f"  用户数: {user_count}")
        print(f"  仓库数: {repo_count}")
        print(f"  提交数: {commit_count}")
        print(f"  合并请求数: {mr_count}")
        print(f"  缓存数: {cache_count}")
        
        return True
        
    except Exception as e:
        print(f"检查数据库状态时出错: {str(e)}")
        return False

def main():
    """
    主函数
    处理命令行参数
    """
    # 创建Flask应用上下文
    app = create_app()
    
    with app.app_context():
        if len(sys.argv) < 2:
            print("数据库管理工具")
            print("使用方法:")
            print("  python init_db.py init      - 初始化数据库")
            print("  python init_db.py sample    - 创建示例数据")
            print("  python init_db.py reset     - 重置数据库")
            print("  python init_db.py drop      - 删除所有表")
            print("  python init_db.py status    - 检查数据库状态")
            return
        
        command = sys.argv[1].lower()
        
        if command == 'init':
            init_database()
        elif command == 'sample':
            create_sample_data()
        elif command == 'reset':
            reset_database()
        elif command == 'drop':
            drop_all_tables()
        elif command == 'status':
            check_database_status()
        else:
            print(f"未知命令: {command}")
            print("支持的命令: init, sample, reset, drop, status")

if __name__ == '__main__':
    main()