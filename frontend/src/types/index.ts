// =============================================
// 全局类型定义
// =============================================

/** 统一 API 响应格式 */
export interface ApiResponse<T = unknown> {
  code: number
  msg: string
  data: T
}

/** 分页数据格式 */
export interface PageData<T> {
  total: number
  items: T[]
}

/** 用户信息 */
export interface UserInfo {
  id: number
  username: string
  real_name: string | null
  tenant_id: string
  user_type: number
  avatar: string | null
  email?: string | null
  phone?: string | null
}

/** 登录响应 */
export interface LoginResult {
  access_token: string
  token_type: string
  user: UserInfo
}

/** 租户信息 */
export interface TenantInfo {
  id: number
  tenant_id: string
  tenant_name: string
  contact_name: string | null
  contact_phone: string | null
  contact_email: string | null
  status: number
  create_time: string | null
}

/** 部门信息 */
export interface DeptInfo {
  id: number
  tenant_id: string
  parent_id: number
  dept_name: string
  order_num: number
  leader: string | null
  phone: string | null
  email: string | null
  status: number
  create_time: string | null
  children?: DeptInfo[]
}

/** 岗位信息 */
export interface PostInfo {
  id: number
  tenant_id: string
  post_code: string
  post_name: string
  post_sort: number
  status: number
  remark: string | null
  create_time: string | null
}

/** 角色信息 */
export interface RoleInfo {
  id: number
  tenant_id: string
  role_name: string
  role_key: string
  role_sort: number
  data_scope: number
  status: number
  remark: string | null
  create_time: string | null
  menu_ids?: number[]
}

/** 菜单信息 */
export interface MenuInfo {
  id: number
  parent_id: number
  menu_name: string
  menu_type: number | null
  path: string | null
  component: string | null
  icon: string | null
  order_num: number
  perms: string | null
  is_frame: number
  visible: number
  status: number
  create_time: string | null
  children?: MenuInfo[]
}

/** 权限信息 */
export interface PermissionInfo {
  id: number
  perm_code: string
  perm_name: string
  perm_type: number
  resource_url: string | null
  method: string | null
  menu_id: number | null
  status: number
  create_time: string | null
}
