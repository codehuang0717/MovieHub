<template>
  <div class="login-page">
    <!-- Background -->
    <div class="login-background">
      <div class="background-overlay"></div>
    </div>

    <!-- Login Container -->
    <div class="login-container">
      <!-- Back to Home -->
      <div class="back-home">
        <router-link to="/" class="back-link">
          <el-icon><ArrowLeft /></el-icon>
          {{ $t('common.back') }}
        </router-link>
      </div>

      <div class="login-form">
        <div class="form-header">
          <h1 class="form-title">{{ $t('auth.login') }}</h1>
          <p class="form-subtitle">{{ $t('auth.welcomeBack') }}</p>
        </div>

        <el-form 
          :model="loginForm" 
          :rules="loginRules" 
          ref="loginFormRef"
          @submit.prevent="handleLogin"
          size="large"
          label-position="top"
        >
          <el-form-item prop="username">
            <el-input 
              v-model="loginForm.username" 
              :placeholder="$t('auth.username')"
              prefix-icon="User"
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input 
              v-model="loginForm.password" 
              type="password" 
              :placeholder="$t('auth.password')"
              prefix-icon="Lock"
              show-password
            />
          </el-form-item>

          <el-form-item>
            <el-button 
              type="primary" 
              :loading="loading"
              @click="handleLogin"
              class="login-button"
            >
              {{ $t('auth.login') }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="form-footer">
          <p class="test-hint">
            {{ $t('auth.testAccount') }}: username <code>test</code> password <code>test123</code>
          </p>
          <p>
            {{ $t('auth.noAccount') }}
            <router-link to="/register" class="register-link">{{ $t('auth.registerNow') }}</router-link>
          </p>
        </div>
      </div>

      <div class="login-features">
        <div class="feature-item">
          <el-icon><Star /></el-icon>
          <span>{{ $t('auth.featureMovies') }}</span>
        </div>
        <div class="feature-item">
          <el-icon><VideoPlay /></el-icon>
          <span>{{ $t('auth.featureRecommendations') }}</span>
        </div>
        <div class="feature-item">
          <el-icon><ChatDotRound /></el-icon>
          <span>{{ $t('auth.featureCommunity') }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { ArrowLeft, Star, VideoPlay, ChatDotRound } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const loginFormRef = ref<FormInstance>()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: t('auth.username') + t('errors.required'), trigger: 'blur' },
    { min: 3, message: t('auth.username') + t('errors.minLength') + '3', trigger: 'blur' }
  ],
  password: [
    { required: true, message: t('auth.password') + t('errors.required'), trigger: 'blur' },
    { min: 6, message: t('auth.password') + t('errors.minLength') + '6', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    await loginFormRef.value.validate()
    
    loading.value = true
    const result = await authStore.login(loginForm)
    
    if (result.success) {
      ElMessage.success(t('auth.loginSuccess'))
      
      const redirect = route.query.redirect as string
      router.push(redirect || { name: 'home' })
    } else {
      const errorMsg = result.error.non_field_errors?.[0] || 
                      result.error.username?.[0] || 
                      result.error.password?.[0] || 
                      t('auth.loginFailed')
      ElMessage.error(errorMsg)
    }
  } catch (error) {
    console.error('Login validation error:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    router.push({ name: 'home' })
  }
})
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Background */
.login-background {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  z-index: -1;
}

.background-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 20% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(255, 255, 255, 0.05) 0%, transparent 50%);
}

/* Login Container */
.login-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 80px;
  align-items: center;
}

/* Back to Home */
.back-home {
  grid-column: 1 / -1;
  margin-bottom: 20px;
}

.back-link {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-size: 1rem;
  transition: color 0.2s;
}

.back-link:hover {
  color: white;
}

/* Login Form */
.login-form {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 48px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.form-header {
  text-align: center;
  margin-bottom: 40px;
}

.form-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.form-subtitle {
  color: #666;
  margin: 0;
  font-size: 1.1rem;
}

:deep(.el-form-item) {
  margin-bottom: 24px;
}

:deep(.el-input__wrapper) {
  border-radius: 12px;
  padding: 16px 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #dcdfe6;
  background: #ffffff;
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

:deep(.el-input__inner) {
  font-size: 1rem;
  color: #1a1a2e;
  height: 24px;
  line-height: 24px;
}

:deep(.el-input__inner::placeholder) {
  color: #909399;
}

:deep(.el-input__prefix),
:deep(.el-input__suffix) {
  color: #909399;
}

:deep(.el-form-item__error) {
  color: #f56c6c;
}

.login-button {
  width: 100%;
  height: 56px;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s ease;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

.form-footer {
  text-align: center;
  margin-top: 24px;
}

.form-footer p {
  color: #666;
  margin: 0;
  font-size: 1rem;
}

.register-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s;
}

.register-link:hover {
  color: #764ba2;
  text-decoration: underline;
}

.test-hint {
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 16px;
  font-size: 0.9rem;
}

.test-hint code {
  background: rgba(102, 126, 234, 0.2);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  color: #667eea;
  font-weight: 600;
}

/* Features */
.login-features {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 16px;
  color: white;
  font-size: 1.2rem;
}

.feature-item .el-icon {
  font-size: 2rem;
  color: rgba(255, 255, 255, 0.9);
}

/* Responsive Design */
@media (max-width: 1200px) {
  .login-container {
    max-width: 900px;
    gap: 60px;
  }
}

@media (max-width: 968px) {
  .login-container {
    grid-template-columns: 1fr;
    gap: 40px;
    max-width: 500px;
  }
  
  .login-features {
    flex-direction: row;
    justify-content: center;
    gap: 24px;
  }
  
  .feature-item {
    flex-direction: column;
    text-align: center;
    gap: 8px;
    font-size: 1rem;
  }
  
  .feature-item .el-icon {
    font-size: 1.5rem;
  }
}

@media (max-width: 768px) {
  .login-page {
    padding: 20px;
  }
  
  .login-container {
    max-width: 100%;
    gap: 32px;
  }
  
  .login-form {
    padding: 32px 20px;
  }
  
  .form-title {
    font-size: 2rem;
  }
  
  .form-subtitle {
    font-size: 1rem;
  }
  
  .login-features {
    flex-direction: column;
    gap: 20px;
  }
  
  .feature-item {
    flex-direction: row;
    justify-content: flex-start;
    font-size: 1rem;
  }
}

@media (max-width: 640px) {
  .login-page {
    padding: 16px;
  }
  
  .login-container {
    gap: 24px;
  }
  
  .login-form {
    padding: 24px 16px;
  }
  
  .form-title {
    font-size: 1.8rem;
  }
  
  .form-subtitle {
    font-size: 0.9rem;
  }
  
  :deep(.el-form-item) {
    margin-bottom: 20px;
  }
  
  :deep(.el-input__wrapper) {
    padding: 12px 16px;
  }
  
  .login-button {
    height: 48px;
    font-size: 1rem;
  }
  
  .form-footer {
    margin-top: 20px;
  }
  
  .form-footer p {
    font-size: 0.9rem;
  }
  
  .login-features {
    flex-direction: column;
    gap: 16px;
  }
  
  .feature-item {
    flex-direction: column;
    text-align: center;
    font-size: 0.9rem;
    padding: 16px;
  }
  
  .feature-item .el-icon {
    font-size: 1.2rem;
  }
}

@media (max-width: 480px) {
  .login-page {
    padding: 12px;
  }
  
  .login-container {
    gap: 20px;
  }
  
  .login-form {
    padding: 20px 12px;
  }
  
  .form-title {
    font-size: 1.6rem;
  }
  
  .back-home {
    margin-bottom: 16px;
  }
  
  .back-link {
    font-size: 0.9rem;
  }
  
  .form-header {
    margin-bottom: 32px;
  }
  
  :deep(.el-input__wrapper) {
    padding: 10px 12px;
  }
  
  .login-button {
    height: 44px;
  }
  
  .feature-item {
    padding: 12px;
  }
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}
</style>