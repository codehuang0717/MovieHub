import './assets/main.css'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import 'element-plus/theme-chalk/dark/css-vars.css'
import { createI18n } from 'vue-i18n'
import en from './locales/en.json'
import zh from './locales/zh.json'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'

const i18n = createI18n({
  legacy: false,
  locale: localStorage.getItem('locale') || 'en',
  messages: {
    en,
    zh
  }
})

const app = createApp(App)

const pinia = createPinia()
app.use(pinia)
app.use(router)
app.use(i18n)

// Initialize authentication state
const authStore = useAuthStore(pinia)
authStore.initializeAuth()

app.mount('#app')
