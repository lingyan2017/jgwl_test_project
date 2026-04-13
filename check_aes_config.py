"""
检查并修复 sys_config 表中的 AES 配置
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text, select
from app.db.session import async_engine
from app.models.sys_config import SysConfig


async def check_and_fix():
    """检查并修复 AES 配置"""
    async with async_engine.begin() as conn:
        print("=" * 80)
        print("检查 sys_config 表中的 AES 配置")
        print("=" * 80)
        
        # 查询所有配置
        result = await conn.execute(select(SysConfig))
        configs = result.scalars().all()
        
        if not configs:
            print("\n❌ sys_config 表中没有数据")
            return
        
        print(f"\n找到 {len(configs)} 条配置:\n")
        
        for config in configs:
            print(f"ID: {config.id}")
            print(f"  sys_code: {config.sys_code}")
            print(f"  status: {config.status}")
            print(f"  run_mode: {config.run_mode}")
            print(f"  aes_key 长度: {len(config.aes_key)} bytes")
            print(f"  aes_iv 长度: {len(config.aes_iv)} bytes")
            print(f"  java_domain_name: {config.java_domain_name}")
            print(f"  go_domain_name: {config.go_domain_name}")
            
            # 检查密钥长度
            key_len = len(config.aes_key)
            iv_len = len(config.aes_iv)
            
            issues = []
            if key_len not in [16, 24, 32]:
                issues.append(f"❌ aes_key 长度 {key_len} 不合法（需要 16/24/32）")
            else:
                issues.append(f"✅ aes_key 长度 {key_len} 正确")
            
            if iv_len != 16:
                issues.append(f"❌ aes_iv 长度 {iv_len} 不合法（需要 16）")
            else:
                issues.append(f"✅ aes_iv 长度 {iv_len} 正确")
            
            for issue in issues:
                print(f"  {issue}")
            
            print()
        
        # 询问是否修复
        has_issues = any(
            len(c.aes_key) not in [16, 24, 32] or len(c.aes_iv) != 16 
            for c in configs
        )
        
        if has_issues:
            print("\n" + "=" * 80)
            print("发现配置问题！")
            print("=" * 80)
            print("\n建议操作：")
            print("1. 手动更新数据库中的 aes_iv 为 16 字节")
            print("2. 或者运行以下 SQL：")
            print("\n   UPDATE sys_config SET aes_iv = '1234567890123456' WHERE id = <id>;")
            print("\n注意：aes_iv 必须正好是 16 字节（16个字符）")
            print("      aes_key 可以是 16、24 或 32 字节")
        else:
            print("\n✅ 所有配置都正确！")


if __name__ == "__main__":
    try:
        asyncio.run(check_and_fix())
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
