<template>
  <AppLayout>
    <div class="categories-page">
      <!-- Content -->
      <main class="main-content">
        <div class="page-header">
          <h1>电影分类</h1>
          <p>探索不同类型的精彩电影</p>
        </div>

        <div class="categories-grid" v-loading="loading">
          <div 
            v-for="genre in tmdbGenres" 
            :key="genre.id" 
            class="category-card"
            @click="goToCategory(genre.id)"
          >
            <div class="category-icon">
              <el-icon size="48"><Film /></el-icon>
            </div>
            <h3>{{ genre.name }}</h3>
            <p>{{ genreDescriptions[genre.name] || '探索这个类型的电影' }}</p>
            <div class="category-stats">
              <el-tag type="primary" size="small">热门电影</el-tag>
            </div>
          </div>
        </div>
      </main>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Film } from '@element-plus/icons-vue'
import AppLayout from '@/layouts/AppLayout.vue'

const router = useRouter()
const loading = ref(false)

// TMDB标准分类列表
const tmdbGenres = ref([
  { id: 28, name: '动作' },
  { id: 12, name: '冒险' },
  { id: 16, name: '动画' },
  { id: 35, name: '喜剧' },
  { id: 80, name: '犯罪' },
  { id: 99, name: '纪录片' },
  { id: 18, name: '剧情' },
  { id: 10751, name: '家庭' },
  { id: 14, name: '奇幻' },
  { id: 36, name: '历史' },
  { id: 27, name: '恐怖' },
  { id: 10402, name: '音乐' },
  { id: 9648, name: '悬疑' },
  { id: 10749, name: '爱情' },
  { id: 878, name: '科幻' },
  { id: 10770, name: '电视电影' },
  { id: 53, name: '惊悚' },
  { id: 10752, name: '战争' },
  { id: 37, name: '西部' }
])

const genreDescriptions: Record<string, string> = {
  '动作': '刺激精彩的动作大片',
  '冒险': '充满冒险的奇幻旅程',
  '动画': '适合全家的精彩动画',
  '喜剧': '让人开怀大笑的轻松喜剧',
  '犯罪': '扣人心弦的犯罪故事',
  '纪录片': '真实世界的精彩记录',
  '剧情': '深刻感人的剧情佳作',
  '家庭': '温馨有趣的家庭影片',
  '奇幻': '充满想象力的奇幻世界',
  '历史': '重温历史的经典时刻',
  '恐怖': '惊险刺激的恐怖片',
  '音乐': '与音乐相关的精彩故事',
  '悬疑': '扑朔迷离的悬疑剧情',
  '爱情': '浪漫动人的爱情故事',
  '科幻': '探索未来的科幻世界',
  '电视电影': '精选电视电影佳作',
  '惊悚': '惊险刺激的惊悚片',
  '战争': '震撼人心的战争史诗',
  '西部': '经典的西部传奇故事'
}

const goToCategory = (genreId: number) => {
  router.push({ name: 'category-movies', params: { id: genreId }})
}

onMounted(() => {
  // 直接使用TMDB标准分类，无需从后端加载
  loading.value = false
})
</script>

<style scoped>
.categories-page {
  min-height: 100vh;
  background: #0d1117;
  color: #f0f6fc;
}

.main-content {
  margin-top: 64px;
  padding: 48px 24px;
  max-width: 1400px;
  margin-left: auto;
  margin-right: auto;
}

.page-header {
  text-align: center;
  margin-bottom: 48px;
}

.page-header h1 {
  font-size: 3rem;
  font-weight: 700;
  margin: 0 0 16px 0;
  background: linear-gradient(135deg, #58a6ff 0%, #79c0ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-header p {
  font-size: 1.2rem;
  color: #8b949e;
  margin: 0;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 32px;
}

.category-card {
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 16px;
  padding: 32px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.category-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #58a6ff 0%, #79c0ff 100%);
  transform: translateY(-100%);
  transition: transform 0.3s ease;
}

.category-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(88, 166, 255, 0.2);
  border-color: #58a6ff;
}

.category-card:hover::before {
  transform: translateY(0);
}

.category-icon {
  color: #58a6ff;
  margin-bottom: 16px;
  transition: all 0.3s ease;
}

.category-card:hover .category-icon {
  transform: scale(1.1) rotate(5deg);
}

.category-card h3 {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 0 12px 0;
  color: #f0f6fc;
}

.category-card p {
  font-size: 1rem;
  color: #8b949e;
  margin: 0 0 20px 0;
  line-height: 1.6;
}

.category-stats {
  margin-top: auto;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .categories-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 24px;
  }
}

@media (max-width: 768px) {
  .main-content {
    margin-top: 56px;
    padding: 32px 16px;
  }
  
  .page-header h1 {
    font-size: 2.5rem;
  }
  
  .page-header p {
    font-size: 1rem;
  }
  
  .categories-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
  }
  
  .category-card {
    padding: 24px;
  }
  
  .category-card h3 {
    font-size: 1.3rem;
  }
  
  .category-card p {
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .main-content {
    padding: 24px 12px;
  }
  
  .categories-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .category-card {
    padding: 20px;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
}
</style>