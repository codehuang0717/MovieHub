import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import router from '@/router'

const API_BASE_URL = 'http://localhost:8000/api/auth'

interface UserProfile {
  avatar: string
  bio?: string
}

interface User {
  id: number
  username: string
  email: string
  first_name?: string
  last_name?: string
  profile?: UserProfile
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const accessToken = ref(localStorage.getItem('accessToken') || '')
  const refreshToken = ref(localStorage.getItem('refreshToken') || '')

  const isAuthenticated = computed(() => !!accessToken.value)

  // Configure axios defaults
  const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    }
  })

  // Add request interceptor to include auth token
  apiClient.interceptors.request.use((config) => {
    if (accessToken.value) {
      config.headers.Authorization = `Bearer ${accessToken.value}`
    }
    return config
  })

  // Add response interceptor to handle token refresh
  apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
      if (error.response?.status === 401) {
        try {
          const response = await axios.post(`${API_BASE_URL}/token/refresh/`, {
            refresh: refreshToken.value
          })
          accessToken.value = response.data.access
          localStorage.setItem('accessToken', response.data.access)

          // Retry the original request
          error.config.headers.Authorization = `Bearer ${response.data.access}`
          return apiClient.request(error.config)
        } catch (refreshError) {
          logout()
          router.push('/login')
          return Promise.reject(refreshError)
        }
      }
      return Promise.reject(error)
    }
  )
  async function login(credentials: { username: string; password: string }) {
    try {
      const response = await apiClient.post('/login/', credentials)

      user.value = response.data.user
      accessToken.value = response.data.access
      refreshToken.value = response.data.refresh

      localStorage.setItem('accessToken', response.data.access)
      localStorage.setItem('refreshToken', response.data.refresh)

      return { success: true, data: response.data }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data || { message: 'Login failed' }
      }
    }
  }

  async function register(userData: {
    username: string
    email: string
    password: string
    password_confirm: string
    first_name?: string
    last_name?: string
  }) {
    try {
      const response = await apiClient.post('/register/', userData)

      user.value = response.data.user
      accessToken.value = response.data.access
      refreshToken.value = response.data.refresh

      localStorage.setItem('accessToken', response.data.access)
      localStorage.setItem('refreshToken', response.data.refresh)

      return { success: true, data: response.data }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data || { message: 'Registration failed' }
      }
    }
  }

  async function logout() {
    try {
      if (refreshToken.value) {
        await apiClient.post('/logout/', { refresh: refreshToken.value })
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      user.value = null
      accessToken.value = ''
      refreshToken.value = ''

      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')

      console.log('User logged out successfully')
    }
  }

  async function fetchProfile() {
    try {
      // Use the correct auth API endpoint
      const response = await apiClient.get('/profile/')
      user.value = response.data
      return { success: true, data: response.data }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to fetch profile' }
      }
    }
  }

  async function updateProfile(profileData: any) {
    try {
      // Use the correct auth API endpoint
      const response = await apiClient.put('/profile/update/', profileData)
      user.value = response.data
      return { success: true, data: response.data }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to update profile' }
      }
    }
  }

  async function uploadAvatar(file: File) {
    try {
      const formData = new FormData()
      formData.append('avatar', file)

      const response = await apiClient.post('/profile/avatar/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      // Update user data with new avatar
      if (user.value) {
        user.value.profile.avatar = response.data.avatar
      }

      return { success: true, data: response.data }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to upload avatar' }
      }
    }
  }

  async function removeAvatar() {
    try {
      const response = await apiClient.delete('/profile/avatar/remove/')

      // Update user data with default avatar
      if (user.value) {
        user.value.profile.avatar = response.data.avatar
      }

      return { success: true, data: response.data }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to remove avatar' }
      }
    }
  }

  function setAccessToken(token: string) {
    accessToken.value = token
    localStorage.setItem('accessToken', token)
  }

  function initializeAuth() {
    if (accessToken.value) {
      fetchProfile().catch(() => {
        logout()
      })
    }
  }

  return {
    user,
    accessToken,
    refreshToken,
    isAuthenticated,
    apiClient,
    login,
    register,
    logout,
    fetchProfile,
    updateProfile,
    uploadAvatar,
    removeAvatar,
    setAccessToken,
    initializeAuth
  }
})
