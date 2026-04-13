# AES 加密接口调用说明

## 功能概述

`/api/v1/test-query-data/call` 接口实现了基于 AES 加密的请求和响应处理：

1. 根据 `sys_code` 和 `language` 查询系统配置
2. 使用配置的 AES key 和 IV 加密请求参数
3. 发送 GET 请求到目标域名（带加密数据）
4. 解密响应数据并返回前端

## 工作流程

```
前端请求 → 后端接收
    ↓
查询 sys_config (根据 sys_code + status=1)
    ↓
选择域名 (java_domain_name 或 go_domain_name)
    ↓
AES 加密 params → encrypted_data
    ↓
GET 请求: {domain}?data={encrypted_data}
    ↓
接收加密响应 → AES 解密
    ↓
返回解密后的数据给前端
    ↓
前端弹窗展示结果
```

## 数据库配置

### sys_config 表字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| aes_key | VARCHAR(128) | AES 加密密钥 (16/24/32 字节) |
| aes_iv | VARCHAR(512) | AES 初始化向量 (16 字节) |
| java_domain_name | VARCHAR(255) | Java 服务域名 |
| go_domain_name | VARCHAR(100) | Go 服务域名 |
| status | INT | 状态: 0-不可用, 1-可用 |
| run_mode | INT | 运行模式: 0-测试环境, 1-生产环境 |
| sys_code | VARCHAR(32) | 系统编码 |

### 配置示例

```sql
INSERT INTO sys_config (
    aes_key, 
    aes_iv, 
    java_domain_name, 
    go_domain_name, 
    status, 
    run_mode, 
    sys_code
) VALUES (
    '1234567890123456',           -- 16字节密钥
    '1234567890123456',           -- 16字节IV
    'http://java-service.com/api',
    'http://go-service.com/api',
    1,                            -- 可用
    0,                            -- 测试环境
    'TEST_SYSTEM'
);
```

## API 使用

### 请求参数

```json
{
  "test_query_data_id": 1,
  "params": {
    "key1": "value1",
    "key2": "value2"
  }
}
```

### 响应格式

**成功响应：**
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "success": true,
    "data": {
      // 解密后的响应数据
    }
  }
}
```

**失败响应：**
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "success": false,
    "error": "错误信息"
  }
}
```

## AES 加密实现

### 加密方式
- 算法：AES-CBC
- 填充：PKCS7
- 输出：Base64 编码

### Python 实现

```python
from app.core.aes_cipher import AESCipher

# 创建加密器
cipher = AESCipher(aes_key, aes_iv)

# 加密 JSON 数据
encrypted = cipher.encrypt_json({"key": "value"})

# 解密数据
decrypted = cipher.decrypt(encrypted_data)
data = cipher.decrypt_json(encrypted_data)
```

## 前端展示

调用接口后，会自动弹出响应结果对话框：

1. **成功**：绿色提示框 + 解密后的数据（JSON 格式化）
2. **失败**：红色提示框 + 错误信息

## 注意事项

1. **密钥安全**：
   - AES key 必须是 16、24 或 32 字节
   - AES iv 必须是 16 字节
   - 建议在生产环境使用环境变量存储密钥

2. **配置要求**：
   - sys_config 中必须存在对应 sys_code 的配置
   - status 必须为 1（可用）
   - 对应的域名必须配置

3. **请求格式**：
   - 始终使用 GET 请求
   - 加密数据通过 URL 参数传递：`?data={encrypted}`

4. **错误处理**：
   - 配置不存在：返回 404
   - 域名未配置：返回 400
   - 加密/解密失败：返回 500
   - 请求失败：记录日志并返回错误信息

## 测试步骤

1. 在 sys_config 表中添加配置
2. 在 test_query_data 表中添加测试数据
3. 前端点击"调用"按钮
4. 查看弹出的响应结果

## 日志记录

所有调用都会记录到 `test_query_data_log` 表：
- request_params: 原始请求参数（JSON）
- response_data: 解密后的响应数据（JSON）
- status: 1-成功, 0-失败
- error_msg: 错误信息（如果有）
