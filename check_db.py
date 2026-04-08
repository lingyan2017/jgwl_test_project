import os
import sys
sys.path.append('.')

from sqlalchemy import create_engine, text
from app.core.config import settings

# 创建同步引擎
DATABASE_URL = f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"

try:
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        # 检查菜单表
        result = conn.execute(text('SELECT id, parent_id, menu_name, path FROM sys_menu ORDER BY id'))
        menus = result.fetchall()
        print('当前菜单:')
        for menu in menus:
            print(f'  {menu.id} -> {menu.parent_id}: {menu.menu_name} ({menu.path})')
        
        print()
        
        # 检查角色菜单关联
        result = conn.execute(text('SELECT role_id, menu_id FROM sys_role_menu ORDER BY role_id, menu_id'))
        role_menus = result.fetchall()
        print('角色菜单关联:')
        for rm in role_menus:
            print(f'  角色 {rm[0]} -> 菜单 {rm[1]}')
        
        print()
        
        # 检查用户和角色
        result = conn.execute(text('SELECT id, username, user_type FROM sys_user WHERE username = "admin"'))
        user = result.fetchone()
        if user:
            print(f'Admin用户: id={user[0]}, username={user[1]}, user_type={user[2]}')
            
            result = conn.execute(text(f'SELECT role_id FROM sys_user_role WHERE user_id = {user[0]}'))
            user_roles = result.fetchall()
            print(f'Admin用户的角色: {[r[0] for r in user_roles]}')
        else:
            print('未找到admin用户')
            
except Exception as e:
    print(f"数据库连接错误: {e}")