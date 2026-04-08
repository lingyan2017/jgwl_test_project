import request from '@/utils/request'

// 获取系统配置列表
export const getSysConfigList = (params: any) => {
  return request({
    url: '/api/v1/sys-config/list',
    method: 'get',
    params
  });
};

// 获取单个系统配置
export const getSysConfig = (id: number) => {
  return request({
    url: `/api/v1/sys-config/get/${id}`,
    method: 'get'
  });
};

// 创建系统配置
export const createSysConfig = (data: any) => {
  return request({
    url: '/api/v1/sys-config/create',
    method: 'post',
    data
  });
};

// 更新系统配置
export const updateSysConfig = (id: number, data: any) => {
  return request({
    url: `/api/v1/sys-config/update/${id}`,
    method: 'put',
    data
  });
};

// 删除系统配置
export const deleteSysConfig = (id: number) => {
  return request({
    url: `/api/v1/sys-config/delete/${id}`,
    method: 'delete'
  });
};