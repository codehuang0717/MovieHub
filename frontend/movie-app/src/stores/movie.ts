import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { useAuthStore } from './auth'

const API_BASE_URL = 'http://localhost:8000/api'

export const useMovieStore = defineStore('movie', () => {
  const movies = ref([])
  const categories = ref([])
  const currentMovie = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    }
  })

  // 添加请求拦截器，自动包含认证token
  apiClient.interceptors.request.use((config) => {
    const authStore = useAuthStore()
    if (authStore.accessToken) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`
    }
    return config
  })

  async function fetchMovies(params = {}) {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.get('/movies/', { params })
      movies.value = response.data.results || response.data
      return { success: true, data: response.data }
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to fetch movies'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function fetchMovieById(id: number) {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.get(`/movies/${id}/`)
      currentMovie.value = response.data
      return { success: true, data: response.data }
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to fetch movie'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function fetchCategories() {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.get('/movies/categories/')
      categories.value = response.data.results || response.data
      return { success: true, data: response.data }
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to fetch categories'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function searchMovies(query: string, filters = {}) {
    loading.value = true
    error.value = null
    
    try {
      const params = { search: query, ...filters }
      const response = await apiClient.get('/movies/search/', { params })
      movies.value = response.data.results || response.data
      return { success: true, data: response.data }
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to search movies'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function fetchMoviesByCategory(categoryId: number) {
    loading.value = true
    error.value = null

    try {
      const response = await apiClient.get(`/movies/`, {
        params: { category: categoryId }
      })
      movies.value = response.data.results || response.data
      return { success: true, data: response.data }
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to fetch movies by category'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function fetchSimilarMovies(movieId: number) {
    loading.value = true
    error.value = null

    try {
      const response = await apiClient.get(`/recommendations/similar/${movieId}/`)
      return { success: true, data: response.data.results || [] }
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to fetch similar movies'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function fetchPersonalizedRecommendations() {
    loading.value = true
    error.value = null

    try {
      const response = await apiClient.get('/recommendations/personalized/')
      return { success: true, data: response.data.results || [] }
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to fetch personalized recommendations'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  return {
    movies,
    categories,
    currentMovie,
    loading,
    error,
    fetchMovies,
    fetchMovieById,
    fetchCategories,
    searchMovies,
    fetchMoviesByCategory,
    fetchSimilarMovies,
    fetchPersonalizedRecommendations
  }
})