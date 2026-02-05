<template>
  <AppLayout>
    <div class="search-page">
      <!-- Content -->
      <main class="main-content">
      <!-- Search Header -->
      <div class="search-header">
        <div class="search-container">
          <!-- Back Button - Only show after search -->
          <div v-if="hasSearched" class="back-button-container">
            <el-button 
              @click="goBack" 
              type="info" 
              size="large" 
              class="back-button"
              :icon="ArrowLeft"
            >
              {{ $t('common.back') }}
            </el-button>
          </div>
          <h1>{{ $t('search.searchMovies') }}</h1>
          <div class="search-box">
            <el-input
              v-model="searchQuery"
              :placeholder="$t('search.enterMovieName')"
              size="large"
              @keyup.enter="handleSearch"
              clearable
              class="search-input"
            >
              <template #append>
                <el-button @click="handleSearch" type="primary" size="large">
                  <el-icon><Search /></el-icon>
                  {{ $t('search.search') }}
                </el-button>
              </template>
            </el-input>
          </div>
        </div>
      </div>

      <!-- Search Results -->
      <div class="search-results">
        <div v-if="!searchQuery" class="search-suggestions">
          <h2>{{ $t('search.popularSearches') }}</h2>
          <div class="suggestions-grid">
            <el-tag 
              v-for="suggestion in popularSearches" 
              :key="suggestion"
              @click="quickSearch(suggestion)"
              class="suggestion-tag"
              size="large"
            >
              {{ suggestion }}
            </el-tag>
          </div>
        </div>

        <div v-else>
          <div class="results-header">
            <h2>{{ $t('search.results') }}</h2>
            <p v-if="searchResults.length > 0">
              {{ $t('search.foundMovies', { count: searchResults.length }) }}
            </p>
            <p v-else-if="!loading" class="no-results">
              {{ $t('search.noResultsFor', { query: searchQuery }) }}
            </p>
          </div>

          <div v-loading="loading" class="movies-grid">
            <div 
              v-for="movie in searchResults" 
              :key="movie.id" 
              class="movie-card"
              @click="goToMovie(movie.id)"
            >
              <div class="movie-poster">
                <img 
                  :src="movie.poster_path" 
                  :alt="movie.title"
                  @error="handleImageError"
                  loading="lazy"
                />
                <div class="movie-rating">
                  <el-icon><Star /></el-icon>
                  {{ movie.vote_average?.toFixed(1) }}
                </div>
              </div>
              <div class="movie-info">
                <h3 class="movie-title">{{ movie.title }}</h3>
                <p class="movie-date">{{ formatDate(movie.release_date) }}</p>
                <div class="movie-genres">
                  <el-tag 
                    v-for="genre in getMovieGenres(movie)" 
                    :key="genre" 
                    size="small"
                  >
                    {{ genre }}
                  </el-tag>
                </div>
                <p v-if="movie.overview" class="movie-overview">{{ movie.overview }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
    </div>
</AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useTMDBStore } from '@/stores/tmdb'
import { Search, Star, ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import AppLayout from '@/layouts/AppLayout.vue'

const { t, locale } = useI18n()
const router = useRouter()
const route = useRoute()
const tmdbStore = useTMDBStore()

const searchQuery = ref('')
const loading = ref(false)
const hasSearched = ref(false)

const searchResults = computed(() => tmdbStore.searchResults)

watch(locale, () => {
  if (hasSearched.value && searchQuery.value) {
    handleSearch()
  }
})

const popularSearches = ref([
  'Avengers', 'Titanic', 'Inception', 'Interstellar', 'The Shawshank Redemption',
  'Forrest Gump', 'The Godfather', 'The Matrix', 'Spirited Away', 'Your Name',
  'The Wandering Earth', 'Ne Zha', 'My Country, My Parents', 'The Captain',
  'The Eight Hundred', 'Wolf Warrior 2', 'Operation Red Sea', 'Detective Chinatown'
])

const tmdbGenres: Record<number, string> = {
  28: t('categories.action'), 12: t('categories.adventure'), 16: t('categories.animation'), 35: t('categories.comedy'), 80: t('categories.crime'), 99: t('categories.documentary'),
  18: t('categories.drama'), 10751: t('categories.family'), 14: t('categories.fantasy'), 36: t('categories.history'), 27: t('categories.horror'),
  10402: t('categories.music'), 9648: t('categories.mystery'), 10749: t('categories.romance'), 878: t('categories.sciFi')
}

const goBack = () => {
  router.back()
}

const goToMovie = (movieId: number) => {
  router.push({ name: 'movie-detail', params: { id: movieId }})
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = '/placeholder-movie.jpg'
}

const formatDate = (dateString: string) => {
  if (!dateString) return t('common.unknown')
  return new Date(dateString).getFullYear()
}

const getMovieGenres = (movie: any) => {
  if (!movie.genre_ids) return []
  return movie.genre_ids.slice(0, 3).map((id: number) => 
    tmdbGenres[id] || t('common.unknown')
  ).filter(Boolean)
}

const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    ElMessage.warning(t('search.enterKeyword'))
    return
  }

  hasSearched.value = true
  loading.value = true
  try {
    await tmdbStore.searchMovies(searchQuery.value.trim())
    router.replace({ name: 'search', query: { q: searchQuery.value.trim() }})
  } catch (error) {
    console.error('Search error:', error)
    ElMessage.error(t('search.searchFailed'))
  } finally {
    loading.value = false
  }
}

const quickSearch = (query: string) => {
  searchQuery.value = query
  handleSearch()
}

watch(() => route.query.q, (newQuery) => {
  if (newQuery) {
    searchQuery.value = newQuery as string
    hasSearched.value = true
    handleSearch()
  } else {
    // 如果没有查询参数，重置搜索状态
    hasSearched.value = false
    searchResults.value = []
  }
}, { immediate: true })

onMounted(() => {
  // Set initial search query from URL
  const query = route.query.q as string
  if (query) {
    searchQuery.value = query
    hasSearched.value = true
  }
})
</script>

<style scoped>
.search-page {
  min-height: 100vh;
  background: #0d1117;
  color: #f0f6fc;
}

.main-content {
  margin-top: 64px;
  min-height: calc(100vh - 64px);
}

/* Search Header */
.search-header {
  background: linear-gradient(135deg, rgba(88, 166, 255, 0.1) 0%, rgba(88, 166, 255, 0.05) 100%);
  padding: 48px 24px;
  border-bottom: 1px solid #30363d;
}

.search-container {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
  position: relative;
}

.back-button-container {
  position: absolute;
  top: 0px;
  left: 0;
  z-index: 10;
}

.back-button {
  background: rgba(22, 27, 34, 0.9) !important;
  border-color: #30363d !important;
  color: #f0f6fc !important;
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
}

.back-button:hover {
  background: rgba(88, 166, 255, 0.2) !important;
  border-color: #58a6ff !important;
  transform: translateX(-4px);
}

.search-header h1 {
  font-size: 3rem;
  font-weight: 700;
  margin: 0 0 24px 0;
  background: linear-gradient(135deg, #58a6ff 0%, #79c0ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.search-box {
  max-width: 600px;
  margin: 0 auto;
}

.search-input {
  width: 100%;
}

:deep(.search-input .el-input__wrapper) {
  background: rgba(22, 27, 34, 0.8);
  border: 2px solid #30363d;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
}

:deep(.search-input .el-input__wrapper:hover) {
  border-color: #58a6ff;
  box-shadow: 0 8px 32px rgba(88, 166, 255, 0.2);
}

:deep(.search-input .el-input__wrapper.is-focus) {
  border-color: #58a6ff;
  box-shadow: 0 8px 32px rgba(88, 166, 255, 0.3);
}

:deep(.search-input .el-input__inner) {
  color: #f0f6fc;
  font-size: 16px;
  padding: 16px 24px;
}

:deep(.search-input .el-input__inner::placeholder) {
  color: #8b949e;
}

/* Search Results */
.search-results {
  padding: 48px 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.search-suggestions {
  text-align: center;
}

.search-suggestions h2 {
  font-size: 2rem;
  font-weight: 600;
  margin: 0 0 32px 0;
  color: #f0f6fc;
}

.suggestions-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
}

.suggestion-tag {
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 20px;
}

.suggestion-tag:hover {
  transform: translateY(-2px);
  background: #58a6ff;
  border-color: #58a6ff;
}

.results-header {
  margin-bottom: 32px;
}

.results-header h2 {
  font-size: 2rem;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #f0f6fc;
}

.results-header p {
  font-size: 1.1rem;
  color: #8b949e;
  margin: 0;
}

.results-count {
  color: #58a6ff;
  font-weight: 600;
}

.no-results {
  color: #f87171;
  font-weight: 500;
}

/* Movies Grid */
.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 32px;
}

.movie-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 12px;
  overflow: hidden;
  background: #161b22;
}

.movie-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4);
}

.movie-poster {
  position: relative;
  aspect-ratio: 2/3;
  overflow: hidden;
}

.movie-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.movie-card:hover .movie-poster img {
  transform: scale(1.05);
}

.movie-rating {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(0, 0, 0, 0.8);
  color: #fbbf24;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
  backdrop-filter: blur(4px);
}

.movie-info {
  padding: 20px;
}

.movie-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 8px 0;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.movie-date {
  font-size: 0.9rem;
  color: #8b949e;
  margin: 0 0 12px 0;
}

.movie-genres {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.movie-overview {
  font-size: 0.9rem;
  color: #8b949e;
  line-height: 1.5;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .movies-grid {
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 24px;
  }
}

@media (max-width: 768px) {
  .search-header {
    padding: 32px 16px;
  }
  
  .search-header h1 {
    font-size: 2.5rem;
  }
  
  .search-results {
    padding: 32px 16px;
  }
  
  .movies-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
  }
}

@media (max-width: 480px) {
  .search-header {
    padding: 24px 12px;
  }
  
  .search-header h1 {
    font-size: 2rem;
  }
  
  .search-results {
    padding: 24px 12px;
  }
  
  .suggestions-grid {
    gap: 8px;
  }
  
  .movies-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .movie-info {
    padding: 16px;
  }
  
  .movie-title {
    font-size: 1rem;
  }
}
</style>