#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask应用启动脚本
用于启动开发服务器或生产服务器
"""

import os
import sys
from app import create_app, db
from config import get_config

def main():
    """
    主函数
    """
    # 获取配置环境
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    print(f"启动环境: {config_name}")
    print("=" * 50)
    
    # 创建应用实例
    app = create_app(config_name)
    
    # 获取配置
    config = get_config(config_name)
    
    # 开发环境配置
    if config_name == 'development':
        print("开发模式启动")
        print(f"调试模式: {app.debug}")
        print(f"数据库: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print("\n按 Ctrl+C 停止服务器")
        print("=" * 50)
        
        # 确保数据库表存在
        with app.app_context():
            try:
                db.create_all()
                print("数据库表检查完成")
            except Exception as e:
                print(f"数据库初始化失败: {e}")
                sys.exit(1)
        
        # 获取端口号
        port = int(os.environ.get('PORT', 5000))
        if len(sys.argv) > 1:
            for i, arg in enumerate(sys.argv):
                if arg == '--port' and i + 1 < len(sys.argv):
                    try:
                        port = int(sys.argv[i + 1])
                    except ValueError:
                        print(f"警告: 无效的端口号 {sys.argv[i + 1]}，使用默认端口 5000")
        
        print(f"访问地址: http://localhost:{port}")
        
        # 启动开发服务器
        app.run(
            host='0.0.0.0',
            port=port,
            debug=True,
            use_reloader=True,
            use_debugger=True
        )
    
    # 生产环境配置
    elif config_name in ['production', 'docker']:
        print("生产模式启动")
        print("使用 Gunicorn 或其他 WSGI 服务器启动应用")
        print("示例命令: gunicorn -w 4 -b 0.0.0.0:5000 run:app")
        
        # 返回应用实例供 WSGI 服务器使用
        return app
    
    # 测试环境
    elif config_name == 'testing':
        print("测试模式启动")
        return app
    
    else:
        print(f"未知的配置环境: {config_name}")
        sys.exit(1)

if __name__ == '__main__':
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("错误: 需要 Python 3.7 或更高版本")
        sys.exit(1)
    
    # 检查必要的环境变量
    if not os.path.exists('.env') and not os.environ.get('SECRET_KEY'):
        print("警告: 未找到 .env 文件，请复制 .env.example 并配置相关参数")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
else:
    # 供 WSGI 服务器使用
    config_name = os.environ.get('FLASK_ENV', 'production')
    app = create_app(config_name)