import request from '@/utils/request'
import type { ApiResponse, PageData, PermissionInfo } from '@/types'

export const getPermissionList = (params?: Record<string, unknown>) =>
  request.get<unknown, ApiResponse<PageData<PermissionInfo>>>('/permissions/list', { params })

export const getPermission = (id: number) =>
  request.get<unknown, ApiResponse<PermissionInfo>>(`/permissions/get/${id}`)

export const createPermission = (data: Record<string, unknown>) =>
  request.post<unknown, ApiResponse<PermissionInfo>>('/permissions/create', data)

export const updatePermission = (id: number, data: Record<string, unknown>) =>
  request.put<unknown, ApiResponse<PermissionInfo>>(`/permissions/update/${id}`, data)

export const deletePermission = (id: number) =>
  request.delete<unknown, ApiResponse<null>>(`/permissions/delete/${id}`)
