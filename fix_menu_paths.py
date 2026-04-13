"""修复菜单路径配置"""
import asyncio
from sqlalchemy import text
from app.db.session import async_engine


async def fix_menu_paths():
    """修复菜单路径配置"""
    
    async with async_engine.begin() as conn:
        print("=" * 100)
        print("开始修复菜单路径配置...")
        print("=" * 100)
        
        # 查询所有菜单
        result = await conn.execute(text("""
            SELECT id, parent_id, menu_name, path 
            FROM sys_menu 
            WHERE deleted = 0 
            ORDER BY parent_id, id
        """))
        
        menus = result.fetchall()
        
        fixed_count = 0
        
        for menu in menus:
            id_, parent_id, name, path = menu
            
            if not path:
                continue
            
            # 如果是顶级菜单（parent_id == 0），确保使用绝对路径
            if parent_id == 0:
                if not path.startswith('/'):
                    new_path = '/' + path
                    await conn.execute(
                        text("UPDATE sys_menu SET path = :new_path WHERE id = :id"),
                        {"new_path": new_path, "id": id_}
                    )
                    print(f"✓ 修复顶级菜单 [{name}]: {path} -> {new_path}")
                    fixed_count += 1
                else:
                    print(f"  顶级菜单 [{name}] 路径正确: {path}")
            
            # 如果是子菜单，确保使用相对路径（不带 /）
            else:
                if path.startswith('/'):
                    new_path = path.lstrip('/')
                    await conn.execute(
                        text("UPDATE sys_menu SET path = :new_path WHERE id = :id"),
                        {"new_path": new_path, "id": id_}
                    )
                    print(f"✓ 修复子菜单 [{name}]: {path} -> {new_path}")
                    fixed_count += 1
                else:
                    print(f"  子菜单 [{name}] 路径正确: {path}")
        
        print("=" * 100)
        print(f"修复完成！共修复 {fixed_count} 个菜单")
        print("=" * 100)
        
        # 显示修复后的菜单结构
        print("\n修复后的菜单结构:")
        print("-" * 100)
        
        result = await conn.execute(text("""
            SELECT id, parent_id, menu_name, path, component 
            FROM sys_menu 
            WHERE deleted = 0 AND status = 1 AND visible = 1
            ORDER BY parent_id, order_num, id
        """))
        
        all_menus = result.fetchall()
        
        # 按父级分组
        top_menus = [m for m in all_menus if m[1] == 0]
        
        for top in top_menus:
            top_id, _, top_name, top_path, _ = top
            print(f"\n{top_name} (path: {top_path})")
            
            children = [m for m in all_menus if m[1] == top_id]
            for child in children:
                _, _, child_name, child_path, child_comp = child
                full_path = f"{top_path}/{child_path}" if child_path else top_path
                print(f"  └─ {child_name}")
                print(f"     路径: {child_path}")
                print(f"     完整URL: http://localhost:5173{full_path}")
                print(f"     组件: {child_comp or 'N/A'}")


if __name__ == "__main__":
    asyncio.run(fix_menu_paths())
