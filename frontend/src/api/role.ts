import request from '@/utils/request'
import type { ApiResponse, PageData, RoleInfo } from '@/types'

export const getRoleList = (params?: Record<string, unknown>) =>
  request.get<unknown, ApiResponse<PageData<RoleInfo>>>('/roles/list', { params })

export const getRole = (id: number) =>
  request.get<unknown, ApiResponse<RoleInfo>>(`/roles/get/${id}`)

export const createRole = (data: Record<string, unknown>) =>
  request.post<unknown, ApiResponse<RoleInfo>>('/roles/create', data)

export const updateRole = (id: number, data: Record<string, unknown>) =>
  request.put<unknown, ApiResponse<RoleInfo>>(`/roles/update/${id}`, data)

export const deleteRole = (id: number) =>
  request.delete<unknown, ApiResponse<null>>(`/roles/delete/${id}`)
