<template>
  <AppLayout>
    <div class="profile-view">
    <div v-if="loading" class="loading">
      <el-skeleton :rows="6" animated />
    </div>

    <div v-else-if="error" class="error">
      <el-alert title="加载失败" :description="error" type="error" show-icon />
    </div>

    <div v-else class="profile-content">
      <el-row :gutter="30">
        <el-col :span="8">
          <el-card class="profile-card">
            <div class="profile-avatar">
              <AvatarUpload
                v-model="profileForm.profile.avatar"
                :size="120"
                :editable="true"
                @success="onAvatarUpdated"
                @error="onAvatarError"
                @removed="onAvatarRemoved"
              />
            </div>

            <div class="profile-info">
              <h2>{{ user.username }}</h2>
              <p class="user-email">{{ user.email }}</p>
              <p v-if="user.profile?.bio" class="user-bio">{{ user.profile.bio }}</p>
            </div>

            <div class="profile-stats">
              <div class="stat-item">
                <div class="stat-number">{{ userStats.watched_count || 0 }}</div>
                <div class="stat-label">{{ $t('profile.watched') }}</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ userStats.rated_count || 0 }}</div>
                <div class="stat-label">{{ $t('profile.rated') }}</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ userStats.collections_count || 0 }}</div>
                <div class="stat-label">{{ $t('profile.collections') }}</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="16">
          <el-tabs v-model="activeTab">
            <el-tab-pane :label="$t('profile.personalInfo')" name="profile">
              <el-card>
                <el-form
                  :model="profileForm"
                  label-width="80px"
                  @submit.prevent="updateProfile"
                >
                  <el-form-item :label="$t('auth.username')">
                    <el-input v-model="profileForm.username" disabled />
                  </el-form-item>

                  <el-form-item :label="$t('auth.email')">
                    <el-input v-model="profileForm.email" type="email" />
                  </el-form-item>

                  <el-form-item :label="$t('profile.name')">
                    <el-input v-model="profileForm.first_name" :placeholder="$t('profile.firstName')" />
                  </el-form-item>

                  <el-form-item :label="'&nbsp;'">
                    <el-input v-model="profileForm.last_name" :placeholder="$t('profile.lastName')" />
                  </el-form-item>

                  <el-form-item :label="$t('profile.bio')">
                    <el-input
                      v-model="profileForm.profile.bio"
                      type="textarea"
                      :rows="4"
                      :placeholder="$t('profile.introduceYourself')"
                    />
                  </el-form-item>
                  <el-form-item>
                    <el-button
                      type="primary"
                      @click="updateProfile"
                      :loading="updatingProfile"
                    >
                      {{ $t('common.save') }}
                    </el-button>
                  </el-form-item>
                </el-form>
              </el-card>
            </el-tab-pane>

            <el-tab-pane :label="$t('profile.history')" name="history">
              <el-card>
                <div v-if="userHistory.length === 0" class="empty-state">
                  <el-empty :description="$t('profile.noHistory')" />
                </div>
                <div v-else class="history-list">
                  <div
                    v-for="item in userHistory"
                    :key="item.id"
                    class="history-item"
                  >
                    <div class="movie-poster">
                      <img
                        v-if="item.movie.poster"
                        :src="item.movie.poster"
                        :alt="item.movie.title"
                        width="60"
                        height="90"
                        @error="handleImageError"
                      />
                      <div v-else class="no-poster">
                        <el-icon><Picture /></el-icon>
                      </div>
                    </div>
                    <div class="movie-info">
                      <h4>{{ item.movie.title }}</h4>
                      <p class="watch-time">
                        {{ $t('profile.watchedAt', { date: formatDate(item.created_at) }) }}
                      </p>
                      <div v-if="item.rating" class="rating">
                        <el-rate v-model="item.rating.score" disabled size="small" />
                      </div>
                    </div>
                  </div>
                </div>
              </el-card>
            </el-tab-pane>

            <el-tab-pane :label="$t('profile.myRatings')" name="ratings">
              <el-card>
                <div v-if="userRatings.length === 0" class="empty-state">
                  <el-empty :description="$t('profile.noRatings')" />
                </div>
                <div v-else class="ratings-list">
                  <div
                    v-for="rating in userRatings"
                    :key="rating.id"
                    class="rating-item"
                  >
                    <div class="movie-poster">
                      <img
                        v-if="rating.movie.poster"
                        :src="rating.movie.poster"
                        :alt="rating.movie.title"
                        width="60"
                        height="90"
                        @error="handleImageError"
                      />
                      <div v-else class="no-poster">
                        <el-icon><Picture /></el-icon>
                      </div>
                    </div>
                    <div class="movie-info">
                      <h4>{{ rating.movie.title }}</h4>
                      <div class="rating-info">
                        <el-rate v-model="rating.score" disabled size="small" />
                        <span class="rating-date">
                          {{ formatDate(rating.created_at) }}
                        </span>
                      </div>
                    </div>
                    <div class="rating-actions">
                      <el-button size="small" @click="editRating(rating)">
                        {{ $t('review.editReview') }}
                      </el-button>
                    </div>
                  </div>
                </div>
              </el-card>
            </el-tab-pane>
          </el-tabs>
        </el-col>
      </el-row>
    </div>
  </div>
</AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { Picture, User } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import AppLayout from '@/layouts/AppLayout.vue'
import AvatarUpload from '@/components/AvatarUpload.vue'

const { t } = useI18n()
const authStore = useAuthStore()

const user = computed(() => {
  const userData = authStore.user
  return userData || {
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    profile: {
      bio: '',
      avatar: ''
    }
  }
})
const loading = ref(false)
const error = ref('')
const updatingProfile = ref(false)
const activeTab = ref('profile')

const profileForm = ref({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  profile: {
    bio: '',
    avatar: ''
  }
})

const userStats = ref({
  watched_count: 0,
  rated_count: 0,
  collections_count: 0
})

const userHistory = ref([])
const userRatings = ref([])

const onAvatarUpdated = (data: any) => {
  console.log('Avatar updated successfully:', data)
  // 更新本地表单数据
  profileForm.value.profile.avatar = data.avatar
  // 可选：重新获取完整的用户档案
  authStore.fetchProfile()
}

const onAvatarError = (error: any) => {
  console.error('Avatar upload error:', error)
}

const onAvatarRemoved = (data: any) => {
  console.log('Avatar removed successfully:', data)
  // 更新本地表单数据
  profileForm.value.profile.avatar = data.avatar
  // 可选：重新获取完整的用户档案
  authStore.fetchProfile()
}

const updateProfile = async () => {
  updatingProfile.value = true
  try {
    // 清洗数据，剔除 avatar 以免引发后端的 ImageField 验证错误
    const dataToSubmit = JSON.parse(JSON.stringify(profileForm.value))
    if (dataToSubmit.profile && 'avatar' in dataToSubmit.profile) {
      delete dataToSubmit.profile.avatar
    }
    
    console.log('Submitting profile form:', dataToSubmit)
    const result = await authStore.updateProfile(dataToSubmit)
    if (result.success) {
      ElMessage.success(t('profile.updateSuccess'))
      console.log('Profile update successful:', result.data)
    } else {
      console.error('Profile update failed:', result.error)
      ElMessage.error(t('profile.updateFailed') + ': ' + (result.error.message || t('errors.unknown')))
    }
  } catch (err) {
    console.error('Profile update error:', err)
    ElMessage.error(t('profile.updateFailed') + ', ' + t('errors.pleaseRetry'))
  } finally {
    updatingProfile.value = false
  }
}

const editRating = (rating: any) => {
  ElMessage.info(t('profile.ratingEditComingSoon'))
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
  const parent = img.parentElement
  if (parent) {
    const noPosterDiv = document.createElement('div')
    noPosterDiv.className = 'no-poster'
    noPosterDiv.innerHTML = '<el-icon><Picture /></el-icon>'
    parent.appendChild(noPosterDiv)
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const loadUserData = async () => {
  if (!authStore.isAuthenticated) {
    error.value = t('movie.pleaseLoginFirst')
    return
  }

  loading.value = true
  try {
    const result = await authStore.fetchProfile()
    if (result.success) {
      console.log('User data loaded:', user.value)
      console.log('Avatar URL:', user.value.profile?.avatar)
      console.log('Avatar type:', typeof user.value.profile?.avatar)

      profileForm.value = {
        username: user.value.username,
        email: user.value.email,
        first_name: user.value.first_name,
        last_name: user.value.last_name,
        profile: {
          bio: user.value.profile?.bio || '',
          avatar: user.value.profile?.avatar || ''
        }
      }

      console.log('Profile form avatar:', profileForm.value.profile.avatar)

    } else {
      throw new Error(result.error?.message || t('errors.loadFailed'))
    }

  } catch (err) {
    console.error('Load user data error:', err)
    error.value = t('profile.loadUserDataFailed')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadUserData()
})
</script>

<style scoped>
.profile-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.profile-card {
  text-align: center;
}

.profile-avatar {
  margin-bottom: 20px;
}



.profile-info h2 {
  font-size: 24px;
  margin: 0 0 5px 0;
}

.user-email {
  color: #666;
  margin: 0 0 10px 0;
}

.user-bio {
  color: #999;
  font-style: italic;
  margin: 0;
  line-height: 1.5;
}

.profile-stats {
  display: flex;
  justify-content: space-around;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.history-list,
.ratings-list {
  max-height: 600px;
  overflow-y: auto;
}

.history-item,
.rating-item {
  display: flex;
  gap: 15px;
  padding: 15px 0;
  border-bottom: 1px solid #ebeef5;
}

.movie-poster {
  width: 60px;
  height: 90px;
  flex-shrink: 0;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
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
  justify-content: center;
  align-items: center;
  background-color: #f5f5f5;
  color: #999;
}

.movie-info {
  flex: 1;
}

.movie-info h4 {
  margin: 0 0 5px 0;
  font-size: 16px;
}

.watch-time,
.rating-date {
  font-size: 12px;
  color: #999;
  margin: 5px 0;
}

.rating-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.rating-actions {
  display: flex;
  align-items: center;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
}

.loading,
.error {
  margin: 50px 0;
}

@media (max-width: 768px) {
  .el-row {
    flex-direction: column;
  }

  .el-col {
    width: 100% !important;
    margin-bottom: 20px;
  }
}
</style>
