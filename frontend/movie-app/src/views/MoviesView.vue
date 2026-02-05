<template>
  <AppLayout>
    <div class="movies-page">
      <!-- Main Content -->
      <main class="main-content">
        <!-- Filter Bar -->
        <div class="filter-bar" :class="{ 'filter-bar-compact': isFilterSticky }">
          <!-- 展开状态：完整筛选框 -->
          <transition name="filter-expand">
            <div class="filter-container" v-show="!isFilterSticky">
              <div class="filter-section">
                <h3>电影类型</h3>
                <div class="genre-filters">
                  <el-button
                    v-for="genre in genres"
                    :key="genre.id"
                    :type="selectedGenre === genre.id ? 'primary' : 'default'"
                    @click="selectGenre(genre.id)"
                    class="genre-btn"
                  >
                    {{ genre.name }}
                  </el-button>
                </div>
              </div>

              <div class="filter-section">
                <h3>{{ $t('movie.sortBy') }}</h3>
                <el-radio-group v-model="sortBy">
                  <el-radio label="popularity.desc">{{ $t('movie.popular') }}</el-radio>
                  <el-radio label="vote_average.desc">{{ $t('movie.topRated') }}</el-radio>
                  <el-radio label="release_date.desc">{{ $t('movie.latestRelease') }}</el-radio>
                  <el-radio label="primary_release_date.desc">{{ $t('movie.upcomingRelease') }}</el-radio>
                </el-radio-group>
              </div>

              <div class="filter-section">
                <h3>{{ $t('movie.otherFilters') }}</h3>
                <el-form-item :label="$t('movie.releaseYear')">
                  <el-select v-model="selectedYear" @change="handleYearChange" :placeholder="$t('movie.selectYear')">
                    <el-option :label="$t('common.all')" value="" />
                    <el-option
                      v-for="year in availableYears"
                      :key="year"
                      :label="year"
                      :value="year"
                    />
                  </el-select>
                </el-form-item>
              </div>
            </div>
          </transition>

          <!-- 紧凑状态：显示类型筛选和基本排序 -->
          <transition name="filter-compact">
            <div class="filter-compact" v-show="isFilterSticky">
              <div class="compact-genres">
                <span class="compact-label">{{ $t('movie.genreType') }}：</span>
                <div class="compact-genre-buttons">
                  <el-button
                    v-for="genre in genres.slice(0, 8)"
                    :key="genre.id"
                    :type="selectedGenre === genre.id ? 'primary' : 'default'"
                    @click="selectGenre(genre.id)"
                    size="small"
                  >
                    {{ genre.name }}
                  </el-button>
                </div>
              </div>
              <div class="compact-sort">
                <span class="compact-label">{{ $t('movie.sortBy') }}：</span>
                <div class="compact-sort-buttons">
                  <el-button
                    :type="sortBy === 'popularity.desc' ? 'primary' : 'default'"
                    @click="sortBy = 'popularity.desc'"
                    size="small"
                  >
                    {{ $t('movie.popular') }}
                  </el-button>
                  <el-button
                    :type="sortBy === 'vote_average.desc' ? 'primary' : 'default'"
                    @click="sortBy = 'vote_average.desc'"
                    size="small"
                  >
                    {{ $t('movie.rating') }}
                  </el-button>
                  <el-button
                    :type="sortBy === 'release_date.desc' ? 'primary' : 'default'"
                    @click="sortBy = 'release_date.desc'"
                    size="small"
                  >
                    {{ $t('movie.latestRelease') }}
                  </el-button>
                </div>
              </div>
            </div>
          </transition>
        </div>

        <!-- Debug Info -->
        <!-- <div v-if="selectedGenre" style="background: #1a1f2e; padding: 10px; margin: 10px 0; border-radius: 5px; color: white;">
          <strong>调试信息：</strong><br>
          当前类型: {{ selectedGenre }}<br>
          当前排序: {{ sortBy }}<br>
          电影数量: {{ currentMovies.length }}<br>
          <small style="color: #8b949e;">注意：现在使用客户端排序确保准确性</small><br>
          <button @click="testDirectAPI" style="margin: 5px; padding: 5px 10px; background: #58a6ff; color: white; border: none; border-radius: 3px; cursor: pointer;">
            测试排序效果
          </button>
            <button @click="testAPI" style="margin: 5px; padding: 5px 10px; background: #58a6ff; color: white; border: none; border-radius: 3px; cursor: pointer;">
            测试API调用
          </button>
        </div> -->

        <!-- Movies Grid -->
        <div class="movies-container">
            <div class="movies-header">
              <h2 v-if="selectedGenreName">{{ $t('movie.genreMovies', { name: selectedGenreName }) }}</h2>
              <h2 v-else>{{ $t('movie.allMovies') }}</h2>
              <div class="header-info">
                <span class="results-count">{{ $t('movie.moviesCount', { count: currentMovies.length, total: totalResults }) }}</span>
                <span class="sort-indicator" v-if="sortBy && selectedGenre">
                  {{ $t('movie.sortLabel', { label: getSortLabel(sortBy) }) }}
                </span>
                <span class="filter-note" v-if="sortBy === 'release_date.desc' || sortBy === 'primary_release_date.desc'">
                  {{ sortBy === 'release_date.desc' ? $t('movie.showReleased') : $t('movie.showUpcoming') }}
                </span>
              </div>
            </div>

          <div class="movies-grid" v-loading="tmdbStore.loading || tmdbStore.genreLoading || isLoadingMovies">
            <div
              v-for="movie in currentMovies"
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
                  :class="{ 'placeholder-image': isPlaceholderImage(movie.poster_path) }"
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
                    :key="genre.id"
                    size="small"
                  >
                    {{ genre.name }}
                  </el-tag>
                </div>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-if="currentMovies.length === 0 && !tmdbStore.loading" class="empty-state">
            <el-empty :description="$t('movie.noMoviesFound')" />
          </div>

          <!-- Pagination -->
          <div v-if="totalResults > 20" class="pagination">
            <el-pagination
              v-model:current-page="currentPage"
              :page-size="20"
              :total="totalResults"
              layout="prev, pager, next, jumper, total"
              @current-change="handlePageChange"
            />
          </div>
        </div>
      </main>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useTMDBStore } from '@/stores/tmdb'
import { Search, User, Star, Collection, SwitchButton, ArrowUp } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import AppLayout from '@/layouts/AppLayout.vue'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const tmdbStore = useTMDBStore()

const searchQuery = ref('')
const sortBy = ref('popularity.desc')
const selectedGenre = ref<number | null>(null)
const selectedYear = ref('')
const currentPage = ref(1)
const totalResults = ref(0)
const isFilterSticky = ref(false)
const scrollTimeout = ref<number | null>(null)
const isAnimating = ref(false)
const currentMoviesData = ref([])
const isLoadingMovies = ref(false)

const genres = computed(() => [
  { id: null, name: t('common.all') },
  { id: 28, name: t('categories.action') },
  { id: 12, name: t('categories.adventure') },
  { id: 16, name: t('categories.animation') },
  { id: 35, name: t('categories.comedy') },
  { id: 80, name: t('categories.crime') },
  { id: 99, name: t('categories.documentary') },
  { id: 18, name: t('categories.drama') },
  { id: 10751, name: t('categories.family') },
  { id: 14, name: t('categories.fantasy') },
  { id: 36, name: t('categories.history') },
  { id: 27, name: t('categories.horror') },
  { id: 10402, name: t('categories.music') },
  { id: 9648, name: t('categories.mystery') },
  { id: 10749, name: t('categories.romance') },
  { id: 878, name: t('categories.sciFi') },
  { id: 10770, name: t('categories.tvMovie') },
  { id: 53, name: t('categories.thriller') },
  { id: 10752, name: t('categories.war') },
  { id: 37, name: t('categories.western') }
])

const { locale } = useI18n()

watch(locale, () => {
  currentMoviesData.value = []
  tmdbStore.genreMovies = []
  loadMovies()
})

// Computed properties
const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: currentYear - 1899 }, (_, i) => currentYear - i)
})

const selectedGenreName = computed(() => {
  const genre = genres.value.find(g => g.id === selectedGenre.value)
  return genre ? genre.name : null
})

const currentMovies = computed(() => {
  // 直接返回API数据，不做客户端过滤
  if (selectedGenre.value && selectedGenre.value !== null) {
    return tmdbStore.genreMovies || []
  } else {
    return currentMoviesData.value || []
  }
})

// Helper functions
const formatDate = (dateString: string) => {
  if (!dateString || dateString === t('common.unknown')) return t('common.unknown')
  return new Date(dateString).getFullYear().toString()
}

const getMovieGenres = (movie: any) => {
  if (!movie.genre_ids) return []
  return movie.genre_ids.map((id: number) =>
    genres.value.find(g => g.id === id)
  ).filter(Boolean).slice(0, 3)
}

const isPlaceholderImage = (posterPath: string) => {
  return posterPath && (posterPath.includes('placeholder-movie.jpg') || posterPath.includes('placeholder-movie.svg'))
}

const getSortLabel = (sortBy: string) => {
  const sortLabels: { [key: string]: string } = {
    'popularity.desc': t('movie.popular'),
    'vote_average.desc': t('movie.topRated'),
    'release_date.desc': t('movie.latestRelease'),
    'primary_release_date.desc': t('movie.upcomingRelease')
  }
  return sortLabels[sortBy] || sortBy
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  if (!img.src.includes('placeholder-movie.svg') && !img.src.includes('placeholder-movie.jpg')) {
    img.src = '/placeholder-movie.svg'
    img.alt = t('movie.noPosterAvailable')
    img.setAttribute('data-error-handled', 'true')
  }
}

// Event handlers
const goToMovie = (movieId: number) => {
  router.push({ name: 'movie-detail', params: { id: movieId }})
}

const performSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({ name: 'search', query: { q: searchQuery.value.trim() }})
  }
}

const updateURL = () => {
  const query: any = {}

  if (selectedGenre.value !== null) {
    query.genre = selectedGenre.value
  }
  if (sortBy.value !== 'popularity.desc') {
    query.sort = sortBy.value
  }
  if (selectedYear.value) {
    query.year = selectedYear.value
  }
  if (currentPage.value > 1) {
    query.page = currentPage.value
  }

  router.replace({ name: 'movies', query })
}

const selectGenre = (genreId: number | null) => {
  // 如果点击的是当前选中的分类，则取消选择
  if (selectedGenre.value === genreId) {
    selectedGenre.value = null
  } else {
    selectedGenre.value = genreId
  }
  currentPage.value = 1

  // 清空当前数据以显示加载状态
  if (!genreId) {
    currentMoviesData.value = [] // 切换到"全部"时清空本地数据
  } else {
    tmdbStore.genreMovies = [] // 切换到特定类型时清空分类数据
  }

  loadMovies()
  updateURL()
}

// Sort change is now handled by the watch on sortBy

const handleYearChange = () => {
  currentPage.value = 1

  // 根据当前选择的类型清空相应的数据
  if (selectedGenre.value) {
    tmdbStore.genreMovies = [] // 清空分类数据
  } else {
    currentMoviesData.value = [] // 清空全部电影数据
  }

  console.log('Year changed to:', selectedYear.value)
  loadMovies()
  updateURL()
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  loadMovies()
  updateURL()
}

const handleScroll = () => {
  // 如果正在动画中，跳过这次滚动处理
  if (isAnimating.value) {
    return
  }

  // 清除之前的定时器
  if (scrollTimeout.value) {
    clearTimeout(scrollTimeout.value)
  }

  // 设置新的定时器，防抖处理 - 增加防抖时间避免频繁触发
  scrollTimeout.value = setTimeout(() => {
    const scrollY = window.scrollY
    const shouldBeSticky = scrollY > 200

    // 只有状态真正改变时才更新，避免不必要的重新渲染
    if (isFilterSticky.value !== shouldBeSticky) {
      // 标记开始动画
      isAnimating.value = true
      isFilterSticky.value = shouldBeSticky

      // 动画完成后重置标记
      setTimeout(() => {
        isAnimating.value = false
      }, 300) // 300ms后重置动画状态，确保动画完成
    }
  }, 50) // 50ms防抖，更好的性能和用户体验
}

const handleLogout = async () => {
  await authStore.logout()
  ElMessage.success(t('auth.logoutSuccess'))
}

const loadMovies = async () => {
  try {
    isLoadingMovies.value = true
    console.log('Loading movies with params:', {
      selectedGenre: selectedGenre.value,
      sortBy: sortBy.value,
      year: selectedYear.value,
      page: currentPage.value
    })

    if (selectedGenre.value && selectedGenre.value !== null) {
      console.log('Loading genre movies with sortBy:', sortBy.value)
      const result = await tmdbStore.fetchMoviesByGenre(selectedGenre.value, currentPage.value, selectedYear.value, sortBy.value)
      totalResults.value = result.total_results || result.total_pages * 20
      console.log('Genre movies loaded:', result.results.length, 'movies', 'sorted by:', sortBy.value)
      console.log('Sample movie sort data:', result.results[0]?.title, 'popularity:', result.results[0]?.popularity, 'vote_average:', result.results[0]?.vote_average)
    } else {
      console.log('Loading all movies with sortBy:', sortBy.value)
      const movieData = await tmdbStore.fetchDiscoverMovies(sortBy.value, currentPage.value, selectedYear.value)

      currentMoviesData.value = movieData.results || []
      totalResults.value = movieData.total_results || 1000
      console.log('Movies loaded:', movieData.results?.length || 0, 'movies for sort:', sortBy.value)
    }
  } catch (error) {
    console.error('Failed to load movies:', error)
    ElMessage.error(t('movie.loadingFailed'))
  } finally {
    isLoadingMovies.value = false
  }
}

const initializeFromRoute = () => {
  const filter = route.query.filter as string

  switch (filter) {
    case 'top_rated':
      sortBy.value = 'vote_average.desc'
      break
    case 'upcoming':
      sortBy.value = 'primary_release_date.desc'
      break
    default:
      sortBy.value = 'popularity.desc'
  }

  // 从URL查询参数中恢复状态
  if (route.query.genre) {
    selectedGenre.value = Number(route.query.genre)
  }
  if (route.query.sort) {
    sortBy.value = route.query.sort as string
  }
  if (route.query.year) {
    selectedYear.value = route.query.year as string
  }
  if (route.query.page) {
    currentPage.value = Number(route.query.page)
  }
}

// Watchers
watch(() => route.query, () => {
  initializeFromRoute()

  // 根据当前选择的类型清空相应的数据
  if (selectedGenre.value) {
    tmdbStore.genreMovies = [] // 清空分类数据
  } else {
    currentMoviesData.value = [] // 清空全部电影数据
  }

  loadMovies()
})

// Watch sortBy changes to ensure sorting works correctly
watch(sortBy, (newSortBy, oldSortBy) => {
  if (newSortBy !== oldSortBy) {
    console.log('=== SORT CHANGE DETECTED ===')
    console.log('Sort changed from', oldSortBy, 'to', newSortBy)
    console.log('Current genre:', selectedGenre.value)
    console.log('Current page before reset:', currentPage.value)

    currentPage.value = 1

    // 根据当前选择的类型清空相应的数据
    if (selectedGenre.value) {
      console.log('Clearing genre movies for sorting')
      tmdbStore.genreMovies = [] // 清空分类数据
    } else {
      console.log('Clearing all movies for sorting')
      currentMoviesData.value = [] // 清空全部电影数据
    }

    console.log('Calling loadMovies with new sort...')
    loadMovies()
    updateURL()
  }
}, { immediate: false })

// Watch selectedGenre changes
watch(selectedGenre, (newGenre, oldGenre) => {
  if (newGenre !== oldGenre) {
    console.log('=== GENRE CHANGE DETECTED ===')
    console.log('Genre changed from', oldGenre, 'to', newGenre)
    console.log('Current sort:', sortBy.value)
  }
}, { immediate: false })

// Test function
const testDirectAPI = async () => {
  console.log('=== TESTING DIRECT API CALL ===')
  try {
    if (selectedGenre.value) {
      console.log('Testing with genre:', selectedGenre.value, 'sort:', sortBy.value)
      
      // 测试不同的排序方式
      const testSorts = ['popularity.desc', 'vote_average.desc', 'release_date.desc']
      
      for (const sortType of testSorts) {
        console.log(`\n--- Testing sort: ${sortType} ---`)
        const result = await tmdbStore.fetchMoviesByGenre(
          selectedGenre.value, 
          1, 
          selectedYear.value, 
          sortType
        )
        console.log('Top 5 movies:', result.results.slice(0, 5).map(m => ({ 
          title: m.title, 
          rating: m.vote_average, 
          popularity: m.popularity,
          release_date: m.release_date 
        })))
      }
    }
  } catch (error) {
    console.error('Direct API test failed:', error)
  }
}

// Simple API test
const testAPI = async () => {
  console.log('=== TESTING API CALLS ===')
  try {
    console.log('Current genre:', selectedGenre.value)
    console.log('Current sort:', sortBy.value)
    console.log('Current year:', selectedYear.value)
    
    // 重新调用一次API来查看结果
    await loadMovies()
  } catch (error) {
    console.error('API test failed:', error)
  }
}

// Lifecycle
onMounted(() => {
  initializeFromRoute()
  loadMovies()
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.movies-page {
  min-height: 100vh;
  background: #0d1117;
  color: #f0f6fc;
}

/* Main Content */
.main-content {
  margin-top: 64px;
}

/* Filter Bar */
.filter-bar {
  background: #161b22;
  border-bottom: 1px solid #30363d;
  padding: 0;
  position: relative;
  z-index: 10;
  transition: all 0.15s ease;
}

.filter-bar-compact {
  position: fixed;
  top: 64px;
  left: 0;
  right: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  z-index: 100;
}

.filter-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px 24px;
  display: flex;
  flex-wrap: wrap;
  gap: 32px;
  align-items: flex-start;
}

/* Filter Animations */
.filter-expand-enter-active {
  transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  transform-origin: top;
}

.filter-expand-leave-active {
  transition: all 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  transform-origin: top;
}

.filter-expand-enter-from,
.filter-expand-leave-to {
  opacity: 0;
  transform: scaleY(0);
  max-height: 0;
}

.filter-expand-enter-to,
.filter-expand-leave-from {
  opacity: 1;
  transform: scaleY(1);
  max-height: 300px;
}

.filter-compact-enter-active {
  transition: all 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.filter-compact-leave-active {
  transition: all 0.15s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.filter-compact-enter-from,
.filter-compact-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.filter-compact-enter-to,
.filter-compact-leave-from {
  opacity: 1;
  transform: translateY(0);
}

/* Compact Filter */
.filter-compact {
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px 24px;
  background: rgba(22, 27, 34, 0.98);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid #30363d;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 24px;
  align-items: center;
}

.compact-genres {
  display: flex;
  align-items: center;
  gap: 16px;
  overflow-x: auto;
  padding: 4px 0;
}

.compact-sort {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
}

.compact-label {
  color: #58a6ff;
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  flex-shrink: 0;
  padding: 6px 12px;
  background: rgba(88, 166, 255, 0.1);
  border-radius: 16px;
  border: 1px solid rgba(88, 166, 255, 0.2);
}

.compact-genre-buttons {
  display: flex;
  gap: 6px;
  flex-wrap: nowrap;
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
  padding: 2px;
}

.compact-genre-buttons::-webkit-scrollbar {
  display: none;
}

.compact-sort-buttons {
  display: flex;
  gap: 6px;
  flex-wrap: nowrap;
}

.compact-genre-buttons .el-button {
  flex-shrink: 0;
  border-radius: 16px;
  padding: 8px 14px;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.1s ease;
  border: 1px solid #30363d;
}

.compact-genre-buttons .el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(88, 166, 255, 0.3);
  border-color: #58a6ff;
}

.compact-genre-buttons .el-button.is-primary {
  background: linear-gradient(135deg, #58a6ff 0%, #79c0ff 100%);
  border: none;
}

/* Movies Container */
.movies-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px 24px;
  margin-top: 0;
  transition: margin-top 0.15s ease;
}

.filter-bar-compact ~ .movies-container {
  margin-top: 140px;
}

.movies-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.header-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.sort-indicator {
  background: rgba(88, 166, 255, 0.2);
  color: #58a6ff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
}

.filter-note {
  background: rgba(250, 179, 36, 0.2);
  color: #facc15;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 400;
}

.movies-header h2 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
  color: #f0f6fc;
}

.results-count {
  color: #8b949e;
  font-size: 1rem;
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 24px;
  margin-bottom: 48px;
}

.movie-card {
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
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

.movie-poster img.placeholder-image {
  object-fit: contain;
  background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
  opacity: 0.8;
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
  padding: 16px;
}

.movie-title {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 8px 0;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  color: #f0f6fc;
}

.movie-date {
  color: #8b949e;
  font-size: 0.875rem;
  margin: 0 0 12px 0;
}

.movie-genres {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.empty-state {
  text-align: center;
  margin: 80px 0;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 48px;
}

/* Filter Sections */
.filter-section {
  flex: 1;
  min-width: 280px;
}

.filter-section h3 {
  margin: 0 0 16px 0;
  color: #f0f6fc;
  font-size: 1.1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-section h3::before {
  content: '';
  width: 4px;
  height: 20px;
  background: linear-gradient(135deg, #58a6ff 0%, #79c0ff 100%);
  border-radius: 2px;
}

.genre-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.genre-btn {
  border-radius: 20px;
  padding: 8px 16px;
  font-size: 0.9rem;
  transition: all 0.1s ease;
  border: 1px solid transparent;
}

.genre-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(88, 166, 255, 0.2);
}

:deep(.el-radio) {
  margin-right: 16px;
  margin-bottom: 12px;
}

:deep(.el-radio__label) {
  color: #f0f6fc;
  font-size: 0.95rem;
}

:deep(.el-radio.is-checked .el-radio__label) {
  color: #58a6ff;
  font-weight: 600;
}

:deep(.el-form-item__label) {
  color: #8b949e;
  font-weight: 500;
}

:deep(.el-radio) {
  color: #f0f6fc;
  margin-bottom: 8px;
}

:deep(.el-radio__label) {
  color: #f0f6fc;
}

:deep(.el-select) {
  --el-select-input-color: #f0f6fc;
  --el-select-input-font-size: 14px;
  --el-select-background-color: #21262d;
  --el-select-border-color-hover: #58a6ff;
  --el-select-border-color: #30363d;
  --el-select-color: #f0f6fc;
}

:deep(.el-select-dropdown) {
  background-color: #21262d;
  border-color: #30363d;
}

:deep(.el-select-dropdown__item) {
  color: #f0f6fc;
}

:deep(.el-select-dropdown__item:hover) {
  background-color: #30363d;
}

:deep(.el-select-dropdown__item.selected) {
  background-color: #58a6ff;
  color: #fff;
}

:deep(.el-pagination) {
  --el-pagination-button-bg-color: #161b22;
  --el-pagination-hover-color: #58a6ff;
  --el-pagination-text-color: #f0f6fc;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .filter-container {
    padding: 0 20px;
  }

  .movies-container {
    padding: 32px 20px;
  }
}

@media (max-width: 1024px) {
  .nav-menu {
    display: none;
  }

  .nav-search {
    display: none;
  }

  .filter-container {
    flex-direction: column;
    gap: 24px;
    padding: 24px 16px;
  }

  .filter-section {
    min-width: auto;
    width: 100%;
  }

  .movies-container {
    padding: 24px 16px;
  }

  .filter-bar-compact ~ .movies-container {
    margin-top: 140px;
  }

  .movies-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  }
}

@media (max-width: 768px) {
  .nav-brand h1 {
    font-size: 20px;
  }

  .nav-auth {
    gap: 8px;
  }

  .nav-auth .el-button {
    padding: 8px 12px;
    font-size: 14px;
  }

  .filter-container {
    padding: 20px 12px;
  }

  .filter-section {
    margin-bottom: 20px;
  }

  .filter-section h3 {
    font-size: 1rem;
    margin-bottom: 12px;
  }

  .genre-filters {
    gap: 6px;
  }

  .genre-btn {
    padding: 6px 12px;
    font-size: 0.85rem;
  }

  .movies-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .movies-header h2 {
    font-size: 1.5rem;
  }

  .movies-container {
    padding: 20px 12px;
  }

  .movies-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 12px;
  }

  .filter-bar-compact ~ .movies-container {
    margin-top: 160px;
  }

  .compact-genres {
    gap: 12px;
  }

  .compact-label {
    font-size: 12px;
    padding: 4px 8px;
  }

  .compact-genre-buttons .el-button {
    padding: 6px 10px;
    font-size: 11px;
  }
}

@media (max-width: 480px) {
  .filter-container {
    padding: 0 8px;
  }

  .genre-filters {
    grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
  }

  .genre-btn {
    font-size: 0.8rem;
    padding: 4px 8px;
  }

  .movies-header h2 {
    font-size: 1.3rem;
  }

  .results-count {
    font-size: 0.9rem;
  }

  .movies-container {
    padding: 16px 8px;
  }

  .movies-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 10px;
  }

  .movie-card {
    border-radius: 8px;
  }

  .movie-poster {
    border-radius: 8px;
  }

  .movie-info {
    padding: 12px;
  }

  .movie-title {
    font-size: 0.9rem;
  }

  .movie-date {
    font-size: 0.8rem;
  }
}
</style>
