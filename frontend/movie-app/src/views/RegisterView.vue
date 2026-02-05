<template>
  <div class="register-view">
    <div class="register-container">
      <div class="register-card">
        <div class="register-header">
          <h1>注册</h1>
          <p>加入我们，发现更多精彩电影</p>
        </div>

        <el-form 
          :model="registerForm" 
          :rules="registerRules" 
          ref="registerFormRef"
          @submit.prevent="handleRegister"
          label-position="top"
        >
          <el-form-item label="用户名" prop="username">
            <el-input 
              v-model="registerForm.username" 
              placeholder="请输入用户名"
              prefix-icon="User"
              size="large"
            />
          </el-form-item>

          <el-form-item label="邮箱" prop="email">
            <el-input 
              v-model="registerForm.email" 
              placeholder="请输入邮箱"
              prefix-icon="Message"
              size="large"
              type="email"
            />
          </el-form-item>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="姓" prop="first_name">
                <el-input 
                  v-model="registerForm.first_name" 
                  placeholder="请输入姓"
                  size="large"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="名" prop="last_name">
                <el-input 
                  v-model="registerForm.last_name" 
                  placeholder="请输入名"
                  size="large"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="密码" prop="password">
            <el-input 
              v-model="registerForm.password" 
              type="password" 
              placeholder="请输入密码"
              prefix-icon="Lock"
              size="large"
              show-password
            />
          </el-form-item>

          <el-form-item label="确认密码" prop="password_confirm">
            <el-input 
              v-model="registerForm.password_confirm" 
              type="password" 
              placeholder="请再次输入密码"
              prefix-icon="Lock"
              size="large"
              show-password
            />
          </el-form-item>

          <el-form-item>
            <el-checkbox v-model="agreeTerms">
              我已阅读并同意 
              <a href="#" @click.prevent="showTerms">用户协议</a> 和 
              <a href="#" @click.prevent="showPrivacy">隐私政策</a>
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
              注册
            </el-button>
          </el-form-item>
        </el-form>

        <div class="register-footer">
          <p>
            已有账号？
            <router-link to="/login" class="link">立即登录</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'

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
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const validateUsername = async (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('请输入用户名'))
  } else if (value.length < 3) {
    callback(new Error('用户名至少3个字符'))
  } else if (!/^[a-zA-Z0-9_]+$/.test(value)) {
    callback(new Error('用户名只能包含字母、数字和下划线'))
  } else {
    // TODO: 检查用户名是否已存在
    callback()
  }
}

const validateEmail = async (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('请输入邮箱'))
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
    callback(new Error('请输入有效的邮箱地址'))
  } else {
    // TODO: 检查邮箱是否已存在
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
    { max: 30, message: '姓不能超过30个字符', trigger: 'blur' }
  ],
  last_name: [
    { max: 30, message: '名不能超过30个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码至少8个字符', trigger: 'blur' },
    { 
      pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/,
      message: '密码必须包含大小写字母和数字', 
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
    ElMessage.warning('请先同意用户协议和隐私政策')
    return
  }
  
  try {
    await registerFormRef.value.validate()
    
    loading.value = true
    const result = await authStore.register(registerForm)
    
    if (result.success) {
      ElMessage.success('注册成功！')
      router.push({ name: 'home' })
    } else {
      const errorMsg = result.error.username?.[0] || 
                     result.error.email?.[0] || 
                     result.error.non_field_errors?.[0] || 
                     '注册失败，请检查输入信息'
      ElMessage.error(errorMsg)
    }
  } catch (error) {
    console.error('Register validation error:', error)
  } finally {
    loading.value = false
  }
}

const showTerms = () => {
  ElMessage.info('用户协议页面开发中...')
}

const showPrivacy = () => {
  ElMessage.info('隐私政策页面开发中...')
}

onMounted(() => {
  // 如果已经登录，跳转到首页
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