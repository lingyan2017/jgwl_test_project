import { defineStore } from 'pinia'
import { ref } from 'vue'
import { loginApi, getMeApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  async function login(username, password, tenantId = 'default') {
    const res = await loginApi({ username, password, tenant_id: tenantId })
    token.value = res.data.access_token
    user.value = res.data.user
    localStorage.setItem('token', token.value)
    localStorage.setItem('user', JSON.stringify(user.value))
  }

  async function fetchMe() {
    const res = await getMeApi()
    user.value = res.data
    localStorage.setItem('user', JSON.stringify(user.value))
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return { token, user, login, fetchMe, logout }
})
