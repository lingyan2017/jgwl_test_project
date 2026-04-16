from app.db.session import engine
from sqlalchemy import text

conn = engine.connect()

print('=' * 120)
print('检查试算测试菜单配置')
print('=' * 120)

# 查询试算测试相关菜单
result = conn.execute(text('''
    SELECT id, parent_id, menu_name, menu_type, path, component, perms, visible, status 
    FROM sys_menu 
    WHERE menu_name LIKE '%试算%' OR path LIKE '%trial%'
'''))

rows = result.fetchall()
if not rows:
    print('\n未找到试算测试菜单！')
    print('\n尝试插入试算测试菜单...')
    
    # 先检查父菜单是否存在
    parent_check = conn.execute(text('SELECT id FROM sys_menu WHERE id = 9'))
    if not parent_check.fetchone():
        print('错误：父菜单(ID=9)不存在！')
        conn.close()
        exit(1)
    
    # 插入试算测试菜单
    conn.execute(text('''
        INSERT INTO sys_menu (parent_id, menu_name, menu_type, path, component, icon, order_num, perms, visible, status)
        VALUES (9, '试算测试', 2, 'trial-calculator', 'system/TrialCalculator', 'Document', 3, 'test:trial-calculator:list', 1, 1)
    '''))
    conn.commit()
    print('成功插入试算测试菜单！')
    
    # 重新查询
    result = conn.execute(text('''
        SELECT id, parent_id, menu_name, menu_type, path, component, perms, visible, status 
        FROM sys_menu 
        WHERE menu_name LIKE '%试算%' OR path LIKE '%trial%'
    '''))
    rows = result.fetchall()

print(f'\n找到 {len(rows)} 条试算测试相关菜单记录:')
print('-' * 120)
for r in rows:
    print(f'ID: {r[0]:3d}, ParentID: {r[1]:3d}, Name: {r[2]:15s}, Type: {r[3]}, Path: {r[4]:20s}, Component: {r[5]:30s}')
    print(f'       Visible: {r[7]}, Status: {r[8]}')
    if r[6]:
        print(f'       Perms: {r[6]}')
print('-' * 120)

# 检查并修复path字段
for row in rows:
    menu_id = row[0]
    menu_path = row[4]
    menu_component = row[5]
    
    # 确保path不包含斜杠前缀（应该是相对路径）
    if menu_path and menu_path.startswith('/'):
        new_path = menu_path.lstrip('/')
        print(f'\n修复菜单 ID={menu_id} 的path: {menu_path} -> {new_path}')
        conn.execute(text('UPDATE sys_menu SET path = :path WHERE id = :id'), {'path': new_path, 'id': menu_id})
        conn.commit()
    
    # 确保component格式正确
    if menu_component and not menu_component.endswith('.vue'):
        expected_component = menu_component
        print(f'菜单 ID={menu_id} 的component: {expected_component}')

# 查询父菜单信息
result2 = conn.execute(text('''
    SELECT id, parent_id, menu_name, menu_type, path, component 
    FROM sys_menu 
    WHERE id = 9
'''))
parent = result2.fetchone()
if parent:
    print(f'\n父菜单信息 (ID=9):')
    print(f'  ID: {parent[0]}, Name: {parent[2]}, Type: {parent[3]}, Path: {parent[4]}, Component: {parent[5]}')

# 查询所有测试管理下的子菜单
result3 = conn.execute(text('''
    SELECT id, parent_id, menu_name, menu_type, path, component, order_num, visible, status 
    FROM sys_menu 
    WHERE parent_id = 9
    ORDER BY order_num
'''))
children = result3.fetchall()
print(f'\n测试管理(parent_id=9)下的所有子菜单 ({len(children)} 个):')
print('-' * 120)
for c in children:
    full_path = f"/{parent[4]}/{c[4]}" if parent else f"/{c[4]}"
    print(f'ID: {c[0]:3d}, Name: {c[2]:20s}, Type: {c[3]}')
    print(f'       Path: {c[4]:25s} -> FullPath: {full_path}')
    print(f'       Component: {c[5]:30s}, Order: {c[6]}, Visible: {c[7]}, Status: {c[8]}')
print('-' * 120)

# 检查超级管理员角色是否有此菜单权限
result4 = conn.execute(text('''
    SELECT rm.role_id, rm.menu_id, m.menu_name
    FROM sys_role_menu rm
    JOIN sys_menu m ON rm.menu_id = m.id
    WHERE m.menu_name LIKE '%试算%'
'''))
role_menus = result4.fetchall()
print(f'\n角色-菜单关联 (试算测试):')
if role_menus:
    for rm in role_menus:
        print(f'  RoleID: {rm[0]}, MenuID: {rm[1]}, MenuName: {rm[2]}')
else:
    print('  未找到关联，正在添加...')
    # 为超级管理员(role_id=1)添加菜单权限
    trial_menu_id = rows[0][0] if rows else None
    if trial_menu_id:
        conn.execute(text('''
            INSERT IGNORE INTO sys_role_menu (role_id, menu_id) VALUES (1, :menu_id)
        '''), {'menu_id': trial_menu_id})
        conn.commit()
        print(f'  已为超级管理员添加菜单权限 (menu_id={trial_menu_id})')

print('\n' + '=' * 120)
print('检查完成！')
print('=' * 120)
print('\n请刷新浏览器页面，然后：')
print('1. 退出登录并重新登录')
print('2. 检查左侧菜单是否显示"试算测试"')
print('3. 点击"试算测试"菜单，查看是否能正常显示页面')
print('\n如果仍然无法显示，请检查：')
print('- 浏览器控制台是否有路由警告')
print('- 网络请求中 /api/v1/menus/user-menus 返回的数据是否包含试算测试菜单')
print('=' * 120)

conn.close()
