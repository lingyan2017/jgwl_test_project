"""添加测试管理菜单数据"""
import asyncio
from sqlalchemy import text
from app.db.session import async_engine


async def add_test_menus():
    """添加测试管理相关的菜单和权限数据"""
    
    async with async_engine.begin() as conn:
        # 检查是否已存在测试管理菜单
        result = await conn.execute(text("SELECT COUNT(*) FROM sys_menu WHERE id = 10"))
        count = result.scalar()
        
        if count > 0:
            print("测试管理菜单已存在，跳过添加")
            return
        
        print("开始添加测试管理菜单...")
        
        # 添加测试管理目录菜单
        await conn.execute(text("""
            INSERT INTO sys_menu (id, parent_id, menu_name, menu_type, path, component, icon, order_num, perms, visible, status) 
            VALUES (10, 0, '测试管理', 1, '/test', NULL, 'Document', 2, NULL, 1, 1)
        """))
        
        # 添加测试查询数据菜单
        await conn.execute(text("""
            INSERT INTO sys_menu (id, parent_id, menu_name, menu_type, path, component, icon, order_num, perms, visible, status) 
            VALUES (11, 10, '测试查询数据', 2, 'test-query-data', 'system/TestQueryDataManage', 'Document', 1, 'test:query:list', 1, 1)
        """))
        
        # 添加系统配置菜单
        await conn.execute(text("""
            INSERT INTO sys_menu (id, parent_id, menu_name, menu_type, path, component, icon, order_num, perms, visible, status) 
            VALUES (12, 10, '系统配置', 2, 'sys-config', 'system/SysConfigManage', 'Setting', 2, 'test:config:list', 1, 1)
        """))
        
        # 为超级管理员角色分配新菜单
        await conn.execute(text("""
            INSERT INTO sys_role_menu (role_id, menu_id) VALUES (1, 10), (1, 11), (1, 12)
        """))
        
        # 添加测试管理相关权限
        permissions = [
            ('test:query:list', '测试查询列表', '/api/v1/test-query-data/list', 'GET'),
            ('test:query:create', '创建测试查询', '/api/v1/test-query-data/create', 'POST'),
            ('test:query:update', '更新测试查询', '/api/v1/test-query-data/update/{id}', 'PUT'),
            ('test:query:delete', '删除测试查询', '/api/v1/test-query-data/delete/{id}', 'DELETE'),
            ('test:query:call', '调用测试接口', '/api/v1/test-query-data/call', 'POST'),
            ('test:config:list', '系统配置列表', '/api/v1/sys-config/list', 'GET'),
            ('test:config:create', '创建系统配置', '/api/v1/sys-config/create', 'POST'),
            ('test:config:update', '更新系统配置', '/api/v1/sys-config/update/{id}', 'PUT'),
            ('test:config:delete', '删除系统配置', '/api/v1/sys-config/delete/{id}', 'DELETE'),
        ]
        
        for perm_code, perm_name, resource_url, method in permissions:
            await conn.execute(text("""
                INSERT INTO sys_permission (perm_code, perm_name, perm_type, resource_url, method) 
                VALUES (:perm_code, :perm_name, 3, :resource_url, :method)
            """), {
                'perm_code': perm_code,
                'perm_name': perm_name,
                'resource_url': resource_url,
                'method': method
            })
        
        print("✓ 测试管理菜单添加成功！")
        print("  - 测试管理 (ID: 10)")
        print("  - 测试查询数据 (ID: 11)")
        print("  - 系统配置 (ID: 12)")
        print("  - 相关权限已添加")


if __name__ == "__main__":
    asyncio.run(add_test_menus())
