"""诊断二级菜单白板问题"""
import asyncio
from sqlalchemy import text
from app.db.session import engine


async def diagnose_menu_issue():
    """诊断菜单配置问题"""
    
    print("=" * 120)
    print("开始诊断二级菜单白板问题...")
    print("=" * 120)
    
    async with engine.begin() as conn:
        # 查询所有菜单
        result = await conn.execute(text("""
            SELECT id, parent_id, menu_name, menu_type, path, component, icon, order_num, visible, status 
            FROM sys_menu 
            WHERE deleted = 0 
            ORDER BY parent_id, order_num, id
        """))
        
        menus = result.fetchall()
        
        print("\n【1. 数据库中的菜单配置】")
        print("-" * 120)
        print(f"{'ID':<5} {'Parent':<8} {'Name':<20} {'Type':<6} {'Path':<30} {'Component':<40}")
        print("-" * 120)
        
        for menu in menus:
            id_, parent_id, name, mtype, path, component, icon, order_num, visible, status = menu
            path_str = path or "NULL"
            comp_str = component or "NULL"
            print(f"{id_:<5} {parent_id:<8} {name:<20} {mtype or 'N/A':<6} {path_str:<30} {comp_str:<40}")
        
        # 找出顶级菜单和子菜单
        top_menus = [m for m in menus if m[1] == 0]
        child_menus = [m for m in menus if m[1] != 0]
        
        print(f"\n顶级菜单数量: {len(top_menus)}")
        print(f"子菜单数量: {len(child_menus)}")
        
        print("\n【2. 检查子菜单路径配置】")
        print("-" * 120)
        
        issues_found = []
        
        for child in child_menus:
            child_id = child[0]
            parent_id = child[1]
            child_name = child[2]
            child_path = child[4]
            child_component = child[5]
            
            # 找到父菜单
            parent = next((m for m in menus if m[0] == parent_id), None)
            if not parent:
                print(f"⚠️  [{child_name}] 找不到父菜单 (parent_id={parent_id})")
                issues_found.append(f"菜单 '{child_name}' 的父菜单不存在")
                continue
            
            parent_name = parent[2]
            parent_path = parent[4]
            
            print(f"\n菜单: {child_name}")
            print(f"  父菜单: {parent_name} (path={parent_path})")
            print(f"  当前path: {child_path or 'NULL'}")
            print(f"  当前component: {child_component or 'NULL'}")
            
            # 检查问题
            if not child_path:
                print(f"  ❌ 错误: 子菜单path为空!")
                issues_found.append(f"菜单 '{child_name}' 的path为空")
            elif child_path.startswith('/'):
                print(f"  ❌ 错误: 子菜单path不应该以'/'开头! 应该是相对路径")
                print(f"     建议修改为: {child_path.lstrip('/')}")
                issues_found.append(f"菜单 '{child_name}' 的path不应该以'/'开头")
            else:
                full_path = f"{parent_path}/{child_path}"
                print(f"  ✓ 完整访问路径: {full_path}")
            
            if not child_component:
                print(f"  ⚠️  警告: component为空")
            elif child_component == 'Layout':
                print(f"  ⚠️  警告: component='Layout'，子菜单应该有具体组件")
            else:
                print(f"  ✓ Component: {child_component}")
        
        print("\n【3. 前端路由预期配置】")
        print("-" * 120)
        print("前端期望的路由结构:")
        print("  - 顶级菜单(目录): path = '/test', component = 'Layout' 或 NULL")
        print("  - 子菜单(页面): path = 'test-query-data' (相对路径, 不带/), component = 'system/TestQueryDataManage'")
        print("  - 最终访问URL: /test/test-query-data")
        
        print("\n【4. 常见问题检查】")
        print("-" * 120)
        
        # 检查是否有子菜单的path以/开头
        absolute_path_menus = [m for m in child_menus if m[4] and m[4].startswith('/')]
        if absolute_path_menus:
            print(f"❌ 发现 {len(absolute_path_menus)} 个子菜单使用了绝对路径(以/开头):")
            for m in absolute_path_menus:
                print(f"   - {m[2]}: path='{m[4]}'")
        else:
            print("✓ 所有子菜单都使用相对路径")
        
        # 检查是否有子菜单没有component
        no_component_menus = [m for m in child_menus if not m[5]]
        if no_component_menus:
            print(f"\n⚠️  发现 {len(no_component_menus)} 个子菜单没有component:")
            for m in no_component_menus:
                print(f"   - {m[2]} (ID={m[0]})")
        else:
            print("\n✓ 所有子菜单都有component配置")
        
        # 检查component是否在映射表中
        valid_components = [
            'Layout',
            'system/TenantManage', 'system/UserManage', 'system/DeptManage', 
            'system/PostManage', 'system/RoleManage', 'system/MenuManage', 
            'system/PermissionManage', 'system/TestQueryDataManage', 'system/SysConfigManage',
            'Dashboard'
        ]
        invalid_components = [m for m in child_menus if m[5] and m[5] not in valid_components]
        if invalid_components:
            print(f"\n❌ 发现 {len(invalid_components)} 个子菜单的component不在映射表中:")
            for m in invalid_components:
                print(f"   - {m[2]}: component='{m[5]}'")
                print(f"      有效的components: {', '.join(valid_components)}")
        else:
            print("\n✓ 所有component都在前端映射表中")
        
        print("\n" + "=" * 120)
        print("【诊断总结】")
        print("=" * 120)
        
        if issues_found:
            print(f"发现 {len(issues_found)} 个问题:")
            for i, issue in enumerate(issues_found, 1):
                print(f"  {i}. {issue}")
            print("\n请修复上述问题后刷新浏览器测试")
        else:
            print("✓ 数据库配置看起来正常")
            print("\n如果仍然白屏，可能的原因:")
            print("  1. 浏览器缓存未清除 - 请强制刷新 (Ctrl+F5)")
            print("  2. 前端路由守卫未正确添加动态路由 - 检查浏览器控制台日志")
            print("  3. 组件加载失败 - 检查浏览器控制台是否有组件加载错误")
            print("  4. localStorage中的菜单数据过期 - 请退出登录后重新登录")


if __name__ == "__main__":
    asyncio.run(diagnose_menu_issue())
