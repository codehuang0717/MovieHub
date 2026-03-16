<template>
  <nav class="navbar">
    <div class="nav-container">
      <div class="nav-brand">
        <router-link to="/" class="brand-link">
          <h1>🎬 MovieHub</h1>
        </router-link>
      </div>

      <div class="nav-menu">
        <router-link to="/" class="nav-item" active-class="nav-active">
          {{ $t('common.home') }}
        </router-link>
        <router-link to="/movies" class="nav-item" active-class="nav-active">
          {{ $t('common.movies') }}
        </router-link>
        <router-link to="/search" class="nav-item" active-class="nav-active">
          {{ $t('common.search') }}
        </router-link>
      </div>

      <div class="nav-search">
        <el-input
          v-model="searchQuery"
          :placeholder="$t('search.placeholder')"
          @keyup.enter="performSearch"
          clearable
          class="search-input"
        >
          <template #suffix>
            <el-icon class="search-icon" @click="performSearch">
              <Search />
            </el-icon>
          </template>
        </el-input>
      </div>

      <div class="nav-auth">
        <el-button @click="switchLanguage" text size="small" class="lang-switch">
          {{ currentLocale === 'zh' ? 'EN' : '中文' }}
        </el-button>
        <template v-if="authStore.isAuthenticated">
          <el-dropdown>
            <div class="user-nav-avatar">
              <img
                v-if="userNavAvatar && !avatarLoadError"
                :src="userNavAvatar"
                :alt="authStore.user?.username || '用户头像'"
                class="nav-avatar-img"
                width="36"
                height="36"
                fetchpriority="high"
                @error="handleAvatarError"
              />
              <div v-else class="nav-avatar-fallback">
                {{ authStore.user?.username?.charAt(0).toUpperCase() || 'U' }}
              </div>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="router.push('/profile')">
                  <el-icon><User /></el-icon> {{ $t('profile.title') }}
                </el-dropdown-item>
                <el-dropdown-item @click="router.push('/watchlist')">
                  <el-icon><Star /></el-icon> {{ $t('watchlist.title') }}
                </el-dropdown-item>
                <el-dropdown-item @click="router.push('/collections')">
                  <el-icon><Collection /></el-icon> {{ $t('collections.myCollections') }}
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon> {{ $t('common.logout') }}
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <el-button @click="handleLogin" text size="large">{{ $t('common.login') }}</el-button>
          <el-button @click="router.push({ name: 'register' })" type="primary" size="large">{{ $t('common.register') }}</el-button>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useTMDBStore } from '@/stores/tmdb'
import { Search, User, Star, Collection, SwitchButton } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const { t, locale } = useI18n()
const router = useRouter()
const authStore = useAuthStore()
const tmdbStore = useTMDBStore()
const searchQuery = ref('')
const avatarLoadError = ref(false)

const currentLocale = computed(() => locale.value)

const switchLanguage = async () => {
  const newLocale = currentLocale.value === 'zh' ? 'en' : 'zh'
  locale.value = newLocale
  localStorage.setItem('locale', newLocale)
  await tmdbStore.reloadAllData()
}

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

const performSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({
      name: 'search',
      query: { q: searchQuery.value.trim() }
    })
  }
}

const handleLogout = async () => {
  await authStore.logout()
  ElMessage.success(t('auth.logoutSuccess'))
  router.push('/')
}

const handleLogin = () => {
  router.push({ name: 'login' })
}

const handleAvatarError = () => {
  avatarLoadError.value = true
  console.log('导航栏头像加载失败，显示默认文字头像')
}
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(13, 17, 23, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #30363d;
  transition: all 0.3s ease;
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
}

.brand-link {
  text-decoration: none;
  color: #58a6ff;
  transition: all 0.2s ease;
}

.brand-link:hover {
  color: #79c0ff;
  transform: scale(1.02);
}

.brand-link h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #58a6ff 0%, #79c0ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 32px;
  flex: 1;
  margin-left: 48px;
}

.nav-item {
  color: #f0f6fc;
  text-decoration: none;
  font-weight: 500;
  font-size: 16px;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.2s ease;
  position: relative;
}

.nav-item:hover {
  color: #58a6ff;
  background: rgba(88, 166, 255, 0.1);
  transform: translateY(-1px);
}

.nav-item.nav-active {
  color: #58a6ff;
  background: rgba(88, 166, 255, 0.15);
}

.nav-item.nav-active::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 30px;
  height: 3px;
  background: #58a6ff;
  border-radius: 2px;
}

.nav-search {
  margin-left: auto;
  margin-right: 24px;
}

.search-input {
  width: 280px;
  transition: all 0.2s ease;
}

.search-input:focus-within {
  width: 320px;
}

:deep(.search-input .el-input__wrapper) {
  background: #21262d;
  border: 1px solid #30363d;
  box-shadow: none;
  border-radius: 24px;
  transition: all 0.2s ease;
}

:deep(.search-input .el-input__wrapper:hover) {
  border-color: #58a6ff;
  box-shadow: 0 0 0 2px rgba(88, 166, 255, 0.1);
}

:deep(.search-input .el-input__wrapper.is-focus) {
  border-color: #58a6ff;
  box-shadow: 0 0 0 2px rgba(88, 166, 255, 0.2);
}

:deep(.search-input .el-input__inner) {
  color: #f0f6fc;
  font-size: 14px;
}

:deep(.search-input .el-input__inner::placeholder) {
  color: #8b949e;
}

.search-icon {
  cursor: pointer;
  color: #8b949e;
  transition: all 0.2s ease;
}

.search-icon:hover {
  color: #58a6ff;
  transform: scale(1.1);
}

.nav-auth {
  display: flex;
  align-items: center;
  gap: 12px;
}

.lang-switch {
  color: #8b949e;
  font-size: 12px;
  padding: 4px 8px;
  border: 1px solid #30363d;
  border-radius: 4px;
}

.lang-switch:hover {
  color: #58a6ff;
  border-color: #58a6ff;
}

.user-nav-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
  position: relative;
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

.user-nav-avatar:hover {
  transform: scale(1.05);
  border-color: rgba(255, 255, 255, 0.3);
  box-shadow: 0 4px 12px rgba(88, 166, 255, 0.3);
}

/* Responsive Design */
@media (max-width: 1200px) {
  .nav-container {
    padding: 0 20px;
  }

  .nav-menu {
    gap: 24px;
  }

  .search-input {
    width: 240px;
  }

  .search-input:focus-within {
    width: 260px;
  }
}

@media (max-width: 992px) {
  .nav-menu {
    display: none;
  }

  .nav-search {
    display: none;
  }

  .nav-container {
    padding: 0 16px;
    justify-content: space-between;
  }

  .nav-brand {
    flex: 1;
  }

  .brand-link h1 {
    font-size: 20px;
  }
}

@media (max-width: 768px) {
  .nav-container {
    padding: 0 12px;
    height: 56px;
  }

  .brand-link h1 {
    font-size: 18px;
  }

  .nav-auth .el-button {
    padding: 6px 12px;
    font-size: 14px;
  }

.user-nav-avatar {
    width: 32px;
    height: 32px;
  }

  .nav-avatar-fallback {
    font-size: 10px;
  }

  .nav-avatar-fallback {
    font-size: 12px;
  }

  .nav-avatar-fallback {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .nav-container {
    padding: 0 8px;
  }

  .brand-link h1 {
    font-size: 16px;
  }

  .nav-auth .el-button {
    padding: 4px 8px;
    font-size: 12px;
  }

  .nav-auth {
    gap: 6px;
  }
}

/* Custom dropdown menu */
:deep(.el-dropdown-menu) {
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

:deep(.el-dropdown-menu__item) {
  color: #f0f6fc;
  transition: all 0.2s ease;
}

:deep(.el-dropdown-menu__item:hover) {
  background: rgba(88, 166, 255, 0.1);
  color: #58a6ff;
}

:deep(.el-dropdown-menu__item.is-divided) {
  border-top: 1px solid #30363d;
}
</style>
