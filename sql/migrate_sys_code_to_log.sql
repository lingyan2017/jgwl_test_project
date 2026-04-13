-- 修改 test_query_data 表结构：移除 sys_code 字段，添加 url_desc 字段
-- 修改 test_query_data_log 表结构：添加 sys_code 字段
-- 执行时间: 2026-04-13

-- 1. 为 test_query_data 表添加 url_desc 字段（如果不存在）
ALTER TABLE test_query_data 
ADD COLUMN url_desc VARCHAR(256) COMMENT 'URL说明' AFTER url;

-- 2. 从 test_query_data 表删除 sys_code 字段
ALTER TABLE test_query_data 
DROP COLUMN sys_code;

-- 3. 为 test_query_data_log 表添加 sys_code 字段
ALTER TABLE test_query_data_log 
ADD COLUMN sys_code VARCHAR(32) NOT NULL COMMENT '系统编码' AFTER test_query_data_id;

-- 4. 更新现有日志数据的 sys_code（可选，根据实际需求调整）
-- UPDATE test_query_data_log tql 
-- INNER JOIN test_query_data tqd ON tql.test_query_data_id = tqd.id 
-- SET tql.sys_code = tqd.sys_code;

-- 注意：如果 test_query_data 表中已有数据，需要先备份 sys_code 到日志表
-- 然后再删除 test_query_data 表的 sys_code 字段
