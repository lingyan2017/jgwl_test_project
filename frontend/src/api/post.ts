import request from '@/utils/request'
import type { ApiResponse, PageData, PostInfo } from '@/types'

export const getPostList = (params?: Record<string, unknown>) =>
  request.get<unknown, ApiResponse<PageData<PostInfo>>>('/posts/list', { params })

export const getPost = (id: number) =>
  request.get<unknown, ApiResponse<PostInfo>>(`/posts/get/${id}`)

export const createPost = (data: Record<string, unknown>) =>
  request.post<unknown, ApiResponse<PostInfo>>('/posts/create', data)

export const updatePost = (id: number, data: Record<string, unknown>) =>
  request.put<unknown, ApiResponse<PostInfo>>(`/posts/update/${id}`, data)

export const deletePost = (id: number) =>
  request.delete<unknown, ApiResponse<null>>(`/posts/delete/${id}`)
