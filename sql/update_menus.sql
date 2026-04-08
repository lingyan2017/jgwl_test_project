-- =============================================
-- JGWL 管理系统 - 数据库更新脚本
-- 为测试查询数据和系统配置功能添加菜单和权限
-- =============================================

-- 添加测试管理顶级菜单
INSERT INTO sys_menu (id, parent_id, menu_name, menu_type, path, component, icon, order_num, perms, visible, status) VALUES
(9, 0, '测试管理', 1, '/test', NULL, 'Document', 3, NULL, 1, 1);

-- 添加测试查询数据和系统配置菜单到测试管理下
INSERT INTO sys_menu (parent_id, menu_name, menu_type, path, component, icon, order_num, perms, visible, status) VALUES
(9, '测试查询数据', 2, 'test-query-data', 'system/TestQueryDataManage', 'Document', 1, 'test:test-query-data:list', 1, 1),
(10, '系统配置',    2, 'sys-config',     'system/SysConfigManage',     'Setting', 2, 'test:sys-config:list',     1, 1);

-- 添加对应的权限
INSERT INTO sys_permission (perm_code, perm_name, perm_type, resource_url, method) VALUES
-- 测试查询数据权限
('test:test-query-data:list',     '测试查询数据列表', 3, '/api/v1/test-query-data/list',          'GET'),
('test:test-query-data:get',      '获取测试查询数据', 3, '/api/v1/test-query-data/get/{id}',      'GET'),
('test:test-query-data:create',   '创建测试查询数据', 3, '/api/v1/test-query-data/create',        'POST'),
('test:test-query-data:update',   '更新测试查询数据', 3, '/api/v1/test-query-data/update/{id}',   'PUT'),
('test:test-query-data:delete',   '删除测试查询数据', 3, '/api/v1/test-query-data/delete/{id}',   'DELETE'),
('test:test-query-data:call',     '调用测试查询数据', 3, '/api/v1/test-query-data/call',          'POST'),
('test:test-query-data:logs',     '测试查询数据日志', 3, '/api/v1/test-query-data/logs/{id}',     'GET'),

-- 系统配置权限
('test:sys-config:list',     '系统配置列表', 3, '/api/v1/sys-config/list',          'GET'),
('test:sys-config:get',      '获取系统配置', 3, '/api/v1/sys-config/get/{id}',      'GET'),
('test:sys-config:create',   '创建系统配置', 3, '/api/v1/sys-config/create',        'POST'),
('test:sys-config:update',   '更新系统配置', 3, '/api/v1/sys-config/update/{id}',   'PUT'),
('test:sys-config:delete',   '删除系统配置', 3, '/api/v1/sys-config/delete/{id}',   'DELETE');

-- 为超级管理员角色分配新菜单权限
INSERT IGNORE INTO sys_role_menu (role_id, menu_id) VALUES
(1, 9),  -- 测试管理菜单
(1, 10), -- 系统配置菜单
(1, (SELECT id FROM sys_menu WHERE path = 'test-query-data' AND parent_id = 9)); -- 测试查询数据菜单

-- 为超级管理员角色分配新权限
INSERT IGNORE INTO sys_role_permission (role_id, perm_id) VALUES
(1, (SELECT id FROM sys_permission WHERE perm_code = 'test:test-query-data:list')),
(1, (SELECT id FROM sys_permission WHERE perm_code = 'test:test-query-data:get')),
(1, (SELECT id FROM sys_permission WHERE perm_code = 'test:test-query-data:create')),
(1, (SELECT id FROM sys_permission WHERE perm_code = 'test:test-query-data:update')),
(1, (SELECT id FROM sys_permission WHERE perm_code = 'test:test-query-data:delete')),
(1, (SELECT id FROM sys_permission WHERE perm_code = 'test:test-query-data:call')),
(1, (SELECT id FROM sys_permission WHERE perm_code = 'test:test-query-data:logs')),
(1, (SELECT id FROM sys_permission WHERE perm_code = 'test:sys-config:list')),
(1, (SELECT id FROM sys_permission WHERE perm_code = 'test:sys-config:get')),
(1, (SELECT id FROM sys_permission WHERE perm_code = 'test:sys-config:create')),
(1, (SELECT id FROM sys_permission WHERE perm_code = 'test:sys-config:update')),
(1, (SELECT id FROM sys_permission WHERE perm_code = 'test:sys-config:delete'));