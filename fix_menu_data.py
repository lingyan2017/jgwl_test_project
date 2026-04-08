"""
修复菜单数据脚本：清理重复和错误的菜单记录
"""
import asyncio
from sqlalchemy import select, delete
from app.db.session import AsyncSessionLocal
from app.models.menu import SysMenu

async def fix_menu_data():
    async with AsyncSessionLocal() as db:
        print("开始修复菜单数据...")
        
        # 1. 查找所有测试管理相关的菜单（包括已删除的）
        result = await db.execute(select(SysMenu).where(
            SysMenu.menu_name.in_(['测试管理', '测试查询数据', '系统配置'])
        ).order_by(SysMenu.id))
        test_menus = result.scalars().all()
        
        print("找到的测试相关菜单:")
        for menu in test_menus:
            status = '已删除' if menu.deleted == 1 else '正常'
            print(f"  ID {menu.id}: {menu.menu_name} (parent_id: {menu.parent_id}, status: {status})")
        
        # 2. 清理旧的重复记录
        # 删除已删除的记录（如ID 10）
        from app.models.role import SysRoleMenu
        for menu in test_menus:
            if menu.deleted == 1:
                print(f"删除已删除的菜单: ID {menu.id} - {menu.menu_name}")
                # 同时删除相关的角色菜单关联
                await db.execute(delete(SysRoleMenu).where(SysRoleMenu.menu_id == menu.id))
                await db.delete(menu)
        
        # 提交删除操作
        await db.commit()
        
        # 3. 再次检查是否还有测试查询数据菜单
        result = await db.execute(select(SysMenu).where(
            SysMenu.menu_name == '测试查询数据'
        ))
        test_query_menus = result.scalars().all()
        
        if len(test_query_menus) == 0:
            print("未找到测试查询数据菜单，需要重新创建...")
            
            # 查找测试管理菜单
            result = await db.execute(select(SysMenu).where(
                SysMenu.menu_name == '测试管理'
            ))
            test_mgmt_menus = result.scalars().all()
            
            if len(test_mgmt_menus) == 0:
                print("未找到测试管理菜单，创建顶级菜单...")
                # 创建测试管理顶级菜单
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
                test_mgmt_id = test_mgmt_menus[0].id
                print(f"使用现有的测试管理菜单: ID {test_mgmt_id}")
            
            # 创建测试查询数据菜单
            test_query_menu = SysMenu(
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
            db.add(test_query_menu)
            await db.flush()
            test_query_id = test_query_menu.id
            print(f"创建测试查询数据菜单: ID {test_query_id}")
            
            # 创建系统配置菜单
            sys_config_menu = SysMenu(
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
            db.add(sys_config_menu)
            await db.flush()
            sys_config_id = sys_config_menu.id
            print(f"创建系统配置菜单: ID {sys_config_id}")
            
            # 为超级管理员角色分配新菜单权限
            from app.models.role import SysRoleMenu
            db.add(SysRoleMenu(role_id=1, menu_id=test_mgmt_id))  # 测试管理
            db.add(SysRoleMenu(role_id=1, menu_id=test_query_id))  # 测试查询数据
            db.add(SysRoleMenu(role_id=1, menu_id=sys_config_id))  # 系统配置
            
            await db.commit()
            print(f"菜单创建完成！")
        else:
            print("测试查询数据菜单已存在，无需创建。")
        
        # 4. 最终验证
        result = await db.execute(select(SysMenu).where(
            SysMenu.menu_name.in_(['测试管理', '测试查询数据', '系统配置']),
            SysMenu.deleted == 0
        ).order_by(SysMenu.id))
        final_menus = result.scalars().all()
        
        print("\n最终的测试相关菜单:")
        for menu in final_menus:
            print(f"  ID {menu.id}: {menu.menu_name} (parent_id: {menu.parent_id})")
        
        print("菜单数据修复完成！")

if __name__ == "__main__":
    asyncio.run(fix_menu_data())