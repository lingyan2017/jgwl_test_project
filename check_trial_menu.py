from app.db.session import engine
from sqlalchemy import text

conn = engine.connect()

# 查询试算测试相关菜单
result = conn.execute(text('''
    SELECT id, parent_id, menu_name, menu_type, path, component, perms, visible, status 
    FROM sys_menu 
    WHERE menu_name LIKE '%试算%' OR path LIKE '%trial%'
'''))

rows = result.fetchall()
print(f'找到 {len(rows)} 条试算测试相关菜单记录:')
print('-' * 120)
for r in rows:
    print(f'ID: {r[0]:3d}, ParentID: {r[1]:3d}, Name: {r[2]:15s}, Type: {r[3]}, Path: {r[4]:20s}, Component: {r[5]:30s}, Visible: {r[7]}, Status: {r[8]}')
    if r[6]:
        print(f'       Perms: {r[6]}')
print('-' * 120)

# 查询父菜单（测试管理）
result2 = conn.execute(text('''
    SELECT id, parent_id, menu_name, menu_type, path, component 
    FROM sys_menu 
    WHERE id = 9
'''))
parent = result2.fetchone()
if parent:
    print(f'\n父菜单信息 (ID=9):')
    print(f'ID: {parent[0]}, ParentID: {parent[1]}, Name: {parent[2]}, Type: {parent[3]}, Path: {parent[4]}, Component: {parent[5]}')

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
    print(f'ID: {c[0]:3d}, Name: {c[2]:20s}, Type: {c[3]}, Path: {c[4]:25s}, Component: {c[5]:30s}, Order: {c[6]}, Visible: {c[7]}, Status: {c[8]}')
print('-' * 120)

conn.close()
