import request from '@/utils/request'
import type { ApiResponse, PageData, MenuInfo } from '@/types'

export const getMenuList = (params?: Record<string, unknown>) =>
  request.get<unknown, ApiResponse<PageData<MenuInfo>>>('/menus/list', { params })

export const getMenuTree = () =>
  request.get<unknown, ApiResponse<MenuInfo[]>>('/menus/tree')

export const getMenu = (id: number) =>
  request.get<unknown, ApiResponse<MenuInfo>>(`/menus/get/${id}`)

export const createMenu = (data: Record<string, unknown>) =>
  request.post<unknown, ApiResponse<MenuInfo>>('/menus/create', data)

export const updateMenu = (id: number, data: Record<string, unknown>) =>
  request.put<unknown, ApiResponse<MenuInfo>>(`/menus/update/${id}`, data)

export const deleteMenu = (id: number) =>
  request.delete<unknown, ApiResponse<null>>(`/menus/delete/${id}`)
