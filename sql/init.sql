-- =============================================
-- JGWL 管理系统 - 数据库初始化脚本
-- 数据库: jgwl_db @ 127.0.0.1:3306
-- =============================================

CREATE DATABASE IF NOT EXISTS jgwl_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE jgwl_db;

-- -------------------------------------------
-- 1. 租户表
-- -------------------------------------------
DROP TABLE IF EXISTS sys_tenant;
CREATE TABLE sys_tenant (
    id          BIGINT       AUTO_INCREMENT PRIMARY KEY,
    tenant_id   VARCHAR(32)  NOT NULL UNIQUE  COMMENT '租户唯一标识',
    tenant_name VARCHAR(128) NOT NULL         COMMENT '租户名称',
    contact_name VARCHAR(64)                  COMMENT '联系人',
    contact_phone VARCHAR(20)                 COMMENT '联系电话',
    contact_email VARCHAR(128)                COMMENT '联系邮箱',
    status      TINYINT      DEFAULT 1        COMMENT '0:禁用 1:启用',
    create_time DATETIME     DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted     TINYINT      DEFAULT 0        COMMENT '0:正常 1:已删除'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='租户表';

-- -------------------------------------------
-- 2. 部门表
-- -------------------------------------------
DROP TABLE IF EXISTS sys_dept;
CREATE TABLE sys_dept (
    id          BIGINT       AUTO_INCREMENT PRIMARY KEY,
    tenant_id   VARCHAR(32)  NOT NULL         COMMENT '租户ID',
    parent_id   BIGINT       DEFAULT 0        COMMENT '父部门ID，0表示顶级',
    dept_name   VARCHAR(64)  NOT NULL         COMMENT '部门名称',
    order_num   INT          DEFAULT 0        COMMENT '显示顺序',
    leader      VARCHAR(64)                   COMMENT '负责人',
    phone       VARCHAR(20)                   COMMENT '联系电话',
    email       VARCHAR(128)                  COMMENT '邮箱',
    status      TINYINT      DEFAULT 1        COMMENT '0:禁用 1:启用',
    create_time DATETIME     DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted     TINYINT      DEFAULT 0,
    INDEX idx_tenant (tenant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='部门表';

-- -------------------------------------------
-- 3. 岗位表
-- -------------------------------------------
DROP TABLE IF EXISTS sys_post;
CREATE TABLE sys_post (
    id          BIGINT       AUTO_INCREMENT PRIMARY KEY,
    tenant_id   VARCHAR(32)  NOT NULL         COMMENT '租户ID',
    post_code   VARCHAR(64)  NOT NULL         COMMENT '岗位编码',
    post_name   VARCHAR(64)  NOT NULL         COMMENT '岗位名称',
    post_sort   INT          DEFAULT 0        COMMENT '显示顺序',
    status      TINYINT      DEFAULT 1        COMMENT '0:禁用 1:启用',
    remark      VARCHAR(500)                  COMMENT '备注',
    create_time DATETIME     DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted     TINYINT      DEFAULT 0,
    INDEX idx_tenant (tenant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='岗位表';

-- -------------------------------------------
-- 4. 角色表
-- -------------------------------------------
DROP TABLE IF EXISTS sys_role;
CREATE TABLE sys_role (
    id          BIGINT       AUTO_INCREMENT PRIMARY KEY,
    tenant_id   VARCHAR(32)  NOT NULL         COMMENT '租户ID',
    role_name   VARCHAR(64)  NOT NULL         COMMENT '角色名称',
    role_key    VARCHAR(64)  NOT NULL         COMMENT '角色标识',
    role_sort   INT          DEFAULT 0        COMMENT '显示顺序',
    data_scope  TINYINT      DEFAULT 1        COMMENT '数据范围:1全部 2自定义 3本部门 4本部门及以下',
    status      TINYINT      DEFAULT 1        COMMENT '0:禁用 1:启用',
    remark      VARCHAR(500)                  COMMENT '备注',
    create_time DATETIME     DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted     TINYINT      DEFAULT 0,
    INDEX idx_tenant (tenant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色表';

-- -------------------------------------------
-- 5. 菜单表（全局，不区分租户）
-- -------------------------------------------
DROP TABLE IF EXISTS sys_menu;
CREATE TABLE sys_menu (
    id          BIGINT       AUTO_INCREMENT PRIMARY KEY,
    parent_id   BIGINT       DEFAULT 0        COMMENT '父菜单ID',
    menu_name   VARCHAR(64)  NOT NULL         COMMENT '菜单名称',
    menu_type   TINYINT                       COMMENT '菜单类型:1目录 2菜单 3按钮',
    path        VARCHAR(256)                  COMMENT '路由地址',
    component   VARCHAR(256)                  COMMENT '组件路径',
    icon        VARCHAR(64)                   COMMENT '菜单图标',
    order_num   INT          DEFAULT 0        COMMENT '显示顺序',
    perms       VARCHAR(256)                  COMMENT '权限标识',
    is_frame    TINYINT      DEFAULT 0        COMMENT '0:否 1:是(外链)',
    visible     TINYINT      DEFAULT 1        COMMENT '0:隐藏 1:显示',
    status      TINYINT      DEFAULT 1        COMMENT '0:禁用 1:启用',
    create_time DATETIME     DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted     TINYINT      DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='菜单表';

-- -------------------------------------------
-- 6. 权限表
-- -------------------------------------------
DROP TABLE IF EXISTS sys_permission;
CREATE TABLE sys_permission (
    id           BIGINT       AUTO_INCREMENT PRIMARY KEY,
    perm_code    VARCHAR(128) NOT NULL UNIQUE COMMENT '权限编码',
    perm_name    VARCHAR(128) NOT NULL        COMMENT '权限名称',
    perm_type    TINYINT      DEFAULT 1       COMMENT '1:菜单 2:按钮 3:接口',
    resource_url VARCHAR(256)                 COMMENT '资源路径',
    method       VARCHAR(16)                  COMMENT 'HTTP方法',
    menu_id      BIGINT                       COMMENT '关联菜单ID',
    status       TINYINT      DEFAULT 1       COMMENT '0:禁用 1:启用',
    create_time  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    update_time  DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted      TINYINT      DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='权限表';

-- -------------------------------------------
-- 7. 用户表
-- -------------------------------------------
DROP TABLE IF EXISTS sys_user;
CREATE TABLE sys_user (
    id          BIGINT       AUTO_INCREMENT PRIMARY KEY,
    tenant_id   VARCHAR(32)  NOT NULL         COMMENT '租户ID',
    username    VARCHAR(64)  NOT NULL         COMMENT '用户名',
    password    VARCHAR(256) NOT NULL         COMMENT '密码(bcrypt)',
    real_name   VARCHAR(64)                   COMMENT '真实姓名',
    avatar      VARCHAR(256)                  COMMENT '头像URL',
    email       VARCHAR(128)                  COMMENT '邮箱',
    phone       VARCHAR(20)                   COMMENT '手机号',
    gender      TINYINT      DEFAULT 0        COMMENT '0:未知 1:男 2:女',
    dept_id     BIGINT                        COMMENT '部门ID',
    post_id     BIGINT                        COMMENT '岗位ID',
    user_type   TINYINT      DEFAULT 2        COMMENT '0:超级管理员 1:租户管理员 2:普通用户',
    status      TINYINT      DEFAULT 1        COMMENT '0:禁用 1:启用',
    last_login  DATETIME                      COMMENT '最后登录时间',
    create_time DATETIME     DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted     TINYINT      DEFAULT 0,
    INDEX idx_tenant (tenant_id),
    UNIQUE KEY uq_username_tenant (username, tenant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- -------------------------------------------
-- 8. 用户-角色关联表
-- -------------------------------------------
DROP TABLE IF EXISTS sys_user_role;
CREATE TABLE sys_user_role (
    id      BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    UNIQUE KEY uq_user_role (user_id, role_id),
    INDEX idx_user (user_id),
    INDEX idx_role (role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户角色关联表';

-- -------------------------------------------
-- 9. 角色-菜单关联表
-- -------------------------------------------
DROP TABLE IF EXISTS sys_role_menu;
CREATE TABLE sys_role_menu (
    id      BIGINT AUTO_INCREMENT PRIMARY KEY,
    role_id BIGINT NOT NULL,
    menu_id BIGINT NOT NULL,
    UNIQUE KEY uq_role_menu (role_id, menu_id),
    INDEX idx_role (role_id),
    INDEX idx_menu (menu_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色菜单关联表';

-- -------------------------------------------
-- 10. 角色-权限关联表
-- -------------------------------------------
DROP TABLE IF EXISTS sys_role_permission;
CREATE TABLE sys_role_permission (
    id      BIGINT AUTO_INCREMENT PRIMARY KEY,
    role_id BIGINT NOT NULL,
    perm_id BIGINT NOT NULL,
    UNIQUE KEY uq_role_perm (role_id, perm_id),
    INDEX idx_role (role_id),
    INDEX idx_perm (perm_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色权限关联表';

-- =============================================
-- 初始化数据
-- =============================================

-- 默认租户
INSERT INTO sys_tenant (tenant_id, tenant_name, contact_name, contact_email, status) VALUES
('default', '默认租户', '超级管理员', 'admin@jgwl.com', 1);

-- 系统菜单
INSERT INTO sys_menu (id, parent_id, menu_name, menu_type, path, component, icon, order_num, perms, visible, status) VALUES
(1,  0, '系统管理', 1, '/system',    NULL,                        'Setting',       1, NULL,                       1, 1),
(2,  1, '租户管理', 2, 'tenant',     'system/TenantManage',       'OfficeBuilding',1, 'system:tenant:list',       1, 1),
(3,  1, '用户管理', 2, 'user',       'system/UserManage',         'User',          2, 'system:user:list',         1, 1),
(4,  1, '部门管理', 2, 'dept',       'system/DeptManage',         'Folder',        3, 'system:dept:list',         1, 1),
(5,  1, '岗位管理', 2, 'post',       'system/PostManage',         'Postcard',      4, 'system:post:list',         1, 1),
(6,  1, '角色管理', 2, 'role',       'system/RoleManage',         'UserFilled',    5, 'system:role:list',         1, 1),
(7,  1, '菜单管理', 2, 'menu',       'system/MenuManage',         'Menu',          6, 'system:menu:list',         1, 1),
(8,  1, '权限管理', 2, 'permission', 'system/PermissionManage',   'Lock',          7, 'system:permission:list',   1, 1);

-- 超级管理员角色
INSERT INTO sys_role (id, tenant_id, role_name, role_key, role_sort, data_scope, status) VALUES
(1, 'default', '超级管理员', 'super_admin', 1, 1, 1);

-- 角色分配所有菜单
INSERT INTO sys_role_menu (role_id, menu_id) VALUES
(1,1),(1,2),(1,3),(1,4),(1,5),(1,6),(1,7),(1,8);

-- 权限数据
INSERT INTO sys_permission (perm_code, perm_name, perm_type, resource_url, method) VALUES
('system:tenant:list',   '租户列表',   3, '/api/v1/tenants/list',        'GET'),
('system:tenant:create', '创建租户',   3, '/api/v1/tenants/create',      'POST'),
('system:tenant:update', '更新租户',   3, '/api/v1/tenants/update/{id}', 'PUT'),
('system:tenant:delete', '删除租户',   3, '/api/v1/tenants/delete/{id}', 'DELETE'),
('system:user:list',     '用户列表',   3, '/api/v1/users/list',          'GET'),
('system:user:create',   '创建用户',   3, '/api/v1/users/create',        'POST'),
('system:user:update',   '更新用户',   3, '/api/v1/users/update/{id}',   'PUT'),
('system:user:delete',   '删除用户',   3, '/api/v1/users/delete/{id}',   'DELETE'),
('system:dept:list',     '部门列表',   3, '/api/v1/depts/list',          'GET'),
('system:dept:create',   '创建部门',   3, '/api/v1/depts/create',        'POST'),
('system:dept:update',   '更新部门',   3, '/api/v1/depts/update/{id}',   'PUT'),
('system:dept:delete',   '删除部门',   3, '/api/v1/depts/delete/{id}',   'DELETE'),
('system:post:list',     '岗位列表',   3, '/api/v1/posts/list',          'GET'),
('system:post:create',   '创建岗位',   3, '/api/v1/posts/create',        'POST'),
('system:post:update',   '更新岗位',   3, '/api/v1/posts/update/{id}',   'PUT'),
('system:post:delete',   '删除岗位',   3, '/api/v1/posts/delete/{id}',   'DELETE'),
('system:role:list',     '角色列表',   3, '/api/v1/roles/list',          'GET'),
('system:role:create',   '创建角色',   3, '/api/v1/roles/create',        'POST'),
('system:role:update',   '更新角色',   3, '/api/v1/roles/update/{id}',   'PUT'),
('system:role:delete',   '删除角色',   3, '/api/v1/roles/delete/{id}',   'DELETE'),
('system:menu:list',     '菜单列表',   3, '/api/v1/menus/list',          'GET'),
('system:menu:create',   '创建菜单',   3, '/api/v1/menus/create',        'POST'),
('system:menu:update',   '更新菜单',   3, '/api/v1/menus/update/{id}',   'PUT'),
('system:menu:delete',   '删除菜单',   3, '/api/v1/menus/delete/{id}',   'DELETE'),
('system:permission:list',   '权限列表', 3, '/api/v1/permissions/list',         'GET'),
('system:permission:create', '创建权限', 3, '/api/v1/permissions/create',       'POST'),
('system:permission:update', '更新权限', 3, '/api/v1/permissions/update/{id}',  'PUT'),
('system:permission:delete', '删除权限', 3, '/api/v1/permissions/delete/{id}',  'DELETE');

-- 注意: admin 用户由 init_db.py 脚本创建（需要bcrypt加密密码）
-- 默认账号: admin / Admin@123  租户: default
