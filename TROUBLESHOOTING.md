# 动态菜单故障排查指南

## 问题：访问 http://localhost:5173/test-query-data 加载不出来

### 原因分析

1. **路径错误** ❌
   - 错误路径：`/test-query-data`
   - 正确路径：`/test/test-query-data`
   
2. **数据库缺少菜单数据** ❌
   - 需要先运行脚本添加测试管理菜单

3. **浏览器缓存了旧菜单** ❌
   - localStorage 中可能缓存了旧的菜单数据

---

## 解决步骤

### 步骤 1：添加菜单数据到数据库

在项目根目录执行：
```bash
uv run python add_test_menus.py
```

预期输出：
```
开始添加测试管理菜单...
✓ 测试管理菜单添加成功！
  - 测试管理 (ID: 10)
  - 测试查询数据 (ID: 11)
  - 系统配置 (ID: 12)
  - 相关权限已添加
```

如果提示"测试管理菜单已存在"，说明数据已经添加过了。

### 步骤 2：检查菜单数据

执行检查脚本：
```bash
uv run python check_menus.py
```

应该能看到类似输出：
```
================================================================================
菜单列表:
================================================================================
ID    Parent   Name            Type   Path                      Component                      Icon           
--------------------------------------------------------------------------------
1     0        系统管理         1      /system                   NULL                           Setting        
2     1        租户管理         2      tenant                    system/TenantManage            OfficeBuilding 
...
10    0        测试管理         1      /test                     NULL                           Document       
11    10       测试查询数据     2      test-query-data           system/TestQueryDataManage     Document       
12    10       系统配置         2      sys-config                system/SysConfigManage         Setting        
================================================================================

总计: 11 个菜单

✓ 测试管理菜单已存在
```

### 步骤 3：清除浏览器缓存

1. 打开浏览器开发者工具（F12）
2. 进入 Application/Storage 标签
3. 找到 Local Storage → http://localhost:5173
4. 删除以下键：
   - `menus`
   - `token`
   - `user`
5. 或者直接在控制台执行：
   ```javascript
   localStorage.clear()
   ```

### 步骤 4：重新登录

1. 访问 http://localhost:5173/login
2. 使用管理员账号登录（admin / Admin@123）
3. 登录后会自动获取菜单并生成路由

### 步骤 5：验证菜单

登录成功后，左侧边栏应该显示：
- 🏠 首页
- ⚙️ 系统管理（可展开）
  - 租户管理
  - 用户管理
  - ...
- 📄 测试管理（可展开）
  - 测试查询数据
  - 系统配置

### 步骤 6：访问测试页面

点击侧边栏的 "测试管理" → "测试查询数据"，或直接在地址栏输入：
```
http://localhost:5173/test/test-query-data
```

---

## 常见问题

### Q1: 控制台报错 "未找到组件: xxx"

**原因**: `componentMap` 中没有对应的组件映射

**解决**: 在 `frontend/src/utils/routes.ts` 的 `componentMap` 中添加：
```typescript
'你的组件路径': () => import('@/views/你的组件.vue'),
```

### Q2: 登录后看不到菜单

**原因**: 
1. 数据库中没有菜单数据
2. 用户角色没有分配菜单权限

**解决**:
```sql
-- 检查菜单是否存在
SELECT * FROM sys_menu WHERE deleted = 0;

-- 检查角色菜单关联
SELECT rm.*, m.menu_name 
FROM sys_role_menu rm
JOIN sys_menu m ON rm.menu_id = m.id
WHERE rm.role_id = 1;  -- 替换为你的角色ID
```

### Q3: 路由跳转404

**原因**: 动态路由未正确添加

**解决**:
1. 打开浏览器控制台
2. 查看是否有 "动态路由添加成功: X 个路由" 的日志
3. 如果没有，检查路由守卫是否执行
4. 清除缓存后重新登录

### Q4: 菜单显示了但点击没反应

**原因**: 路由 path 配置错误

**解决**: 检查数据库中菜单的 `path` 字段：
- 顶级菜单：`/test`（带斜杠）
- 子菜单：`test-query-data`（不带斜杠，相对路径）

---

## 调试技巧

### 查看当前菜单数据

在浏览器控制台执行：
```javascript
console.log('Menus:', JSON.parse(localStorage.getItem('menus')))
```

### 查看当前路由

在浏览器控制台执行：
```javascript
// Vue 3
console.log('Routes:', window.$router?.getRoutes())
// 或在组件内
import { useRouter } from 'vue-router'
const router = useRouter()
console.log(router.getRoutes())
```

### 手动触发菜单刷新

在浏览器控制台执行：
```javascript
// 清除缓存
localStorage.removeItem('menus')
// 刷新页面
location.reload()
```

---

## 快速修复命令

如果还是不行，执行以下完整流程：

```bash
# 1. 确保菜单数据存在
uv run python add_test_menus.py

# 2. 检查菜单数据
uv run python check_menus.py

# 3. 重启前端开发服务器
# Ctrl+C 停止当前服务，然后重新启动
cd frontend
npm run dev
```

然后在浏览器中：
1. 清除 localStorage
2. 重新登录
3. 访问 http://localhost:5173/test/test-query-data
