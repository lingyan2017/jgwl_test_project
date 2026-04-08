import { defineStore } from 'pinia'
import { ref } from 'vue'
import { loginApi, getMeApi } from '@/api/auth'
import type { UserInfo } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>(localStorage.getItem('token') ?? '')
  const user = ref<UserInfo | null>(
    JSON.parse(localStorage.getItem('user') ?? 'null') as UserInfo | null,
  )

  async function login(username: string, password: string, tenantId = 'default'): Promise<void> {
    const res = await loginApi({ username, password, tenant_id: tenantId })
    token.value = res.data.access_token
    user.value = res.data.user
    localStorage.setItem('token', token.value)
    localStorage.setItem('user', JSON.stringify(user.value))
  }

  async function fetchMe(): Promise<void> {
    const res = await getMeApi()
    user.value = res.data
    localStorage.setItem('user', JSON.stringify(user.value))
  }

  function logout(): void {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return { token, user, login, fetchMe, logout }
})
