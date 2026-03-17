<template>
  <AppLayout>
    <div class="collections-page">
      <div class="page-header">
        <h1>{{ $t('collections.myCollections') }}</h1>
        <el-button type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon>
          {{ $t('collections.createCollection') }}
        </el-button>
      </div>

      <div v-if="loading" class="loading">
        <el-skeleton :rows="4" animated />
      </div>

      <div v-else-if="error" class="error">
        <el-alert :title="$t('errors.loadFailed')" :description="error" type="error" show-icon />
      </div>

      <div v-else class="collections-grid">
        <el-row :gutter="20">
          <el-col
            v-for="collection in collections"
            :key="collection.id"
            :xs="24" :sm="12" :md="8" :lg="6"
          >
            <el-card class="collection-card" @click="viewCollection(collection)">
              <div class="collection-header">
                <h3>{{ collection.name }}</h3>
                <div class="collection-meta">
                  <span class="movie-count">{{ $t('collections.moviesCount', { count: collection.movies_count || collection.movies?.length || 0 }) }}</span>
                  <el-tag v-if="collection.is_public" size="small" type="success">
                    {{ $t('collections.public') }}
                  </el-tag>
                  <el-tag v-else size="small" type="info">
                    {{ $t('collections.private') }}
                  </el-tag>
                </div>
              </div>

              <div v-if="collection.description" class="collection-description">
                {{ collection.description }}
              </div>

              <div v-if="collection.movies?.length > 0" class="preview-movies">
                <div
                  v-for="movie in collection.movies.slice(0, 4)"
                  :key="movie.id"
                  class="preview-movie"
                >
                  <img
                    :src="movie.poster_path || movie.poster"
                    :alt="movie.title"
                    width="100"
                    height="150"
                    @error="handleImageError"
                  />
                </div>
                <div v-if="(collection.movies_count || 0) > 4" class="more-movies">
                  +{{ collection.movies_count - 4 }}
                </div>
              </div>

              <div class="collection-actions">
                <el-button size="small" @click.stop="editCollection(collection)">
                  {{ $t('common.edit') }}
                </el-button>
                <el-button size="small" type="danger" @click.stop="deleteCollection(collection)">
                  {{ $t('common.delete') }}
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <div v-if="collections.length === 0" class="no-collections">
          <el-empty :description="$t('collections.noCollections')">
            <el-button type="primary" @click="showCreateDialog">
              {{ $t('collections.createFirst') }}
            </el-button>
          </el-empty>
        </div>
      </div>

      <el-dialog
        v-model="dialogVisible"
        :title="editingCollection ? $t('collections.editCollection') : $t('collections.createCollection')"
        width="500px"
      >
        <el-form
          :model="collectionForm"
          :rules="collectionRules"
          ref="collectionFormRef"
          label-width="80px"
        >
          <el-form-item :label="$t('collections.name')" prop="name">
            <el-input v-model="collectionForm.name" :placeholder="$t('collections.enterName')" />
          </el-form-item>

          <el-form-item :label="$t('collections.description')" prop="description">
            <el-input
              v-model="collectionForm.description"
              type="textarea"
              :rows="3"
              :placeholder="$t('collections.enterDescription')"
            />
          </el-form-item>

          <el-form-item :label="$t('collections.visibility')">
            <el-switch
              v-model="collectionForm.is_public"
              :active-text="$t('collections.public')"
              :inactive-text="$t('collections.private')"
            />
          </el-form-item>
        </el-form>

        <template #footer>
          <el-button @click="dialogVisible = false">{{ $t('common.cancel') }}</el-button>
          <el-button type="primary" @click="saveCollection" :loading="saving">
            {{ editingCollection ? $t('common.update') : $t('common.create') }}
          </el-button>
        </template>
      </el-dialog>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import AppLayout from '@/layouts/AppLayout.vue'
import { useCollectionStore } from '@/stores/collections'

const { t } = useI18n()
const router = useRouter()
const collectionStore = useCollectionStore()

const collections = computed(() => collectionStore.collections)
const loading = computed(() => collectionStore.loading)
const error = computed(() => collectionStore.error)

const dialogVisible = ref(false)
const saving = ref(false)
const editingCollection = ref<any>(null)
const collectionFormRef = ref<FormInstance>()

const collectionForm = reactive({
  name: '',
  description: '',
  is_public: false
})

const collectionRules = computed<FormRules>(() => ({
  name: [
    { required: true, message: t('collections.nameRequired'), trigger: 'blur' },
    { min: 1, max: 100, message: t('collections.nameLength'), trigger: 'blur' }
  ],
  description: [
    { max: 500, message: t('collections.descLength'), trigger: 'blur' }
  ]
}))

const showCreateDialog = () => {
  editingCollection.value = null
  collectionForm.name = ''
  collectionForm.description = ''
  collectionForm.is_public = false
  dialogVisible.value = true
}

const viewCollection = (collection: any) => {
  router.push({ name: 'collection-detail', params: { id: collection.id } })
}

const editCollection = (collection: any) => {
  editingCollection.value = collection
  collectionForm.name = collection.name
  collectionForm.description = collection.description || ''
  collectionForm.is_public = collection.is_public
  dialogVisible.value = true
}

const saveCollection = async () => {
  if (!collectionFormRef.value) return

  try {
    await collectionFormRef.value.validate()
    saving.value = true

    const payload = {
      name: collectionForm.name.trim(),
      description: collectionForm.description.trim(),
      is_public: collectionForm.is_public
    }

    if (editingCollection.value) {
      await collectionStore.updateCollection(editingCollection.value.id, payload)
      ElMessage.success(t('collections.updateSuccess'))
    } else {
      await collectionStore.createCollection(payload)
      ElMessage.success(t('collections.createSuccess'))
    }

    dialogVisible.value = false
    await collectionStore.fetchCollections()
  } catch (err) {
    console.error('Save collection error:', err)
  } finally {
    saving.value = false
  }
}

const deleteCollection = async (collection: any) => {
  try {
    await ElMessageBox.confirm(
      t('collections.deleteConfirm', { name: collection.name }),
      t('collections.deleteTitle'),
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'warning'
      }
    )

    await collectionStore.deleteCollection(collection.id)
    ElMessage.success(t('collections.deleteSuccess'))
  } catch (err) {
    if (err !== 'cancel') {
      console.error('Delete collection error:', err)
    }
  }
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = '/placeholder-movie.jpg'
}

const loadCollections = async () => {
  try {
    await collectionStore.fetchCollections()
  } catch (err) {
    console.error('Load collections error:', err)
  }
}

onMounted(() => {
  loadCollections()
})
</script>

<style scoped>
.collections-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 96px 24px 48px;
  min-height: 100vh;
  color: #f0f6fc;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
}

.page-header h1 {
  font-size: 2.2rem;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(135deg, #58a6ff 0%, #79c0ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.collections-grid {
  margin-bottom: 32px;
}

.collection-card {
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  margin-bottom: 20px;
  height: 300px;
  display: flex;
  flex-direction: column;
}

.collection-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 16px 32px rgba(0, 0, 0, 0.4);
}

:deep(.collection-card.el-card) {
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 14px;
}

:deep(.collection-card .el-card__body) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.collection-header {
  margin-bottom: 12px;
}

.collection-header h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #f0f6fc;
  margin: 0 0 10px 0;
}

.collection-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.movie-count {
  color: #8b949e;
  font-size: 0.9rem;
}

.collection-description {
  color: #c9d1d9;
  font-size: 0.95rem;
  line-height: 1.5;
  margin-bottom: 14px;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.preview-movies {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 6px;
  margin-bottom: 16px;
  height: 90px;
}

.preview-movie {
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  background: #0d1117;
}

.preview-movie img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.more-movies {
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(88, 166, 255, 0.12);
  color: #79c0ff;
  font-size: 0.8rem;
  border-radius: 8px;
  border: 1px dashed rgba(88, 166, 255, 0.4);
}

.collection-actions {
  display: flex;
  gap: 8px;
  margin-top: auto;
}

.no-collections,
.loading,
.error {
  margin: 60px 0;
}

:deep(.el-dialog) {
  border-radius: 16px;
}

:deep(.el-dialog__header) {
  border-bottom: 1px solid #30363d;
}

@media (max-width: 992px) {
  .collections-page {
    padding: 88px 20px 40px;
  }

  .collection-card {
    height: 280px;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .collections-page {
    padding: 80px 16px 32px;
  }

  .collection-card {
    height: 260px;
  }
}

@media (max-width: 480px) {
  .collections-page {
    padding: 72px 12px 24px;
  }

  .page-header h1 {
    font-size: 1.6rem;
  }
}
</style>
