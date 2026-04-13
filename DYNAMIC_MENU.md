# 动态菜单功能实现说明

## 概述

系统已从硬编码菜单升级为从数据库动态加载菜单，实现了基于角色的菜单权限控制。

## 实现原理

### 1. 数据流程

```
用户登录 
  ↓
获取用户信息 + 菜单树 (从 sys_menu 表)
  ↓
存储到 Pinia Store + localStorage
  ↓
根据菜单数据动态生成路由
  ↓
将路由添加到 Vue Router
  ↓
侧边栏根据菜单数据动态渲染
```

### 2. 核心文件

#### 后端
- `app/models/menu.py` - 菜单数据模型
- `app/api/v1/menu.py` - 菜单API接口
  - `GET /menus/tree` - 获取菜单树（所有启用的菜单）
  - `GET /menus/list` - 获取菜单列表（分页）

#### 前端
- `frontend/src/stores/auth.ts` - 认证Store，新增菜单管理
  - `menus` - 存储用户菜单
  - `fetchMenus()` - 从后端获取菜单
  - 登录后自动调用 `fetchMenus()`

- `frontend/src/utils/routes.ts` - 路由工具（新建）
  - `generateRoutes()` - 根据菜单数据生成路由配置
  - `componentMap` - 组件路径映射表
  - `getStoredMenus()` - 从localStorage恢复菜单

- `frontend/src/router/index.ts` - 路由配置
  - 简化为基础路由（login + layout）
  - 路由守卫中动态添加菜单路由
  - 使用 `hasAddedRoutes` 标记避免重复添加

- `frontend/src/layout/index.vue` - 布局组件
  - 移除硬编码菜单
  - 使用 `v-for` 遍历 `authStore.menus` 动态渲染
  - 支持3级菜单嵌套
  - `getIconComponent()` - 动态加载Element Plus图标

## 数据库菜单结构

### sys_menu 表关键字段

| 字段 | 说明 | 示例 |
|------|------|------|
| id | 菜单ID | 10 |
| parent_id | 父菜单ID，0表示顶级 | 0, 10 |
| menu_name | 菜单名称 | 测试管理 |
| menu_type | 菜单类型：1目录 2菜单 3按钮 | 1, 2 |
| path | 路由地址 | /test, test-query-data |
| component | 组件路径 | system/TestQueryDataManage |
| icon | 图标名称（Element Plus图标） | Document, Setting |
| order_num | 显示顺序 | 1, 2 |
| visible | 是否可见：0隐藏 1显示 | 1 |
| status | 是否启用：0禁用 1启用 | 1 |

### 组件路径映射

在 `routes.ts` 的 `componentMap` 中定义：

```typescript
const componentMap: Record<string, any> = {
  'system/TenantManage': () => import('@/views/system/TenantManage.vue'),
  'system/UserManage': () => import('@/views/system/UserManage.vue'),
  'system/TestQueryDataManage': () => import('@/views/system/TestQueryDataManage.vue'),
  // ... 更多组件
}
```

**注意**: 数据库中 `component` 字段的值必须与 `componentMap` 中的key一致。

## 初始化菜单数据

执行以下命令添加测试管理菜单：

```bash
uv run python add_test_menus.py
```

这将添加：
- 测试管理（目录，ID: 10）
- 测试查询数据（菜单，ID: 11）
- 系统配置（菜单，ID: 12）
- 相关权限数据

## 添加新菜单的步骤

### 1. 创建Vue组件
在 `frontend/src/views/` 下创建新组件，例如：
```
frontend/src/views/example/ExampleManage.vue
```

### 2. 更新组件映射
在 `frontend/src/utils/routes.ts` 的 `componentMap` 中添加：
```typescript
'example/ExampleManage': () => import('@/views/example/ExampleManage.vue'),
```

### 3. 添加菜单数据到数据库

方法一：使用SQL
```sql
INSERT INTO sys_menu (parent_id, menu_name, menu_type, path, component, icon, order_num, visible, status) 
VALUES (0, '示例管理', 1, '/example', NULL, 'Folder', 3, 1, 1);

-- 获取刚插入的ID，假设为20
INSERT INTO sys_menu (parent_id, menu_name, menu_type, path, component, icon, order_num, visible, status) 
VALUES (20, '示例列表', 2, 'list', 'example/ExampleManage', 'List', 1, 1, 1);
```

方法二：通过菜单管理界面（需要超级管理员权限）

### 4. 分配菜单给角色
```sql
-- 假设角色ID为1，菜单ID为20和21
INSERT INTO sys_role_menu (role_id, menu_id) VALUES (1, 20), (1, 21);
```

### 5. 刷新页面
用户重新登录后即可看到新菜单。

## 图标使用

支持的图标为 Element Plus Icons，常用图标：
- HomeFilled, Setting, User, Folder, Menu, Lock
- OfficeBuilding, Postcard, UserFilled, Document
- Search, Edit, Delete, Plus, Check

完整列表：https://element-plus.org/zh-CN/component/icon.html

## 注意事项

1. **菜单缓存**: 菜单数据会缓存在 localStorage，清除缓存需重新登录
2. **路由命名**: 确保菜单的 `path` 唯一，避免路由冲突
3. **组件路径**: 数据库中的 `component` 必须与 `componentMap` 中的key完全匹配
4. **权限控制**: 当前实现仅控制菜单显示，接口权限需在后端单独控制
5. **多级菜单**: 当前支持最多3级菜单嵌套

## 优势

✅ 菜单可配置，无需修改代码  
✅ 基于角色的菜单权限控制  
✅ 支持动态增删改菜单  
✅ 菜单缓存提升加载速度  
✅ 统一管理，易于维护
