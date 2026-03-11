import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { useAuthStore } from './auth'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ? `${import.meta.env.VITE_API_BASE_URL}/reviews` : 'http://localhost:8000/api/reviews'

export const useCollectionStore = defineStore('collections', () => {
  const authStore = useAuthStore()
  const collections = ref([])
  const loading = ref(false)
  const error = ref('')

  const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json'
    }
  })

  apiClient.interceptors.request.use((config) => {
    const token = authStore.accessToken || localStorage.getItem('accessToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  })

  apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
      if (error.response?.status === 401) {
        try {
          const response = await axios.post('http://localhost:8000/api/auth/token/refresh/', {
            refresh: authStore.refreshToken || localStorage.getItem('refreshToken')
          })
          authStore.setAccessToken(response.data.access)
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

  async function fetchCollections() {
    loading.value = true
    error.value = ''
    try {
      const response = await apiClient.get('/collections/')
      collections.value = response.data.results || response.data
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.error || err.message || '加载收藏夹失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createCollection(payload: { name: string; description?: string; is_public: boolean }) {
    const response = await apiClient.post('/collections/', payload)
    collections.value.unshift(response.data)
    return response.data
  }

  async function updateCollection(collectionId: number, payload: { name: string; description?: string; is_public: boolean }) {
    const response = await apiClient.patch(`/collections/${collectionId}/`, payload)
    const index = collections.value.findIndex((item: any) => item.id === collectionId)
    if (index > -1) {
      collections.value[index] = response.data
    }
    return response.data
  }

  async function deleteCollection(collectionId: number) {
    await apiClient.delete(`/collections/${collectionId}/`)
    const index = collections.value.findIndex((item: any) => item.id === collectionId)
    if (index > -1) {
      collections.value.splice(index, 1)
    }
    return true
  }

  async function addMovieToCollection(collectionId: number, movieId: number) {
    const response = await apiClient.post(`/collections/${collectionId}/movies/${movieId}/`)
    return response.data
  }

  async function removeMovieFromCollection(collectionId: number, movieId: number) {
    const response = await apiClient.delete(`/collections/${collectionId}/movies/${movieId}/remove/`)
    return response.data
  }

  return {
    collections,
    loading,
    error,
    fetchCollections,
    createCollection,
    updateCollection,
    deleteCollection,
    addMovieToCollection,
    removeMovieFromCollection
  }
})
