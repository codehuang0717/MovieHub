<template>
  <div class="watchlist-test">
    <h2>想看列表功能测试</h2>
    
    <div class="test-section">
      <h3>当前想看列表</h3>
      <div v-if="watchlistStore.loading" class="loading">
        <el-skeleton :rows="3" animated />
      </div>
      <div v-else-if="watchlistStore.error" class="error">
        <el-alert :title="watchlistStore.error" type="error" show-icon />
      </div>
      <div v-else-if="watchlistStore.watchlist.length === 0" class="empty">
        <el-empty description="想看列表为空" />
      </div>
      <div v-else class="watchlist-items">
        <div v-for="item in watchlistStore.watchlist" :key="item.id" class="watchlist-item">
          <div class="movie-info">
            <strong>ID: {{ item.movie }}</strong>
            <span>状态: {{ item.status }}</span>
            <small>添加时间: {{ formatDate(item.created_at) }}</small>
          </div>
          <el-button size="small" @click="removeFromWatchlist(item.id)" type="danger">
            移除
          </el-button>
        </div>
      </div>
    </div>
    
    <div class="test-section">
      <h3>测试添加到想看列表</h3>
      <div class="test-controls">
        <el-input 
          v-model.number="testMovieId" 
          placeholder="输入电影ID" 
          type="number"
          style="width: 200px; margin-right: 10px;"
        />
        <el-button 
          @click="addToWatchlist" 
          :loading="adding" 
          type="primary"
        >
          添加到想看列表
        </el-button>
        <el-button 
          @click="toggleWatchlist" 
          :loading="toggling" 
          type="success"
        >
          切换想看状态
        </el-button>
        <el-button 
          @click="refreshWatchlist" 
          :loading="refreshing" 
        >
          刷新列表
        </el-button>
      </div>
      
      <div v-if="testResult" class="test-result">
        <el-alert :title="testResult.message" :type="testResult.type" show-icon :closable="false" />
      </div>
    </div>
    
    <div class="test-section">
      <h3>调试信息</h3>
      <div class="debug-info">
        <p><strong>总数量:</strong> {{ watchlistStore.watchlist.length }}</p>
        <p><strong>加载状态:</strong> {{ watchlistStore.loading }}</p>
        <p><strong>错误信息:</strong> {{ watchlistStore.error || '无' }}</p>
        <p><strong>测试电影ID:</strong> {{ testMovieId || '未设置' }}</p>
        <p><strong>是否在想看列表:</strong> {{ watchlistStore.isInWatchlist(testMovieId) ? '是' : '否' }}</p>
      </div>
    </div>
    
    <div class="test-section">
      <h3>常用测试ID</h3>
      <div class="test-ids">
        <el-button 
          v-for="id in testIds" 
          :key="id"
          size="small"
          @click="testMovieId = id"
          style="margin: 2px;"
        >
          {{ id }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useWatchlistStore } from '@/stores/watchlist'
import { ElMessage } from 'element-plus'

const watchlistStore = useWatchlistStore()

const testMovieId = ref(1)
const adding = ref(false)
const toggling = ref(false)
const refreshing = ref(false)
const testResult = ref<any>(null)

// 一些常见的测试ID
const testIds = [1, 2, 3, 11, 13, 100, 550, 597, 603, 629]

const addToWatchlist = async () => {
  if (!testMovieId.value) {
    ElMessage.warning('请输入电影ID')
    return
  }
  
  adding.value = true
  testResult.value = null
  
  try {
    const result = await watchlistStore.toggleWatchlist(testMovieId.value)
    testResult.value = {
      message: result.added ? '成功添加到想看列表' : '已从想看列表移除',
      type: result.added ? 'success' : 'warning'
    }
    ElMessage.success(testResult.value.message)
  } catch (error: any) {
    testResult.value = {
      message: `操作失败: ${error.message}`,
      type: 'error'
    }
    ElMessage.error(testResult.value.message)
  } finally {
    adding.value = false
  }
}

const toggleWatchlist = async () => {
  if (!testMovieId.value) {
    ElMessage.warning('请输入电影ID')
    return
  }
  
  toggling.value = true
  testResult.value = null
  
  try {
    const result = await watchlistStore.toggleWatchlist(testMovieId.value)
    testResult.value = {
      message: result.added ? '已添加到想看列表' : '已从想看列表移除',
      type: result.added ? 'success' : 'warning'
    }
    ElMessage.success(testResult.value.message)
  } catch (error: any) {
    testResult.value = {
      message: `切换失败: ${error.message}`,
      type: 'error'
    }
    ElMessage.error(testResult.value.message)
  } finally {
    toggling.value = false
  }
}

const removeFromWatchlist = async (watchlistId: number) => {
  try {
    await watchlistStore.removeFromWatchlist(watchlistId)
    ElMessage.success('已从想看列表移除')
  } catch (error: any) {
    ElMessage.error(`移除失败: ${error.message}`)
  }
}

const refreshWatchlist = async () => {
  refreshing.value = true
  try {
    await watchlistStore.fetchWatchlist()
    ElMessage.success('想看列表已刷新')
  } catch (error: any) {
    ElMessage.error(`刷新失败: ${error.message}`)
  } finally {
    refreshing.value = false
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 初始化
watchlistStore.fetchWatchlist()
</script>

<style scoped>
.watchlist-test {
  padding: 20px;
  max-width: 1000px;
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

.test-controls {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.test-result {
  margin-top: 15px;
}

.watchlist-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.watchlist-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
}

.movie-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.movie-info strong {
  font-size: 16px;
  color: #303133;
}

.movie-info span {
  font-size: 14px;
  color: #409eff;
}

.movie-info small {
  font-size: 12px;
  color: #909399;
}

.debug-info p {
  margin: 6px 0;
  font-family: monospace;
  font-size: 13px;
}

.test-ids {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.loading,
.error,
.empty {
  text-align: center;
  padding: 20px;
}

h2 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 40px;
}
</style>