<template>
  <div class="avatar-upload">
    <div class="avatar-container">
      <img 
        :src="avatarUrl" 
        alt="用户头像" 
        class="avatar-image"
        @error="handleImageError"
      />
      <div class="avatar-overlay" v-if="isEditing">
        <div class="overlay-text">
          <i class="icon-camera"></i>
          <span>更换头像</span>
        </div>
      </div>
      <input 
        ref="fileInput"
        type="file"
        accept="image/jpeg,image/png,image/gif,image/webp"
        @change="handleFileSelect"
        style="display: none"
      />
    </div>
    
    <div class="avatar-controls" v-if="isEditing">
      <button 
        @click="selectFile" 
        class="btn btn-primary"
        :disabled="uploading"
      >
        <i class="icon-upload" v-if="!uploading"></i>
        <i class="icon-loading" v-if="uploading"></i>
        {{ uploading ? '上传中...' : '选择头像' }}
      </button>
      
      <button 
        v-if="avatarUrl && avatarUrl !== defaultAvatarUrl"
        @click="removeAvatar"
        class="btn btn-secondary"
        :disabled="uploading"
      >
        <i class="icon-delete"></i>
        移除头像
      </button>
    </div>
    
    <div class="upload-info">
      <p class="upload-tips">
        支持格式：JPEG、PNG、GIF、WebP<br>
        文件大小：最大5MB
      </p>
      <div v-if="uploadProgress > 0 && uploading" class="progress-bar">
        <div 
          class="progress-fill" 
          :style="{ width: uploadProgress + '%' }"
        ></div>
      </div>
    </div>
    
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'AvatarUpload',
  props: {
    // 当前头像URL
    value: {
      type: String,
      default: ''
    },
    // 是否处于编辑模式
    isEditing: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      uploading: false,
      uploadProgress: 0,
      error: null,
      defaultAvatarUrl: '/media/avatars/default.jpg'
    }
  },
  computed: {
    avatarUrl: {
      get() {
        return this.value || this.defaultAvatarUrl
      },
      set(newUrl) {
        this.$emit('input', newUrl)
      }
    }
  },
  methods: {
    selectFile() {
      this.$refs.fileInput.click()
    },
    
    async handleFileSelect(event) {
      const file = event.target.files[0]
      if (!file) return
      
      // 验证文件
      if (!this.validateFile(file)) {
        return
      }
      
      await this.uploadAvatar(file)
      
      // 重置input以允许重复选择同一文件
      event.target.value = ''
    },
    
    validateFile(file) {
      // 检查文件类型
      const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
      if (!allowedTypes.includes(file.type)) {
        this.error = '只支持 JPEG、PNG、GIF 和 WebP 格式的图片'
        setTimeout(() => { this.error = null }, 5000)
        return false
      }
      
      // 检查文件大小 (5MB)
      const maxSize = 5 * 1024 * 1024
      if (file.size > maxSize) {
        this.error = '文件大小不能超过 5MB'
        setTimeout(() => { this.error = null }, 5000)
        return false
      }
      
      this.error = null
      return true
    },
    
    async uploadAvatar(file) {
      this.uploading = true
      this.uploadProgress = 0
      this.error = null
      
      try {
        const formData = new FormData()
        formData.append('avatar', file)
        
        const response = await this.$axios.post('/api/auth/profile/avatar/upload/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${this.$store.getters.token}`
          },
          onUploadProgress: (progressEvent) => {
            this.uploadProgress = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            )
          }
        })
        
        // 更新头像URL
        this.avatarUrl = response.data.avatar
        
        // 可选：同时更新用户档案中的bio等其他信息
        await this.updateUserProfile({ avatar: response.data.avatar })
        
        this.$emit('success', response.data.avatar)
        
      } catch (error) {
        console.error('头像上传失败:', error)
        this.error = error.response?.data?.error || '上传失败，请重试'
      } finally {
        this.uploading = false
        this.uploadProgress = 0
      }
    },
    
    async removeAvatar() {
      if (!confirm('确定要移除头像吗？')) return
      
      this.uploading = true
      
      try {
        const response = await this.$axios.delete('/api/auth/profile/avatar/remove/', {
          headers: {
            'Authorization': `Bearer ${this.$store.getters.token}`
          }
        })
        
        this.avatarUrl = response.data.avatar
        this.$emit('removed', response.data.avatar)
        
      } catch (error) {
        console.error('头像移除失败:', error)
        this.error = error.response?.data?.error || '移除失败，请重试'
      } finally {
        this.uploading = false
      }
    },
    
    async updateUserProfile(profileData) {
      // 可选：同时更新其他profile字段
      try {
        const response = await this.$axios.put(
          '/api/auth/profile/update/',
          { profile: profileData },
          {
            headers: {
              'Authorization': `Bearer ${this.$store.getters.token}`
            }
          }
        )
        this.$emit('profile-updated', response.data)
      } catch (error) {
        console.error('档案更新失败:', error)
      }
    },
    
    handleImageError() {
      // 图片加载失败时显示默认头像
      this.avatarUrl = this.defaultAvatarUrl
    }
  }
}
</script>

<style scoped>
.avatar-upload {
  max-width: 300px;
}

.avatar-container {
  position: relative;
  display: inline-block;
}

.avatar-image {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #e2e8f0;
  transition: all 0.3s ease;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.avatar-container:hover .avatar-overlay {
  opacity: 1;
}

.overlay-text {
  text-align: center;
  font-size: 14px;
}

.overlay-text i {
  display: block;
  font-size: 24px;
  margin-bottom: 4px;
}

.avatar-controls {
  margin-top: 16px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
}

.btn-secondary {
  background-color: #6b7280;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #4b5563;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.upload-info {
  margin-top: 12px;
}

.upload-tips {
  font-size: 12px;
  color: #6b7280;
  line-height: 1.4;
  margin: 0;
}

.progress-bar {
  margin-top: 8px;
  height: 4px;
  background-color: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #3b82f6;
  transition: width 0.3s ease;
}

.error-message {
  margin-top: 12px;
  padding: 8px 12px;
  background-color: #fee;
  color: #c33;
  border-radius: 6px;
  font-size: 14px;
}

/* 加载动画 */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.icon-loading {
  animation: spin 1s linear infinite;
}
</style>