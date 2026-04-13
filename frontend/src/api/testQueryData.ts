import request from '@/utils/request'

// 获取测试查询数据列表
export const getTestQueryDataList = (params: any) => {
  return request({
    url: '/test-query-data/list',
    method: 'get',
    params
  });
};

// 获取单个测试查询数据
export const getTestQueryData = (id: number) => {
  return request({
    url: `/test-query-data/get/${id}`,
    method: 'get'
  });
};

// 创建测试查询数据
export const createTestQueryData = (data: any) => {
  return request({
    url: '/test-query-data/create',
    method: 'post',
    data
  });
};

// 更新测试查询数据
export const updateTestQueryData = (id: number, data: any) => {
  return request({
    url: `/test-query-data/update/${id}`,
    method: 'put',
    data
  });
};

// 删除测试查询数据
export const deleteTestQueryData = (id: number) => {
  return request({
    url: `/test-query-data/delete/${id}`,
    method: 'delete'
  });
};

// 调用测试查询数据
export const callTestQueryData = (data: any) => {
  return request({
    url: '/test-query-data/call',
    method: 'post',
    data
  });
};

// 获取测试查询数据日志
export const getTestQueryDataLogs = (test_query_data_id: number, params: any) => {
  return request({
    url: `/test-query-data/logs/${test_query_data_id}`,
    method: 'get',
    params
  });
};

// 获取最新一条测试查询数据日志（当前用户）
export const getLatestTestQueryDataLog = (test_query_data_id: number) => {
  return request({
    url: `/test-query-data/latest-log/${test_query_data_id}`,
    method: 'get'
  });
};