import request from '@/utils/request'
import type { ApiResponse, PageData, UserInfo } from '@/types'

export const getUserList = (params?: Record<string, unknown>) =>
  request.get<unknown, ApiResponse<PageData<UserInfo>>>('/users/list', { params })

export const getUser = (id: number) =>
  request.get<unknown, ApiResponse<UserInfo>>(`/users/get/${id}`)

export const createUser = (data: Record<string, unknown>) =>
  request.post<unknown, ApiResponse<UserInfo>>('/users/create', data)

export const updateUser = (id: number, data: Record<string, unknown>) =>
  request.put<unknown, ApiResponse<UserInfo>>(`/users/update/${id}`, data)

export const deleteUser = (id: number) =>
  request.delete<unknown, ApiResponse<null>>(`/users/delete/${id}`)

export const getUserRoles = (id: number) =>
  request.get<unknown, ApiResponse<number[]>>(`/users/roles/${id}`)
