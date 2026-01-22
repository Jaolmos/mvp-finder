import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // Rutas públicas
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { requiresAuth: false, layout: 'auth' }
    },
    // Rutas protegidas
    {
      path: '/',
      name: 'dashboard',
      component: () => import('@/views/DashboardView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/posts',
      name: 'posts',
      component: () => import('@/views/PostsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/posts/:id',
      name: 'post-detail',
      component: () => import('@/views/PostDetailView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/topics',
      name: 'topics',
      component: () => import('@/views/TopicsView.vue'),
      meta: { requiresAuth: true }
    },
    // Redirección para rutas no encontradas
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ]
})

// Navigation guard para autenticación
router.beforeEach(async (to, _from) => {
  const authStore = useAuthStore()

  // Si la ruta requiere autenticación
  if (to.meta.requiresAuth) {
    // Verificar si hay token guardado
    if (!authStore.isAuthenticated) {
      // Redirigir a login
      return { name: 'login', query: { redirect: to.fullPath } }
    }

    // Si hay token pero no usuario, verificar autenticación
    if (!authStore.user) {
      const isValid = await authStore.checkAuth()
      if (!isValid) {
        return { name: 'login', query: { redirect: to.fullPath } }
      }
    }
  }

  // Si ya está autenticado y va a login, redirigir al dashboard
  if (to.name === 'login' && authStore.isAuthenticated) {
    return { name: 'dashboard' }
  }

  return true
})

export default router
