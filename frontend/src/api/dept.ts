import request from '@/utils/request'
import type { ApiResponse, PageData, DeptInfo } from '@/types'

export const getDeptList = (params?: Record<string, unknown>) =>
  request.get<unknown, ApiResponse<PageData<DeptInfo>>>('/depts/list', { params })

export const getDeptTree = (params?: Record<string, unknown>) =>
  request.get<unknown, ApiResponse<DeptInfo[]>>('/depts/tree', { params })

export const getDept = (id: number) =>
  request.get<unknown, ApiResponse<DeptInfo>>(`/depts/get/${id}`)

export const createDept = (data: Record<string, unknown>) =>
  request.post<unknown, ApiResponse<DeptInfo>>('/depts/create', data)

export const updateDept = (id: number, data: Record<string, unknown>) =>
  request.put<unknown, ApiResponse<DeptInfo>>(`/depts/update/${id}`, data)

export const deleteDept = (id: number) =>
  request.delete<unknown, ApiResponse<null>>(`/depts/delete/${id}`)
