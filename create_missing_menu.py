"""
手动创建缺失的菜单项脚本
"""
import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.menu import SysMenu
from app.models.role import SysRoleMenu
from app.models.permission import SysPermission, SysRolePermission

async def create_missing_menu():
    async with AsyncSessionLocal() as db:
        print("检查并创建缺失的菜单项...")
        
        # 检查是否存在测试查询数据菜单
        result = await db.execute(select(SysMenu).where(SysMenu.menu_name == '测试查询数据'))
        test_query_menu = result.scalar_one_or_none()
        
        if test_query_menu:
            print(f"测试查询数据菜单已存在: ID {test_query_menu.id}")
            # 如果是已删除状态，则恢复
            if test_query_menu.deleted == 1:
                test_query_menu.deleted = 0
                await db.commit()
                print("已恢复已删除的测试查询数据菜单")
        else:
            # 查找测试管理菜单
            result = await db.execute(select(SysMenu).where(SysMenu.menu_name == '测试管理'))
            test_mgmt_menu = result.scalar_one_or_none()
            
            if not test_mgmt_menu:
                # 创建测试管理菜单
                test_mgmt = SysMenu(
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
                db.add(test_mgmt)
                await db.flush()
                test_mgmt_id = test_mgmt.id
                print(f"创建测试管理菜单: ID {test_mgmt_id}")
            else:
                test_mgmt_id = test_mgmt_menu.id
                print(f"使用现有的测试管理菜单: ID {test_mgmt_id}")
            
            # 检查是否存在测试查询数据菜单
            result = await db.execute(select(SysMenu).where(
                SysMenu.menu_name == '测试查询数据',
                SysMenu.parent_id == test_mgmt_id
            ))
            test_query_menu = result.scalar_one_or_none()
            
            if not test_query_menu:
                # 创建测试查询数据菜单
                test_query = SysMenu(
                    parent_id=test_mgmt_id,
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
                db.add(test_query)
                await db.flush()
                test_query_id = test_query.id
                print(f"创建测试查询数据菜单: ID {test_query_id}")
                
                # 检查系统配置菜单是否存在
                result = await db.execute(select(SysMenu).where(
                    SysMenu.menu_name == '系统配置',
                    SysMenu.parent_id == test_mgmt_id
                ))
                sys_config_menu = result.scalar_one_or_none()
                
                if not sys_config_menu:
                    # 创建系统配置菜单
                    sys_config = SysMenu(
                        parent_id=test_mgmt_id,
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
                    db.add(sys_config)
                    await db.flush()
                    sys_config_id = sys_config.id
                    print(f"创建系统配置菜单: ID {sys_config_id}")
                else:
                    sys_config_id = sys_config_menu.id
                    print(f"系统配置菜单已存在: ID {sys_config_id}")
                
                # 为超级管理员角色分配菜单权限
                # 检查是否已经存在关联
                from sqlalchemy import and_
                result = await db.execute(select(SysRoleMenu).where(
                    and_(SysRoleMenu.role_id == 1, SysRoleMenu.menu_id == test_query_id)
                ))
                existing = result.scalar_one_or_none()
                
                if not existing:
                    db.add(SysRoleMenu(role_id=1, menu_id=test_query_id))
                    print(f"为超级管理员分配测试查询数据菜单权限")
                
                result = await db.execute(select(SysRoleMenu).where(
                    and_(SysRoleMenu.role_id == 1, SysRoleMenu.menu_id == sys_config_id)
                ))
                existing = result.scalar_one_or_none()
                
                if not existing:
                    db.add(SysRoleMenu(role_id=1, menu_id=sys_config_id))
                    print(f"为超级管理员分配系统配置菜单权限")
                
                # 添加相关权限
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
                    result = await db.execute(select(SysPermission).where(SysPermission.perm_code == perm_code))
                    permission = result.scalar_one_or_none()
                    
                    if not permission:
                        perm = SysPermission(
                            perm_code=perm_code,
                            perm_name=perm_name,
                            perm_type=perm_type,
                            resource_url=resource_url,
                            method=method,
                            status=1
                        )
                        db.add(perm)
                        await db.flush()
                        
                        # 为超级管理员角色分配权限
                        from app.models.role import SysRolePermission
                        result = await db.execute(select(SysRolePermission).where(
                            and_(SysRolePermission.role_id == 1, SysRolePermission.perm_id == perm.id)
                        ))
                        existing_role_perm = result.scalar_one_or_none()
                        
                        if not existing_role_perm:
                            db.add(SysRolePermission(role_id=1, perm_id=perm.id))
                            print(f"为超级管理员分配权限: {perm_code}")
                
                await db.commit()
                print("所有菜单和权限已创建并分配完成！")
            else:
                print(f"测试查询数据菜单已存在: ID {test_query_menu.id}")

if __name__ == "__main__":
    asyncio.run(create_missing_menu())