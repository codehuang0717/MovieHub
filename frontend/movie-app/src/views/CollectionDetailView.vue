<template>
  <AppLayout>
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="6" animated />
    </div>

    <div v-else-if="!collection" class="error-container">
      <el-result icon="error" title="收藏夹不存在" sub-title="该收藏夹可能已被删除">
        <template #extra>
          <el-button type="primary" @click="router.push('/collections')">返回收藏夹</el-button>
        </template>
      </el-result>
    </div>

    <div v-else class="collection-detail-page">
      <!-- Collection Header -->
      <div class="collection-header">
        <div class="collection-info">
          <div class="collection-title-section">
            <h1 class="collection-title">{{ collection.name }}</h1>
            <div class="collection-meta">
              <el-tag v-if="collection.is_public" size="small" type="success">
                公开
              </el-tag>
              <el-tag v-else size="small" type="info">
                私密
              </el-tag>
              <span class="movie-count">{{ collection.movies?.length || 0 }} 部电影</span>
            </div>
          </div>
          <p v-if="collection.description" class="collection-description">
            {{ collection.description }}
          </p>
        </div>
        <div class="collection-actions">
          <el-button @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
          <el-button @click="editCollection">
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <el-button type="danger" @click="deleteCollection">
            <el-icon><Delete /></el-icon>
            删除
          </el-button>
        </div>
      </div>

      <!-- Movies Grid -->
      <div class="movies-section">
        <div class="section-header">
          <h2>收藏的电影</h2>
          <div class="section-actions">
            <el-input
              v-model="searchQuery"
              placeholder="搜索电影..."
              :prefix-icon="Search"
              clearable
              style="width: 300px"
              @input="handleSearch"
            />
          </div>
        </div>

        <div v-if="filteredMovies.length === 0" class="empty-state">
          <el-empty 
            :description="searchQuery ? '没有找到匹配的电影' : '该收藏夹还没有添加任何电影'"
          />
        </div>

        <div v-else class="movies-grid">
          <div
            v-for="movie in filteredMovies"
            :key="movie.id"
            class="movie-card"
            @click="goToMovie(movie)"
          >
            <div class="movie-poster">
              <img
                :src="movie.poster_path || movie.poster"
                :alt="movie.title"
                @error="handleImageError"
              />
              <div class="movie-rating" v-if="movie.vote_average">
                <el-icon><Star /></el-icon>
                {{ movie.vote_average?.toFixed(1) }}
              </div>
            </div>
            <div class="movie-info">
              <h3 class="movie-title">{{ movie.title }}</h3>
              <p class="movie-date">
                {{ formatDate(movie.release_date) }}
              </p>
              <div class="movie-genres" v-if="movie.genres?.length">
                <el-tag
                  v-for="genre in movie.genres.slice(0, 3)"
                  :key="genre.id"
                  size="small"
                >
                  {{ genre.name }}
                </el-tag>
              </div>
              <div class="movie-actions">
                <el-button
                  size="small"
                  type="danger"
                  :loading="removingMovieIds.includes(movie.id)"
                  @click.stop="removeMovieFromCollection(movie)"
                >
                  取消收藏
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Edit Dialog -->
      <el-dialog v-model="editDialogVisible" title="编辑收藏夹" width="520px">
        <el-form
          ref="editFormRef"
          :model="editForm"
          :rules="editRules"
          label-position="top"
        >
          <el-form-item label="收藏夹名称" prop="name">
            <el-input v-model="editForm.name" />
          </el-form-item>
          <el-form-item label="描述" prop="description">
            <el-input
              v-model="editForm.description"
              type="textarea"
              :rows="3"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
          <el-form-item label="可见性" prop="is_public">
            <el-switch
              v-model="editForm.is_public"
              active-text="公开"
              inactive-text="私密"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="saveCollection">
            保存
          </el-button>
        </template>
      </el-dialog>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { Search, ArrowLeft, Edit, Delete, Star } from '@element-plus/icons-vue'
import AppLayout from '@/layouts/AppLayout.vue'
import { useCollectionStore } from '@/stores/collections'

const router = useRouter()
const route = useRoute()
const collectionStore = useCollectionStore()

const collection = ref<any>(null)
const loading = ref(false)
const searchQuery = ref('')
const editDialogVisible = ref(false)
const saving = ref(false)
const removingMovieIds = ref<number[]>([])
const editFormRef = ref<FormInstance>()

const editForm = ref({
  name: '',
  description: '',
  is_public: false
})

const editRules = {
  name: [
    { required: true, message: '请输入收藏夹名称', trigger: 'blur' },
    { min: 1, max: 100, message: '名称长度在1到100个字符之间', trigger: 'blur' }
  ],
  description: [
    { max: 500, message: '描述不能超过500个字符', trigger: 'blur' }
  ]
}

const collectionId = computed(() => parseInt(route.params.id as string))

const filteredMovies = computed(() => {
  if (!collection.value?.movies) return []
  
  if (!searchQuery.value.trim()) {
    return collection.value.movies
  }

  const query = searchQuery.value.toLowerCase()
  return collection.value.movies.filter((movie: any) =>
    movie.title.toLowerCase().includes(query) ||
    movie.original_title?.toLowerCase().includes(query) ||
    movie.genres?.some((genre: any) => genre.name.toLowerCase().includes(query))
  )
})

const formatDate = (dateString: string) => {
  if (!dateString || dateString === '未知') return '未知'
  return new Date(dateString).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = '/placeholder-movie.jpg'
}

const goBack = () => {
  router.push('/collections')
}

const goToMovie = (movie: any) => {
  // 优先使用 tmdb_id，否则回退到本地 id
  const movieId = movie.tmdb_id || movie.id
  router.push({ name: 'movie-detail', params: { id: movieId }})
}

const handleSearch = () => {
  // 搜索逻辑已在 computed 中处理
}

const editCollection = () => {
  if (!collection.value) return
  
  editForm.value = {
    name: collection.value.name,
    description: collection.value.description || '',
    is_public: collection.value.is_public
  }
  editDialogVisible.value = true
}

const saveCollection = async () => {
  if (!editFormRef.value || !collection.value) return

  try {
    await editFormRef.value.validate()
    saving.value = true

    const payload = {
      name: editForm.value.name.trim(),
      description: editForm.value.description.trim(),
      is_public: editForm.value.is_public
    }

    await collectionStore.updateCollection(collection.value.id, payload)
    collection.value = {
      ...collection.value,
      ...payload
    }
    editDialogVisible.value = false
    ElMessage.success('收藏夹已更新')
  } catch (error) {
    console.error('Save collection error:', error)
  } finally {
    saving.value = false
  }
}

const deleteCollection = async () => {
  if (!collection.value) return

  try {
    await ElMessageBox.confirm(
      `确定要删除收藏夹 "${collection.value.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await collectionStore.deleteCollection(collection.value.id)
    ElMessage.success('收藏夹已删除')
    router.push('/collections')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete collection error:', error)
    }
  }
}

const removeMovieFromCollection = async (movie: any) => {
  if (!collection.value) return

  try {
    removingMovieIds.value.push(movie.id)
    await collectionStore.removeMovieFromCollection(collection.value.id, movie.id)
    ElMessage.success(`已移除《${movie.title}》`)
    
    // 更新本地收藏夹数据
    if (collection.value.movies) {
      collection.value.movies = collection.value.movies.filter((m: any) => m.id !== movie.id)
    }
  } catch (error) {
    console.error('Remove movie error:', error)
    ElMessage.error('移除失败')
  } finally {
    removingMovieIds.value = removingMovieIds.value.filter(id => id !== movie.id)
  }
}

const loadCollection = async () => {
  loading.value = true
  try {
    // 从 store 中查找收藏夹
    const found = collectionStore.collections.find((c: any) => c.id === collectionId.value)
    if (found) {
      collection.value = found
    } else {
      // 如果在 store 中没找到，可能需要单独获取
      ElMessage.error('收藏夹不存在')
      router.push('/collections')
    }
  } catch (error) {
    console.error('Load collection error:', error)
    ElMessage.error('加载收藏夹失败')
    router.push('/collections')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // 确保收藏夹列表已加载
  if (collectionStore.collections.length === 0) {
    collectionStore.fetchCollections().then(() => {
      loadCollection()
    }).catch(() => {
      loadCollection()
    })
  } else {
    loadCollection()
  }
})
</script>

<style scoped>
.collection-detail-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 96px 24px 48px;
  min-height: 100vh;
  color: #f0f6fc;
}

.collection-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
  margin-bottom: 32px;
  padding: 24px;
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 16px;
}

.collection-info {
  flex: 1;
}

.collection-title-section {
  margin-bottom: 12px;
}

.collection-title {
  font-size: 2.2rem;
  font-weight: 700;
  margin: 0 0 12px 0;
  background: linear-gradient(135deg, #58a6ff 0%, #79c0ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.collection-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.movie-count {
  color: #8b949e;
  font-size: 0.9rem;
}

.collection-description {
  color: #c9d1d9;
  line-height: 1.6;
  margin: 0;
  font-size: 1.05rem;
}

.collection-actions {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}

.movies-section {
  margin-top: 32px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-header h2 {
  font-size: 1.8rem;
  font-weight: 600;
  margin: 0;
  color: #f0f6fc;
}

.section-actions {
  display: flex;
  gap: 12px;
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
  transform: translateY(-6px);
  box-shadow: 0 16px 32px rgba(0, 0, 0, 0.4);
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

.movie-actions {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #30363d;
  display: flex;
  gap: 8px;
}

.empty-state {
  text-align: center;
  margin: 60px 0;
}

.loading-container,
.error-container {
  margin-top: 64px;
}

:deep(.el-dialog) {
  border-radius: 16px;
}

:deep(.el-dialog__header) {
  border-bottom: 1px solid #30363d;
}

@media (max-width: 992px) {
  .collection-detail-page {
    padding: 88px 20px 40px;
  }

  .collection-header {
    flex-direction: column;
    gap: 16px;
  }

  .movies-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 16px;
  }
}

@media (max-width: 768px) {
  .collection-detail-page {
    padding: 80px 16px 32px;
  }

  .collection-title {
    font-size: 1.8rem;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .section-actions {
    width: 100%;
  }

  .section-actions .el-input {
    width: 100% !important;
  }

  .movies-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 12px;
  }

  .collection-actions {
    flex-wrap: wrap;
  }
}

@media (max-width: 480px) {
  .collection-detail-page {
    padding: 72px 12px 24px;
  }

  .collection-title {
    font-size: 1.5rem;
  }

  .movies-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 10px;
  }
}
</style>