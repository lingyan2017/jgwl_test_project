import request from '@/utils/request'
export const getTenantList = (params) => request.get('/tenants/list', { params })
export const getTenant = (id) => request.get(`/tenants/get/${id}`)
export const createTenant = (data) => request.post('/tenants/create', data)
export const updateTenant = (id, data) => request.put(`/tenants/update/${id}`, data)
export const deleteTenant = (id) => request.delete(`/tenants/delete/${id}`)
