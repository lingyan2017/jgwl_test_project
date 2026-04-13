"""检查菜单数据"""
import asyncio
from sqlalchemy import text
from app.db.session import async_engine


async def check_menus():
    """检查数据库中的菜单数据"""
    
    async with async_engine.begin() as conn:
        # 查询所有菜单
        result = await conn.execute(text("""
            SELECT id, parent_id, menu_name, menu_type, path, component, icon, order_num, visible, status 
            FROM sys_menu 
            WHERE deleted = 0 
            ORDER BY parent_id, order_num, id
        """))
        
        menus = result.fetchall()
        
        if not menus:
            print("❌ 数据库中没有菜单数据！")
            return
        
        print("=" * 80)
        print("菜单列表:")
        print("=" * 80)
        print(f"{'ID':<5} {'Parent':<8} {'Name':<15} {'Type':<6} {'Path':<25} {'Component':<30} {'Icon':<15}")
        print("-" * 80)
        
        for menu in menus:
            id_, parent_id, name, mtype, path, component, icon, order_num, visible, status = menu
            path_str = path or "NULL"
            comp_str = component or "NULL"
            icon_str = icon or "NULL"
            print(f"{id_:<5} {parent_id:<8} {name:<15} {mtype or 'N/A':<6} {path_str:<25} {comp_str:<30} {icon_str:<15}")
        
        print("=" * 80)
        print(f"\n总计: {len(menus)} 个菜单")
        
        # 检查测试管理菜单
        test_menu = await conn.execute(text("SELECT COUNT(*) FROM sys_menu WHERE id = 10"))
        test_count = test_menu.scalar()
        
        if test_count == 0:
            print("\n⚠️  测试管理菜单不存在，请运行: uv run python add_test_menus.py")
        else:
            print("\n✓ 测试管理菜单已存在")


if __name__ == "__main__":
    asyncio.run(check_menus())
