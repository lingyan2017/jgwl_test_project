import request from '@/utils/request'
export const loginApi = (data) => request.post('/auth/login', data)
export const getMeApi = () => request.get('/auth/me')
export const logoutApi = () => request.post('/auth/logout')
