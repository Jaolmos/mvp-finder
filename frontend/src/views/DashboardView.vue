<script setup lang="ts">
import { onMounted, onUnmounted, computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import PostCard from '@/components/PostCard.vue'
import { usePostsStore } from '@/stores/posts'
import { scraperService, postService } from '@/services'
import type { OllamaStatus } from '@/services/scraper'
import type { PostStats } from '@/services/posts'

const router = useRouter()
const postsStore = usePostsStore()

// Estado de sincronización
const isSyncing = ref(false)
const syncMessage = ref('')
const syncError = ref('')

// Estado de análisis IA
const isAnalyzing = ref(false)
const analyzeMessage = ref('')
const analyzeError = ref('')
const ollamaStatus = ref<OllamaStatus | null>(null)

// Progreso del análisis con polling
const analyzeProgress = ref(0)
const analyzeTarget = ref(5)
const initialAnalyzedCount = ref(0)
let pollingInterval: ReturnType<typeof setInterval> | null = null

// Claves para persistir estado del análisis
const ANALYSIS_STATE_KEY = 'mvp_finder_analysis_state'

interface AnalysisState {
  inProgress: boolean
  initialCount: number
  target: number
  startedAt: number
}

// Estadísticas globales
const globalStats = ref<PostStats | null>(null)

// Guardar estado del análisis en localStorage
const saveAnalysisState = (state: AnalysisState | null) => {
  if (state) {
    localStorage.setItem(ANALYSIS_STATE_KEY, JSON.stringify(state))
  } else {
    localStorage.removeItem(ANALYSIS_STATE_KEY)
  }
}

// Cargar estado del análisis desde localStorage
const loadAnalysisState = (): AnalysisState | null => {
  const saved = localStorage.getItem(ANALYSIS_STATE_KEY)
  if (!saved) return null

  try {
    const state = JSON.parse(saved) as AnalysisState
    // Expirar después de 10 minutos
    if (Date.now() - state.startedAt > 10 * 60 * 1000) {
      localStorage.removeItem(ANALYSIS_STATE_KEY)
      return null
    }
    return state
  } catch {
    localStorage.removeItem(ANALYSIS_STATE_KEY)
    return null
  }
}

// Reanudar análisis si estaba en progreso
const resumeAnalysisIfNeeded = async () => {
  const state = loadAnalysisState()
  if (!state || !state.inProgress) return

  // Restaurar estado
  initialAnalyzedCount.value = state.initialCount
  analyzeTarget.value = state.target
  isAnalyzing.value = true

  // Calcular progreso actual
  const currentAnalyzed = globalStats.value?.analyzed_posts ?? 0
  analyzeProgress.value = currentAnalyzed - initialAnalyzedCount.value

  // Si ya terminó, limpiar
  if (analyzeProgress.value >= analyzeTarget.value) {
    analyzeMessage.value = `Análisis completado (${analyzeProgress.value} posts analizados)`
    isAnalyzing.value = false
    saveAnalysisState(null)
    setTimeout(() => {
      analyzeMessage.value = ''
    }, 5000)
    return
  }

  // Continuar polling
  analyzeMessage.value = `Analizando... (${analyzeProgress.value}/${analyzeTarget.value} completados)`
  startAnalysisPolling()
}

// Cargar posts, stats y estado de Ollama al montar
onMounted(async () => {
  await Promise.all([
    postsStore.fetchPosts({ page_size: 10 }),
    loadOllamaStatus(),
    loadStats()
  ])

  // Verificar si hay análisis en progreso
  await resumeAnalysisIfNeeded()
})

// Cargar estado de Ollama
const loadOllamaStatus = async () => {
  try {
    ollamaStatus.value = await scraperService.getOllamaStatus()
  } catch (error) {
    console.error('Error al cargar estado de Ollama:', error)
    ollamaStatus.value = null
  }
}

// Cargar estadísticas globales
const loadStats = async () => {
  try {
    globalStats.value = await postService.getStats()
  } catch (error) {
    console.error('Error al cargar stats:', error)
  }
}

// Estadísticas calculadas
const stats = computed(() => {
  return {
    total: globalStats.value?.total_posts ?? postsStore.pagination.count,
    analyzed: globalStats.value?.analyzed_posts ?? 0,
    favorites: globalStats.value?.favorites_count ?? postsStore.favoriteCount
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

const goToAnalyzedPosts = () => {
  router.push({ name: 'posts', query: { analyzed: 'true' } })
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

    // Esperar 3 segundos y recargar posts y stats
    setTimeout(async () => {
      await Promise.all([
        postsStore.fetchPosts({ page_size: 10 }),
        loadStats()
      ])
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

// Iniciar polling para seguir el progreso del análisis
const startAnalysisPolling = () => {
  const maxPolls = 20 // 5 minutos máximo (20 * 15 segundos)
  let pollCount = 0

  pollingInterval = setInterval(async () => {
    pollCount++

    try {
      const stats = await postService.getStats()
      const currentAnalyzed = stats.analyzed_posts
      analyzeProgress.value = currentAnalyzed - initialAnalyzedCount.value

      // Actualizar mensaje con progreso
      analyzeMessage.value = `Analizando... (${analyzeProgress.value}/${analyzeTarget.value} completados)`

      // Verificar si terminó o se alcanzó el timeout
      if (analyzeProgress.value >= analyzeTarget.value || pollCount >= maxPolls) {
        stopAnalysisPolling()
      }
    } catch (error) {
      console.error('Error al consultar progreso:', error)
    }
  }, 15000) // Cada 15 segundos
}

// Detener polling y finalizar análisis
const stopAnalysisPolling = async () => {
  if (pollingInterval) {
    clearInterval(pollingInterval)
    pollingInterval = null
  }

  // Limpiar estado persistido
  saveAnalysisState(null)

  // Recargar datos finales
  await Promise.all([
    postsStore.fetchPosts({ page_size: 10 }),
    loadStats()
  ])

  const finalProgress = analyzeProgress.value
  isAnalyzing.value = false
  analyzeMessage.value = `Análisis completado (${finalProgress} posts analizados)`

  // Limpiar mensaje después de 5 segundos
  setTimeout(() => {
    analyzeMessage.value = ''
    analyzeProgress.value = 0
  }, 5000)
}

// Analizar posts con Ollama
const handleAnalyze = async () => {
  // Verificar estado de Ollama
  if (!ollamaStatus.value?.ready) {
    analyzeError.value = 'Ollama no está listo. Verifica que el modelo esté descargado.'
    setTimeout(() => {
      analyzeError.value = ''
    }, 5000)
    return
  }

  try {
    isAnalyzing.value = true
    analyzeError.value = ''
    analyzeProgress.value = 0

    // Guardar conteo inicial para calcular progreso
    initialAnalyzedCount.value = globalStats.value?.analyzed_posts ?? 0
    analyzeMessage.value = 'Iniciando análisis... (esto tarda ~3-4 minutos)'

    // Persistir estado para poder retomar si el usuario navega
    saveAnalysisState({
      inProgress: true,
      initialCount: initialAnalyzedCount.value,
      target: analyzeTarget.value,
      startedAt: Date.now()
    })

    const response = await scraperService.analyzePosts({ limit: analyzeTarget.value })

    // Iniciar polling para seguir el progreso real
    analyzeMessage.value = `Analizando... (0/${analyzeTarget.value} completados)`
    startAnalysisPolling()

  } catch (error: any) {
    saveAnalysisState(null)
    isAnalyzing.value = false
    analyzeError.value = error.response?.data?.message || 'Error al analizar posts'

    // Limpiar error después de 5 segundos
    setTimeout(() => {
      analyzeError.value = ''
    }, 5000)
  }
}

// Cleanup al desmontar el componente
onUnmounted(() => {
  if (pollingInterval) {
    clearInterval(pollingInterval)
    pollingInterval = null
  }
})
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
          class="bg-dark-700 rounded-lg p-4 sm:p-6 border border-dark-600 hover:border-secondary-500 hover:bg-dark-600 transition-all cursor-pointer shadow-lg"
          @click="goToAnalyzedPosts"
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

      <!-- Mensajes de sincronización y análisis -->
      <div v-if="syncMessage || syncError || analyzeMessage || analyzeError" class="mb-6 space-y-3">
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
        <div
          v-if="analyzeMessage"
          class="bg-primary-500/20 border border-primary-500 text-primary-300 px-4 py-3 rounded-lg"
        >
          {{ analyzeMessage }}
        </div>
        <div
          v-if="analyzeError"
          class="bg-red-500/20 border border-red-500 text-red-300 px-4 py-3 rounded-lg"
        >
          {{ analyzeError }}
        </div>
      </div>

      <!-- Estado de Ollama -->
      <div v-if="ollamaStatus" class="mb-6">
        <div
          class="bg-dark-700 rounded-lg p-3 border flex items-center gap-3"
          :class="
            ollamaStatus.ready
              ? 'border-green-500/50 bg-green-500/10'
              : 'border-yellow-500/50 bg-yellow-500/10'
          "
        >
          <div
            class="w-3 h-3 rounded-full"
            :class="ollamaStatus.ready ? 'bg-green-500' : 'bg-yellow-500'"
          ></div>
          <div class="text-sm">
            <span class="font-medium" :class="ollamaStatus.ready ? 'text-green-300' : 'text-yellow-300'">
              Ollama:
            </span>
            <span class="text-dark-300 ml-2">
              {{
                ollamaStatus.ready
                  ? `Listo (${ollamaStatus.model})`
                  : ollamaStatus.ollama_available
                    ? 'Modelo no descargado'
                    : 'No disponible'
              }}
            </span>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
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

        <!-- Analizar Posts con IA -->
        <button
          @click="handleAnalyze"
          :disabled="isAnalyzing || !ollamaStatus?.ready"
          class="bg-dark-700 rounded-lg p-4 sm:p-6 border border-dark-600 hover:border-primary-500 hover:bg-dark-600 transition-all text-left group shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-lg font-semibold text-white mb-2 group-hover:text-primary-400 transition-colors">
                {{ isAnalyzing ? 'Analizando...' : 'Analizar Posts' }}
              </h3>
              <p class="text-dark-300 text-sm">
                Extraer insights con IA ({{ ollamaStatus?.ready ? '5 posts' : 'no disponible' }})
              </p>
            </div>
            <svg
              v-if="!isAnalyzing"
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
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
              />
            </svg>
            <div
              v-else
              class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"
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
