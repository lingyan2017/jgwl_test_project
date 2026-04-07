import request from '@/utils/request'
export const getPostList = (params) => request.get('/posts/list', { params })
export const getPost = (id) => request.get(`/posts/get/${id}`)
export const createPost = (data) => request.post('/posts/create', data)
export const updatePost = (id, data) => request.put(`/posts/update/${id}`, data)
export const deletePost = (id) => request.delete(`/posts/delete/${id}`)
