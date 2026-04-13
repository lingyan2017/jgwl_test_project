-- =============================================
-- 添加测试管理菜单
-- =============================================

USE jgwl_db;

-- 添加测试管理目录菜单
INSERT INTO sys_menu (id, parent_id, menu_name, menu_type, path, component, icon, order_num, perms, visible, status) VALUES
(10, 0, '测试管理', 1, '/test', NULL, 'Document', 2, NULL, 1, 1);

-- 添加测试查询数据菜单
INSERT INTO sys_menu (id, parent_id, menu_name, menu_type, path, component, icon, order_num, perms, visible, status) VALUES
(11, 10, '测试查询数据', 2, 'test-query-data', 'system/TestQueryDataManage', 'Document', 1, 'test:query:list', 1, 1);

-- 添加系统配置菜单
INSERT INTO sys_menu (id, parent_id, menu_name, menu_type, path, component, icon, order_num, perms, visible, status) VALUES
(12, 10, '系统配置', 2, 'sys-config', 'system/SysConfigManage', 'Setting', 2, 'test:config:list', 1, 1);

-- 为超级管理员角色分配新菜单
INSERT INTO sys_role_menu (role_id, menu_id) VALUES
(1, 10), (1, 11), (1, 12);

-- 添加测试管理相关权限
INSERT INTO sys_permission (perm_code, perm_name, perm_type, resource_url, method) VALUES
('test:query:list',     '测试查询列表',   3, '/api/v1/test-query-data/list',          'GET'),
('test:query:create',   '创建测试查询',   3, '/api/v1/test-query-data/create',        'POST'),
('test:query:update',   '更新测试查询',   3, '/api/v1/test-query-data/update/{id}',   'PUT'),
('test:query:delete',   '删除测试查询',   3, '/api/v1/test-query-data/delete/{id}',   'DELETE'),
('test:query:call',     '调用测试接口',   3, '/api/v1/test-query-data/call',          'POST'),
('test:config:list',    '系统配置列表',   3, '/api/v1/sys-config/list',               'GET'),
('test:config:create',  '创建系统配置',   3, '/api/v1/sys-config/create',             'POST'),
('test:config:update',  '更新系统配置',   3, '/api/v1/sys-config/update/{id}',        'PUT'),
('test:config:delete',  '删除系统配置',   3, '/api/v1/sys-config/delete/{id}',        'DELETE');
