<template>
  <AppLayout>
    <div class="movie-home">

    <!-- Hero Section with Carousel -->
    <section class="hero-section" v-if="heroMovies.length">
      <el-carousel
        class="hero-carousel"
        height="80vh"
        indicator-position="outside"
        :interval="6000"
        arrow="always"
      >
        <el-carousel-item
          v-for="movie in heroMovies"
          :key="movie.id"
        >
          <div class="hero-slide">
            <div class="hero-backdrop" :style="{ backgroundImage: `url(${movie.backdrop_path})` }">
              <div class="hero-overlay"></div>
            </div>
            <div class="hero-content">
              <div class="hero-info">
                <div class="hero-kicker">本周主推</div>
                <h1 class="hero-title">{{ movie.title }}</h1>
                <p class="hero-overview">{{ movie.overview }}</p>
                <div class="hero-meta">
                  <span class="hero-rating">
                    <el-icon><Star /></el-icon> {{ movie.vote_average?.toFixed(1) }}
                  </span>
                  <span class="hero-date">{{ formatDate(movie.release_date) }}</span>
                </div>
                <div class="hero-actions">
                  <el-button type="primary" size="large" @click="goToMovie(movie.id)">
                    <el-icon><VideoPlay /></el-icon> 查看详情
                  </el-button>
                  <el-button size="large" @click="addToWatchlist(movie)">
                    <el-icon><Plus /></el-icon> 加入想看
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </el-carousel-item>
      </el-carousel>
    </section>

    <!-- Popular Movies -->
    <section class="movies-section">
      <div class="section-header">
        <h2>🔥 热门电影</h2>
        <el-button text @click="router.push('/movies')">查看更多 →</el-button>
      </div>

      <div class="movies-grid" v-loading="tmdbStore.loading">
        <div
          v-for="movie in tmdbStore.popularMovies.slice(0, 8)"
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
          </div>
        </div>
      </div>
    </section>

    <!-- Upcoming Movies -->
    <section class="movies-section">
      <div class="section-header">
        <h2>🎬 即将上映</h2>
        <el-button text @click="router.push('/movies?filter=upcoming')">查看更多 →</el-button>
      </div>

      <div class="movies-grid" v-loading="tmdbStore.loading">
        <div
          v-for="movie in tmdbStore.upcomingMovies.slice(0, 6)"
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
          </div>
        </div>
      </div>
    </section>

    <!-- Top Rated -->
    <section class="movies-section">
      <div class="section-header">
        <h2>⭐ 高分电影</h2>
        <el-button text @click="router.push('/movies?filter=top_rated')">查看更多 →</el-button>
      </div>

      <div class="movies-grid" v-loading="tmdbStore.loading">
        <div
          v-for="movie in tmdbStore.topRatedMovies.slice(0, 6)"
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
          </div>
        </div>
      </div>
    </section>
  </div>
</AppLayout>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTMDBStore } from '@/stores/tmdb'
import { useWatchlistStore } from '@/stores/watchlist'
import { Star, VideoPlay, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import AppLayout from '@/layouts/AppLayout.vue'

const router = useRouter()
const authStore = useAuthStore()
const tmdbStore = useTMDBStore()
const watchlistStore = useWatchlistStore()

const heroMovies = computed(() => tmdbStore.popularMovies.slice(0, 5))

const goToMovie = (movieId: number) => {
  router.push({ name: 'movie-detail', params: { id: movieId }})
}



const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = '/placeholder-movie.jpg'
}

const formatDate = (dateString: string) => {
  if (!dateString || dateString === '未知') return '未知'
  return new Date(dateString).getFullYear()
}

const addToWatchlist = async (movie: any) => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    // 首先需要将TMDB电影添加到数据库
    // 暂时使用TMDB ID，后端应该有相应的处理逻辑
    const result = await watchlistStore.toggleWatchlist(movie.id)

    if (result.added) {
      ElMessage.success(`已将《${movie.title}》加入想看列表`)
    } else {
      ElMessage.info(`已将《${movie.title}》从想看列表移除`)
    }
  } catch (error) {
    ElMessage.error('操作失败，请稍后重试')
  }
}



const loadHomeData = async () => {
  try {
    await Promise.all([
      tmdbStore.fetchPopularMovies(),
      tmdbStore.fetchUpcomingMovies(),
      tmdbStore.fetchTopRatedMovies()
    ])
  } catch (error) {
    console.error('Failed to load home data:', error)
    ElMessage.error('加载数据失败')
  }
}

onMounted(() => {
  loadHomeData()
})
</script>

<style scoped>
.movie-home {
  min-height: 100vh;
  background: #0d1117;
  color: #f0f6fc;
}

/* Navigation */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(13, 17, 23, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #30363d;
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
}

.brand-link {
  text-decoration: none;
  color: #58a6ff;
}

.brand-link h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 32px;
  flex: 1;
  margin-left: 48px;
}

.nav-item {
  color: #f0f6fc;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
  position: relative;
}

.nav-item:hover {
  color: #58a6ff;
}

.nav-item.router-link-active {
  color: #58a6ff;
}

.nav-item.router-link-active::after {
  content: '';
  position: absolute;
  bottom: -20px;
  left: 0;
  right: 0;
  height: 2px;
  background: #58a6ff;
}

.nav-search {
  margin-left: auto;
  margin-right: 24px;
}

.search-input {
  width: 280px;
}

:deep(.search-input .el-input__wrapper) {
  background: #21262d;
  border: 1px solid #30363d;
  box-shadow: none;
}

:deep(.search-input .el-input__wrapper:hover) {
  border-color: #58a6ff;
}

:deep(.search-input .el-input__inner) {
  color: #f0f6fc;
}

.search-icon {
  cursor: pointer;
  color: #8b949e;
  transition: color 0.2s;
}

.search-icon:hover {
  color: #58a6ff;
}

.nav-auth {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #58a6ff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.user-avatar:hover {
  transform: scale(1.05);
  background: #1f6feb;
}

/* Hero Section */
.hero-section {
  position: relative;
  height: 80vh;
  min-height: 600px;
  margin-top: 64px;
  overflow: hidden;
}

.hero-carousel {
  height: 100%;
}

:deep(.hero-carousel .el-carousel__container) {
  height: 100% !important;
}

.hero-slide {
  position: relative;
  height: 100%;
}

.hero-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    90deg,
    rgba(13, 17, 23, 0.9) 0%,
    rgba(13, 17, 23, 0.6) 50%,
    rgba(13, 17, 23, 0.3) 100%
  );
}

.hero-content {
  position: relative;
  z-index: 1;
  height: 100%;
  display: flex;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
}

.hero-info {
  max-width: 600px;
}

.hero-kicker {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  color: #79c0ff;
  background: rgba(88, 166, 255, 0.15);
  border: 1px solid rgba(88, 166, 255, 0.3);
  padding: 6px 12px;
  border-radius: 999px;
  margin-bottom: 16px;
}

.hero-title {
  font-size: 4rem;
  font-weight: 700;
  margin: 0 0 24px 0;
  line-height: 1.1;
  background: linear-gradient(135deg, #58a6ff 0%, #79c0ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-overview {
  font-size: 1.2rem;
  line-height: 1.6;
  color: #c9d1d9;
  margin: 0 0 32px 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.hero-meta {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 32px;
}

.hero-rating {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #fbbf24;
  font-weight: 600;
}

.hero-date {
  color: #8b949e;
  font-size: 1rem;
}

.hero-actions {
  display: flex;
  gap: 16px;
}

/* Movies Sections */
.movies-section {
  max-width: 1400px;
  margin: 0 auto;
  padding: 64px 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.section-header h2 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
  color: #f0f6fc;
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 24px;
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
}

.movie-date {
  color: #8b949e;
  font-size: 0.875rem;
  margin: 0;
}

/* Responsive Design */
@media (max-width: 1400px) {
  .hero-content {
    padding: 0 32px;
  }

  .movies-section {
    padding: 48px 32px;
  }
}

@media (max-width: 1200px) {
  .nav-container {
    padding: 0 20px;
  }

  .hero-content {
    padding: 0 20px;
    flex-direction: column;
    text-align: center;
    gap: 32px;
  }

  .hero-info {
    max-width: 100%;
  }

  .hero-title {
    font-size: 3rem;
  }

  .movies-grid {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  }

  .movies-section {
    padding: 40px 20px;
  }
}

@media (max-width: 992px) {
  .nav-menu {
    display: none;
  }

  .nav-search {
    display: none;
  }

  .hero-title {
    font-size: 2.5rem;
  }

  .hero-overview {
    font-size: 1rem;
  }

  .hero-actions {
    justify-content: center;
  }

  .movies-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 20px;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .movies-section {
    padding: 32px 16px;
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }

  .hero-overview {
    font-size: 0.9rem;
    -webkit-line-clamp: 2;
  }

  .hero-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .hero-actions {
    flex-direction: column;
    width: 100%;
  }

  .hero-actions .el-button {
    width: 100%;
  }

  .movies-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 16px;
  }

  .section-header h2 {
    font-size: 1.5rem;
  }

  .movies-section {
    padding: 24px 12px;
  }
}

@media (max-width: 480px) {
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

  .hero-section {
    height: 60vh;
    min-height: 500px;
  }

  .hero-title {
    font-size: 1.8rem;
  }

  .movies-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 12px;
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

  .section-header h2 {
    font-size: 1.3rem;
  }
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #0d1117;
}

::-webkit-scrollbar-thumb {
  background: #30363d;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #484f58;
}
</style>
