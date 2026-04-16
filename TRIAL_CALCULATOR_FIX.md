# 试算测试页面显示问题修复说明

## 问题描述
试算测试菜单在菜单管理中正常显示，但点击后页面无显示。

## 问题原因
1. **前端路由配置缺失**：`frontend/src/router/index.ts` 中缺少试算测试的静态路由配置
2. **默认菜单缺失**：`frontend/src/layout/index.vue` 中的默认菜单（后备菜单）未包含试算测试菜单项

## 修复内容

### 1. 添加静态路由配置
**文件**: `frontend/src/router/index.ts`

在测试管理相关路由部分添加了试算测试路由：
```typescript
{ 
  path: 'test/trial-calculator', 
  name: 'TrialCalculator', 
  component: () => import('@/views/system/TrialCalculator.vue'), 
  meta: { title: '试算测试', requiresAuth: true } 
}
```

### 2. 添加默认菜单项
**文件**: `frontend/src/layout/index.vue`

在测试管理的默认菜单中添加了试算测试菜单项：
```vue
<el-menu-item index="/test/trial-calculator">
  <el-icon><Document /></el-icon>
  <template #title>试算测试</template>
</el-menu-item>
```

### 3. 数据库检查和修复脚本
创建了 `fix_trial_menu.py` 脚本，用于：
- 检查数据库中试算测试菜单配置
- 如果菜单不存在则自动创建
- 验证菜单路径和组件配置
- 确保超级管理员角色有访问权限

## 使用步骤

### 方法一：运行修复脚本（推荐）
```bash
python fix_trial_menu.py
```

该脚本会：
1. 检查数据库中是否存在试算测试菜单
2. 如果不存在则自动创建
3. 验证并修复菜单配置
4. 为超级管理员分配权限

### 方法二：手动执行SQL
如果脚本无法运行，可以手动执行以下SQL：

```sql
-- 插入试算测试菜单
INSERT INTO sys_menu (parent_id, menu_name, menu_type, path, component, icon, order_num, perms, visible, status)
VALUES (9, '试算测试', 2, 'trial-calculator', 'system/TrialCalculator', 'Document', 3, 'test:trial-calculator:list', 1, 1);

-- 为超级管理员角色分配菜单权限
INSERT IGNORE INTO sys_role_menu (role_id, menu_id) 
SELECT 1, id FROM sys_menu WHERE menu_name = '试算测试' AND parent_id = 9;
```

## 验证步骤

1. **重启前端开发服务器**（如果正在运行）
   ```bash
   cd frontend
   npm run dev
   ```

2. **清除浏览器缓存并刷新页面**
   - 按 `Ctrl + Shift + R` (Windows) 或 `Cmd + Shift + R` (Mac) 强制刷新
   - 或者清除浏览器缓存后重新加载

3. **退出并重新登录**
   - 点击右上角用户头像
   - 选择"退出登录"
   - 重新登录系统

4. **检查菜单显示**
   - 查看左侧菜单"测试管理"下是否显示"试算测试"
   - 点击"试算测试"菜单
   - 确认页面正常显示

5. **检查浏览器控制台**
   - 打开开发者工具（F12）
   - 查看Console标签是否有错误
   - 查看Network标签确认 `/api/v1/menus/user-menus` 请求返回的数据中包含试算测试菜单

## 常见问题排查

### 问题1：菜单仍然不显示
**解决方案**：
- 检查数据库连接是否正常
- 运行 `python fix_trial_menu.py` 查看输出信息
- 确认当前用户的角色是否有试算测试菜单权限

### 问题2：点击菜单后页面空白
**解决方案**：
- 检查浏览器控制台是否有路由警告
- 确认 `TrialCalculator.vue` 文件存在于 `frontend/src/views/system/` 目录
- 检查路由路径是否正确：应该是 `/test/trial-calculator`

### 问题3：动态菜单加载失败
**解决方案**：
- 检查后端API `/api/v1/menus/user-menus` 是否正常返回数据
- 查看后端日志是否有错误
- 确认前端已正确配置代理或API地址

## 技术细节

### 路由匹配机制
前端使用两级路由策略：
1. **静态路由**：作为后备，在 `router/index.ts` 中定义
2. **动态路由**：从后端API获取，通过 `addDynamicRoutes()` 动态添加

当动态路由加载失败时，会使用静态路由和默认菜单。

### 菜单路径规则
- 一级菜单（目录）：`/{path}`
- 二级菜单：`/{parent_path}/{child_path}`
- 三级菜单：`/{parent_path}/{child_path}/{grandchild_path}`

例如：
- 测试管理：`/test`
- 试算测试：`/test/trial-calculator`

### 组件加载
组件路径格式：`system/TrialCalculator`
实际文件位置：`frontend/src/views/system/TrialCalculator.vue`

## 相关文件清单

### 前端文件
- `frontend/src/router/index.ts` - 路由配置
- `frontend/src/layout/index.vue` - 布局组件（菜单）
- `frontend/src/views/system/TrialCalculator.vue` - 试算测试页面
- `frontend/src/api/trial.ts` - 试算API接口

### 后端文件
- `app/api/v1/menu.py` - 菜单API
- `app/models/menu.py` - 菜单模型
- `sql/add_trial_calculator_menu.sql` - 菜单初始化SQL

### 工具脚本
- `fix_trial_menu.py` - 菜单检查和修复脚本
- `check_trial_menu.py` - 菜单检查脚本

## 完成时间
2026-04-16
