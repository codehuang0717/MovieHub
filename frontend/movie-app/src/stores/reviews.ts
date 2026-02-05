import { defineStore } from 'pinia'
import axios from 'axios'
import { useAuthStore } from './auth'

const API_BASE_URL = 'http://localhost:8000/api/reviews'

export const useReviewStore = defineStore('reviews', () => {
  const authStore = useAuthStore()

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

  async function fetchMovieRatings(movieId: number) {
    const response = await apiClient.get(`/movies/${movieId}/ratings/`)
    return response.data
  }

  async function fetchUserRating(movieId: number) {
    const response = await apiClient.get('/ratings/', {
      params: { tmdb_movie_id: movieId }
    })
    return response.data
  }

  async function submitRating(movieId: number, score: number) {
    const response = await apiClient.post('/ratings/', {
      tmdb_movie_id: movieId,
      score
    })
    return response.data
  }

  async function updateRating(ratingId: number, score: number) {
    const response = await apiClient.patch(`/ratings/${ratingId}/`, { score })
    return response.data
  }

  async function fetchMovieComments(movieId: number) {
    const response = await apiClient.get(`/movies/${movieId}/comments/`)
    return response.data
  }

  async function createComment(movieId: number, content: string, isLongReview: boolean) {
    const response = await apiClient.post('/comments/', {
      tmdb_movie_id: movieId,
      content,
      is_long_review: isLongReview
    })
    return response.data
  }

  async function updateComment(commentId: number, content: string, isLongReview: boolean) {
    const response = await apiClient.patch(`/comments/${commentId}/`, {
      content,
      is_long_review: isLongReview
    })
    return response.data
  }

  async function deleteComment(commentId: number) {
    await apiClient.delete(`/comments/${commentId}/`)
    return true
  }

  async function toggleCommentLike(commentId: number) {
    const response = await apiClient.post(`/comments/${commentId}/like/`)
    return response.data
  }

  return {
    fetchMovieRatings,
    fetchUserRating,
    submitRating,
    updateRating,
    fetchMovieComments,
    createComment,
    updateComment,
    deleteComment,
    toggleCommentLike
  }
})
