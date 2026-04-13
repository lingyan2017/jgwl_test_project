import { defineStore } from 'pinia'
import { ref } from 'vue'
import { loginApi, getMeApi } from '@/api/auth'
import { getMenuTree } from '@/api/menu'
import type { UserInfo, MenuInfo } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>(localStorage.getItem('token') ?? '')
  const user = ref<UserInfo | null>(
    JSON.parse(localStorage.getItem('user') ?? 'null') as UserInfo | null,
  )
  const menus = ref<MenuInfo[]>([])

  async function login(username: string, password: string, tenantId = 'default'): Promise<void> {
    const res = await loginApi({ username, password, tenant_id: tenantId })
    token.value = res.data.access_token
    user.value = res.data.user
    localStorage.setItem('token', token.value)
    localStorage.setItem('user', JSON.stringify(user.value))
    // 注意：不在这里获取菜单，由路由守卫统一处理
  }

  async function fetchMe(): Promise<void> {
    const res = await getMeApi()
    user.value = res.data
    localStorage.setItem('user', JSON.stringify(user.value))
  }

  async function fetchMenus(): Promise<void> {
    try {
      const res = await getMenuTree()
      menus.value = res.data
      localStorage.setItem('menus', JSON.stringify(menus.value))
    } catch (error) {
      console.error('获取菜单失败:', error)
      menus.value = []
    }
  }

  function logout(): void {
    token.value = ''
    user.value = null
    menus.value = []
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('menus')
  }

  return { token, user, menus, login, fetchMe, fetchMenus, logout }
})
