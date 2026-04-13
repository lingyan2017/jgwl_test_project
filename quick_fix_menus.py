"""快速检查并添加菜单数据"""
import asyncio
from sqlalchemy import text
from app.db.session import async_engine


async def main():
    print("=" * 80)
    print("检查菜单数据...")
    print("=" * 80)
    
    async with async_engine.begin() as conn:
        # 检查所有菜单
        result = await conn.execute(text("""
            SELECT id, parent_id, menu_name, path, component 
            FROM sys_menu 
            WHERE deleted = 0 
            ORDER BY id
        """))
        
        menus = result.fetchall()
        
        if not menus:
            print("\n❌ 数据库中没有菜单数据！\n")
            print("正在添加基础菜单数据...")
            
            # 添加系统管理菜单
            await conn.execute(text("""
                INSERT INTO sys_menu (id, parent_id, menu_name, menu_type, path, component, icon, order_num, visible, status) VALUES
                (1,  0, '系统管理', 1, '/system',    NULL,                        'Setting',       1, 1, 1),
                (2,  1, '租户管理', 2, 'tenant',     'system/TenantManage',       'OfficeBuilding',1, 1, 1),
                (3,  1, '用户管理', 2, 'user',       'system/UserManage',         'User',          2, 1, 1),
                (4,  1, '部门管理', 2, 'dept',       'system/DeptManage',         'Folder',        3, 1, 1),
                (5,  1, '岗位管理', 2, 'post',       'system/PostManage',         'Postcard',      4, 1, 1),
                (6,  1, '角色管理', 2, 'role',       'system/RoleManage',         'UserFilled',    5, 1, 1),
                (7,  1, '菜单管理', 2, 'menu',       'system/MenuManage',         'Menu',          6, 1, 1),
                (8,  1, '权限管理', 2, 'permission', 'system/PermissionManage',   'Lock',          7, 1, 1);
            """))
            
            # 添加测试管理菜单
            await conn.execute(text("""
                INSERT INTO sys_menu (id, parent_id, menu_name, menu_type, path, component, icon, order_num, visible, status) VALUES
                (10, 0, '测试管理', 1, '/test', NULL, 'Document', 2, 1, 1),
                (11, 10, '测试查询数据', 2, 'test-query-data', 'system/TestQueryDataManage', 'Document', 1, 1, 1),
                (12, 10, '系统配置', 2, 'sys-config', 'system/SysConfigManage', 'Setting', 2, 1, 1);
            """))
            
            # 为超级管理员角色分配菜单
            await conn.execute(text("""
                INSERT IGNORE INTO sys_role_menu (role_id, menu_id) 
                SELECT 1, id FROM sys_menu WHERE deleted = 0;
            """))
            
            print("✓ 菜单数据添加成功！\n")
            
            # 重新查询
            result = await conn.execute(text("""
                SELECT id, parent_id, menu_name, path, component 
                FROM sys_menu 
                WHERE deleted = 0 
                ORDER BY id
            """))
            menus = result.fetchall()
        
        print(f"\n找到 {len(menus)} 个菜单:\n")
        print(f"{'ID':<5} {'Parent':<8} {'Name':<15} {'Path':<25} {'Component'}")
        print("-" * 80)
        
        for menu in menus:
            id_, parent_id, name, path, component = menu
            path_str = path or "NULL"
            comp_str = component or "NULL"
            print(f"{id_:<5} {parent_id:<8} {name:<15} {path_str:<25} {comp_str}")
        
        print("\n" + "=" * 80)
        print("✓ 检查完成！")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
