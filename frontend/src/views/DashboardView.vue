<script setup lang="ts">
import { onMounted, computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import PostCard from '@/components/PostCard.vue'
import { usePostsStore } from '@/stores/posts'
import { scraperService } from '@/services'

const router = useRouter()
const postsStore = usePostsStore()

// Estado de sincronización
const isSyncing = ref(false)
const syncMessage = ref('')
const syncError = ref('')

// Cargar posts al montar
onMounted(async () => {
  await postsStore.fetchPosts({ page_size: 10 })
})

// Estadísticas calculadas
const stats = computed(() => {
  const totalPosts = postsStore.pagination.count
  const analyzedPosts = postsStore.posts.filter((p) => p.summary).length
  const topics = new Set(postsStore.posts.map((p) => p.topic.name)).size

  return {
    total: totalPosts,
    analyzed: analyzedPosts,
    topics: topics
  }
})

// Posts recientes (máximo 5)
const recentPosts = computed(() => {
  return postsStore.posts.slice(0, 5)
})

// Navegar a todas las vistas
const goToPosts = () => {
  router.push({ name: 'posts' })
}

const goToTopics = () => {
  router.push({ name: 'topics' })
}

const handleToggleFavorite = async (id: number) => {
  await postsStore.toggleFavorite(id)
}

const handlePostClick = (id: number) => {
  router.push({ name: 'post-detail', params: { id } })
}

// Sincronizar posts de Product Hunt
const handleSync = async () => {
  try {
    isSyncing.value = true
    syncError.value = ''
    syncMessage.value = ''

    const response = await scraperService.syncPosts()
    syncMessage.value = response.message

    // Esperar 3 segundos y recargar posts
    setTimeout(async () => {
      await postsStore.fetchPosts({ page_size: 10 })
      syncMessage.value = 'Sincronización completada'

      // Limpiar mensaje después de 3 segundos
      setTimeout(() => {
        syncMessage.value = ''
      }, 3000)
    }, 3000)
  } catch (error: any) {
    syncError.value = error.response?.data?.message || 'Error al sincronizar posts'

    // Limpiar error después de 5 segundos
    setTimeout(() => {
      syncError.value = ''
    }, 5000)
  } finally {
    isSyncing.value = false
  }
}
</script>

<template>
  <AppLayout>
    <div>
      <div class="mb-6">
        <h1 class="text-xl md:text-2xl font-bold text-white">Dashboard</h1>
      </div>

      <!-- Stats cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <!-- Total Posts -->
        <div
          class="bg-dark-700 rounded-lg p-4 sm:p-6 border border-dark-600 hover:border-primary-500 hover:bg-dark-600 transition-all cursor-pointer shadow-lg"
          @click="goToPosts"
        >
          <div class="flex items-center justify-between mb-2">
            <div class="text-dark-300 text-sm font-medium">Total Posts</div>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-8 w-8 text-primary-500/50"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>
          <div class="text-3xl font-bold text-white">{{ stats.total }}</div>
        </div>

        <!-- Posts Analizados -->
        <div
          class="bg-dark-700 rounded-lg p-4 sm:p-6 border border-dark-600 hover:border-secondary-500 hover:bg-dark-600 transition-all shadow-lg"
        >
          <div class="flex items-center justify-between mb-2">
            <div class="text-dark-300 text-sm font-medium">Posts Analizados</div>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-8 w-8 text-secondary-500/50"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
              />
            </svg>
          </div>
          <div class="text-3xl font-bold text-white">{{ stats.analyzed }}</div>
        </div>

        <!-- Favoritos -->
        <div class="bg-dark-700 rounded-lg p-4 sm:p-6 border border-dark-600 hover:border-accent hover:bg-dark-600 transition-all shadow-lg">
          <div class="flex items-center justify-between mb-2">
            <div class="text-dark-300 text-sm font-medium">Favoritos</div>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-8 w-8 text-accent/50"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
              />
            </svg>
          </div>
          <div class="text-3xl font-bold text-accent">{{ postsStore.favoriteCount }}</div>
        </div>
      </div>

      <!-- Mensajes de sincronización -->
      <div v-if="syncMessage || syncError" class="mb-6">
        <div
          v-if="syncMessage"
          class="bg-secondary-500/20 border border-secondary-500 text-secondary-300 px-4 py-3 rounded-lg"
        >
          {{ syncMessage }}
        </div>
        <div
          v-if="syncError"
          class="bg-red-500/20 border border-red-500 text-red-300 px-4 py-3 rounded-lg"
        >
          {{ syncError }}
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <!-- Ir a Posts -->
        <button
          @click="goToPosts"
          class="bg-dark-700 rounded-lg p-4 sm:p-6 border border-dark-600 hover:border-primary-500 hover:bg-dark-600 transition-all text-left group shadow-lg"
        >
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-lg font-semibold text-white mb-2 group-hover:text-primary-400 transition-colors">
                Ver todos los posts
              </h3>
              <p class="text-dark-300 text-sm">Explorar, filtrar y analizar posts de Product Hunt</p>
            </div>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-8 w-8 text-primary-500/50 group-hover:text-primary-500 transition-colors"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M13 7l5 5m0 0l-5 5m5-5H6"
              />
            </svg>
          </div>
        </button>

        <!-- Ir a Topics -->
        <button
          @click="goToTopics"
          class="bg-dark-700 rounded-lg p-4 sm:p-6 border border-dark-600 hover:border-secondary-500 hover:bg-dark-600 transition-all text-left group shadow-lg"
        >
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-lg font-semibold text-white mb-2 group-hover:text-secondary-400 transition-colors">
                Gestionar topics
              </h3>
              <p class="text-dark-300 text-sm">
                Añadir, activar o desactivar fuentes de contenido
              </p>
            </div>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-8 w-8 text-secondary-500/50 group-hover:text-secondary-500 transition-colors"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M13 7l5 5m0 0l-5 5m5-5H6"
              />
            </svg>
          </div>
        </button>

        <!-- Sincronizar Posts -->
        <button
          @click="handleSync"
          :disabled="isSyncing"
          class="bg-dark-700 rounded-lg p-4 sm:p-6 border border-dark-600 hover:border-accent hover:bg-dark-600 transition-all text-left group shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-lg font-semibold text-white mb-2 group-hover:text-accent transition-colors">
                {{ isSyncing ? 'Sincronizando...' : 'Sincronizar Posts' }}
              </h3>
              <p class="text-dark-300 text-sm">
                Obtener nuevos productos de Product Hunt
              </p>
            </div>
            <svg
              v-if="!isSyncing"
              xmlns="http://www.w3.org/2000/svg"
              class="h-8 w-8 text-accent/50 group-hover:text-accent transition-colors"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
            <div
              v-else
              class="animate-spin rounded-full h-8 w-8 border-b-2 border-accent"
            ></div>
          </div>
        </button>
      </div>

      <!-- Posts Recientes -->
      <div class="bg-dark-800 rounded-lg p-4 sm:p-6 border border-dark-700">
        <div class="flex items-center justify-between mb-4 sm:mb-6">
          <h2 class="text-lg sm:text-xl font-semibold text-white">Posts Recientes</h2>
          <button
            @click="goToPosts"
            class="text-primary-400 hover:text-primary-300 text-sm font-medium transition-colors"
          >
            Ver todos →
          </button>
        </div>

        <!-- Loading -->
        <div v-if="postsStore.loading" class="flex justify-center items-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
        </div>

        <!-- Empty state -->
        <div v-else-if="recentPosts.length === 0" class="text-center py-12">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-16 w-16 mx-auto mb-4 text-dark-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
            />
          </svg>
          <h3 class="text-lg font-semibold text-white mb-2">No hay posts</h3>
          <p class="text-dark-400 mb-4">Configura tus topics y sincroniza para comenzar.</p>
          <button
            @click="goToTopics"
            class="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-colors"
          >
            Ir a Topics
          </button>
        </div>

        <!-- Posts list -->
        <div v-else class="space-y-4">
          <PostCard
            v-for="post in recentPosts"
            :key="post.id"
            :post="post"
            @toggle-favorite="handleToggleFavorite"
            @click="handlePostClick"
          />
        </div>
      </div>
    </div>
  </AppLayout>
</template>
