"""测试菜单API"""
import asyncio
import httpx


async def test_menu_api():
    """测试菜单树API"""
    
    BASE_URL = "http://127.0.0.1:8000"
    
    # 先登录获取token
    async with httpx.AsyncClient() as client:
        # 登录
        login_response = await client.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={
                "username": "admin",
                "password": "Admin@123",
                "tenant_id": "default"
            }
        )
        
        if login_response.status_code != 200:
            print(f"登录失败: {login_response.status_code}")
            print(login_response.text)
            return
        
        token_data = login_response.json()
        token = token_data["data"]["access_token"]
        print(f"✓ 登录成功，获取到 token")
        
        # 获取菜单树
        headers = {"Authorization": f"Bearer {token}"}
        menu_response = await client.get(
            f"{BASE_URL}/api/v1/menus/tree",
            headers=headers
        )
        
        if menu_response.status_code != 200:
            print(f"获取菜单失败: {menu_response.status_code}")
            print(menu_response.text)
            return
        
        menu_data = menu_response.json()
        menus = menu_data["data"]
        
        print(f"\n✓ 获取到 {len(menus)} 个顶级菜单\n")
        
        def print_menu(menu, level=0):
            indent = "  " * level
            path = menu.get('path', 'NULL')
            component = menu.get('component', 'NULL')
            children_count = len(menu.get('children', []))
            
            print(f"{indent}ID:{menu['id']:2d} | {menu['menu_name']:<15} | path:{path:<25} | component:{component:<35} | children:{children_count}")
            
            for child in menu.get('children', []):
                print_menu(child, level + 1)
        
        for menu in menus:
            print_menu(menu)
        
        print("\n" + "=" * 120)
        print("预期访问路径:")
        print("=" * 120)
        
        def print_expected_url(menu, parent_path=""):
            current_path = menu.get('path', '')
            if not current_path:
                return
            
            # 构建完整路径
            if parent_path:
                full_path = f"{parent_path}/{current_path}" if not current_path.startswith('/') else current_path
            else:
                full_path = current_path
            
            if menu.get('children'):
                for child in menu['children']:
                    print_expected_url(child, full_path)
            else:
                # 叶子节点，显示完整URL
                url = f"http://localhost:5173{full_path}"
                print(f"{menu['menu_name']:<20} -> {url}")
        
        for menu in menus:
            print_expected_url(menu)


if __name__ == "__main__":
    asyncio.run(test_menu_api())
