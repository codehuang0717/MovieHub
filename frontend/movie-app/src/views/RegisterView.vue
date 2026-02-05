<template>
  <div class="register-view">
    <div class="register-container">
      <div class="register-card">
        <div class="register-header">
          <h1>{{ $t('auth.register') }}</h1>
          <p>{{ $t('auth.joinNow') }}</p>
        </div>

        <el-form 
          :model="registerForm" 
          :rules="registerRules" 
          ref="registerFormRef"
          @submit.prevent="handleRegister"
          label-position="top"
        >
          <el-form-item :label="$t('auth.username')" prop="username">
            <el-input 
              v-model="registerForm.username" 
              :placeholder="$t('auth.username')"
              prefix-icon="User"
              size="large"
            />
          </el-form-item>

          <el-form-item :label="$t('auth.email')" prop="email">
            <el-input 
              v-model="registerForm.email" 
              :placeholder="$t('auth.email')"
              prefix-icon="Message"
              size="large"
              type="email"
            />
          </el-form-item>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item :label="$t('auth.firstName')" prop="first_name">
                <el-input 
                  v-model="registerForm.first_name" 
                  :placeholder="$t('auth.firstName')"
                  size="large"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('auth.lastName')" prop="last_name">
                <el-input 
                  v-model="registerForm.last_name" 
                  :placeholder="$t('auth.lastName')"
                  size="large"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item :label="$t('auth.password')" prop="password">
            <el-input 
              v-model="registerForm.password" 
              type="password" 
              :placeholder="$t('auth.password')"
              prefix-icon="Lock"
              size="large"
              show-password
            />
          </el-form-item>

          <el-form-item :label="$t('auth.confirmPassword')" prop="password_confirm">
            <el-input 
              v-model="registerForm.password_confirm" 
              type="password" 
              :placeholder="$t('auth.confirmPassword')"
              prefix-icon="Lock"
              size="large"
              show-password
            />
          </el-form-item>

          <el-form-item>
            <el-checkbox v-model="agreeTerms">
              {{ $t('auth.agreeTermsPrefix') }} 
              <a href="#" @click.prevent="showTerms">{{ $t('auth.termsOfService') }}</a> {{ $t('auth.and') }} 
              <a href="#" @click.prevent="showPrivacy">{{ $t('auth.privacyPolicy') }}</a>
            </el-checkbox>
          </el-form-item>

          <el-form-item>
            <el-button 
              type="primary" 
              size="large" 
              :loading="loading"
              @click="handleRegister"
              :disabled="!agreeTerms"
              class="register-button"
            >
              {{ $t('auth.register') }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="register-footer">
          <p>
            {{ $t('auth.hasAccount') }}
            <router-link to="/login" class="link">{{ $t('auth.loginNow') }}</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'

const { t } = useI18n()
const router = useRouter()
const authStore = useAuthStore()

const registerFormRef = ref<FormInstance>()
const loading = ref(false)
const agreeTerms = ref(false)

const registerForm = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  password: '',
  password_confirm: ''
})

const validatePasswordConfirm = (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error(t('auth.confirmPassword') + t('errors.required')))
  } else if (value !== registerForm.password) {
    callback(new Error(t('auth.passwordMismatch')))
  } else {
    callback()
  }
}

const validateUsername = async (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error(t('auth.username') + t('errors.required')))
  } else if (value.length < 3) {
    callback(new Error(t('auth.username') + t('errors.minLength') + '3'))
  } else if (!/^[a-zA-Z0-9_]+$/.test(value)) {
    callback(new Error(t('auth.usernameInvalid')))
  } else {
    callback()
  }
}

const validateEmail = async (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error(t('auth.email') + t('errors.required')))
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
    callback(new Error(t('auth.emailInvalid')))
  } else {
    callback()
  }
}

const registerRules = {
  username: [
    { validator: validateUsername, trigger: 'blur' }
  ],
  email: [
    { validator: validateEmail, trigger: 'blur' }
  ],
  first_name: [
    { max: 30, message: t('auth.firstName') + t('errors.maxLength') + '30', trigger: 'blur' }
  ],
  last_name: [
    { max: 30, message: t('auth.lastName') + t('errors.maxLength') + '30', trigger: 'blur' }
  ],
  password: [
    { required: true, message: t('auth.password') + t('errors.required'), trigger: 'blur' },
    { min: 8, message: t('auth.password') + t('errors.minLength') + '8', trigger: 'blur' },
    { 
      pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/,
      message: t('auth.passwordRequirements'), 
      trigger: 'blur' 
    }
  ],
  password_confirm: [
    { validator: validatePasswordConfirm, trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  if (!agreeTerms.value) {
    ElMessage.warning(t('auth.agreeTerms'))
    return
  }
  
  try {
    await registerFormRef.value.validate()
    
    loading.value = true
    const result = await authStore.register(registerForm)
    
    if (result.success) {
      ElMessage.success(t('auth.registerSuccess'))
      router.push({ name: 'home' })
    } else {
      const errorMsg = result.error.username?.[0] || 
                      result.error.email?.[0] || 
                      result.error.non_field_errors?.[0] || 
                      t('auth.registerFailed')
      ElMessage.error(errorMsg)
    }
  } catch (error) {
    console.error('Register validation error:', error)
  } finally {
    loading.value = false
  }
}

const showTerms = () => {
  ElMessage.info(t('auth.termsComingSoon'))
}

const showPrivacy = () => {
  ElMessage.info(t('auth.privacyComingSoon'))
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    router.push({ name: 'home' })
  }
})
</script>

<style scoped>
.register-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.register-container {
  width: 100%;
  max-width: 500px;
}

.register-card {
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.register-header h1 {
  font-size: 32px;
  color: #303133;
  margin: 0 0 10px 0;
}

.register-header p {
  color: #909399;
  margin: 0;
  font-size: 14px;
}

.register-button {
  width: 100%;
  height: 45px;
  font-size: 16px;
}

.register-footer {
  text-align: center;
  margin-top: 30px;
}

.register-footer p {
  color: #606266;
  margin: 0;
}

.link {
  color: #409eff;
  text-decoration: none;
  font-weight: 500;
}

.link:hover {
  text-decoration: underline;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #303133;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
}

:deep(.el-checkbox__label) {
  font-size: 14px;
  color: #606266;
}

:deep(.el-checkbox__label a) {
  color: #409eff;
  text-decoration: none;
}

:deep(.el-checkbox__label a:hover) {
  text-decoration: underline;
}
</style>