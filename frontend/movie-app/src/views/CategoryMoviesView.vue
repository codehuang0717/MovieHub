<template>
  <AppLayout>
    <div class="category-movies-view">
      <div class="page-header">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ name: 'home' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item :to="{ name: 'categories' }">分类</el-breadcrumb-item>
          <el-breadcrumb-item>{{ categoryName }}</el-breadcrumb-item>
        </el-breadcrumb>
        <h1>{{ categoryName }}</h1>
        <p v-if="categoryDescription">{{ categoryDescription }}</p>
      </div>

      <div class="filters">
        <el-select v-model="sortBy" placeholder="排序方式" @change="filterMovies">
          <el-option label="热门度" value="popularity.desc"></el-option>
          <el-option label="评分最高" value="vote_average.desc"></el-option>
          <el-option label="最新上映" value="release_date.desc"></el-option>
          <el-option label="名称" value="original_title.asc"></el-option>
        </el-select>
        
        <el-select v-model="selectedYear" placeholder="年份" @change="filterMovies" style="margin-left: 10px;">
          <el-option label="全部" value="" />
          <el-option 
            v-for="year in availableYears" 
            :key="year" 
            :label="year" 
            :value="year.toString()" 
          />
        </el-select>
      </div>

      <div v-if="tmdbStore.loading" class="loading">
        <el-skeleton :rows="6" animated />
      </div>

      <div v-else-if="tmdbStore.error" class="error">
        <el-alert title="加载失败" :description="tmdbStore.error" type="error" show-icon />
      </div>

      <div v-else class="movies-grid">
        <el-row :gutter="20">
          <el-col v-for="movie in currentMovies" :key="movie.id" :xs="24" :sm="12" :md="8" :lg="6">
            <el-card class="movie-card" @click="goToMovieDetail(movie.id)">
              <div class="movie-poster">
                <img 
                  v-if="movie.poster_path" 
                  :src="movie.poster_path" 
                  :alt="movie.title"
                  width="200"
                  height="300"
                  @error="handleImageError"
                />
                <div v-else class="no-poster">
                  <el-icon><Picture /></el-icon>
                  <span>暂无海报</span>
                </div>
                <div class="movie-rating">
                  <el-icon><Star /></el-icon>
                  {{ movie.vote_average?.toFixed(1) }}
                </div>
              </div>
              <div class="movie-info">
                <h3 class="movie-title">{{ movie.title }}</h3>
                <p class="movie-meta">
                  {{ formatDate(movie.release_date) }}
                </p>
                <div class="movie-genres">
                  <el-tag 
                    v-for="genre in getMovieGenres(movie)" 
                    :key="genre" 
                    size="small"
                  >
                    {{ genre }}
                  </el-tag>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <div v-if="currentMovies.length === 0" class="no-results">
          <el-empty description="该分类暂无电影" />
        </div>
      </div>

      <div v-if="totalPages > 1" class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[12, 24, 48]"
          :total="totalMovies"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useTMDBStore } from '@/stores/tmdb'
import { Picture, Star } from '@element-plus/icons-vue'
import AppLayout from '@/layouts/AppLayout.vue'

const route = useRoute()
const router = useRouter()
const { t, locale } = useI18n()
const tmdbStore = useTMDBStore()

const genres = computed(() => [
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

const categoryId = computed(() => parseInt(route.params.id as string))
const categoryName = computed(() => {
  const genre = genres.value.find(g => g.id === categoryId.value)
  return genre ? genre.name : t('common.unknown')
})
const categoryDescription = computed(() => {
  const descriptions: Record<number, string> = {
    28: t('categoryDescriptions.action'),
    12: t('categoryDescriptions.adventure'),
    16: t('categoryDescriptions.animation'),
    35: t('categoryDescriptions.comedy'),
    80: t('categoryDescriptions.crime'),
    99: t('categoryDescriptions.documentary'),
    18: t('categoryDescriptions.drama'),
    10751: t('categoryDescriptions.family'),
    14: t('categoryDescriptions.fantasy'),
    36: t('categoryDescriptions.history'),
    27: t('categoryDescriptions.horror'),
    10402: t('categoryDescriptions.music'),
    9648: t('categoryDescriptions.mystery'),
    10749: t('categoryDescriptions.romance'),
    878: t('categoryDescriptions.sciFi'),
    10770: t('categoryDescriptions.tvMovie'),
    53: t('categoryDescriptions.thriller'),
    10752: t('categoryDescriptions.war'),
    37: t('categoryDescriptions.western')
  }
  return descriptions[categoryId.value] || ''
})

watch(locale, () => {
  filterMovies()
})

const sortBy = ref('popularity.desc')
const selectedYear = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const totalMovies = ref(0)
const totalPages = ref(0)
const genreMovies = ref([])

const currentMovies = computed(() => genreMovies.value)

const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: currentYear - 1899 }, (_, i) => currentYear - i)
})

const goToMovieDetail = (id: number) => {
  router.push({ name: 'movie-detail', params: { id } })
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = '/placeholder-movie.jpg'
}

const formatDate = (dateString: string) => {
  if (!dateString) return '未知'
  return new Date(dateString).getFullYear().toString()
}

const getMovieGenres = (movie: any) => {
  if (!movie.genre_ids) return []
  return movie.genre_ids.map((id: number) => 
    genres.find(g => g.id === id)?.name
  ).filter(Boolean).slice(0, 3)
}

const filterMovies = async () => {
  try {
    const result = await tmdbStore.fetchMoviesByGenre(
      categoryId.value, 
      currentPage.value, 
      selectedYear.value
    )
    genreMovies.value = result.results || []
    totalMovies.value = result.total_results || 0
    totalPages.value = result.total_pages || 0
  } catch (error) {
    console.error('Failed to filter movies:', error)
  }
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  filterMovies()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  filterMovies()
}

onMounted(() => {
  filterMovies()
})
</script>

<style scoped>
.category-movies-view {
  min-height: 100vh;
  background: #0d1117;
  color: #f0f6fc;
  margin-top: 64px;
  padding: 32px 24px;
  max-width: 1400px;
  margin-left: auto;
  margin-right: auto;
}

.page-header {
  margin-bottom: 32px;
}

.page-header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 16px 0;
  background: linear-gradient(135deg, #58a6ff 0%, #79c0ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-header p {
  color: #8b949e;
  margin: 0;
  font-size: 1.1rem;
}

.filters {
  margin-bottom: 32px;
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.movies-grid {
  margin-bottom: 32px;
}

.movie-card {
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  margin-bottom: 24px;
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 12px;
  overflow: hidden;
}

.movie-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4);
  border-color: #58a6ff;
}

.movie-poster {
  height: 300px;
  overflow: hidden;
  position: relative;
  aspect-ratio: 2/3;
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

.no-poster {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: #21262d;
  color: #8b949e;
}

.no-poster .el-icon {
  font-size: 48px;
  margin-bottom: 10px;
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
  color: #f0f6fc;
}

.movie-meta {
  font-size: 0.9rem;
  color: #8b949e;
  margin: 0 0 12px 0;
}

.movie-genres {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.loading,
.error,
.no-results {
  margin: 50px 0;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 32px;
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
</style>