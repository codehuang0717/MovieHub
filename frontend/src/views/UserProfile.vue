<template>
  <div class="user-profile">
    <div class="profile-header">
      <h2>个人中心</h2>
    </div>
    
    <div class="profile-content">
      <!-- 头像上传区域 -->
      <div class="avatar-section">
        <h3>个人头像</h3>
        <AvatarUpload 
          v-model="userProfile.profile.avatar"
          @success="onAvatarUpdated"
          @removed="onAvatarRemoved"
          @profile-updated="onProfileUpdated"
        />
      </div>
      
      <!-- 基本信息 -->
      <div class="info-section">
        <h3>基本信息</h3>
        <form @submit.prevent="saveProfile" class="profile-form">
          <div class="form-group">
            <label for="email">邮箱</label>
            <input 
              type="email" 
              id="email" 
              v-model="userProfile.email" 
              required
            />
          </div>
          
          <div class="form-group">
            <label for="firstName">名字</label>
            <input 
              type="text" 
              id="firstName" 
              v-model="userProfile.first_name"
            />
          </div>
          
          <div class="form-group">
            <label for="lastName">姓氏</label>
            <input 
              type="text" 
              id="lastName" 
              v-model="userProfile.last_name"
            />
          </div>
          
          <div class="form-group">
            <label for="bio">个人简介</label>
            <textarea 
              id="bio" 
              v-model="userProfile.profile.bio"
              rows="4"
              placeholder="介绍一下自己..."
              maxlength="500"
            ></textarea>
            <div class="char-count">
              {{ (userProfile.profile.bio || '').length }}/500
            </div>
          </div>
          
          <div class="form-actions">
            <button 
              type="submit" 
              class="btn-save"
              :disabled="saving"
            >
              {{ saving ? '保存中...' : '保存修改' }}
            </button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- 成功提示 -->
    <div v-if="successMessage" class="success-message">
      {{ successMessage }}
    </div>
    
    <!-- 错误提示 -->
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>
  </div>
</template>

<script>
import AvatarUpload from '@/components/AvatarUpload.vue'

export default {
  name: 'UserProfile',
  components: {
    AvatarUpload
  },
  data() {
    return {
      userProfile: {
        email: '',
        first_name: '',
        last_name: '',
        profile: {
          avatar: '',
          bio: ''
        }
      },
      saving: false,
      successMessage: '',
      errorMessage: ''
    }
  },
  async mounted() {
    await this.loadUserProfile()
  },
  methods: {
    async loadUserProfile() {
      try {
        const response = await this.$axios.get('/api/auth/profile/', {
          headers: {
            'Authorization': `Bearer ${this.$store.getters.token}`
          }
        })
        
        this.userProfile = response.data
        
      } catch (error) {
        console.error('加载用户档案失败:', error)
        this.errorMessage = '加载用户信息失败'
      }
    },
    
    async saveProfile() {
      this.saving = true
      this.successMessage = ''
      this.errorMessage = ''
      
      try {
        const profileData = {
          email: this.userProfile.email,
          first_name: this.userProfile.first_name,
          last_name: this.userProfile.last_name,
          profile: {
            bio: this.userProfile.profile.bio || ''
          }
        }
        
        const response = await this.$axios.put(
          '/api/auth/profile/update/',
          profileData,
          {
            headers: {
              'Authorization': `Bearer ${this.$store.getters.token}`
            }
          }
        )
        
        this.userProfile = response.data
        this.successMessage = '个人资料已更新！'
        
        // 3秒后清除成功消息
        setTimeout(() => {
          this.successMessage = ''
        }, 3000)
        
      } catch (error) {
        console.error('保存档案失败:', error)
        this.errorMessage = error.response?.data?.profile?.bio?.[0] || 
                           error.response?.data?.email?.[0] ||
                           '保存失败，请重试'
      } finally {
        this.saving = false
      }
    },
    
    onAvatarUpdated(avatarUrl) {
      this.userProfile.profile.avatar = avatarUrl
      this.successMessage = '头像更新成功！'
      setTimeout(() => { this.successMessage = '' }, 3000)
    },
    
    onAvatarRemoved(avatarUrl) {
      this.userProfile.profile.avatar = avatarUrl
      this.successMessage = '头像已移除！'
      setTimeout(() => { this.successMessage = '' }, 3000)
    },
    
    onProfileUpdated(profile) {
      this.userProfile = profile
      this.successMessage = '资料更新成功！'
      setTimeout(() => { this.successMessage = '' }, 3000)
    }
  }
}
</script>

<style scoped>
.user-profile {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}

.profile-header {
  margin-bottom: 32px;
}

.profile-header h2 {
  margin: 0;
  color: #1f2937;
  font-size: 28px;
  font-weight: 600;
}

.profile-content {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 32px;
}

@media (max-width: 768px) {
  .profile-content {
    grid-template-columns: 1fr;
    gap: 24px;
  }
}

.avatar-section,
.info-section {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.avatar-section h3,
.info-section h3 {
  margin: 0 0 20px 0;
  color: #374151;
  font-size: 18px;
  font-weight: 600;
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-weight: 500;
  color: #374151;
  font-size: 14px;
}

.form-group input,
.form-group textarea {
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: #6b7280;
}

.form-actions {
  margin-top: 8px;
}

.btn-save {
  background-color: #3b82f6;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.btn-save:hover:not(:disabled) {
  background-color: #2563eb;
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.success-message {
  margin-top: 20px;
  padding: 12px 16px;
  background-color: #d1fae5;
  color: #065f46;
  border-radius: 6px;
  font-size: 14px;
  border: 1px solid #a7f3d0;
}

.error-message {
  margin-top: 20px;
  padding: 12px 16px;
  background-color: #fee;
  color: #c33;
  border-radius: 6px;
  font-size: 14px;
  border: 1px solid #fcc;
}
</style>