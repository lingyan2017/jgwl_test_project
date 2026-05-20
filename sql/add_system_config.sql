-- =============================================
-- JGWL 管理系统 - 数据库更新脚本
-- 1. 创建 system_config 表
-- 2. 为系统配置项功能添加菜单和权限
-- =============================================

-- 创建 system_config 表
CREATE TABLE IF NOT EXISTS `system_config` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `item_name` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '配置项名称',
  `description` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '配置项的简要描述',
  `item_type` tinyint(4) NOT NULL COMMENT '配置项数据类型',
  `item_value` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '配置项值',
  `weight` int(11) NOT NULL DEFAULT '0' COMMENT '显示权重',
  `version` int(11) NOT NULL COMMENT '版本号',
  `status` tinyint(4) NOT NULL COMMENT '是否有效.0: 无效; 1: 有效',
  `online_time` bigint(20) unsigned NOT NULL COMMENT '上线时间',
  `offline_time` bigint(20) unsigned NOT NULL COMMENT '下线时间',
  `ctime` bigint(20) unsigned NOT NULL COMMENT '记录创建时间',
  `utime` bigint(20) unsigned NOT NULL COMMENT '记录更新时间',
  `op_uid` bigint(20) unsigned NOT NULL DEFAULT '0',
  `remark` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '备注',
  `sys_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '平台标识 公共为common 单平台的为平台自己标识',
  `quarantine` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '排除的平台，有些平台不使用公共的，用sys_code+","号分割',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `item_name` (`item_name`,`version`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统参数配置';

-- 添加系统配置项菜单（如果不存在）
INSERT IGNORE INTO sys_menu (parent_id, menu_name, menu_type, path, component, icon, order_num, perms, visible, status)
SELECT
    9,                                    -- 父菜单ID（测试管理）
    '系统配置项',                          -- 菜单名称
    2,                                    -- 菜单类型（2-菜单项）
    'system-config',                      -- 路径
    'system/SystemConfigManage',          -- 组件路径
    'Setting',                            -- 图标
    5,                                    -- 排序号
    'test:system-config:list',            -- 权限标识
    1,                                    -- 可见性
    1                                     -- 状态
FROM DUAL
WHERE EXISTS (SELECT 1 FROM sys_menu WHERE id = 9);

-- 添加系统配置项权限（如果不存在）
INSERT IGNORE INTO sys_permission (perm_code, perm_name, perm_type, resource_url, method) VALUES
('test:system-config:list',   '系统配置项列表', 3, '/api/v1/system-config/list',      'GET'),
('test:system-config:create', '系统配置项新增', 3, '/api/v1/system-config/create',    'POST'),
('test:system-config:update', '系统配置项编辑', 3, '/api/v1/system-config/update/*',  'PUT'),
('test:system-config:delete', '系统配置项删除', 3, '/api/v1/system-config/delete/*',  'DELETE');

-- 为超级管理员角色分配系统配置项菜单权限（如果不存在）
INSERT IGNORE INTO sys_role_menu (role_id, menu_id)
SELECT 1, id
FROM sys_menu
WHERE menu_name = '系统配置项' AND parent_id = 9;

-- 为超级管理员角色分配系统配置项所有权限（如果不存在）
INSERT IGNORE INTO sys_role_permission (role_id, perm_id)
SELECT 1, id
FROM sys_permission
WHERE perm_code LIKE 'test:system-config:%';
