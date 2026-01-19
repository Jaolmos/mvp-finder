<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import { usePostsStore } from '@/stores/posts'

const route = useRoute()
const router = useRouter()
const postsStore = usePostsStore()

const postId = computed(() => parseInt(route.params.id as string))

// Cargar post al montar
onMounted(async () => {
  if (postId.value) {
    await postsStore.fetchPost(postId.value)
  }
})

// Formatear fecha
const formattedDate = computed(() => {
  if (!postsStore.currentPost) return ''
  const date = new Date(postsStore.currentPost.created_at)
  return date.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
})

// Toggle favorito
const handleToggleFavorite = async () => {
  if (postsStore.currentPost) {
    await postsStore.toggleFavorite(postsStore.currentPost.id)
  }
}

// Volver atrás
const goBack = () => {
  router.push({ name: 'posts' })
}

// Abrir en Reddit
const openInReddit = () => {
  if (postsStore.currentPost) {
    window.open(postsStore.currentPost.url, '_blank')
  }
}
</script>

<template>
  <AppLayout>
    <div>
      <!-- Botón volver -->
      <button
        @click="goBack"
        class="mb-6 flex items-center gap-2 text-dark-400 hover:text-white transition-colors"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M10 19l-7-7m0 0l7-7m-7 7h18"
          />
        </svg>
        Volver a posts
      </button>

      <!-- Loading state -->
      <div v-if="postsStore.loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>

      <!-- Error state -->
      <div
        v-else-if="postsStore.error"
        class="bg-red-500/10 border border-red-500/50 rounded-lg p-6"
      >
        <h2 class="text-xl font-semibold text-red-400 mb-2">Error al cargar el post</h2>
        <p class="text-red-300">{{ postsStore.error }}</p>
      </div>

      <!-- Post detail -->
      <div v-else-if="postsStore.currentPost" class="space-y-6">
        <!-- Header card -->
        <div class="bg-dark-800 rounded-lg p-6 border border-dark-700">
          <div class="flex items-start justify-between mb-4">
            <div class="flex-1">
              <h1 class="text-3xl font-bold text-white mb-4">
                {{ postsStore.currentPost.title }}
              </h1>

              <div class="flex items-center gap-4 text-sm text-dark-400 flex-wrap">
                <span class="flex items-center gap-1">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-4 w-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                    />
                  </svg>
                  {{ postsStore.currentPost.author }}
                </span>

                <span class="flex items-center gap-1">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-4 w-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"
                    />
                  </svg>
                  r/{{ postsStore.currentPost.subreddit }}
                </span>

                <span class="flex items-center gap-1 text-secondary-400">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-4 w-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M5 15l7-7 7 7"
                    />
                  </svg>
                  {{ postsStore.currentPost.score }} puntos
                </span>

                <span class="flex items-center gap-1">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-4 w-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  {{ formattedDate }}
                </span>
              </div>
            </div>

            <!-- Botón favorito -->
            <button
              @click="handleToggleFavorite"
              class="ml-4 p-3 rounded-lg transition-colors"
              :class="
                postsStore.currentPost.is_favorite
                  ? 'bg-accent/10 text-accent hover:bg-accent/20'
                  : 'bg-dark-700 text-dark-400 hover:bg-dark-600 hover:text-accent'
              "
              :title="
                postsStore.currentPost.is_favorite ? 'Quitar de favoritos' : 'Añadir a favoritos'
              "
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-6 w-6"
                :fill="postsStore.currentPost.is_favorite ? 'currentColor' : 'none'"
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
            </button>
          </div>

          <!-- Botón abrir en Reddit -->
          <button
            @click="openInReddit"
            class="flex items-center gap-2 px-4 py-2 bg-secondary-500 hover:bg-secondary-600 text-white rounded-lg font-medium transition-colors"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
              />
            </svg>
            Ver en Reddit
          </button>
        </div>

        <!-- Content card -->
        <div class="bg-dark-800 rounded-lg p-6 border border-dark-700">
          <h2 class="text-xl font-semibold text-white mb-4">Contenido</h2>
          <div class="prose prose-invert max-w-none">
            <p class="text-dark-200 whitespace-pre-wrap leading-relaxed">
              {{ postsStore.currentPost.content }}
            </p>
          </div>
        </div>

        <!-- AI Analysis card (si existe) -->
        <div
          v-if="postsStore.currentPost.summary"
          class="bg-gradient-to-br from-primary-500/10 to-secondary-500/10 rounded-lg p-6 border border-primary-500/30"
        >
          <div class="flex items-center gap-2 mb-4">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6 text-primary-400"
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
            <h2 class="text-xl font-semibold text-white">Análisis IA</h2>
          </div>

          <div class="space-y-4">
            <div>
              <h3 class="text-sm font-medium text-primary-300 mb-1">Resumen</h3>
              <p class="text-white">{{ postsStore.currentPost.summary }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
