import asyncio
import sys
import os
sys.path.insert(0, r'D:\mycode\myprojects\project_py\jgwl_project\jgwl_test_project')

from sqlalchemy import text
from app.db.session import AsyncSessionLocal

async def add_trial_menu():
    async with AsyncSessionLocal() as db:
        try:
            # 检查是否存在测试管理菜单（ID=9）
            result = await db.execute(text("SELECT id FROM sys_menu WHERE menu_name = '测试管理' LIMIT 1"))
            test_mgmt_menu = result.fetchone()
            
            if test_mgmt_menu:
                test_mgmt_id = test_mgmt_menu[0]
                print(f"找到测试管理菜单，ID: {test_mgmt_id}")
                
                # 检查试算测试菜单是否已存在
                result = await db.execute(
                    text("SELECT id FROM sys_menu WHERE menu_name = '试算测试' AND parent_id = :parent_id"),
                    {"parent_id": test_mgmt_id}
                )
                existing_menu = result.fetchone()
                
                if existing_menu:
                    print("试算测试菜单已存在")
                else:
                    # 插入试算测试菜单
                    await db.execute(
                        text("""
                            INSERT INTO sys_menu 
                            (parent_id, menu_name, menu_type, path, component, icon, order_num, perms, visible, status) 
                            VALUES 
                            (:parent_id, :menu_name, :menu_type, :path, :component, :icon, :order_num, :perms, :visible, :status)
                        """),
                        {
                            "parent_id": test_mgmt_id,
                            "menu_name": "试算测试",
                            "menu_type": 2,
                            "path": "trial-calculator",
                            "component": "system/TrialCalculator",
                            "icon": "Document",
                            "order_num": 3,
                            "perms": "test:trial-calculator:list",
                            "visible": 1,
                            "status": 1
                        }
                    )
                    print("试算测试菜单已添加")
                    
                    # 获取新插入菜单的ID
                    result = await db.execute(
                        text("SELECT id FROM sys_menu WHERE menu_name = '试算测试' AND parent_id = :parent_id"),
                        {"parent_id": test_mgmt_id}
                    )
                    new_menu = result.fetchone()
                    if new_menu:
                        new_menu_id = new_menu[0]
                        
                        # 检查权限是否已存在
                        result = await db.execute(
                            text("SELECT id FROM sys_permission WHERE perm_code = 'test:trial-calculator:list'")
                        )
                        perm_exists = result.fetchone()
                        
                        if not perm_exists:
                            # 添加权限
                            await db.execute(
                                text("""
                                    INSERT INTO sys_permission 
                                    (perm_code, perm_name, perm_type, resource_url, method) 
                                    VALUES 
                                    ('test:trial-calculator:list', '试算测试列表', 3, '/api/v1/test-trial/trial-calculate', 'POST')
                                """)
                            )
                            print("权限已添加")
                            
                        # 再次获取权限ID
                        result = await db.execute(
                            text("SELECT id FROM sys_permission WHERE perm_code = 'test:trial-calculator:list'")
                        )
                        perm_result = result.fetchone()
                        if perm_result:
                            perm_id = perm_result[0]
                            
                            # 为超级管理员角色分配菜单权限
                            await db.execute(
                                text("""
                                    INSERT IGNORE INTO sys_role_menu (role_id, menu_id) 
                                    VALUES (1, :menu_id)
                                """),
                                {"menu_id": new_menu_id}
                            )
                            
                            # 为超级管理员角色分配权限
                            await db.execute(
                                text("""
                                    INSERT IGNORE INTO sys_role_permission (role_id, perm_id) 
                                    VALUES (1, :perm_id)
                                """),
                                {"perm_id": perm_id}
                            )
                            
                            print("权限分配完成")
            
            await db.commit()
            print("操作完成")
        except Exception as e:
            await db.rollback()
            print(f"错误: {e}")

if __name__ == "__main__":
    asyncio.run(add_trial_menu())