import request from '@/utils/request'
export const getDeptList = (params) => request.get('/depts/list', { params })
export const getDeptTree = (params) => request.get('/depts/tree', { params })
export const getDept = (id) => request.get(`/depts/get/${id}`)
export const createDept = (data) => request.post('/depts/create', data)
export const updateDept = (id, data) => request.put(`/depts/update/${id}`, data)
export const deleteDept = (id) => request.delete(`/depts/delete/${id}`)
