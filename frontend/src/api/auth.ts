import request from '@/utils/request'
import type { ApiResponse, LoginResult, UserInfo } from '@/types'

interface LoginData {
  username: string
  password: string
  tenant_id: string
}

export const loginApi = (data: LoginData) =>
  request.post<unknown, ApiResponse<LoginResult>>('/auth/login', data)

export const getMeApi = () =>
  request.get<unknown, ApiResponse<UserInfo>>('/auth/me')

export const logoutApi = () =>
  request.post<unknown, ApiResponse<null>>('/auth/logout')
