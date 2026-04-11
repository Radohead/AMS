import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getToken, setToken, removeToken } from '@/utils/auth'
import api from '@/api'

export const useUserStore = defineStore('user', () => {
  const token = ref(getToken() || '')
  const userInfo = ref(null)
  const permissions = ref([])

  const isLoggedIn = computed(() => !!token.value)

  async function login(username, password) {
    const res = await api.post('/auth/login', { username, password })
    token.value = res.access_token
    userInfo.value = res.user
    setToken(res.access_token)
    return res
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    permissions.value = []
    removeToken()
  }

  async function getUserInfo() {
    try {
      const res = await api.get('/auth/me')
      userInfo.value = res

      // 获取权限
      const permRes = await api.get('/auth/permissions')
      permissions.value = permRes
    } catch (error) {
      logout()
      throw error
    }
  }

  function hasPermission(resource, action) {
    return permissions.value.some(p => p.resource === resource && p.action === action)
  }

  async function changePassword(oldPassword, newPassword) {
    const res = await api.put('/auth/me/password', {
      old_password: oldPassword,
      new_password: newPassword
    })
    return res
  }

  return {
    token,
    userInfo,
    permissions,
    isLoggedIn,
    login,
    logout,
    getUserInfo,
    hasPermission,
    changePassword
  }
})
