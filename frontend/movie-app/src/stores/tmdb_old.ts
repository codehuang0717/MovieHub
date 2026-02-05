import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'

const TMDB_API_KEY = import.meta.env.VITE_TMDB_API_KEY || '2d89ddec4f8acd4c9f2036ea7321f326'
const TMDB_BASE_URL = 'https://api.themoviedb.org/3'

export const useTMDBStore = defineStore('tmdb', () => {
  const popularMovies = ref([])
  const topRatedMovies = ref([])
  const upcomingMovies = ref([])
  const nowPlayingMovies = ref([])
  const genreMovies = ref([])
  const searchResults = ref([])
  const movieDetails = ref(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const genreLoading = ref(false)

  const tmdbClient = axios.create({
    baseURL: TMDB_BASE_URL,
    params: {
      api_key: TMDB_API_KEY,
      language: 'zh-CN'
    }
  })

  const getImageUrl = (path: string, size = 'w500') => {
    if (!path || path.trim() === '') {
      return '/placeholder-movie.svg'
    }
    return `https://image.tmdb.org/t/p/${size}${path}`
  }

  const fetchPopularMovies = async (page = 1, year?: string) => {
    loading.value = true
    error.value = null

    try {
      const params: any = { page }
      if (year) {
        params.primary_release_year = year
      }

      const response = await tmdbClient.get('/movie/popular', {
        params
      })

      popularMovies.value = response.data.results.map((movie: any) => ({
        ...movie,
        poster_path: getImageUrl(movie.poster_path),
        backdrop_path: getImageUrl(movie.backdrop_path, 'w1280'),
        release_date: movie.release_date || '未知',
        vote_average: movie.vote_average || 0
      }))

      return response.data
    } catch (err) {
      error.value = '获取热门电影失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchTopRatedMovies = async (page = 1, year?: string) => {
    loading.value = true

    try {
      const params: any = { page }
      if (year) {
        params.primary_release_year = year
      }

      const response = await tmdbClient.get('/movie/top_rated', {
        params
      })

      topRatedMovies.value = response.data.results.map((movie: any) => ({
        ...movie,
        poster_path: getImageUrl(movie.poster_path),
        backdrop_path: getImageUrl(movie.backdrop_path, 'w1280'),
        release_date: movie.release_date || '未知',
        vote_average: movie.vote_average || 0
      }))

      return response.data
    } catch (err) {
      error.value = '获取高分电影失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchUpcomingMovies = async (page = 1) => {
    loading.value = true

    try {
      const response = await tmdbClient.get('/movie/upcoming', {
        params: { page }
      })

      upcomingMovies.value = response.data.results.map((movie: any) => ({
        ...movie,
        poster_path: getImageUrl(movie.poster_path),
        backdrop_path: getImageUrl(movie.backdrop_path, 'w1280'),
        release_date: movie.release_date || '未知',
        vote_average: movie.vote_average || 0
      }))

      return response.data
    } catch (err) {
      error.value = '获取即将上映电影失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchNowPlayingMovies = async (page = 1, year?: string) => {
    loading.value = true

    try {
      const params: any = { page }
      if (year) {
        params.primary_release_year = year
      }

      const response = await tmdbClient.get('/movie/now_playing', {
        params
      })

      nowPlayingMovies.value = response.data.results.map((movie: any) => ({
        ...movie,
        poster_path: getImageUrl(movie.poster_path),
        backdrop_path: getImageUrl(movie.backdrop_path, 'w1280'),
        release_date: movie.release_date || '未知',
        vote_average: movie.vote_average || 0
      }))

      return response.data
    } catch (err) {
      error.value = '获取正在上映电影失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const searchMovies = async (query: string, page = 1) => {
    loading.value = true
    error.value = null

    try {
      const response = await tmdbClient.get('/search/movie', {
        params: { query, page }
      })

      searchResults.value = response.data.results.map((movie: any) => ({
        ...movie,
        poster_path: getImageUrl(movie.poster_path),
        backdrop_path: getImageUrl(movie.backdrop_path, 'w1280'),
        release_date: movie.release_date || '未知',
        vote_average: movie.vote_average || 0
      }))

      return response.data
    } catch (err) {
      error.value = '搜索电影失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchMovieDetails = async (movieId: number) => {
    loading.value = true
    error.value = null

    try {
      const [movieResponse, creditsResponse] = await Promise.all([
        tmdbClient.get(`/movie/${movieId}`),
        tmdbClient.get(`/movie/${movieId}/credits`)
      ])

      const movie = movieResponse.data
      const credits = creditsResponse.data

      movieDetails.value = {
        ...movie,
        poster_path: getImageUrl(movie.poster_path),
        backdrop_path: getImageUrl(movie.backdrop_path, 'w1280'),
        release_date: movie.release_date || '未知',
        vote_average: movie.vote_average || 0,
        cast: credits.cast?.slice(0, 10) || [],
        crew: credits.crew || [],
        genres: movie.genres || []
      }

      return movieDetails.value
    } catch (err) {
      error.value = '获取电影详情失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchMoviesByGenre = async (genreId: number, page = 1, year?: string, sortBy: string = 'popularity.desc') => {
    genreLoading.value = true

    try {
      const params: any = {
        with_genres: genreId,
        sort_by: sortBy,
        page,
        language: 'zh-CN',
        include_adult: false,
        include_video: false,
        vote_count_gte: 50 // 确保有足够的票数来进行有意义的评分排序
      }

      // 添加日期过滤
      const today = new Date().toISOString().split('T')[0]
      
      switch (sortBy) {
        case 'release_date.desc':
          // 最新上映：只显示今天及之前上映的电影
          params['primary_release_date.lte'] = today
          params.sort_by = 'primary_release_date.desc'
          console.log('Filter for released movies:', params['primary_release_date.lte'])
          break
        case 'primary_release_date.desc':
          // 即将上映：只显示今天及之后上映的电影，升序排列
          params['primary_release_date.gte'] = today
          params.sort_by = 'primary_release_date.asc'
          console.log('Filter for upcoming movies:', params['primary_release_date.gte'])
          break
      }
      
      // 添加年份过滤（如果有）
      if (year) {
        params.primary_release_year = parseInt(year)
      }

      console.log('FetchMoviesByGenre final params:', params)
      console.log('=== BEFORE API CALL (GENRE) ===')
      console.log('sort_by param:', params.sort_by)
      console.log('primary_release_date.lte:', params['primary_release_date.lte'])
      console.log('primary_release_date.gte:', params['primary_release_date.gte'])

      const response = await tmdbClient.get('/discover/movie', {
        params
      })

      console.log('=== AFTER API RESPONSE (GENRE) ===')
      console.log('Total results:', response.data.total_results)
      console.log('First 3 movies:')
      response.data.results.slice(0, 3).forEach((movie, index) => {
        console.log(`${index + 1}. ${movie.title} (${movie.release_date})`)
      })

      const results = response.data.results.map((movie: any) => ({
        ...movie,
        poster_path: getImageUrl(movie.poster_path),
        backdrop_path: getImageUrl(movie.backdrop_path, 'w1280'),
        release_date: movie.release_date || '未知',
        vote_average: movie.vote_average || 0
      }))

      console.log('API Response:', results.length, 'movies for genre', genreId, 'sorted by', sortBy)
      console.log('Top 3 movies:', results.slice(0, 3).map(m => ({ title: m.title, rating: m.vote_average, popularity: m.popularity })))

      genreMovies.value = results
      return { ...response.data, results }
    } catch (err) {
      error.value = '获取分类电影失败'
      throw err
    } finally {
      genreLoading.value = false
    }
  }

  const fetchDiscoverMovies = async (sortBy: string = 'popularity.desc', page = 1, year?: string) => {
    loading.value = true
    error.value = null

    try {
      const params: any = {
        sort_by: sortBy,
        page,
        language: 'zh-CN',
        include_adult: false,
        include_video: false
      }

      // 添加日期过滤
      const today = new Date().toISOString().split('T')[0]
      
      switch (sortBy) {
        case 'release_date.desc':
          // 最新上映：只显示今天及之前上映的电影
          params['primary_release_date.lte'] = today
          params.sort_by = 'primary_release_date.desc'
          console.log('Filter for released movies:', params['primary_release_date.lte'])
          break
        case 'primary_release_date.desc':
          // 即将上映：只显示今天及之后上映的电影，升序排列
          params['primary_release_date.gte'] = today
          params.sort_by = 'primary_release_date.asc'
          console.log('Filter for upcoming movies:', params['primary_release_date.gte'])
          break
      }
      
      // 添加年份过滤（如果有）
      if (year) {
        params.primary_release_year = parseInt(year)
      }

      console.log('FetchDiscoverMovies final params:', params)
      console.log('=== BEFORE API CALL ===')
      console.log('sort_by param:', params.sort_by)
      console.log('primary_release_date.lte:', params['primary_release_date.lte'])
      console.log('primary_release_date.gte:', params['primary_release_date.gte'])

      const response = await tmdbClient.get('/discover/movie', {
        params
      })

      console.log('=== AFTER API RESPONSE ===')
      console.log('Total results:', response.data.total_results)
      console.log('First 3 movies:')
      response.data.results.slice(0, 3).forEach((movie, index) => {
        console.log(`${index + 1}. ${movie.title} (${movie.release_date}) - sort_field: ${movie.popularity || 'N/A'}`)
      })

      const results = response.data.results.map((movie: any) => ({
        ...movie,
        poster_path: getImageUrl(movie.poster_path),
        backdrop_path: getImageUrl(movie.backdrop_path, 'w1280'),
        release_date: movie.release_date || '未知',
        vote_average: movie.vote_average || 0
      }))

      popularMovies.value = results

      return { ...response.data, results }
    } catch (err) {
      error.value = '获取电影失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    popularMovies,
    topRatedMovies,
    upcomingMovies,
    nowPlayingMovies,
    genreMovies,
    searchResults,
    movieDetails,
    loading,
    genreLoading,
    error,
    tmdbClient,
    getImageUrl,
    fetchPopularMovies,
    fetchTopRatedMovies,
    fetchUpcomingMovies,
    fetchNowPlayingMovies,
    searchMovies,
    fetchMovieDetails,
    fetchMoviesByGenre,
    fetchDiscoverMovies
  }
})
