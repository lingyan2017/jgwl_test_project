"""修复子菜单路径为相对路径"""
import asyncio
from sqlalchemy import text
from app.db.session import engine


async def fix_child_menu_paths():
    """修复子菜单的路径配置"""
    
    print("=" * 120)
    print("开始修复子菜单路径...")
    print("=" * 120)
    
    async with engine.begin() as conn:
        # 查询所有菜单
        result = await conn.execute(text("""
            SELECT id, parent_id, menu_name, path 
            FROM sys_menu 
            WHERE deleted = 0 
            ORDER BY parent_id, order_num, id
        """))
        
        menus = result.fetchall()
        
        # 找出所有子菜单（parent_id != 0）
        child_menus = [m for m in menus if m[1] != 0]
        
        print(f"\n找到 {len(child_menus)} 个子菜单")
        print("-" * 120)
        
        fixed_count = 0
        
        for child in child_menus:
            child_id = child[0]
            parent_id = child[1]
            child_name = child[2]
            child_path = child[3]
            
            if not child_path:
                print(f"⚠️  [{child_name}] (ID={child_id}): path为空，跳过")
                continue
            
            # 检查是否以 / 开头
            if child_path.startswith('/'):
                # 需要修复：去掉开头的 /
                new_path = child_path.lstrip('/')
                print(f"🔧 修复 [{child_name}] (ID={child_id}): '{child_path}' -> '{new_path}'")
                
                # 执行更新
                await conn.execute(
                    text("UPDATE sys_menu SET path = :path WHERE id = :id"),
                    {"path": new_path, "id": child_id}
                )
                fixed_count += 1
            else:
                print(f"✓ [{child_name}] (ID={child_id}): path='{child_path}' 已经是相对路径")
        
        print("\n" + "=" * 120)
        print(f"修复完成！共修复 {fixed_count} 个菜单")
        print("=" * 120)
        
        if fixed_count > 0:
            print("\n✅ 请执行以下操作:")
            print("  1. 退出登录")
            print("  2. 清除浏览器缓存 (Ctrl+Shift+Delete)")
            print("  3. 重新登录")
            print("  4. 测试二级菜单是否正常显示")
        else:
            print("\n✓ 所有子菜单路径配置正确，无需修复")
            print("\n如果仍然白屏，请检查:")
            print("  1. 浏览器控制台是否有错误信息")
            print("  2. localStorage 中的菜单数据是否过期（建议退出重登）")


if __name__ == "__main__":
    asyncio.run(fix_child_menu_paths())
