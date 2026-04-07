"""
初始化数据库：创建超级管理员用户（admin / Admin@123）
运行方式: uv run python init_db.py
"""

import asyncio

from sqlalchemy import select, text

from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal, engine
from app.db.base import Base

# 导入所有模型，确保 Base.metadata 包含所有表
from app.models.tenant import SysTenant  # noqa: F401
from app.models.user import SysUser  # noqa: F401
from app.models.dept import SysDept  # noqa: F401
from app.models.post import SysPost  # noqa: F401
from app.models.role import SysRole, SysUserRole, SysRoleMenu, SysRolePermission  # noqa: F401
from app.models.menu import SysMenu  # noqa: F401
from app.models.permission import SysPermission  # noqa: F401


async def init():
    async with AsyncSessionLocal() as db:
        # 检查 admin 用户是否已存在
        result = await db.execute(
            select(SysUser).where(SysUser.username == "admin", SysUser.tenant_id == "default")
        )
        existing = result.scalar_one_or_none()

        if existing:
            print("admin 用户已存在，跳过创建。")
        else:
            # 创建超级管理员用户
            admin = SysUser(
                tenant_id="default",
                username="admin",
                password=get_password_hash("Admin@123"),
                real_name="超级管理员",
                user_type=0,
                status=1,
            )
            db.add(admin)
            await db.flush()

            # 绑定角色（角色ID=1）
            db.add(SysUserRole(user_id=admin.id, role_id=1))
            await db.commit()
            print(f"admin 用户创建成功，ID={admin.id}，密码=Admin@123")

        print("初始化完成！")
        print("默认账号: admin / Admin@123  租户: default")


if __name__ == "__main__":
    asyncio.run(init())
