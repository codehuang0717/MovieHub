import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
    },
    {
      path: '/movies',
      name: 'movies',
      component: () => import('../views/MoviesView.vue'),
    },
    {
      path: '/movies/:id',
      name: 'movie-detail',
      component: () => import('../views/MovieDetailView.vue'),
    },
    {
      path: '/categories',
      name: 'categories',
      component: () => import('../views/CategoriesView.vue'),
    },
    {
      path: '/categories/:id',
      name: 'category-movies',
      component: () => import('../views/CategoryMoviesView.vue'),
    },
    {
      path: '/search',
      name: 'search',
      component: () => import('../views/SearchView.vue'),
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
    },
    {
      path: '/collections',
      name: 'collections',
      component: () => import('../views/CollectionsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/collections/:id',
      name: 'collection-detail',
      component: () => import('../views/CollectionDetailView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/watchlist',
      name: 'watchlist',
      component: () => import('../views/WatchlistView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/api-test',
      name: 'api-test',
      component: () => import('../views/ApiTestView.vue'),
    },
    {
      path: '/avatar-test',
      name: 'avatar-test',
      component: () => import('../views/AvatarTestView.vue'),
    },
    {
      path: '/avatar-sync-test',
      name: 'avatar-sync-test',
      component: () => import('../views/AvatarSyncTestView.vue'),
    },
    {
      path: '/watchlist-test',
      name: 'watchlist-test',
      component: () => import('../views/WatchlistTestView.vue'),
    },
  ],
})

// Navigation guard for protected routes
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (to.name === 'login' && authStore.isAuthenticated) {
    next({ name: 'home' })
  } else {
    next()
  }
})

// Scroll behavior for routes
router.afterEach(() => {
  // Scroll to top when navigating to a new route
  window.scrollTo(0, 0)
})

export default router
