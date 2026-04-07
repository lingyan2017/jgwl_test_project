import request from '@/utils/request'
export const getUserList = (params) => request.get('/users/list', { params })
export const getUser = (id) => request.get(`/users/get/${id}`)
export const createUser = (data) => request.post('/users/create', data)
export const updateUser = (id, data) => request.put(`/users/update/${id}`, data)
export const deleteUser = (id) => request.delete(`/users/delete/${id}`)
export const getUserRoles = (id) => request.get(`/users/roles/${id}`)
