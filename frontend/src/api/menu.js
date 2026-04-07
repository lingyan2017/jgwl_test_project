import request from '@/utils/request'
export const getMenuList = (params) => request.get('/menus/list', { params })
export const getMenuTree = () => request.get('/menus/tree')
export const getMenu = (id) => request.get(`/menus/get/${id}`)
export const createMenu = (data) => request.post('/menus/create', data)
export const updateMenu = (id, data) => request.put(`/menus/update/${id}`, data)
export const deleteMenu = (id) => request.delete(`/menus/delete/${id}`)
