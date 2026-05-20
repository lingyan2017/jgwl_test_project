-- =============================================
-- JGWL 管理系统 - 数据库更新脚本
-- 为STP/OPM支付测试功能添加菜单和权限
-- =============================================

-- 添加支付测试菜单（如果不存在）
INSERT IGNORE INTO sys_menu (parent_id, menu_name, menu_type, path, component, icon, order_num, perms, visible, status)
SELECT
    9,                                    -- 父菜单ID（测试管理）
    '支付测试',                           -- 菜单名称
    2,                                    -- 菜单类型（2-菜单项）
    'payment-test',                       -- 路径
    'system/PaymentTest',                 -- 组件路径
    'Money',                              -- 图标
    4,                                    -- 排序号
    'test:payment-test:list',             -- 权限标识
    1,                                    -- 可见性
    1                                     -- 状态
FROM DUAL
WHERE EXISTS (SELECT 1 FROM sys_menu WHERE id = 9);

-- 添加支付测试权限（如果不存在）
INSERT IGNORE INTO sys_permission (perm_code, perm_name, perm_type, resource_url, method) VALUES
('test:payment-test:list', '支付测试', 3, '/api/v1/payment-test/test-payment', 'POST');

-- 为超级管理员角色分配支付测试菜单权限（如果不存在）
INSERT IGNORE INTO sys_role_menu (role_id, menu_id)
SELECT 1, id
FROM sys_menu
WHERE menu_name = '支付测试' AND parent_id = 9;

-- 为超级管理员角色分配支付测试权限（如果不存在）
INSERT IGNORE INTO sys_role_permission (role_id, perm_id)
SELECT 1, id
FROM sys_permission
WHERE perm_code = 'test:payment-test:list';
