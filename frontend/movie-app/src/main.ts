import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
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

// Register all Element Plus icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

const pinia = createPinia()
app.use(pinia)
app.use(router)
app.use(i18n)
app.use(ElementPlus, {
  size: 'default',
  zIndex: 3000,
})

// Initialize authentication state
const authStore = useAuthStore(pinia)
authStore.initializeAuth()

app.mount('#app')
