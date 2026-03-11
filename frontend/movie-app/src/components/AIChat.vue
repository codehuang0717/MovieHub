<template>
  <div class="ai-chat-container">
    <transition name="slide-up">
      <div v-if="isOpen" class="chat-dialog">
        <div class="chat-header">
          <div class="chat-header-info">
            <el-icon class="ai-icon"><ChatDotRound /></el-icon>
            <span>AI Chat</span>
          </div>
          <div class="chat-header-actions">
            <el-button text circle size="small" @click="clearChatAction" :title="'Clear Chat'">
              <el-icon><Delete /></el-icon>
            </el-button>
            <el-button text circle size="small" @click="showSettings = true" :title="'Settings'">
              <el-icon><Setting /></el-icon>
            </el-button>
            <el-button text circle size="small" @click="closeChat" :title="'Close'">
              <el-icon><Close /></el-icon>
            </el-button>
          </div>
        </div>

        <div class="chat-messages" ref="messagesContainer">
          <div v-if="messages.length === 0" class="welcome-message">
            <div class="welcome-avatar">
              <el-icon><ChatDotRound /></el-icon>
            </div>
            <p class="welcome-title">AI Movie Assistant</p>
            <p class="welcome-desc">I can help you discover new movies based on your taste!</p>

            <div class="user-stats-panel" v-if="isLoggedIn && userStats">
              <div class="stats-header">
                <el-icon><User /></el-icon>
                <span>Your Data</span>
              </div>
              <div class="stats-row">
                <div class="stat-item">
                  <span class="stat-value">{{ userStats.collections_count }}</span>
                  <span class="stat-label">Collections</span>
                </div>
                <div class="stat-item">
                  <span class="stat-value">{{ userStats.ratings_count }}</span>
                  <span class="stat-label">Ratings</span>
                </div>
              </div>
              <div class="stats-genres" v-if="userStats.favorite_genres?.length">
                <el-icon><MagicStick /></el-icon>
                <span>Like {{ userStats.favorite_genres.join(' · ') }}</span>
              </div>
            </div>
            <div class="login-hint" v-else>
              <el-icon><Warning /></el-icon>
              <span>Please log in to see your stats.</span>
            </div>
          </div>

          <div
            v-for="(msg, index) in messages"
            :key="index"
            :class="['message', msg.role]"
          >
            <div class="message-bubble">
              <div class="message-avatar">
                <el-icon v-if="msg.role === 'assistant'"><ChatDotRound /></el-icon>
                <el-icon v-else><User /></el-icon>
              </div>
              <div class="message-content">
                <div v-if="msg.type === 'recommendations'" class="recommendations-grid">
                  <div
                    v-for="movie in msg.movies"
                    :key="movie.id"
                    class="recommendation-card"
                    @click="goToMovie(movie.id)"
                  >
                    <div class="rec-poster">
                      <img :src="movie.poster_path" :alt="movie.title" @error="handleImageError" />
                      <div class="rec-score">
                        <el-icon><Star /></el-icon>
                        {{ movie.vote_average?.toFixed(1) }}
                      </div>
                    </div>
                    <div class="rec-info">
                      <h4>{{ movie.title }}</h4>
                      <p>{{ movie.release_date?.split('-')[0] }}</p>
                    </div>
                  </div>
                </div>
                <div v-else class="message-text" v-html="formatMessage(msg.content)"></div>
              </div>
            </div>
          </div>

          <div v-if="loading" class="loading-bubble">
            <div class="loading-avatar">
              <el-icon><ChatDotRound /></el-icon>
            </div>
            <div class="loading-content">
              <div class="typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        </div>

        <div class="chat-input-area">
          <div class="quick-bubbles" v-if="messages.length < 3">
            <div
              v-for="prompt in quickPrompts"
              :key="prompt.label"
              class="quick-bubble"
              @click="useQuickPromptAction(prompt.label)"
            >
              <el-icon><component :is="prompt.icon" /></el-icon>
              <span>{{ prompt.label }}</span>
            </div>
          </div>
          <div class="input-row">
            <el-input
              v-model="userInput"
              :placeholder="'Ask me about movies...'"
              @keyup.enter="sendMessage"
              :disabled="loading"
              size="large"
            />
            <el-button type="primary" size="large" @click="sendMessage" :loading="loading">
              <el-icon><Position /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </transition>

    <div class="chat-toggle-button" @click="toggleChat">
      <el-badge v-if="unreadCount > 0" :value="unreadCount" class="badge">
        <el-icon v-if="!isOpen"><ChatDotRound /></el-icon>
        <el-icon v-else><Close /></el-icon>
      </el-badge>
      <el-icon v-else size="28"><ChatDotRound /></el-icon>
    </div>

    <el-dialog v-model="showSettings" :title="'AI Chat Settings'" width="400px" class="settings-dialog">
      <div class="settings-content">
        <div class="setting-group">
          <label>Recommendation Engine</label>
          <div class="engine-options">
              <div
                :class="['engine-option', { active: aiService === 'smart' }]"
                @click="aiService = 'smart'"
              >
                <el-icon><MagicStick /></el-icon>
                <span>Smart Recommend</span>
              </div>
            <div
              :class="['engine-option', { active: aiService === 'openai' }]"
              @click="aiService = 'openai'"
            >
              <el-icon><Cpu /></el-icon>
              <span>OpenAI GPT</span>
            </div>
          </div>
        </div>

        <div class="setting-group" v-if="aiService === 'openai'">
          <label>OpenAI API Key</label>
          <el-input
            v-model="apiKey"
            type="password"
            :placeholder="'Enter OpenAI API Key'"
            show-password
          />
          <div class="setting-hint">Your API key is stored locally and never sent to our servers.</div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showSettings = false">Cancel</el-button>
          <el-button type="primary" @click="saveSettings">Save</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  ChatDotRound, Close, Setting, Position, User, Star,
  Delete, MagicStick, Film, Compass, Warning, InfoFilled, Cpu
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const authStore = useAuthStore()
const STORAGE_KEY = 'ai-chat-messages'

const isOpen = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)
const showSettings = ref(false)
const unreadCount = ref(0)
const aiService = ref('smart')
const apiKey = ref('')
const userInput = ref('')
const loading = ref(false)

interface Movie {
  id: number
  title: string
  poster_path: string
  release_date: string
  vote_average: number
}

interface UserStats {
  collections_count: number
  ratings_count: number
  favorite_genres: string[]
  top_rated_movies: Movie[]
}

const userStats = ref<UserStats | null>(null)
const messages = ref<Array<{ role: string; content?: string; type?: string; movies?: Movie[] }>>([])

const quickPrompts = [
  { label: 'Sci-Fi Movies', icon: Compass, i18nKey: 'aiChat.promptSciFi' },
  { label: 'Comedy Movies', icon: MagicStick, i18nKey: 'aiChat.promptComedy' },
  { label: 'Suspense Movies', icon: Film, i18nKey: 'aiChat.promptSuspense' }
]

const useQuickPromptAction = (promptLabel: string) => {
  const promptItem = quickPrompts.find(p => p.label === promptLabel)
  if (promptItem) {
    userInput.value = promptItem.label
  } else {
    userInput.value = promptLabel
  }
  sendMessage()
}

const clearChatAction = () => {
  messages.value = []
  localStorage.removeItem(STORAGE_KEY)
  ElMessage.success('Chat cleared')
}

const isLoggedIn = computed(() => authStore.isAuthenticated)
const accessToken = computed(() => authStore.accessToken)

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' }
})

apiClient.interceptors.request.use(config => {
  if (accessToken.value) {
    config.headers.Authorization = `Bearer ${accessToken.value}`
  }
  return config
})

const goToMovie = (id: number) => {
  router.push({ name: 'movie-detail', params: { id } })
  closeChat()
}

const closeChat = () => {
  isOpen.value = false
}

const toggleChat = async () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    unreadCount.value = 0
    if (isLoggedIn.value) {
      await loadUserStats()
    }
  }
}

const useQuickPrompt = (promptLabel: string) => {
  const promptItem = quickPrompts.find(p => p.label === promptLabel)
  if (promptItem) {
    userInput.value = promptItem.label
  } else {
    userInput.value = promptLabel
  }
  sendMessage()
}

const clearChat = () => {
  messages.value = []
  localStorage.removeItem(STORAGE_KEY)
  ElMessage.success('Chat cleared')
}

const loadUserStats = async () => {
  try {
    const [collectionsRes, ratingsRes] = await Promise.all([
      apiClient.get('/reviews/collections/'),
      apiClient.get('/reviews/ratings/')
    ])

    const collections = collectionsRes.data || []
    const ratings = (ratingsRes.data?.results || ratingsRes.data || []).slice(0, 20)
    const genreCount: Record<string, number> = {}
    const highRatedMovies: Movie[] = []

    for (const rating of ratings) {
      const score = rating.score || 0
      if (score >= 4) {
        const movie = rating.movie || {}
        if (movie.genres) {
          for (const genre of movie.genres) {
            genreCount[genre.name] = (genreCount[genre.name] || 0) + 1
          }
        }
        highRatedMovies.push({
          id: movie.id || rating.movie_id || 0,
          title: movie.title || rating.movie_title || 'Unknown Movie',
          poster_path: movie.poster || movie.poster_path || '/placeholder-movie.svg',
          release_date: movie.release_date || rating.release_date || 'Unknown',
          vote_average: movie.average_rating || score || 0
        })
      }
    }

    const sortedGenres = Object.entries(genreCount)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 3)
      .map(([name]) => name)

    userStats.value = {
      collections_count: collections.length || 0,
      ratings_count: ratings.length || 0,
      favorite_genres: sortedGenres,
      top_rated_movies: highRatedMovies.slice(0, 5)
    }
  } catch (error) {
    console.error('Failed to load user stats:', error)
    userStats.value = null
  }
}

const sendMessage = async () => {
  if (!userInput.value.trim() || loading.value) return

  const userMessage = userInput.value.trim()
  userInput.value = ''

  messages.value.push({ role: 'user', content: userMessage, type: 'text' })
  saveMessages()
  loading.value = true
  scrollToBottom()

  try {
    if (aiService.value === 'smart') {
      await getSmartRecommendations(userMessage)
    } else {
      await getOpenAIRecommendations(userMessage)
    }
  } catch (error) {
    messages.value.push({
      role: 'assistant',
      content: 'Sorry, an error occurred. Please try again later.',
      type: 'text'
    })
  } finally {
    loading.value = false
    saveMessages()
    scrollToBottom()
  }
}

const saveMessages = () => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages.value))
  } catch (e) {}
}

const loadMessages = () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) messages.value = JSON.parse(saved)
  } catch (e) {
    messages.value = []
  }
}

const getSmartRecommendations = async (query: string) => {
  await new Promise(resolve => setTimeout(resolve, 1000))

  const lowerQuery = query.toLowerCase()
  let recommendations: Movie[] = []

  const genreKeywords: Record<string, string[]> = {
    'Sci-Fi': ['scifi', 'science', 'sci-fi', 'science fiction', '科幻'],
    'Romance': ['romance', 'love', '浪漫', '恋爱'],
    'Comedy': ['comedy', 'funny', '搞笑', '幽默'],
    'Thriller': ['thriller', 'suspense', '惊悚', '推理'],
    'Action': ['action', '打斗'],
    'Animation': ['animation', 'anime', '动漫', '卡通'],
    'Horror': ['horror', 'scary', '害怕'],
    'War': ['war', 'military', '军事'],
    'Documentary': ['documentary', '纪录']
  }

  let matchedGenre = ''
  for (const [genre, keywords] of Object.entries(genreKeywords)) {
    if (keywords.some(kw => lowerQuery.includes(kw))) {
      matchedGenre = genre
      break
    }
  }

  const movieDatabase: Record<string, Movie[]> = {
    'Sci-Fi': [
      { id: 157336, title: 'Interstellar', poster_path: 'https://image.tmdb.org/t/p/w200/gEU2QniL6E8ahG0Sm62X719qVJh.jpg', release_date: '2014-11-05', vote_average: 8.6 },
      { id: 155, title: 'Inception', poster_path: 'https://image.tmdb.org/t/p/w200/9gk7admalRg2G2d5p4nMDa3ysjA.jpg', release_date: '2010-07-14', vote_average: 8.8 },
      { id: 27205, title: 'The Dark Knight Rises', poster_path: 'https://image.tmdb.org/t/p/w200/9WJE5xv7k6K8z2Y1t0K1K5G5Z8k.jpg', release_date: '2012-07-18', vote_average: 8.4 }
    ],
    'Romance': [
      { id: 11216, title: 'Titanic', poster_path: 'https://image.tmdb.org/t/p/w200/9xjZS2rlVxm8SFx8kPC3aO9mnrz.jpg', release_date: '1997-12-18', vote_average: 7.9 },
      { id: 49026, title: 'Before Sunrise', poster_path: 'https://image.tmdb.org/t/p/w200/gC1n7kvLSkpuFs6hZhYfbY7rYvq.jpg', release_date: '1995-04-20', vote_average: 8.0 },
      { id: 452876, title: 'A Bread of Love', poster_path: 'https://image.tmdb.org/t/p/w200/w2PMyoyLU22YvrGK3smVM9fW1jj.jpg', release_date: '2021-01-29', vote_average: 7.9 }
    ],
    'Comedy': [
      { id: 497572, title: 'Restart Life', poster_path: 'https://image.tmdb.org/t/p/w200/h5UzYZquMwO9FVn15R2eK2itmHu.jpg', release_date: '2022-11-04', vote_average: 8.5 },
      { id: 429617, title: 'Spider-Man: Into the Spider-Verse', poster_path: 'https://image.tmdb.org/t/p/w200/3IlKqUFCh6cCDM2WN4Ug7UG0FHs.jpg', release_date: '2018-12-07', vote_average: 8.4 },
      { id: 438631, title: 'Detective Chinatown', poster_path: 'https://image.tmdb.org/t/p/w200/iqZ4IKW7lU9zLqCMc9WBB1lZQUZ.jpg', release_date: '2015-12-31', vote_average: 7.5 }
    ],
    'Thriller': [
      { id: 278, title: 'The Shawshank Redemption', poster_path: 'https://image.tmdb.org/t/p/w200/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg', release_date: '1994-09-23', vote_average: 9.3 },
      { id: 550988, title: 'The Invisible Guest', poster_path: 'https://image.tmdb.org/t/p/w200/6hgI4j9o3k7v7bT5q8j4T6bX8k0.jpg', release_date: '2016-09-06', vote_average: 8.1 },
      { id: 3594, title: 'Triangle', poster_path: 'https://image.tmdb.org/t/p/w200/g0LDPJdcE6iCM9tG2f5Kbz0CNyN.jpg', release_date: '2009-10-16', vote_average: 7.5 }
    ],
    'Action': [
      { id: 27205, title: 'The Dark Knight', poster_path: 'https://image.tmdb.org/t/p/w200/9WJE5xv7k6K8z2Y1t0K1K5G5Z8k.jpg', release_date: '2008-07-16', vote_average: 9.0 },
      { id: 238, title: 'The Godfather', poster_path: 'https://image.tmdb.org/t/p/w200/3TlQYNuCU8g9U6XvX3pMlVCT5vZ.jpg', release_date: '1972-03-14', vote_average: 8.7 },
      { id: 299534, title: 'Captain America: The Winter Soldier', poster_path: 'https://image.tmdb.org/t/p/w200/tV8dYDW5b1K6zhFfLc3CvJkd1qU.jpg', release_date: '2014-03-20', vote_average: 7.7 }
    ],
    'Animation': [
      { id: 372058, title: 'Your Name', poster_path: 'https://image.tmdb.org/t/p/w200/q719jXXEzOoYaps6babgKnONONX.jpg', release_date: '2016-08-26', vote_average: 8.5 },
      { id: 4935, title: "Howl's Moving Castle", poster_path: 'https://image.tmdb.org/t/p/w200/v9yGJquH7ZXckXP4VPPV77XxX1G.jpg', release_date: '2004-11-20', vote_average: 8.2 },
      { id: 63844, title: 'Inside Out', poster_path: 'https://image.tmdb.org/t/p/w200/oDB4HBK89cw8U1jQXvP2EIVn6ZU.jpg', release_date: '2015-06-09', vote_average: 8.1 }
    ],
    'Horror': [
      { id: 439503, title: 'Hereditary', poster_path: 'https://image.tmdb.org/t/p/w200/tj1hSyu3LLM5X0GftBEtD2M2X3N.jpg', release_date: '2018-06-07', vote_average: 7.3 },
      { id: 546554, title: 'Gonjiam: Haunted Asylum', poster_path: 'https://image.tmdb.org/t/p/w200/pO4M7pTcv2f2X7E6a3wB4k6u3x7.jpg', release_date: '2018-03-28', vote_average: 6.9 },
      { id: 487310, title: 'The Nun', poster_path: 'https://image.tmdb.org/t/p/w200/5X3Cg2Z1Y1Y1Y6Y1Y1Y1Y1Y1Y1.jpg', release_date: '2018-09-06', vote_average: 5.9 }
    ],
    'default': [
      { id: 27205, title: 'The Dark Knight', poster_path: 'https://image.tmdb.org/t/p/w200/9WJE5xv7k6K8z2Y1t0K1K5G5Z8k.jpg', release_date: '2008-07-16', vote_average: 9.0 },
      { id: 238, title: 'The Godfather', poster_path: 'https://image.tmdb.org/t/p/w200/3TlQYNuCU8g9U6XvX3pMlVCT5vZ.jpg', release_date: '1972-03-14', vote_average: 8.7 },
      { id: 680, title: 'Fight Club', poster_path: 'https://image.tmdb.org/t/p/w200/p8F2G3B4V6F8E7D6S5A4B3C2D1.jpg', release_date: '1999-10-15', vote_average: 8.4 }
    ]
  }

  recommendations = (matchedGenre && movieDatabase[matchedGenre]) ? movieDatabase[matchedGenre] : movieDatabase['default']

  let intro = ''
  if (userStats.value?.favorite_genres?.length) {
    intro = `Since you like ${userStats.value.favorite_genres.join(', ')}, I recommend ${matchedGenre || 'these'} movies:`
  } else if (userStats.value?.ratings_count) {
    intro = 'Based on your viewing history, I recommend:'
  } else {
    intro = 'Here are some popular movies I recommend:'
  }

  messages.value.push({ role: 'assistant', content: intro, type: 'text' })
  messages.value.push({ role: 'assistant', type: 'recommendations', movies: recommendations })

  const followUp = userStats.value?.favorite_genres?.length
    ? `Do you like ${userStats.value.favorite_genres.join(' or ')}? What other type would you like?`
    : 'What other type would you like? Tell me!'

  messages.value.push({ role: 'assistant', content: followUp, type: 'text' })
}

const getOpenAIRecommendations = async (query: string) => {
  if (!apiKey.value) {
    messages.value.push({
      role: 'assistant',
      content: 'Please configure API Key in settings first. Click the settings button in the top right corner.',
      type: 'text'
    })
    return
  }

  const favoriteGenres = userStats.value?.favorite_genres?.join(', ') || 'Unknown'
  const highRatedMovies = userStats.value?.top_rated_movies?.map((m: Movie) => m.title).join(', ') || 'None'

  const systemPrompt = `You are a movie recommendation expert.

User Profile:
- Collections: ${userStats.value?.collections_count || 0} movies
- Ratings: ${userStats.value?.ratings_count || 0} movies
- Favorite Genres: ${favoriteGenres}
- Top Rated Movies: ${highRatedMovies}

Task: Based on user query and profile, recommend 3-5 relevant movies.

Important Rules:
1. Must provide accurate TMDB movie ID (6+ digits)
2. Recommended movies must be real
3. Must be relevant to user query and preferences

Output Format:
Brief recommendation reason (1 sentence)
---
ID: 157336, Interstellar
ID: 155, Inception
ID: 27205, The Dark Knight Rises`

  try {
    const response = await axios.post('https://api.openai.com/v1/chat/completions', {
      model: 'gpt-3.5-turbo',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: query }
      ],
      max_tokens: 800,
      temperature: 0.7
    }, {
      headers: {
        'Authorization': `Bearer ${apiKey.value}`,
        'Content-Type': 'application/json'
      }
    })

    const aiResponse = response.data.choices[0].message.content
    console.log('AI Response:', aiResponse)

    const movieItems: Array<{ id?: string; title: string }> = []

    const idPattern = /ID[:\s]*(\d+)/g
    let match
    while ((match = idPattern.exec(aiResponse)) !== null) {
      movieItems.push({ id: match[1], title: '' })
    }

    const lines = aiResponse.split('\n')
    for (const line of lines) {
      const cleanLine = line.trim()
      if (!cleanLine) continue

      const titleMatch = cleanLine.replace(/ID[:\s]*\d+[,，]?\s*/, '').trim()
      if (titleMatch && titleMatch.length > 1 && titleMatch.length < 50) {
        const existing = movieItems.find(m => m.title === titleMatch)
        if (!existing) {
          movieItems.push({
            id: undefined,
            title: titleMatch.replace(/^[^\w\u4e00-\u9fff]+/, '').trim()
          })
        }
      }
    }

    console.log('Parsed movie items:', movieItems)

    const tmdbApiKey = '2d89ddec4f8acd4c9f2036ea7321f326'
    const validMovies: Movie[] = []
    const processedTitles = new Set<string>()

    for (const item of movieItems) {
      if (validMovies.length >= 3) break

      let movieData: Movie | null = null

      let targetId: string | undefined = item.id

      if (!targetId && item.title) {
        const lowerTitle = item.title.toLowerCase()
        for (const [key, id] of Object.entries(knownMovies)) {
          if (lowerTitle.includes(key.toLowerCase()) || key.toLowerCase().includes(lowerTitle)) {
            targetId = String(id)
            console.log(`Matched known movie: ${item.title} -> ID ${targetId}`)
            break
          }
        }
      }

      if (targetId && targetId.length >= 5) {
        try {
          const res = await axios.get(`https://api.themoviedb.org/3/movie/${targetId}`, {
            params: { api_key: tmdbApiKey, language: 'en-US' }
          })
          if (res.data && res.data.id) {
            movieData = {
              id: res.data.id,
              title: res.data.title,
              poster_path: res.data.poster_path
                ? `https://image.tmdb.org/t/p/w200${res.data.poster_path}`
                : '/placeholder-movie.svg',
              release_date: res.data.release_date || 'Unknown',
              vote_average: res.data.vote_average || 0
            }
            console.log(`Found by ID ${targetId}:`, movieData.title)
          }
        } catch (e) {
          console.warn(`Failed to fetch movie ${targetId}`)
        }
      }

      if (!movieData && item.title && !processedTitles.has(item.title)) {
        try {
          const cleanTitle = item.title
            .replace(/[，。！？、]/g, ' ')
            .replace(/\s+/g, ' ')
            .trim()
            .split(' ')[0]

          if (cleanTitle.length >= 2) {
          const searchRes = await axios.get(`https://api.themoviedb.org/3/search/movie`, {
            params: { api_key: tmdbApiKey, query: cleanTitle, language: 'en-US', page: 1 }
          })

            if (searchRes.data.results && searchRes.data.results.length > 0) {
              const best = searchRes.data.results.find((m: any) => {
                const mTitle = m.title.toLowerCase()
                const queryTitle = cleanTitle.toLowerCase()
                return mTitle.includes(queryTitle) || queryTitle.includes(mTitle)
              }) || searchRes.data.results[0]

              if (best && best.id) {
                movieData = {
                  id: best.id,
                  title: best.title,
                  poster_path: best.poster_path
                    ? `https://image.tmdb.org/t/p/w200${best.poster_path}`
                    : '/placeholder-movie.svg',
                  release_date: best.release_date || 'Unknown',
                  vote_average: best.vote_average || 0
                }
                processedTitles.add(cleanTitle)
                console.log(`Found by search "${cleanTitle}":`, movieData.title)
              }
            }
          }
        } catch (e) {
          console.warn(`Failed to search movie "${item.title}"`)
        }
      }

      if (movieData && !validMovies.find(m => m.id === movieData!.id)) {
        validMovies.push(movieData)
      }
    }

    console.log('Final valid movies:', validMovies)

    if (validMovies.length > 0) {
      const introText = aiResponse.split('---')[0].split('\n').slice(0, 2).join('\n').trim()
      messages.value.push({ role: 'assistant', content: introText || 'Here are some movies I recommend:', type: 'text' })
      messages.value.push({ role: 'assistant', type: 'recommendations', movies: validMovies })
      messages.value.push({ role: 'assistant', content: 'Click on a movie to see details. What other type would you like?', type: 'text' })
      return
    }

    messages.value.push({ role: 'assistant', content: aiResponse, type: 'text' })
  } catch (error: any) {
    if (error.response?.status === 401) {
      messages.value.push({ role: 'assistant', content: 'API Key is invalid. Please check your settings.', type: 'text' })
    } else if (error.response?.status === 429) {
      messages.value.push({ role: 'assistant', content: 'Too many requests. Please try again later.', type: 'text' })
    } else {
      console.error('OpenAI API error:', error)
      messages.value.push({ role: 'assistant', content: 'AI service is temporarily unavailable. Please try again later.', type: 'text' })
    }
  }
}

const formatMessage = (content: string) => {
  if (!content) return ''
  return content.replace(/\n/g, '<br>')
}

const formatDate = (dateString: string) => {
  if (!dateString || dateString === 'Unknown') return 'Unknown'
  try {
    return new Date(dateString).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
  } catch { return dateString }
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = '/placeholder-movie.svg'
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const saveSettings = () => {
  localStorage.setItem('ai-chat-service', aiService.value)
  localStorage.setItem('ai-chat-api-key', apiKey.value)
  showSettings.value = false
  ElMessage.success('Settings saved')
}

onMounted(async () => {
  loadMessages()
  const savedService = localStorage.getItem('ai-chat-service')
  const savedKey = localStorage.getItem('ai-chat-api-key')
  if (savedService) aiService.value = savedService
  if (savedKey) apiKey.value = savedKey
})
</script>

<style scoped>
.ai-chat-container { position: fixed; bottom: 20px; right: 20px; z-index: 9999; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }

.chat-toggle-button {
  width: 56px; height: 56px; border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white; display: flex; align-items: center; justify-content: center;
  cursor: pointer; box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.chat-toggle-button:hover { transform: scale(1.08); box-shadow: 0 6px 25px rgba(102, 126, 234, 0.5); }
.badge :deep(.el-badge__content) { background: #f56c6c; }

.chat-dialog {
  position: absolute; bottom: 76px; right: 0; width: 480px; height: 680px;
  background: #ffffff; border-radius: 20px; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  display: flex; flex-direction: column; overflow: hidden;
}

.chat-header {
  padding: 18px 24px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex; justify-content: space-between; align-items: center;
}
.chat-header-info { display: flex; align-items: center; gap: 12px; color: white; font-weight: 600; font-size: 17px; }
.ai-icon { font-size: 24px; }
.chat-header-actions { display: flex; gap: 6px; }
.chat-header-actions .el-button { color: rgba(255,255,255,0.85); }
.chat-header-actions .el-button:hover { color: white; background: rgba(255,255,255,0.15); }

.chat-messages {
  flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; gap: 20px;
  background: #f8f9fc;
}

.welcome-message { text-align: center; padding: 32px 24px; background: linear-gradient(180deg, #fff 0%, #f8f9fc 100%); }
.welcome-avatar {
  width: 72px; height: 72px; border-radius: 22px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white; display: flex; align-items: center; justify-content: center;
  margin: 0 auto 20px; font-size: 32px; box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}
.welcome-title { margin: 0 0 8px; font-size: 22px; font-weight: 700; color: #1a1a2e; }
.welcome-desc { margin: 0 0 24px; font-size: 15px; color: #6b7280; }

.user-stats-panel {
  background: white; border-radius: 18px; padding: 22px; text-align: left;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06); border: 1px solid #e5e7eb;
}
.stats-header { display: flex; align-items: center; gap: 8px; font-size: 14px; color: #6b7280; margin-bottom: 16px; }
.stats-row { display: flex; gap: 32px; margin-bottom: 14px; }
.stat-item { display: flex; flex-direction: column; }
.stat-value { font-size: 28px; font-weight: 700; color: #667eea; }
.stat-label { font-size: 13px; color: #9ca3af; }
.stats-genres { display: flex; align-items: center; gap: 8px; font-size: 14px; color: #6b7280; }
.stats-genres .el-icon { color: #f59e0b; }

.login-hint {
  display: flex; align-items: center; justify-content: center; gap: 10px;
  padding: 14px 20px; background: #fef3c7; border-radius: 14px; color: #92400e; font-size: 14px;
}

.message { display: flex; }
.message.user { flex-direction: row-reverse; }

.message-bubble {
  display: flex; align-items: flex-start; gap: 12px; max-width: 88%;
}

.message.assistant .message-bubble { align-items: flex-start; }
.message.user .message-bubble { flex-direction: row-reverse; align-items: flex-start; }

.message-avatar {
  width: 40px; height: 40px; border-radius: 14px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.message.assistant .message-avatar { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
.message.user .message-avatar { background: #e5e7eb; color: #6b7280; }

.message-content {
  background: #f0f0f5; border-radius: 18px; padding: 14px 18px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #e0e0e8;
  color: #1a1a2e;
}
.message.user .message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white; border: none;
}

.message-text { font-size: 15px; line-height: 1.6; }

.recommendations-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 10px; }

.recommendation-card {
  background: #f8f9fc; border-radius: 14px; overflow: hidden; cursor: pointer;
  transition: all 0.2s ease; border: 1px solid #e5e7eb;
}
.recommendation-card:hover { transform: translateY(-4px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); }

.rec-poster { position: relative; aspect-ratio: 2/3; overflow: hidden; }
.rec-poster img { width: 100%; height: 100%; object-fit: cover; }
.rec-score {
  position: absolute; top: 8px; right: 8px;
  background: rgba(0,0,0,0.8); color: #fbbf24;
  padding: 4px 8px; border-radius: 8px; font-size: 12px;
  display: flex; align-items: center; gap: 4px;
}

.rec-info { padding: 12px; }
.rec-info h4 { margin: 0 0 6px; font-size: 13px; font-weight: 600; color: #1f2937; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.rec-info p { margin: 0; font-size: 12px; color: #9ca3af; }

.loading-bubble { display: flex; align-items: flex-start; gap: 10px; }
.loading-avatar {
  width: 36px; height: 36px; border-radius: 12px;
  background: linear-gradient(135deg, #667eea, #764ba2); color: white;
  display: flex; align-items: center; justify-content: center;
}
.loading-content { background: #f0f0f5; border-radius: 16px; padding: 14px 18px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #e0e0e8; color: #1a1a2e; }

.typing-indicator { display: flex; gap: 4px; }
.typing-indicator span {
  width: 8px; height: 8px; border-radius: 50%; background: #667eea;
  animation: bounce 1.4s infinite ease-in-out both;
}
.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }

.chat-input-area { padding: 20px; background: white; border-top: 1px solid #f3f4f6; }

.quick-bubbles { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 14px; }

.quick-bubble {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 18px; background: #f3f4f6; border-radius: 22px;
  font-size: 14px; color: #4b5563; cursor: pointer;
  transition: all 0.2s ease; border: 1px solid #e5e7eb;
}
.quick-bubble:hover { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-color: transparent; }
.quick-bubble .el-icon { font-size: 15px; }

.input-row { display: flex; gap: 12px; }
.input-row .el-input { --el-input-border-radius: 14px; }
.input-row .el-button { --el-button-border-radius: 14px; padding: 14px 24px; }

.settings-content { padding: 8px 0; }
.setting-group { margin-bottom: 28px; }
.setting-group label { display: block; margin-bottom: 12px; font-weight: 600; color: #374151; font-size: 15px; }

.engine-options { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.engine-option {
  padding: 20px; border-radius: 14px; border: 2px solid #e5e7eb;
  cursor: pointer; transition: all 0.2s ease; text-align: center;
}
.engine-option:hover { border-color: #667eea; background: #f5f3ff; }
.engine-option.active { border-color: #667eea; background: linear-gradient(135deg, rgba(102,126,234,0.1) 0%, rgba(118,75,162,0.1) 100%); }
.engine-option .el-icon { font-size: 28px; color: #667eea; margin-bottom: 10px; display: block; }
.engine-name { display: block; font-weight: 600; color: #1f2937; font-size: 15px; margin-bottom: 6px; }
.engine-desc { display: block; font-size: 12px; color: #9ca3af; }

.setting-tip { display: flex; align-items: center; gap: 8px; margin-top: 10px; font-size: 13px; color: #6b7280; }

.slide-up-enter-active, .slide-up-leave-active { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.slide-up-enter-from, .slide-up-leave-to { opacity: 0; transform: translateY(20px) scale(0.95); }

@media (max-width: 520px) {
  .chat-dialog { width: calc(100vw - 24px); right: -8px; height: calc(100vh - 140px); min-height: 550px; }
  .recommendations-grid { grid-template-columns: repeat(2, 1fr); }
  .welcome-message { padding: 24px 16px; }
  .user-stats-panel { padding: 16px; }
  .stats-row { gap: 20px; }
  .stat-value { font-size: 24px; }
}
</style>
