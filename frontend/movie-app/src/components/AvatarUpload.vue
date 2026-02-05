<template>
  <div class="avatar-upload-component">
    <!-- 头像主容器 -->
    <div 
      class="avatar-container" 
      @click="handleAvatarClick"
      @mouseenter="handleMouseEnter"
      @mouseleave="handleMouseLeave"
      ref="avatarContainer"
    >
      <div class="avatar-wrapper">
        <img 
          v-if="avatarUrl && !imageError" 
          :src="avatarUrl" 
          :alt="altText"
          class="avatar-image"
          @error="handleImageError"
        />
        <div v-else class="avatar-placeholder">
          <el-icon :size="32"><User /></el-icon>
          <span>{{ placeholderText }}</span>
        </div>
        
        <!-- 悬停遮罩 -->
        <div class="avatar-overlay" :class="{ 'show-overlay': isHovering }">
          <div class="overlay-content">
            <el-icon :size="24"><Camera /></el-icon>
            <span>{{ isEditing ? '点击编辑' : '点击上传' }}</span>
          </div>
        </div>
        
        <!-- 加载遮罩 -->
        <div v-if="uploading" class="loading-overlay">
          <el-icon :size="24" class="is-loading"><Loading /></el-icon>
          <span>{{ uploadProgress > 0 ? `${uploadProgress}%` : '上传中...' }}</span>
        </div>
      </div>
      
      <!-- 进度条 -->
      <div v-if="uploading && uploadProgress > 0" class="upload-progress">
        <div 
          class="progress-bar"
          :style="{ width: uploadProgress + '%' }"
        ></div>
      </div>
    </div>
    
    <!-- 操作弹出层 -->
    <teleport to="body">
      <div 
        v-if="showDropdown" 
        class="avatar-dropdown"
        :style="dropdownStyle"
        @click.stop
        ref="dropdownRef"
      >
        <div class="dropdown-item" @click="handleUploadClick">
          <el-icon><Upload /></el-icon>
          <span>选择头像</span>
        </div>
        <div 
          v-if="hasCustomAvatar" 
          class="dropdown-item danger" 
          @click="handleRemoveAvatar"
        >
          <el-icon><Delete /></el-icon>
          <span>移除头像</span>
        </div>
        <div class="dropdown-tips">
          <span>支持格式：JPEG、PNG、GIF、WebP，最大5MB</span>
        </div>
      </div>
    </teleport>
    
    <!-- 点击外部关闭下拉菜单的遮罩 -->
    <teleport to="body">
      <div 
        v-if="showDropdown" 
        class="dropdown-overlay"
        @click="hideDropdown"
      ></div>
    </teleport>
    
    <!-- 隐藏的文件输入 -->
    <input
      ref="fileInput"
      type="file"
      :accept="acceptTypes"
      @change="handleFileChange"
      style="display: none"
    />
    
    <!-- 错误提示 -->
    <div v-if="errorMessage" class="error-message">
      <el-alert 
        :title="errorMessage" 
        type="error" 
        show-icon 
        :closable="true"
        @close="errorMessage = ''"
      />
    </div>
    
    <!-- 成功提示 -->
    <div v-if="successMessage" class="success-message">
      <el-alert 
        :title="successMessage" 
        type="success" 
        show-icon 
        :closable="true"
        @close="successMessage = ''"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Camera, Upload, Delete, Loading } from '@element-plus/icons-vue'

interface Props {
  // 当前头像URL
  modelValue?: string
  // 是否处于编辑模式
  editable?: boolean
  // 占位符文本
  placeholder?: string
  // 图片alt文本
  alt?: string
  // 头像大小
  size?: number
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'success', data: any): void
  (e: 'error', error: any): void
  (e: 'removed', data: any): void
}

const props = withDefaults(defineProps<Props>(), {
  editable: true,
  placeholder: '用户头像',
  alt: '用户头像',
  size: 120
})

const emit = defineEmits<Emits>()
const authStore = useAuthStore()

// 响应式数据
const fileInput = ref<HTMLInputElement>()
const avatarContainer = ref<HTMLElement>()
const dropdownRef = ref<HTMLElement>()
const uploading = ref(false)
const uploadProgress = ref(0)
const errorMessage = ref('')
const successMessage = ref('')
const imageError = ref(false)
const isHovering = ref(false)
const showDropdown = ref(false)
const dropdownPosition = ref({ top: 0, left: 0 })

// 计算属性
const isEditing = computed(() => props.editable)
const avatarUrl = computed(() => {
  const url = props.modelValue || ''
  
  if (!url) return ''
  
  // 如果是完整URL，直接使用
  if (url.startsWith('http')) {
    // 如果是localhost:8000，转换为代理URL
    if (url.includes('localhost:8000')) {
      return url.replace('http://localhost:8000', '')
    }
    return url
  }
  
  // 如果是相对路径，直接使用（会通过Vite代理）
  return url.startsWith('/') ? url : `/${url}`
})
const hasCustomAvatar = computed(() => {
  const defaultUrl = '/media/avatars/default.jpg'
  return avatarUrl.value && 
         avatarUrl.value !== defaultUrl && 
         !avatarUrl.value.includes('default.jpg')
})
const acceptTypes = computed(() => {
  return 'image/jpeg,image/png,image/gif,image/webp'
})
const altText = computed(() => props.alt)
const placeholderText = computed(() => props.placeholder)
const dropdownStyle = computed(() => ({
  top: `${dropdownPosition.value.top}px`,
  left: `${dropdownPosition.value.left}px`
}))

// 样式计算
const avatarStyle = computed(() => ({
  width: `${props.size}px`,
  height: `${props.size}px`
}))

// 事件处理
const handleAvatarClick = () => {
  if (!isEditing.value || uploading.value) return
  
  // 计算下拉菜单位置
  if (avatarContainer.value) {
    const rect = avatarContainer.value.getBoundingClientRect()
    dropdownPosition.value = {
      top: rect.bottom + 5,
      left: rect.left + (rect.width / 2) - 100 // 居中对齐，下拉菜单宽度约200px
    }
  }
  
  showDropdown.value = true
}

const handleFileChange = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (!file) return
  
  // 重置文件输入以允许重复选择同一文件
  target.value = ''
  
  // 验证文件
  if (!validateFile(file)) return
  
  // 上传文件
  await uploadAvatar(file)
}

const validateFile = (file: File): boolean => {
  // 清除之前的错误
  errorMessage.value = ''
  successMessage.value = ''
  
  // 检查文件类型
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    errorMessage.value = '只支持 JPEG、PNG、GIF 和 WebP 格式的图片'
    setTimeout(() => { errorMessage.value = '' }, 5000)
    return false
  }
  
  // 检查文件大小 (5MB)
  const maxSize = 5 * 1024 * 1024
  if (file.size > maxSize) {
    errorMessage.value = '文件大小不能超过 5MB'
    setTimeout(() => { errorMessage.value = '' }, 5000)
    return false
  }
  
  return true
}

const uploadAvatar = async (file: File) => {
  uploading.value = true
  uploadProgress.value = 0
  imageError.value = false
  
  try {
    // 创建用于跟踪进度的XHR
    const xhr = new XMLHttpRequest()
    
    // 设置进度监听
    xhr.upload.addEventListener('progress', (event) => {
      if (event.lengthComputable) {
        uploadProgress.value = Math.round((event.loaded * 100) / event.total)
      }
    })
    
    // 创建Promise以处理XHR
    const uploadPromise = new Promise((resolve, reject) => {
      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          try {
            const response = JSON.parse(xhr.responseText)
            resolve(response)
          } catch (e) {
            reject(new Error('响应解析失败'))
          }
        } else {
          reject(new Error(`上传失败: ${xhr.statusText}`))
        }
      })
      
      xhr.addEventListener('error', () => {
        reject(new Error('网络错误'))
      })
      
      xhr.addEventListener('timeout', () => {
        reject(new Error('上传超时'))
      })
    })
    
    // 准备FormData
    const formData = new FormData()
    formData.append('avatar', file)
    
    // 配置和发送请求
    xhr.open('POST', '/api/auth/profile/avatar/upload/')
    xhr.setRequestHeader('Authorization', `Bearer ${authStore.accessToken}`)
    xhr.timeout = 30000 // 30秒超时
    xhr.send(formData)
    
    // 等待上传完成
    const result = await uploadPromise as any
    
    // 更新头像URL
    emit('update:modelValue', result.avatar)
    emit('success', result)
    
    successMessage.value = '头像上传成功！'
    setTimeout(() => { successMessage.value = '' }, 3000)
    
    ElMessage.success('头像上传成功')
    
  } catch (error: any) {
    console.error('Avatar upload error:', error)
    
    const errorMsg = error.message || '上传失败，请重试'
    errorMessage.value = errorMsg
    setTimeout(() => { errorMessage.value = '' }, 5000)
    
    emit('error', error)
    ElMessage.error(errorMsg)
    
  } finally {
    uploading.value = false
    uploadProgress.value = 0
  }
}

const handleRemoveAvatar = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要移除头像吗？移除后将使用默认头像。',
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    uploading.value = true
    
    const result = await authStore.removeAvatar()
    
    if (result.success) {
      emit('update:modelValue', result.data.avatar)
      emit('removed', result.data)
      
      successMessage.value = '头像已移除！'
      setTimeout(() => { successMessage.value = '' }, 3000)
      
      ElMessage.success('头像已移除')
    } else {
      throw new Error(result.error.message || '移除失败')
    }
    
  } catch (error: any) {
    if (error === 'cancel') return
    
    console.error('Avatar remove error:', error)
    
    const errorMsg = error.message || '移除失败，请重试'
    errorMessage.value = errorMsg
    setTimeout(() => { errorMessage.value = '' }, 5000)
    
    emit('error', error)
    ElMessage.error(errorMsg)
    
  } finally {
    uploading.value = false
  }
}

const handleImageError = () => {
  imageError.value = true
}

const handleMouseEnter = () => {
  if (isEditing.value && !uploading.value) {
    isHovering.value = true
  }
}

const handleMouseLeave = () => {
  isHovering.value = false
}

const handleUploadClick = () => {
  hideDropdown()
  fileInput.value?.click()
}

const hideDropdown = () => {
  showDropdown.value = false
}

// 全局点击监听器
const handleGlobalClick = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!dropdownRef.value?.contains(target) && !avatarContainer.value?.contains(target)) {
    hideDropdown()
  }
}

// 生命周期
onMounted(() => {
  document.addEventListener('click', handleGlobalClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleGlobalClick)
})

// 暴露方法给父组件
defineExpose({
  triggerUpload: handleAvatarClick,
  clearError: () => { errorMessage.value = '' },
  clearSuccess: () => { successMessage.value = '' },
  hideDropdown
})
</script>

<style scoped>
.avatar-upload-component {
  display: inline-block;
}

.avatar-container {
  position: relative;
  display: inline-block;
  cursor: pointer;
}

.avatar-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid #e2e8f0;
  transition: all 0.3s ease;
  background-color: #f8fafc;
}

.avatar-wrapper:hover {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.avatar-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: #6b7280;
  background-color: #f9fafb;
  text-align: center;
  padding: 10px;
}

.avatar-placeholder span {
  margin-top: 8px;
  font-size: 12px;
  line-height: 1.2;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.avatar-overlay.show-overlay {
  opacity: 1;
}

.overlay-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  text-align: center;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  gap: 8px;
  font-size: 12px;
}

.loading-overlay .is-loading {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.upload-progress {
  margin-top: 8px;
  height: 4px;
  background-color: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #2563eb);
  transition: width 0.3s ease;
  border-radius: 2px;
}

.avatar-actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
  justify-content: center;
}

.upload-tips {
  margin-top: 8px;
  text-align: center;
}

.upload-tips p {
  font-size: 12px;
  color: #6b7280;
  line-height: 1.4;
  margin: 0;
}

.error-message,
.success-message {
  margin-top: 12px;
}

.error-message :deep(.el-alert),
.success-message :deep(.el-alert) {
  padding: 8px 12px;
  font-size: 13px;
}

/* 下拉菜单样式 */
.avatar-dropdown {
  position: fixed;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  z-index: 3000;
  min-width: 200px;
  overflow: hidden;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  border-bottom: 1px solid #f5f7fa;
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover {
  background-color: #f5f7fa;
}

.dropdown-item.danger {
  color: #f56c6c;
}

.dropdown-item.danger:hover {
  background-color: #fef0f0;
}

.dropdown-item .el-icon {
  flex-shrink: 0;
  font-size: 16px;
}

.dropdown-item span {
  font-size: 14px;
  line-height: 1.2;
}

.dropdown-tips {
  padding: 8px 16px;
  background-color: #f8f9fa;
  font-size: 12px;
  color: #6b7280;
  line-height: 1.3;
  border-top: 1px solid #e4e7ed;
}

.dropdown-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: transparent;
  z-index: 2999;
}

/* 响应式设计 */
@media (max-width: 640px) {
  .overlay-content span {
    font-size: 11px;
  }
  
  .avatar-dropdown {
    min-width: 180px;
  }
  
  .dropdown-item {
    padding: 10px 12px;
  }
  
  .dropdown-item span {
    font-size: 13px;
  }
}
</style>