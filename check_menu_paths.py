"""检查和修复菜单路径配置"""
import asyncio
from sqlalchemy import text
from app.db.session import async_engine


async def check_and_fix_menus():
    """检查并修复菜单路径配置"""
    
    async with async_engine.begin() as conn:
        # 查询所有菜单
        result = await conn.execute(text("""
            SELECT id, parent_id, menu_name, menu_type, path, component, icon, order_num, visible, status 
            FROM sys_menu 
            WHERE deleted = 0 
            ORDER BY parent_id, order_num, id
        """))
        
        menus = result.fetchall()
        
        print("=" * 100)
        print("当前菜单配置:")
        print("=" * 100)
        print(f"{'ID':<5} {'Parent':<8} {'Name':<20} {'Type':<6} {'Path':<30} {'Component':<35}")
        print("-" * 100)
        
        for menu in menus:
            id_, parent_id, name, mtype, path, component, icon, order_num, visible, status = menu
            path_str = path or "NULL"
            comp_str = component or "NULL"
            print(f"{id_:<5} {parent_id:<8} {name:<20} {mtype or 'N/A':<6} {path_str:<30} {comp_str:<35}")
        
        print("=" * 100)
        
        # 找出所有顶级菜单
        top_menus = [m for m in menus if m[1] == 0]
        print(f"\n顶级菜单数量: {len(top_menus)}")
        
        # 检查每个顶级菜单的子菜单
        for top_menu in top_menus:
            top_id = top_menu[0]
            top_name = top_menu[2]
            top_path = top_menu[4]
            
            children = [m for m in menus if m[1] == top_id]
            print(f"\n[{top_name}] (ID={top_id}, Path={top_path})")
            print(f"  子菜单数量: {len(children)}")
            
            if children:
                for child in children:
                    child_id = child[0]
                    child_name = child[2]
                    child_path = child[4]
                    
                    # 检查子菜单路径是否正确
                    if child_path:
                        if child_path.startswith('/'):
                            print(f"    ⚠️  [{child_name}] 路径错误: {child_path} (应该是相对路径，不带 /)")
                            print(f"       建议修改为: {child_path.lstrip('/')}")
                        else:
                            print(f"    ✓ [{child_name}] 路径正确: {child_path}")
                            
                            # 验证完整路径
                            full_path = f"{top_path}/{child_path}" if not top_path.startswith('/') else f"{top_path}/{child_path}"
                            print(f"       完整访问路径: {full_path}")
                    else:
                        print(f"    ⚠️  [{child_name}] 路径为空!")
            else:
                print(f"  ⚠️  没有子菜单!")
        
        print("\n" + "=" * 100)
        print("修复建议:")
        print("=" * 100)
        print("1. 顶级菜单(目录)的 path 应该使用绝对路径，如: /system, /test")
        print("2. 子菜单的 path 应该使用相对路径(不带/)，如: user, test-query-data")
        print("3. 完整访问 URL = 父菜单 path + '/' + 子菜单 path")
        print("\n例如:")
        print("  - 测试管理(父): path = /test")
        print("  - 测试查询数据(子): path = test-query-data")
        print("  - 完整访问路径: /test/test-query-data")


if __name__ == "__main__":
    asyncio.run(check_and_fix_menus())
