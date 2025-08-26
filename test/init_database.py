import asyncio
import sys
import os

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.database import create_tables, get_async_session
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy import select

async def init_database():
    """初始化数据库并创建测试用户"""
    try:
        print("🔧 正在创建数据库表...")
        await create_tables()
        print("✅ 数据库表创建成功")
        
        # 创建测试用户
        async for session in get_async_session():
            # 检查是否已存在测试用户
            result = await session.execute(select(User).where(User.username == "testuser"))
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"✅ 测试用户已存在: ID={existing_user.id}, 用户名={existing_user.username}")
            else:
                # 创建新的测试用户
                test_user = User(
                    username="testuser",
                    email="test@example.com",
                    hashed_password=get_password_hash("password123"),
                    is_active=True
                )
                
                session.add(test_user)
                await session.commit()
                await session.refresh(test_user)
                
                print(f"✅ 测试用户创建成功: ID={test_user.id}, 用户名={test_user.username}")
            
            # 显示所有用户
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            print(f"\n📊 数据库中共有 {len(users)} 个用户:")
            for user in users:
                print(f"- ID: {user.id}, 用户名: {user.username}, 邮箱: {user.email}, 激活状态: {user.is_active}")
            
            break
            
    except Exception as e:
        print(f"❌ 初始化数据库时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(init_database())