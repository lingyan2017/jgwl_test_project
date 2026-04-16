import sys
import os
sys.path.insert(0, r'D:\\mycode\\myprojects\\project_py\\jgwl_project\\jgwl_test_project')

from sqlalchemy import text
from app.db.session import AsyncSessionLocal

async def test_connection():
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(text(\"SELECT 1\"))
            print(\"数据库连接成功\")
            # 查询测试管理菜单
            result = await db.execute(text(\"SELECT id, menu_name FROM sys_menu WHERE menu_name = '测试管理'\"))
            rows = result.fetchall()
            print(f\"找到测试管理菜单数量: {len(rows)}\")
            for row in rows:
                print(f\"ID: {row[0]}, 名称: {row[1]}\")
    except Exception as e:
        print(f\"数据库连接失败: {e}\")

import asyncio
asyncio.run(test_connection())
