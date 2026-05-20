import request from '@/utils/request'

export const getSystemConfigList = (params: any) => {
  return request({
    url: '/system-config/list',
    method: 'get',
    params
  });
};

export const getSystemConfig = (id: number) => {
  return request({
    url: `/system-config/get/${id}`,
    method: 'get'
  });
};

export const createSystemConfig = (data: any) => {
  return request({
    url: '/system-config/create',
    method: 'post',
    data
  });
};

export const updateSystemConfig = (id: number, data: any) => {
  return request({
    url: `/system-config/update/${id}`,
    method: 'put',
    data
  });
};

export const deleteSystemConfig = (id: number) => {
  return request({
    url: `/system-config/delete/${id}`,
    method: 'delete'
  });
};
