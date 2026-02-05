<template>
  <AppLayout>
    <div class="movie-detail-page">
      <!-- Loading State -->
      <div v-if="tmdbStore.loading" class="loading-container">
        <el-skeleton :rows="8" animated />
      </div>

      <!-- Error State -->
      <div v-else-if="!movie" class="error-container">
        <el-result icon="error" :title="$t('errors.loadFailed')" :sub-title="$t('errors.loadMovieFailed')">
          <template #extra>
            <el-button type="primary" @click="router.push('/movies')">{{ $t('movie.backToList') }}</el-button>
          </template>
        </el-result>
      </div>

      <!-- Movie Content -->
      <div v-else class="movie-content">
        <!-- Hero Section -->
        <section class="movie-hero">
          <div class="hero-backdrop" :style="{ backgroundImage: `url(${movie.backdrop_path})` }">
            <div class="hero-overlay"></div>
          </div>

          <div class="hero-content">
            <!-- Back Button - Position outside hero-container -->
            <div class="back-button-container">
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
            
            <div class="hero-container">

              <div class="movie-poster">
                <img :src="movie.poster_path" :alt="movie.title" @error="handleImageError" />
              </div>

              <div class="movie-info">
                <h1 class="movie-title">{{ movie.title }}</h1>
                <h2 v-if="movie.tagline" class="movie-tagline">{{ movie.tagline }}</h2>

                <div class="movie-meta">
                  <span class="movie-rating">
                    <el-icon><Star /></el-icon>
                    {{ movie.vote_average?.toFixed(1) }} / 10
                  </span>
                  <span class="movie-votes">{{ t('movieDetail.voteCount', { count: formatNumber(movie.vote_count) }) }}</span>
                  <span class="movie-date">{{ formatDate(movie.release_date) }}</span>
                  <span class="movie-runtime">{{ formatRuntime(movie.runtime) }}</span>
                </div>

                <div class="movie-genres">
                  <el-tag v-for="genre in movie.genres" :key="genre.id" size="large">
                    {{ genre.name }}
                  </el-tag>
                </div>

                <div class="movie-actions">
                  <el-button type="primary" size="large" @click="addToWatchlist">
                    <el-icon><Plus /></el-icon> {{ $t('home.addToWatchlist') }}
                  </el-button>
                  <el-button size="large" @click="addToCollection">
                    <el-icon><Collection /></el-icon> {{ $t('collections.myCollections') }}
                  </el-button>
                  <el-button size="large" @click="rateMovie">
                    <el-icon><Star /></el-icon> {{ $t('review.rating') }}
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Content Sections -->
        <div class="content-container">
          <!-- Overview -->
          <section class="content-section">
            <h3>{{ $t('movie.overview') }}</h3>
            <p class="movie-overview">{{ movie.overview }}</p>
          </section>

          <!-- Ratings -->
          <section class="content-section ratings-section">
            <div class="ratings-header">
              <h3>{{ $t('review.ratingsAndReviews') }}</h3>
              <div class="ratings-summary">
                <div class="average-score">
                  <div class="score-value">{{ formatAverage(ratingStats?.average_rating) }}</div>
                  <div class="score-label">{{ $t('review.overallRating') }}</div>
                </div>
                <div class="score-meta">
                  <div class="score-count">{{ ratingStats?.total_ratings || 0 }} {{ $t('review.peopleRated') }}</div>
                  <div class="score-tip">{{ $t('review.basedOnStats') }}</div>
                </div>
              </div>
            </div>

            <div class="ratings-body">
              <div class="rating-distribution">
                <div v-for="star in [5, 4, 3, 2, 1]" :key="star" class="rating-row">
                  <span class="rating-star">{{ star }} {{ $t('review.star') }}</span>
                  <div class="rating-bar">
                    <div class="rating-bar-fill" :style="{ width: `${getRatingPercent(star)}%` }"></div>
                  </div>
                  <span class="rating-count">{{ ratingStats?.[`rating_${star}`] || 0 }}</span>
                </div>
              </div>

              <div class="user-rating-card">
                <div class="user-rating-title">{{ $t('review.myRating') }}</div>
                <el-rate
                  v-model="userRatingInput"
                  :max="5"
                  :disabled="ratingSubmitting"
                  @change="submitUserRating"
                />
                <div v-if="!authStore.isAuthenticated" class="user-rating-hint">
                  {{ $t('review.loginToRate') }}
                </div>
                <div v-else class="user-rating-hint">
                  {{ userRatingId ? $t('review.alreadyRated') : $t('review.rateAndComment') }}
                </div>
              </div>
            </div>
          </section>

          <!-- Comments -->
          <section class="content-section comments-section">
            <div class="comments-header">
              <h3>{{ $t('review.comments') }}</h3>
              <span class="comments-count">{{ comments.length }} {{ $t('review.items') }}</span>
            </div>

            <div v-if="authStore.isAuthenticated" class="comment-form">
              <el-input
                v-model="commentForm.content"
                type="textarea"
                :rows="4"
                maxlength="2000"
                show-word-limit
                :placeholder="$t('review.writeFeelings')"
              />
              <div class="comment-actions">
                <el-switch
                  v-model="commentForm.is_long_review"
                  :active-text="$t('review.longReview')"
                  :inactive-text="$t('review.shortReview')"
                />
                <el-button type="primary" :loading="commentSubmitting" @click="submitComment">
                  {{ $t('review.submitReview') }}
                </el-button>
              </div>
            </div>
            <div v-else class="comment-login-hint">
              {{ $t('review.loginToRate') }}
            </div>

            <div class="comments-list" v-loading="commentsLoading">
              <div v-for="comment in comments" :key="comment.id" class="comment-card">
                <div class="comment-header">
                  <div class="comment-user">
                    <div class="comment-avatar">
                      <img
                        v-if="comment.user_avatar"
                        :src="comment.user_avatar"
                        :alt="comment.user"
                        class="comment-avatar-img"
                        @error="handleImageError"
                      />
                      <span v-else>
                        {{ comment.user?.charAt(0).toUpperCase() || 'U' }}
                      </span>
                    </div>
                    <div>
                      <div class="comment-name">{{ comment.user }}</div>
                      <div class="comment-date">{{ formatDateTime(comment.created_at) }}</div>
                    </div>
                  </div>
                  <div class="comment-tags">
                    <el-tag v-if="comment.is_long_review" size="small" type="warning">{{ $t('review.longReview') }}</el-tag>
                    <el-button text size="small" @click="toggleLike(comment)">
                      <el-icon><Pointer /></el-icon>
                      {{ comment.likes_count || 0 }}
                    </el-button>
                    <el-button
                      v-if="isOwnComment(comment)"
                      text
                      size="small"
                      type="danger"
                      @click="removeComment(comment)"
                    >
                      {{ $t('review.delete') }}
                    </el-button>
                  </div>
                </div>
                <p class="comment-content">{{ comment.content }}</p>
              </div>
            </div>

            <div v-if="!commentsLoading && comments.length === 0" class="comments-empty">
              <el-empty :description="$t('review.beFirstToComment')" />
            </div>
          </section>

          <!-- Cast -->
          <section class="content-section" v-if="movie.cast && movie.cast.length > 0">
            <h3>{{ $t('movie.cast') }}</h3>
            <div class="cast-grid">
              <div
                v-for="person in movie.cast.slice(0, 8)"
                :key="person.id"
                class="cast-item"
              >
                <div class="cast-avatar">
                  <img
                    v-if="person.profile_path"
                    :src="`https://image.tmdb.org/t/p/w200${person.profile_path}`"
                    :alt="person.name"
                    @error="handleImageError"
                  />
                  <div v-else class="no-avatar">
                    <el-icon><User /></el-icon>
                  </div>
                </div>
                <div class="cast-info">
                  <h4>{{ person.name }}</h4>
                  <p>{{ person.character }}</p>
                </div>
              </div>
            </div>
          </section>

          <!-- Additional Info -->
          <section class="content-section">
            <h3>{{ $t('movieDetail.movieInfo') }}</h3>
            <div class="movie-details">
              <div class="detail-row">
                <span class="detail-label">{{ $t('movieDetail.director') }}：</span>
                <span class="detail-value">
                  {{ getDirectors().map(d => d.name).join(', ') }}
                </span>
              </div>
              <div class="detail-row">
                <span class="detail-label">{{ $t('movieDetail.writer') }}：</span>
                <span class="detail-value">
                  {{ getWriters().map(w => w.name).join(', ') }}
                </span>
              </div>
              <div class="detail-row">
                <span class="detail-label">{{ $t('movieDetail.productionCountries') }}：</span>
                <span class="detail-value">{{ movie.production_countries?.map(c => c.name).join(', ') || t('common.unknown') }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">{{ $t('movieDetail.productionCompanies') }}：</span>
                <span class="detail-value">{{ movie.production_companies?.map(c => c.name).join(', ') || t('common.unknown') }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">{{ $t('movieDetail.budget') }}：</span>
                <span class="detail-value">{{ formatCurrency(movie.budget) }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">{{ $t('movieDetail.revenue') }}：</span>
                <span class="detail-value">{{ formatCurrency(movie.revenue) }}</span>
              </div>
            </div>
          </section>

          <!-- Recommended Movies -->
          <section class="content-section">
            <h3>{{ $t('home.recommendations') }}</h3>
            <div class="recommended-movies">
              <div
                v-for="movie in similarMovies"
                :key="movie.id"
                class="recommended-movie-card"
                @click="goToMovie(movie.id)"
              >
                <div class="recommended-poster">
                  <img :src="movie.poster_path" :alt="movie.title" @error="handleImageError" />
                </div>
                <div class="recommended-info">
                  <h4>{{ movie.title }}</h4>
                  <p>{{ formatDate(movie.release_date) }}</p>
                  <div class="recommended-rating">
                    <el-icon><Star /></el-icon>
                    {{ movie.vote_average?.toFixed(1) }}
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>

        <el-dialog v-model="collectionDialogVisible" :title="$t('collection.addToCollection')" width="520px">
          <div v-if="collectionStore.loading" class="dialog-loading">
            <el-skeleton :rows="3" animated />
          </div>
          <div v-else class="collection-dialog">
            <div v-if="collectionStore.collections.length === 0" class="collection-empty">
              <el-empty :description="$t('collection.noCollections')" />
            </div>
            <div v-else class="collection-list">
              <div
                v-for="collection in collectionStore.collections"
                :key="collection.id"
                class="collection-option"
              >
                <div class="collection-option-info">
                  <div class="collection-option-title">{{ collection.name }}</div>
                  <div class="collection-option-meta">
                    {{ $t('collection.moviesInCollection', { count: collection.movies_count || 0 }) }}
                  </div>
                </div>
                <el-button size="small" @click="addMovieToCollection(collection)">
                  {{ $t('collection.add') }}
                </el-button>
              </div>
            </div>

            <div class="collection-create">
              <div class="collection-create-title">{{ $t('collection.createNewCollection') }}</div>
              <el-input v-model="newCollectionForm.name" :placeholder="$t('collection.collectionTitle')" />
              <el-input
                v-model="newCollectionForm.description"
                type="textarea"
                :rows="2"
                :placeholder="$t('collection.collectionDesc')"
              />
              <div class="collection-create-actions">
                <el-switch
                  v-model="newCollectionForm.is_public"
                  :active-text="$t('collection.public')"
                  :inactive-text="$t('collection.private')"
                />
                <el-button type="primary" :loading="collectionCreating" @click="createAndAddToCollection">
                  {{ $t('collection.createAndAdd') }}
                </el-button>
              </div>
            </div>
          </div>
          <template #footer>
            <el-button @click="collectionDialogVisible = false">{{ $t('collection.close') }}</el-button>
          </template>
        </el-dialog>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useTMDBStore } from '@/stores/tmdb'
import { useWatchlistStore } from '@/stores/watchlist'
import { useReviewStore } from '@/stores/reviews'
import { useCollectionStore } from '@/stores/collections'
import { User, Star, Collection, Plus, ArrowLeft, Pointer } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AppLayout from '@/layouts/AppLayout.vue'

const { t, locale } = useI18n()
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const tmdbStore = useTMDBStore()
const watchlistStore = useWatchlistStore()
const reviewStore = useReviewStore()
const collectionStore = useCollectionStore()

const movie = computed(() => tmdbStore.movieDetails)
const similarMovies = ref([])
const movieId = computed(() => parseInt(route.params.id as string))
const ratingStats = ref<any>(null)
const userRatingInput = ref(0)
const userRatingId = ref<number | null>(null)
const ratingSubmitting = ref(false)
const comments = ref<any[]>([])
const commentsLoading = ref(false)
const commentSubmitting = ref(false)
const commentForm = reactive({
  content: '',
  is_long_review: false
})
const collectionDialogVisible = ref(false)
const collectionCreating = ref(false)
const newCollectionForm = reactive({
  name: '',
  description: '',
  is_public: false
})

watch(locale, () => {
  loadMovieData()
})

const goBack = () => {
  // Use router.back() to go to the previous page with preserved state
  router.back()
}

const goToMovie = (id: number) => {
  router.push({ name: 'movie-detail', params: { id }})
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = '/placeholder-movie.jpg'
}

const formatDate = (dateString: string) => {
  if (!dateString) return t('common.unknown')
  return new Date(dateString).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formatRuntime = (minutes: number) => {
  if (!minutes) return t('common.unknown')
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return t('movieDetail.runtimeMinutes', { minutes: hours * 60 + mins })
}

const formatNumber = (num: number) => {
  if (!num) return '0'
  return new Intl.NumberFormat('zh-CN').format(num)
}

const formatCurrency = (amount: number) => {
  if (!amount || amount === 0) return t('common.unknown')
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount)
}

const formatAverage = (value: number | null) => {
  if (!value) return '0.0'
  return Number(value).toFixed(1)
}

const formatDateTime = (dateString: string) => {
  if (!dateString) return t('common.unknown')
  return new Date(dateString).toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getRatingPercent = (star: number) => {
  const total = ratingStats.value?.total_ratings || 0
  const count = ratingStats.value?.[`rating_${star}`] || 0
  if (!total) return 0
  return Math.round((count / total) * 100)
}

const isOwnComment = (comment: any) => {
  return authStore.user?.username && comment.user === authStore.user.username
}

const getDirectors = () => {
  if (!movie.value?.crew) return []
  return movie.value.crew.filter((person: any) => person.job === 'Director')
}

const getWriters = () => {
  if (!movie.value?.crew) return []
  return movie.value.crew.filter((person: any) =>
    person.job === 'Writer' || person.job === 'Screenplay'
  )
}

const addToWatchlist = async () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning(t('movie.pleaseLoginFirst'))
    router.push('/login')
    return
  }

  if (!movie.value) {
    ElMessage.warning(t('movie.loadDataFailed'))
    return
  }

  try {
    console.log('Adding to watchlist, movie ID:', movie.value?.id)
    const result = await watchlistStore.toggleWatchlist(movie.value.id)
    console.log('Add to watchlist result:', result)

    if (result.added) {
      ElMessage.success(t('movie.addedToWatchlist', { title: movie.value?.title }))
    } else {
      ElMessage.info(t('movie.removedFromWatchlist', { title: movie.value?.title }))
    }
  } catch (error: any) {
    console.error('Add to watchlist error:', error)
    ElMessage.error(t('movie.operationFailed'))
  }
}

const addToCollection = () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning(t('movie.pleaseLoginFirst'))
    router.push('/login')
    return
  }

  collectionDialogVisible.value = true
  collectionStore.fetchCollections().catch((error) => {
    console.error('Load collections error:', error)
  })
}

const rateMovie = () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning(t('movie.pleaseLoginFirst'))
    router.push('/login')
    return
  }

  const section = document.querySelector('.ratings-section')
  if (section) {
    section.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

const loadRatings = async () => {
  try {
    const data = await reviewStore.fetchMovieRatings(movieId.value)
    ratingStats.value = data.stats
  } catch (error) {
    console.error('Load ratings error:', error)
    ratingStats.value = null
  }

  if (!authStore.isAuthenticated) {
    userRatingId.value = null
    userRatingInput.value = 0
    return
  }

  try {
    const userRatings = await reviewStore.fetchUserRating(movieId.value)
    const list = Array.isArray(userRatings)
      ? userRatings
      : (userRatings.results || userRatings)
    const rating = list[0]
    userRatingId.value = rating?.id || null
    userRatingInput.value = rating?.score || 0
  } catch (error) {
    console.error('Load user rating error:', error)
  }
}

const submitUserRating = async () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning(t('movie.pleaseLoginFirst'))
    router.push('/login')
    return
  }

  if (!userRatingInput.value) {
    ElMessage.warning(t('review.ratingRequired'))
    return
  }

  ratingSubmitting.value = true
  try {
    if (userRatingId.value) {
      await reviewStore.updateRating(userRatingId.value, userRatingInput.value)
    } else {
      await reviewStore.submitRating(movieId.value, userRatingInput.value)
    }
    ElMessage.success(t('review.ratingSubmitted'))
    await loadRatings()
  } catch (error) {
    console.error('Submit rating error:', error)
    ElMessage.error(t('review.ratingFailed'))
  } finally {
    ratingSubmitting.value = false
  }
}

const loadComments = async () => {
  commentsLoading.value = true
  try {
    const data = await reviewStore.fetchMovieComments(movieId.value)
    comments.value = data.results || data
  } catch (error) {
    console.error('Load comments error:', error)
    comments.value = []
  } finally {
    commentsLoading.value = false
  }
}

const submitComment = async () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning(t('movie.pleaseLoginFirst'))
    router.push('/login')
    return
  }

  if (!commentForm.content.trim()) {
    ElMessage.warning(t('review.contentRequired'))
    return
  }

  commentSubmitting.value = true
  try {
    await reviewStore.createComment(
      movieId.value,
      commentForm.content.trim(),
      commentForm.is_long_review
    )
    commentForm.content = ''
    commentForm.is_long_review = false
    await loadComments()
    ElMessage.success(t('review.commentSubmitted'))
  } catch (error) {
    console.error('Submit comment error:', error)
    ElMessage.error(t('review.commentFailed'))
  } finally {
    commentSubmitting.value = false
  }
}

const toggleLike = async (comment: any) => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning(t('movie.pleaseLoginFirst'))
    router.push('/login')
    return
  }

  try {
    const result = await reviewStore.toggleCommentLike(comment.id)
    comment.user_liked = result.liked
    comment.likes_count = result.likes_count
  } catch (error) {
    console.error('Toggle like error:', error)
  }
}

const removeComment = async (comment: any) => {
  try {
    await ElMessageBox.confirm(t('review.deleteConfirm'), t('review.deleteTitle'), {
      confirmButtonText: t('common.delete'),
      cancelButtonText: t('common.cancel'),
      type: 'warning'
    })

    await reviewStore.deleteComment(comment.id)
    comments.value = comments.value.filter(item => item.id !== comment.id)
    ElMessage.success(t('review.commentDeleted'))
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete comment error:', error)
    }
  }
}

const addMovieToCollection = async (collection: any) => {
  if (!movie.value) return

  try {
    await collectionStore.addMovieToCollection(collection.id, movieId.value)
    ElMessage.success(t('collection.addedSuccess', { name: collection.name }))
  } catch (error) {
    console.error('Add movie to collection error:', error)
    ElMessage.error(t('collection.addFailed'))
  }
}

const createAndAddToCollection = async () => {
  const name = newCollectionForm.name.trim()
  if (!name) {
    ElMessage.warning(t('collection.nameRequired'))
    return
  }

  collectionCreating.value = true
  try {
    const created = await collectionStore.createCollection({
      name,
      description: newCollectionForm.description.trim(),
      is_public: newCollectionForm.is_public
    })
    await collectionStore.addMovieToCollection(created.id, movieId.value)
    ElMessage.success(t('collection.createdSuccess'))
    newCollectionForm.name = ''
    newCollectionForm.description = ''
    newCollectionForm.is_public = false
    await collectionStore.fetchCollections()
  } catch (error) {
    console.error('Create collection error:', error)
    ElMessage.error(t('collection.createFailed'))
  } finally {
    collectionCreating.value = false
  }
}

const loadMovieData = async () => {
  try {
    await tmdbStore.fetchMovieDetails(movieId.value)
  } catch (error) {
    console.error('Failed to load movie details:', error)
    ElMessage.error('加载电影详情失败')
    return
  }

  try {
    const tmdbResult = await tmdbStore.fetchRecommendedMovies(movieId.value)
    if (tmdbResult && tmdbResult.length > 0) {
      similarMovies.value = tmdbResult.slice(0, 6)
    } else {
      try {
        const similarResult = await tmdbStore.fetchSimilarMovies(movieId.value)
        similarMovies.value = similarResult.slice(0, 6)
      } catch (similarError) {
        console.error('Failed to load similar movies:', similarError)
        similarMovies.value = []
      }
    }
  } catch (error) {
    console.error('Failed to load recommended movies:', error)
    similarMovies.value = []
  }

  await Promise.all([loadRatings(), loadComments()])
}

onMounted(() => {
  loadMovieData()
})

watch(movieId, () => {
  loadMovieData()
})
</script>

<style scoped>
.movie-detail-page {
  background: #0d1117;
  color: #f0f6fc;
  min-height: 100vh;
}

.hero-content {
  margin-top: 64px; /* 为导航栏留出空间 */
}

/* Movie Hero */
.movie-hero {
  position: relative;
  min-height: 60vh;
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
    rgba(13, 17, 23, 0.95) 0%,
    rgba(13, 17, 23, 0.7) 50%,
    rgba(13, 17, 23, 0.4) 100%
  );
}

.hero-content {
  position: relative;
  z-index: 1;
  padding: 80px 0;
}

.back-button-container {
  position: absolute;
  top: 40px;
  left: 24px;
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

.hero-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  gap: 48px;
  align-items: flex-start;
}

.movie-poster {
  flex-shrink: 0;
  width: 300px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4);
}

.movie-poster img {
  width: 100%;
  height: auto;
  display: block;
}

.movie-info {
  flex: 1;
  padding-top: 20px;
}

.movie-title {
  font-size: 3.5rem;
  font-weight: 700;
  margin: 0 0 16px 0;
  line-height: 1.1;
  background: linear-gradient(135deg, #58a6ff 0%, #79c0ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.movie-tagline {
  font-size: 1.5rem;
  font-weight: 400;
  color: #79c0ff;
  margin: 0 0 32px 0;
  font-style: italic;
}

.movie-meta {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 32px;
  flex-wrap: wrap;
}

.movie-rating {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #fbbf24;
  font-size: 1.2rem;
  font-weight: 600;
}

.movie-votes, .movie-date, .movie-runtime {
  color: #8b949e;
  font-size: 1rem;
}

.movie-genres {
  display: flex;
  gap: 12px;
  margin-bottom: 32px;
  flex-wrap: wrap;
}

.movie-actions {
  display: flex;
  gap: 16px;
}

/* Content Sections */
.content-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 48px 24px;
}

.content-section {
  margin-bottom: 64px;
}

.content-section h3 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 24px 0;
  color: #f0f6fc;
  border-bottom: 2px solid #30363d;
  padding-bottom: 8px;
}

.movie-overview {
  font-size: 1.2rem;
  line-height: 1.8;
  color: #c9d1d9;
  margin: 0;
}

/* Ratings */
.ratings-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  flex-wrap: wrap;
}

.ratings-summary {
  display: flex;
  align-items: center;
  gap: 24px;
}

.average-score {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 12px 18px;
  background: rgba(88, 166, 255, 0.12);
  border: 1px solid rgba(88, 166, 255, 0.3);
  border-radius: 12px;
}

.score-value {
  font-size: 2.2rem;
  font-weight: 700;
  color: #79c0ff;
}

.score-label {
  font-size: 0.9rem;
  color: #8b949e;
}

.score-meta {
  color: #8b949e;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.ratings-body {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  margin-top: 24px;
}

.rating-distribution {
  background: #161b22;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #30363d;
}

.rating-row {
  display: grid;
  grid-template-columns: 50px 1fr 40px;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
  color: #c9d1d9;
}

.rating-row:last-child {
  margin-bottom: 0;
}

.rating-star {
  font-size: 0.9rem;
  color: #8b949e;
}

.rating-bar {
  height: 8px;
  background: #0d1117;
  border-radius: 999px;
  overflow: hidden;
}

.rating-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #fbbf24 0%, #f97316 100%);
  border-radius: 999px;
}

.rating-count {
  text-align: right;
  font-size: 0.85rem;
  color: #8b949e;
}

.user-rating-card {
  background: #161b22;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #30363d;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.user-rating-title {
  font-weight: 600;
  color: #f0f6fc;
}

.user-rating-hint {
  color: #8b949e;
  font-size: 0.9rem;
}

/* Comments */
.comments-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.comments-count {
  color: #8b949e;
}

.comment-form {
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comment-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.comment-login-hint {
  padding: 16px;
  background: rgba(88, 166, 255, 0.08);
  border: 1px dashed rgba(88, 166, 255, 0.4);
  border-radius: 12px;
  color: #79c0ff;
  margin-bottom: 16px;
}

.comments-list {
  margin-top: 16px;
  display: grid;
  gap: 16px;
}

.comment-card {
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 12px;
  padding: 16px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.comment-user {
  display: flex;
  gap: 12px;
  align-items: center;
}

.comment-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #58a6ff 0%, #79c0ff 100%);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  overflow: hidden;
}

.comment-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.comment-name {
  font-weight: 600;
  color: #f0f6fc;
}

.comment-date {
  font-size: 0.85rem;
  color: #8b949e;
}

.comment-tags {
  display: flex;
  align-items: center;
  gap: 8px;
}

.comment-content {
  margin: 12px 0 0 0;
  color: #c9d1d9;
  line-height: 1.6;
}

.comments-empty {
  margin-top: 20px;
}

/* Collection Dialog */
.collection-dialog {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.dialog-loading {
  padding: 12px 0;
}

.collection-empty {
  padding: 12px 0;
}

.collection-list {
  display: grid;
  gap: 12px;
}

.collection-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid #30363d;
  background: #161b22;
}

.collection-option-title {
  font-weight: 600;
  color: #f0f6fc;
}

.collection-option-meta {
  color: #8b949e;
  font-size: 0.85rem;
}

.collection-create {
  border-top: 1px dashed #30363d;
  padding-top: 16px;
  display: grid;
  gap: 12px;
}

.collection-create-title {
  color: #f0f6fc;
  font-weight: 600;
}

.collection-create-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

/* Cast Grid */
.cast-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 24px;
}

.cast-item {
  display: flex;
  gap: 16px;
  align-items: center;
  background: #161b22;
  padding: 16px;
  border-radius: 8px;
  transition: transform 0.2s;
}

.cast-item:hover {
  transform: translateY(-4px);
}

.cast-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.cast-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-avatar {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #30363d;
  color: #8b949e;
}

.cast-avatar .el-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.cast-info h4 {
  margin: 0 0 4px 0;
  color: #f0f6fc;
  font-size: 1rem;
}

.cast-info p {
  margin: 0;
  color: #8b949e;
  font-size: 0.9rem;
}

/* Movie Details */
.movie-details {
  background: #161b22;
  padding: 32px;
  border-radius: 12px;
}

.detail-row {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.detail-label {
  color: #8b949e;
  min-width: 100px;
  font-weight: 600;
}

.detail-value {
  color: #f0f6fc;
  flex: 1;
}

/* Similar Movies */
.recommended-movies {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 24px;
}

.recommended-movie-card {
  cursor: pointer;
  transition: transform 0.3s ease;
  border-radius: 8px;
  overflow: hidden;
  background: #161b22;
}

.recommended-movie-card:hover {
  transform: translateY(-8px);
}

.recommended-poster {
  aspect-ratio: 2/3;
  overflow: hidden;
}

.recommended-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.recommended-movie-card:hover .recommended-poster img {
  transform: scale(1.05);
}

.recommended-info {
  padding: 16px;
}

.recommended-info h4 {
  margin: 0 0 8px 0;
  color: #f0f6fc;
  font-size: 1rem;
  line-height: 1.4;
}

.recommended-info p {
  margin: 0 0 8px 0;
  color: #8b949e;
  font-size: 0.9rem;
}

.recommended-rating {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #fbbf24;
  font-size: 0.9rem;
}

/* Loading State */
.loading-container {
  margin-top: 64px;
  padding: 24px;
  background: #0d1117;
  min-height: 60vh;
}

/* Error */
.error-container {
  margin-top: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  background: #0d1117;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .hero-container {
    padding: 0 20px;
  }

  .movie-poster {
    width: 260px;
  }

  .movie-title {
    font-size: 3rem;
  }

  .content-container {
    padding: 32px 20px;
  }
}

@media (max-width: 992px) {
  .hero-container {
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 32px;
    padding: 60px 16px 40px;
  }

  .movie-poster {
    width: 240px;
  }

  .movie-title {
    font-size: 2.8rem;
  }

  .movie-tagline {
    font-size: 1.3rem;
  }

  .movie-meta {
    justify-content: center;
    flex-wrap: wrap;
  }

  .movie-actions {
    justify-content: center;
    flex-wrap: wrap;
  }

  .content-container {
    padding: 32px 16px;
  }

  .ratings-body {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .movie-title {
    font-size: 2.2rem;
  }

  .movie-tagline {
    font-size: 1.1rem;
  }

  .movie-meta {
    font-size: 0.9rem;
  }

  .movie-actions {
    gap: 12px;
  }

  .content-container {
    padding: 24px 12px;
  }

  .content-section {
    margin-bottom: 48px;
  }

  .content-section h3 {
    font-size: 1.5rem;
  }

  .movie-overview {
    font-size: 1rem;
  }

  .comment-actions {
    flex-direction: column;
    align-items: flex-start;
  }

  .cast-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 16px;
  }

  .cast-item {
    flex-direction: column;
    text-align: center;
    padding: 12px;
  }

  .cast-avatar {
    width: 80px;
    height: 80px;
    }

  .cast-info h4 {
    font-size: 0.9rem;
  }

  .cast-info p {
    font-size: 0.8rem;
  }
}
</style>
