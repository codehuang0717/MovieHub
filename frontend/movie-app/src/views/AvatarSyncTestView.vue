<template>
  <div class="avatar-sync-test">
    <h2>导航栏头像同步测试</h2>
    
    <div class="test-section">
      <h3>当前用户信息</h3>
      <div class="user-info">
        <p><strong>用户名:</strong> {{ authStore.user?.username }}</p>
        <p><strong>头像URL:</strong> {{ authStore.user?.profile?.avatar }}</p>
        <p><strong>导航栏头像URL:</strong> {{ userNavAvatar }}</p>
      </div>
    </div>
    
    <div class="test-section">
      <h3>导航栏预览</h3>
      <div class="nav-preview">
        <div class="user-nav-avatar">
          <img 
            v-if="userNavAvatar && !avatarLoadError"
            :src="userNavAvatar" 
            :alt="authStore.user?.username || '用户头像'"
            class="nav-avatar-img"
            @error="handleAvatarError"
          />
          <div v-else class="nav-avatar-fallback">
            {{ authStore.user?.username?.charAt(0).toUpperCase() || 'U' }}
          </div>
        </div>
        <p>导航栏中的头像显示效果</p>
      </div>
    </div>
    
    <div class="test-section">
      <h3>测试操作</h3>
      <div class="test-actions">
        <el-button @click="refreshProfile" :loading="loading">
          刷新用户信息
        </el-button>
        <el-button @click="testAvatarUpdate">
          测试头像更新
        </el-button>
        <el-button @click="goToProfile">
          前往个人中心
        </el-button>
      </div>
    </div>
    
    <div class="test-section">
      <h3>调试信息</h3>
      <div class="debug-info">
        <p><strong>是否已登录:</strong> {{ authStore.isAuthenticated }}</p>
        <p><strong>头像加载错误:</strong> {{ avatarLoadError }}</p>
        <p><strong>头像URL类型:</strong> {{ typeof authStore.user?.profile?.avatar }}</p>
        <p><strong>处理后的URL:</strong> {{ userNavAvatar }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const avatarLoadError = ref(false)
const loading = ref(false)

// 计算导航栏头像URL
const userNavAvatar = computed(() => {
  const avatarUrl = authStore.user?.profile?.avatar
  if (!avatarUrl) return ''
  
  // 处理URL格式
  if (avatarUrl.startsWith('http')) {
    // 如果是localhost:8000，转换为代理URL
    if (avatarUrl.includes('localhost:8000')) {
      return avatarUrl.replace('http://localhost:8000', '')
    }
    return avatarUrl
  }
  
  // 相对路径直接使用
  return avatarUrl.startsWith('/') ? avatarUrl : `/${avatarUrl}`
})

const refreshProfile = async () => {
  loading.value = true
  avatarLoadError.value = false
  
  try {
    const result = await authStore.fetchProfile()
    if (result.success) {
      ElMessage.success('用户信息刷新成功')
    } else {
      throw new Error(result.error?.message || '刷新失败')
    }
  } catch (error: any) {
    console.error('刷新失败:', error)
    ElMessage.error('刷新失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const testAvatarUpdate = () => {
  ElMessage.info('请在个人中心测试头像上传功能')
  router.push('/profile')
}

const goToProfile = () => {
  router.push('/profile')
}

const handleAvatarError = () => {
  avatarLoadError.value = true
  console.log('测试页面头像加载失败')
}
</script>

<style scoped>
.avatar-sync-test {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.test-section {
  margin: 30px 0;
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #fafafa;
}

.test-section h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #409eff;
}

.user-info p,
.debug-info p {
  margin: 8px 0;
  font-family: monospace;
  font-size: 13px;
  line-height: 1.4;
}

.nav-preview {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-nav-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
  background: #f0f0f0;
}

.nav-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.nav-avatar-fallback {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #58a6ff 0%, #79c0ff 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
}

.test-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

h2 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 40px;
}
</style>