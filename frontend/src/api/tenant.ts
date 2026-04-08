import request from '@/utils/request'
import type { ApiResponse, PageData, TenantInfo } from '@/types'

export const getTenantList = (params?: Record<string, unknown>) =>
  request.get<unknown, ApiResponse<PageData<TenantInfo>>>('/tenants/list', { params })

export const getTenant = (id: number) =>
  request.get<unknown, ApiResponse<TenantInfo>>(`/tenants/get/${id}`)

export const createTenant = (data: Record<string, unknown>) =>
  request.post<unknown, ApiResponse<TenantInfo>>('/tenants/create', data)

export const updateTenant = (id: number, data: Record<string, unknown>) =>
  request.put<unknown, ApiResponse<TenantInfo>>(`/tenants/update/${id}`, data)

export const deleteTenant = (id: number) =>
  request.delete<unknown, ApiResponse<null>>(`/tenants/delete/${id}`)
