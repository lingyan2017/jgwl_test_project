import request from '@/utils/request'
export const getRoleList = (params) => request.get('/roles/list', { params })
export const getRole = (id) => request.get(`/roles/get/${id}`)
export const createRole = (data) => request.post('/roles/create', data)
export const updateRole = (id, data) => request.put(`/roles/update/${id}`, data)
export const deleteRole = (id) => request.delete(`/roles/delete/${id}`)
