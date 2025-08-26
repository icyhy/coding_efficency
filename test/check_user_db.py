import asyncio
import sys
import os

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_async_session
from app.models.user import User

async def check_user():
    """检查数据库中的用户"""
    try:
        # 获取数据库会话
        async for session in get_async_session():
            # 查询所有用户
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            print(f"数据库中共有 {len(users)} 个用户:")
            for user in users:
                print(f"- ID: {user.id}, 用户名: {user.username}, 邮箱: {user.email}, 激活状态: {user.is_active}")
            
            # 特别检查ID为1的用户
            result = await session.execute(select(User).where(User.id == 1))
            user_1 = result.scalar_one_or_none()
            
            if user_1:
                print(f"\nID为1的用户详情:")
                print(f"- ID: {user_1.id}")
                print(f"- 用户名: {user_1.username}")
                print(f"- 邮箱: {user_1.email}")
                print(f"- 激活状态: {user_1.is_active}")
                print(f"- 创建时间: {user_1.created_at}")
            else:
                print("\n❌ 数据库中不存在ID为1的用户！")
            
            break
            
    except Exception as e:
        print(f"❌ 检查用户时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_user())