import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { useAuthStore } from './auth'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ? `${import.meta.env.VITE_API_BASE_URL}/reviews` : 'http://localhost:8000/api/reviews'

export const useWatchlistStore = defineStore('watchlist', () => {
  const authStore = useAuthStore()
  const watchlist = ref([])
  const loading = ref(false)
  const error = ref('')

  // Configure axios defaults
  const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    }
  })

  // Add request interceptor to include auth token
  apiClient.interceptors.request.use((config) => {
    const token = authStore.accessToken || localStorage.getItem('accessToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      console.log('Adding auth header:', config.headers.Authorization)
    } else {
      console.log('No auth token available')
    }
    return config
  })

  // Add response interceptor to handle token refresh
  apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
      if (error.response?.status === 401) {
        try {
          const response = await axios.post('http://localhost:8000/api/auth/token/refresh/', {
            refresh: authStore.refreshToken || localStorage.getItem('refreshToken')
          })
          authStore.setAccessToken(response.data.access)
          
          // Retry the original request
          error.config.headers.Authorization = `Bearer ${response.data.access}`
          return apiClient.request(error.config)
        } catch (refreshError) {
          console.error('Token refresh failed:', refreshError)
          authStore.logout()
          window.location.href = '/login'
        }
      }
      return Promise.reject(error)
    }
  )

  async function fetchWatchlist() {
    loading.value = true
    error.value = ''

    try {
      console.log('Fetching watchlist...')
      const response = await apiClient.get('/watchlist/')
      console.log('Watchlist API response:', response)
      console.log('Response status:', response.status)
      console.log('Response data type:', typeof response.data)
      
      // 处理不同的响应格式
      let watchlistData = response.data
      
      if (Array.isArray(response.data)) {
        watchlistData = response.data
        console.log('Data is direct array:', watchlistData.length, 'items')
      } else if (response.data && response.data.results && Array.isArray(response.data.results)) {
        watchlistData = response.data.results
        console.log('Data is paginated:', watchlistData.length, 'items')
      } else if (response.data && Array.isArray(response.data.watchlist)) {
        watchlistData = response.data.watchlist
        console.log('Data is in watchlist field:', watchlistData.length, 'items')
      } else {
        console.warn('Unexpected data format:', response.data)
        watchlistData = []
      }
      
      watchlist.value = watchlistData
      console.log('Final watchlist assignment:', watchlist.value)
      console.log('Watchlist array length:', watchlist.value.length)
      
      return response.data
    } catch (err: any) {
      console.error('Watchlist fetch error:', err)
      console.error('Error response:', err.response?.data)
      console.error('Error status:', err.response?.status)
      error.value = '加载想看列表失败: ' + (err.response?.data?.error || err.message || '未知错误')
      throw err
    } finally {
      loading.value = false
    }
  }

  async function toggleWatchlist(movieId: number) {
    console.log('Toggling watchlist for movie:', movieId)
    
    try {
      console.log('Toggling watchlist...')
      const response = await apiClient.post(`/watchlist/toggle/${movieId}/`)
      console.log('Watchlist toggle response:', response.data)
      
      if (response.data.in_watchlist) {
        // Added to watchlist
        console.log('Added to watchlist:', response.data.item)
        watchlist.value.unshift(response.data.item)
        return { added: true, item: response.data.item }
      } else {
        // Removed from watchlist
        console.log('Removed from watchlist for movie:', movieId)
        const index = watchlist.value.findIndex(item => 
          (item.movie === movieId) || (item.tmdb_movie_id === movieId)
        )
        if (index > -1) {
          watchlist.value.splice(index, 1)
        }
        return { added: false }
      }
    } catch (err: any) {
      console.error('Toggle watchlist error:', err)
      console.error('Error response:', err.response?.data)
      error.value = '操作失败: ' + (err.response?.data?.error || err.message || '未知错误')
      throw err
    }
  }

  async function updateWatchlistStatus(watchlistId: number, status: string) {
    try {
      const response = await apiClient.patch(`/watchlist/${watchlistId}/`, { status })
      
      const index = watchlist.value.findIndex(item => item.id === watchlistId)
      if (index > -1) {
        watchlist.value[index] = response.data
      }
      
      return response.data
    } catch (err) {
      error.value = '更新状态失败'
      throw err
    }
  }

  async function removeFromWatchlist(watchlistId: number) {
    try {
      await apiClient.delete(`/watchlist/${watchlistId}/`)
      
      const index = watchlist.value.findIndex(item => item.id === watchlistId)
      if (index > -1) {
        watchlist.value.splice(index, 1)
      }
      
      return true
    } catch (err) {
      error.value = '移除失败'
      throw err
    }
  }

  async function fetchWatchlistStats() {
    try {
      const response = await apiClient.get('/watchlist/stats/')
      return response.data
    } catch (err) {
      error.value = '获取统计信息失败'
      throw err
    }
  }

  function isInWatchlist(movieId: number) {
    return watchlist.value.some(item => 
      item.movie === movieId || item.tmdb_movie_id === movieId
    )
  }

  function getWatchlistItem(movieId: number) {
    return watchlist.value.find(item => 
      item.movie === movieId || item.tmdb_movie_id === movieId
    )
  }

  return {
    watchlist,
    loading,
    error,
    fetchWatchlist,
    toggleWatchlist,
    updateWatchlistStatus,
    removeFromWatchlist,
    fetchWatchlistStats,
    isInWatchlist,
    getWatchlistItem
  }
})