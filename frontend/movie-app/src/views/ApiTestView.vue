<template>
  <div class="api-test">
    <h2>API 测试页面</h2>
    
    <div class="test-section">
      <h3>1. 测试分类API</h3>
      <el-button @click="testCategories" :loading="testing.categories">
        测试分类
      </el-button>
      <div v-if="categoriesResult" class="result">
        <pre>{{ JSON.stringify(categoriesResult, null, 2) }}</pre>
      </div>
    </div>

    <div class="test-section">
      <h3>2. 测试电影API</h3>
      <el-button @click="testMovies" :loading="testing.movies">
        测试电影
      </el-button>
      <div v-if="moviesResult" class="result">
        <pre>{{ JSON.stringify(moviesResult, null, 2) }}</pre>
      </div>
    </div>

    <div class="test-section">
      <h3>3. 测试登录状态</h3>
      <p>已登录: {{ authStore.isAuthenticated }}</p>
      <p>用户: {{ authStore.user?.username || '未登录' }}</p>
      <p>Token: {{ authStore.accessToken ? '有' : '无' }}</p>
    </div>

    <div class="test-section">
      <h3>4. 测试用户登录</h3>
      <el-button @click="testLogin" :loading="testing.login">
        测试登录 (用户名: admin, 密码: admin123)
      </el-button>
      <div v-if="loginResult" class="result">
        <pre>{{ JSON.stringify(loginResult, null, 2) }}</pre>
      </div>
    </div>

    <div class="test-section">
      <h3>5. 测试想看列表API</h3>
      <div class="button-group">
        <el-button @click="testWatchlist" :loading="testing.watchlist">
          获取想看列表
        </el-button>
        <el-button @click="testToggleWatchlist(6)" :loading="testing.toggle">
          切换想看状态 (ID: 6)
        </el-button>
        <el-button @click="testAddToWatchlist(6)" :loading="testing.add">
          添加到想看 (ID: 6)
        </el-button>
        <el-button @click="testRemoveFromWatchlist(6)" :loading="testing.remove">
          移除想看 (ID: 6)
        </el-button>
      </div>
      <div v-if="watchlistResult" class="result">
        <h4>{{ watchlistResult.title }}</h4>
        <pre>{{ JSON.stringify(watchlistResult.data, null, 2) }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useMovieStore } from '@/stores/movie'
import { useWatchlistStore } from '@/stores/watchlist'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const authStore = useAuthStore()
const movieStore = useMovieStore()
const watchlistStore = useWatchlistStore()

const testing = ref({
  categories: false,
  movies: false,
  login: false,
  watchlist: false,
  toggle: false,
  add: false,
  remove: false
})

const categoriesResult = ref(null)
const moviesResult = ref(null)
const loginResult = ref(null)
const watchlistResult = ref(null)

const testCategories = async () => {
  testing.value.categories = true
  try {
    const result = await movieStore.fetchCategories()
    categoriesResult.value = result
    ElMessage.success('分类API测试完成')
  } catch (error) {
    ElMessage.error('分类API测试失败')
    console.error(error)
  } finally {
    testing.value.categories = false
  }
}

const testMovies = async () => {
  testing.value.movies = true
  try {
    const result = await movieStore.fetchMovies()
    moviesResult.value = result
    ElMessage.success('电影API测试完成')
  } catch (error) {
    ElMessage.error('电影API测试失败')
    console.error(error)
  } finally {
    testing.value.movies = false
  }
}

const testLogin = async () => {
  testing.value.login = true
  try {
    const result = await authStore.login({
      username: 'admin',
      password: 'admin123'
    })
    loginResult.value = result
    if (result.success) {
      ElMessage.success('登录测试成功')
    } else {
      ElMessage.error('登录测试失败')
    }
  } catch (error) {
    ElMessage.error('登录测试失败')
    console.error(error)
  } finally {
    testing.value.login = false
  }
}

// 想看列表测试函数
const testWatchlist = async () => {
  testing.value.watchlist = true
  try {
    const result = await watchlistStore.fetchWatchlist()
    watchlistResult.value = {
      title: '想看列表获取结果',
      data: result
    }
    console.log('Watchlist result:', result)
    ElMessage.success('想看列表获取完成')
  } catch (error: any) {
    watchlistResult.value = {
      title: '想看列表获取错误',
      data: {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data
      }
    }
    ElMessage.error('获取失败')
    console.error(error)
  } finally {
    testing.value.watchlist = false
  }
}

const testToggleWatchlist = async (movieId: number) => {
  testing.value.toggle = true
  try {
    const result = await watchlistStore.toggleWatchlist(movieId)
    watchlistResult.value = {
      title: `切换想看状态结果 (ID: ${movieId})`,
      data: result
    }
    console.log('Toggle result:', result)
    ElMessage.success(`成功: ${result.added ? '添加' : '移除'}`)
  } catch (error: any) {
    watchlistResult.value = {
      title: `切换想看状态错误 (ID: ${movieId})`,
      data: {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data
      }
    }
    ElMessage.error('切换失败')
    console.error(error)
  } finally {
    testing.value.toggle = false
  }
}

const testAddToWatchlist = async (movieId: number) => {
  testing.value.add = true
  try {
    const response = await axios.post(`http://localhost:8000/api/reviews/watchlist/toggle/${movieId}/`, {}, {
      headers: {
        'Authorization': `Bearer ${authStore.accessToken}`,
        'Content-Type': 'application/json'
      }
    })
    
    watchlistResult.value = {
      title: `直接API调用 - 添加到想看 (ID: ${movieId})`,
      data: response.data
    }
    
    console.log('Direct API add result:', response.data)
    ElMessage.success('API调用成功')
  } catch (error: any) {
    watchlistResult.value = {
      title: `直接API调用 - 添加到想看错误 (ID: ${movieId})`,
      data: {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data
      }
    }
    ElMessage.error('API调用失败')
    console.error(error)
  } finally {
    testing.value.add = false
  }
}

const testRemoveFromWatchlist = async (movieId: number) => {
  testing.value.remove = true
  try {
    // 首先获取想看列表找到对应的watchlist项
    await watchlistStore.fetchWatchlist()
    const item = watchlistStore.getWatchlistItem(movieId)
    
    if (item) {
      const result = await watchlistStore.removeFromWatchlist(item.id)
      watchlistResult.value = {
        title: `移除想看项目 (ID: ${movieId})`,
        data: { removed: result }
      }
      console.log('Remove result:', result)
      ElMessage.success('移除成功')
    } else {
      watchlistResult.value = {
        title: `未找到想看项目 (ID: ${movieId})`,
        data: { error: 'Item not found in watchlist' }
      }
      console.warn('Item not found in watchlist')
      ElMessage.warning('未找到对应的项目')
    }
  } catch (error: any) {
    watchlistResult.value = {
      title: `移除想看项目错误 (ID: ${movieId})`,
      data: {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data
      }
    }
    ElMessage.error('移除失败')
    console.error(error)
  } finally {
    testing.value.remove = false
  }
}
</script>

<style scoped>
.api-test {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.test-section {
  margin: 30px 0;
  padding: 20px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
}

.test-section h3 {
  margin-top: 0;
  color: #409eff;
}

.result {
  margin-top: 15px;
  padding: 15px;
  background-color: #f5f5f5;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
}

.result pre {
  margin: 0;
  font-size: 12px;
  white-space: pre-wrap;
}
</style>