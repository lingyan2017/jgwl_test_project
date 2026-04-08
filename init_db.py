"""
初始化数据库：创建超级管理员用户（admin / Admin@123）
运行方式: uv run python init_db.py
"""

import asyncio
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

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

        # 检查测试管理菜单是否已存在
        result = await db.execute(select(SysMenu).where(SysMenu.path == "test"))
        test_menu_exists = result.scalar_one_or_none()

        if test_menu_exists:
            print("测试管理菜单已存在，跳过创建。")
        else:
            # 添加测试管理顶级菜单
            test_menu = SysMenu(
                parent_id=0,
                menu_name="测试管理",
                menu_type=1,
                path="/test",
                component=None,
                icon="Document",
                order_num=3,
                perms=None,
                visible=1,
                status=1
            )
            db.add(test_menu)
            await db.flush()

            # 添加测试查询数据菜单
            test_query_data_menu = SysMenu(
                parent_id=test_menu.id,
                menu_name="测试查询数据",
                menu_type=2,
                path="test-query-data",
                component="system/TestQueryDataManage",
                icon="Document",
                order_num=1,
                perms="test:test-query-data:list",
                visible=1,
                status=1
            )
            db.add(test_query_data_menu)
            await db.flush()

            # 添加系统配置菜单
            sys_config_menu = SysMenu(
                parent_id=test_menu.id,
                menu_name="系统配置",
                menu_type=2,
                path="sys-config",
                component="system/SysConfigManage",
                icon="Setting",
                order_num=2,
                perms="test:sys-config:list",
                visible=1,
                status=1
            )
            db.add(sys_config_menu)
            await db.flush()

            # 添加测试查询数据权限
            permissions_data = [
                ("test:test-query-data:list", "测试查询数据列表", 3, "/api/v1/test-query-data/list", "GET"),
                ("test:test-query-data:get", "获取测试查询数据", 3, "/api/v1/test-query-data/get/{id}", "GET"),
                ("test:test-query-data:create", "创建测试查询数据", 3, "/api/v1/test-query-data/create", "POST"),
                ("test:test-query-data:update", "更新测试查询数据", 3, "/api/v1/test-query-data/update/{id}", "PUT"),
                ("test:test-query-data:delete", "删除测试查询数据", 3, "/api/v1/test-query-data/delete/{id}", "DELETE"),
                ("test:test-query-data:call", "调用测试查询数据", 3, "/api/v1/test-query-data/call", "POST"),
                ("test:test-query-data:logs", "测试查询数据日志", 3, "/api/v1/test-query-data/logs/{id}", "GET"),
                
                # 系统配置权限
                ("test:sys-config:list", "系统配置列表", 3, "/api/v1/sys-config/list", "GET"),
                ("test:sys-config:get", "获取系统配置", 3, "/api/v1/sys-config/get/{id}", "GET"),
                ("test:sys-config:create", "创建系统配置", 3, "/api/v1/sys-config/create", "POST"),
                ("test:sys-config:update", "更新系统配置", 3, "/api/v1/sys-config/update/{id}", "PUT"),
                ("test:sys-config:delete", "删除系统配置", 3, "/api/v1/sys-config/delete/{id}", "DELETE"),
            ]

            for perm_code, perm_name, perm_type, resource_url, method in permissions_data:
                perm = SysPermission(
                    perm_code=perm_code,
                    perm_name=perm_name,
                    perm_type=perm_type,
                    resource_url=resource_url,
                    method=method,
                    status=1
                )
                try:
                    db.add(perm)
                    await db.flush()
                except IntegrityError:
                    # 如果权限已存在，则跳过
                    await db.rollback()
                    print(f"权限 {perm_code} 已存在，跳过创建。")
                    continue

            # 为超级管理员角色分配新菜单权限
            try:
                db.add(SysRoleMenu(role_id=1, menu_id=test_menu.id))  # 测试管理菜单
                db.add(SysRoleMenu(role_id=1, menu_id=test_query_data_menu.id))  # 测试查询数据菜单
                db.add(SysRoleMenu(role_id=1, menu_id=sys_config_menu.id))  # 系统配置菜单
                await db.commit()
            except IntegrityError:
                # 如果关系已存在，则跳过
                await db.rollback()
                print("部分菜单角色关系已存在，跳过创建。")

            # 为超级管理员角色分配新权限
            for perm_code, _, _, _, _ in permissions_data:
                result = await db.execute(select(SysPermission).where(SysPermission.perm_code == perm_code))
                permission = result.scalar_one_or_none()
                if permission:
                    try:
                        db.add(SysRolePermission(role_id=1, perm_id=permission.id))
                        await db.commit()
                    except IntegrityError:
                        # 如果权限角色关系已存在，则跳过
                        await db.rollback()
                        print(f"权限角色关系 {perm_code} 已存在，跳过创建。")
                        continue

            print(f"测试管理菜单及其权限创建成功！")
            print(f"菜单ID: {test_menu.id} (测试管理), {test_query_data_menu.id} (测试查询数据), {sys_config_menu.id} (系统配置)")

        print("初始化完成！")
        print("默认账号: admin / Admin@123  租户: default")


if __name__ == "__main__":
    asyncio.run(init())