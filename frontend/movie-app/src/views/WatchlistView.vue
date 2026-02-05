<template>
  <AppLayout>
    <div class="watchlist-view">
      <div class="page-header">
        <h1>我的想看列表</h1>
        <div class="watchlist-stats">
          <el-tag type="primary">{{ watchlistStats.total }} 部电影</el-tag>
          <el-tag type="success">{{ watchlistStats.watching }} 部在看</el-tag>
          <el-tag type="info">{{ watchlistStats.watched }} 部已看</el-tag>
        </div>
      </div>

      <div class="filters">
        <el-radio-group v-model="statusFilter" @change="filterWatchlist">
          <el-radio-button label="all">全部</el-radio-button>
          <el-radio-button label="want_to_watch">想看</el-radio-button>
          <el-radio-button label="watching">在看</el-radio-button>
          <el-radio-button label="watched">已看</el-radio-button>
        </el-radio-group>

        <el-select v-model="sortBy" placeholder="排序方式" @change="filterWatchlist">
          <el-option label="添加时间" value="created_at"></el-option>
          <el-option label="更新时间" value="updated_at"></el-option>
          <el-option label="电影评分" value="rating"></el-option>
          <el-option label="上映时间" value="release_date"></el-option>
        </el-select>
      </div>

      <div v-if="loading" class="loading">
        <el-skeleton :rows="6" animated />
      </div>

      <div v-else-if="error" class="error">
        <el-alert title="加载失败" :description="error" type="error" show-icon />
      </div>

      <div v-else class="watchlist-content">
        <div v-if="filteredWatchlist.length === 0" class="no-results">
          <el-empty description="暂无相关电影">
            <el-button type="primary" @click="router.push({ name: 'movies' })">
              浏览电影
            </el-button>
          </el-empty>
        </div>

        <div v-else class="movies-grid">
          <el-row :gutter="20">
            <el-col v-for="item in filteredWatchlist" :key="item.id" :xs="24" :sm="12" :md="8" :lg="6">
              <el-card class="watchlist-item" @click="goToMovieDetail(getMovieId(item))">
                <div class="movie-poster">
                  <img v-if="getMoviePoster(item)" :src="getMoviePoster(item)"
                    :alt="getMovieTitle(item)" @error="handleImageError" />
                  <div v-else class="no-poster">
                    <el-icon>
                      <Picture />
                    </el-icon>
                    <span>暂无海报</span>
                  </div>
                  <div class="status-badge" :class="`status-${item.status}`">
                    <el-tag :type="getStatusType(item.status)" size="small">
                      {{ getStatusText(item.status) }}
                    </el-tag>
                  </div>
                </div>

                <div class="movie-info">
                  <h4>{{ getMovieTitle(item) }}</h4>
                  <p class="movie-meta">
                    <span>{{ getMovieYear(item) }}</span>
                  </p>
                  <p v-if="getMovieRating(item)" class="movie-rating">
                    <el-icon>
                      <Star />
                    </el-icon>
                    {{ getMovieRating(item) }} / 10
                  </p>
                </div>

                <div class="watchlist-actions">
                  <el-dropdown @command="(command) => handleAction(command, item)" @click.stop>
                    <el-button size="small" text>
                      状态 <el-icon>
                        <ArrowDown />
                      </el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="want_to_watch">
                          想看
                        </el-dropdown-item>
                        <el-dropdown-item command="watching">
                          在看
                        </el-dropdown-item>
                        <el-dropdown-item command="watched">
                          已看
                        </el-dropdown-item>
                        <el-dropdown-item command="remove" divided>
                          移除
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useWatchlistStore } from '@/stores/watchlist'
import { Picture, ArrowDown, Star } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import AppLayout from '@/layouts/AppLayout.vue'

const router = useRouter()
const watchlistStore = useWatchlistStore()

// Reactive state
const statusFilter = ref('all')
const sortBy = ref('created_at')

// Computed properties
const loading = computed(() => watchlistStore.loading)
const error = computed(() => watchlistStore.error)
const watchlist = computed(() => watchlistStore.watchlist)

const watchlistStats = computed(() => {
  return {
    total: watchlist.value.length,
    want_to_watch: watchlist.value.filter(item => item.status === 'want_to_watch').length,
    watching: watchlist.value.filter(item => item.status === 'watching').length,
    watched: watchlist.value.filter(item => item.status === 'watched').length
  }
})

const filteredWatchlist = computed(() => {
  let filtered = watchlist.value

  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(item => item.status === statusFilter.value)
  }

  // 排序逻辑
  filtered.sort((a, b) => {
    switch (sortBy.value) {
      case 'created_at':
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      case 'updated_at':
        return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
      case 'rating':
        return (b.movie_info?.vote_average || 0) - (a.movie_info?.vote_average || 0)
      case 'release_date':
        return new Date(b.movie_info?.release_date).getTime() - new Date(a.movie_info?.release_date).getTime()
      default:
        return 0
    }
  })

  return filtered
})

// Helper functions
const getMovieId = (item: any) => {
  return item.tmdb_movie_id || item.movie
}

const getMovieTitle = (item: any) => {
  return item.movie_title || item.movie_info?.title || '未知电影'
}

const getMoviePoster = (item: any) => {
  return item.movie_poster || item.movie_info?.poster_path
}

const getMovieYear = (item: any) => {
  // 优先从 movie_info 获取
  let date = item.movie_info?.release_date
  
  // 如果没有日期，尝试从其他字段获取
  if (!date) {
    date = item.release_date
  }
  
  if (!date) return '未知年份'
  
  try {
    return new Date(date).getFullYear().toString()
  } catch {
    return '未知年份'
  }
}

const getMovieRating = (item: any) => {
  // 优先从 movie_info 获取
  let rating = item.movie_info?.vote_average
  
  // 如果还是没有，尝试从其他可能的字段获取
  if (!rating) {
    rating = item.vote_average || item.average_rating
  }
  
  return rating ? parseFloat(rating).toFixed(1) : null
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'want_to_watch': return 'info'
    case 'watching': return 'warning'
    case 'watched': return 'success'
    default: return 'info'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'want_to_watch': return '想看'
    case 'watching': return '在看'
    case 'watched': return '已看'
    default: return '未知'
  }
}

// Event handlers
const goToMovieDetail = (movieId: number) => {
  router.push({ name: 'movie-detail', params: { id: movieId } })
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = '/placeholder-movie.jpg'
}

const updateWatchlistStatus = async (watchlistId: number, status: string) => {
  try {
    await watchlistStore.updateWatchlistStatus(watchlistId, status)
    ElMessage.success(`状态已更新为: ${getStatusText(status)}`)
    
    // 状态更新后重新加载整个想看列表以确保数据完整性
    setTimeout(async () => {
      await loadWatchlist()
    }, 500)
  } catch (error) {
    ElMessage.error('更新状态失败')
  }
}

const removeFromWatchlist = async (item: any) => {
  try {
    await watchlistStore.removeFromWatchlist(item.id)
    ElMessage.success(`已从想看列表移除: ${getMovieTitle(item)}`)
  } catch (error) {
    ElMessage.error('移除失败')
  }
}

const handleAction = async (command: string, item: any) => {
  switch (command) {
    case 'want_to_watch':
    case 'watching':
    case 'watched':
      await updateWatchlistStatus(item.id, command)
      break
    case 'remove':
      await removeFromWatchlist(item)
      break
  }
}

const filterWatchlist = () => {
  // 触发重新计算
}

const loadWatchlist = async () => {
  console.log('Loading watchlist...')
  try {
    const result = await watchlistStore.fetchWatchlist()
    console.log('Watchlist load result:', result)
    console.log('Current watchlist store state:', watchlistStore.watchlist)
    console.log('Watchlist length:', watchlistStore.watchlist.length)
    
    if (watchlistStore.watchlist.length > 0) {
      console.log('First watchlist item:', watchlistStore.watchlist[0])
      console.log('First item movie_info:', watchlistStore.watchlist[0].movie_info)
      
      // 检查数据结构
      watchlistStore.watchlist.forEach((item, index) => {
        console.log(`Item ${index}:`, {
          id: item.id,
          movie_id: item.movie,
          tmdb_movie_id: item.tmdb_movie_id,
          movie_title: item.movie_title,
          has_movie_info: !!item.movie_info,
          release_date: item.movie_info?.release_date,
          vote_average: item.movie_info?.vote_average
        })
      })
    }
  } catch (error: any) {
    console.error('Failed to load watchlist:', error)
    console.error('Error response:', error.response?.data)
  }
}

// Lifecycle
onMounted(() => {
  loadWatchlist()
})
</script>

<style scoped>
.watchlist-view {
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.page-header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(135deg, #58a6ff 0%, #79c0ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.watchlist-stats {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.filters {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding: 24px 32px;
  background: linear-gradient(135deg, #161b22 0%, #1a1f2e 100%);
  border: 1px solid #30363d;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
}

.filters::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #58a6ff 0%, #79c0ff 50%, #58a6ff 100%);
}

.movies-grid {
  margin-bottom: 32px;
}

.watchlist-item {
  cursor: pointer;
  transition: transform 0.2s;
  margin-bottom: 24px;
  position: relative;
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 12px;
  overflow: hidden;
}

.watchlist-item:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4);
  border-color: #58a6ff;
}

.movie-poster {
  height: 300px;
  overflow: hidden;
  border-radius: 8px;
  position: relative;
  aspect-ratio: 2/3;
}

.movie-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
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

.status-badge {
  position: absolute;
  top: 10px;
  right: 10px;
}

.movie-info {
  padding: 20px;
}

.movie-info h4 {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #f0f6fc;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.movie-meta {
  font-size: 0.9rem;
  color: #8b949e;
  margin: 0 0 12px 0;
}

.movie-rating {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #fbbf24;
  font-size: 0.9rem;
  margin: 0;
}

.watchlist-actions {
  margin-top: 12px;
}

.loading,
.error,
.no-results {
  margin: 50px 0;
}

/* Responsive Design */
@media (max-width: 768px) {
  .watchlist-view {
    padding: 20px 16px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .filters {
    flex-direction: column;
    gap: 16px;
    padding: 20px 16px;
  }

  .watchlist-stats {
    flex-wrap: wrap;
    gap: 8px;
  }
}
</style>