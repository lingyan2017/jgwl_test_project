-- =============================================
-- JGWL 管理系统 - 数据库更新脚本
-- 为试算测试功能添加菜单和权限
-- =============================================

-- 添加试算测试菜单（如果不存在）
INSERT IGNORE INTO sys_menu (parent_id, menu_name, menu_type, path, component, icon, order_num, perms, visible, status) 
SELECT 
    9,                                    -- 父菜单ID（测试管理）
    '试算测试',                           -- 菜单名称
    2,                                    -- 菜单类型（2-菜单项）
    'trial-calculator',                   -- 路径
    'system/TrialCalculator',             -- 组件路径
    'Document',                           -- 图标
    3,                                    -- 排序号
    'test:trial-calculator:list',         -- 权限标识
    1,                                    -- 可见性
    1                                     -- 状态
FROM DUAL 
WHERE EXISTS (SELECT 1 FROM sys_menu WHERE id = 9);

-- 添加试算测试权限（如果不存在）
INSERT IGNORE INTO sys_permission (perm_code, perm_name, perm_type, resource_url, method) VALUES
('test:trial-calculator:list', '试算测试列表', 3, '/api/v1/test-trial/trial-calculate', 'POST');

-- 为超级管理员角色分配试算测试菜单权限（如果不存在）
INSERT IGNORE INTO sys_role_menu (role_id, menu_id) 
SELECT 1, id 
FROM sys_menu 
WHERE menu_name = '试算测试' AND parent_id = 9;

-- 为超级管理员角色分配试算测试权限（如果不存在）
INSERT IGNORE INTO sys_role_permission (role_id, perm_id) 
SELECT 1, id 
FROM sys_permission 
WHERE perm_code = 'test:trial-calculator:list';