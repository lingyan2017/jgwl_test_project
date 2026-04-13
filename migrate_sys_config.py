"""
更新 sys_config 表结构的迁移脚本
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.db.session import async_engine


async def migrate():
    """执行数据库迁移"""
    async with async_engine.begin() as conn:
        print("开始迁移 sys_config 表...")
        
        # 1. 删除旧字段
        print("删除旧字段 item_name, item_value...")
        await conn.execute(text("""
            ALTER TABLE sys_config 
            DROP COLUMN IF EXISTS item_name,
            DROP COLUMN IF EXISTS item_value;
        """))
        
        # 2. 添加新字段
        print("添加新字段...")
        await conn.execute(text("""
            ALTER TABLE sys_config
            ADD COLUMN IF NOT EXISTS aes_key VARCHAR(128) NOT NULL DEFAULT '' COMMENT 'aes加密key',
            ADD COLUMN IF NOT EXISTS aes_iv VARCHAR(512) NOT NULL DEFAULT '' COMMENT 'aes加密iv',
            ADD COLUMN IF NOT EXISTS java_domain_name VARCHAR(255) NOT NULL DEFAULT '' COMMENT 'apiservice域名',
            ADD COLUMN IF NOT EXISTS go_domain_name VARCHAR(100) NOT NULL DEFAULT '' COMMENT 'api域名',
            ADD COLUMN IF NOT EXISTS status INT NOT NULL DEFAULT 0 COMMENT '状态 0不可用,1可用',
            ADD COLUMN IF NOT EXISTS run_mode INT NOT NULL DEFAULT 0 COMMENT '0测试环境,1生产环境';
        """))
        
        # 3. 更新索引
        print("更新索引...")
        await conn.execute(text("""
            ALTER TABLE sys_config
            DROP INDEX IF EXISTS idx_item_name,
            ADD INDEX IF NOT EXISTS idx_sys_code (sys_code);
        """))
        
        print("迁移完成！")


if __name__ == "__main__":
    print("警告：此操作将修改数据库结构，请确保已备份数据！")
    confirm = input("是否继续？(yes/no): ")
    
    if confirm.lower() == 'yes':
        try:
            asyncio.run(migrate())
            print("✅ 迁移成功！")
        except Exception as e:
            print(f"❌ 迁移失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("已取消迁移")
