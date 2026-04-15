-- 添加has_image字段到test_query_data表
ALTER TABLE test_query_data ADD COLUMN has_image TINYINT DEFAULT 0 COMMENT '是否包含图片：0-否，1-是';