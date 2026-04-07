import request from '@/utils/request'
export const getPermissionList = (params) => request.get('/permissions/list', { params })
export const getPermission = (id) => request.get(`/permissions/get/${id}`)
export const createPermission = (data) => request.post('/permissions/create', data)
export const updatePermission = (id, data) => request.put(`/permissions/update/${id}`, data)
export const deletePermission = (id) => request.delete(`/permissions/delete/${id}`)
