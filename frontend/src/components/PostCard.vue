<script setup lang="ts">
import { computed } from 'vue'
import type { Post } from '@/services/posts'

const props = defineProps<{
  post: Post
}>()

const emit = defineEmits<{
  toggleFavorite: [id: number]
  click: [id: number]
}>()

const formattedDate = computed(() => {
  const date = new Date(props.post.created_at_reddit)
  return date.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
})

const truncatedContent = computed(() => {
  // El campo content puede no existir en el listado
  if (!props.post.content) return ''
  const maxLength = 150
  if (props.post.content.length <= maxLength) {
    return props.post.content
  }
  return props.post.content.substring(0, maxLength) + '...'
})

const handleToggleFavorite = (e: Event) => {
  e.stopPropagation()
  emit('toggleFavorite', props.post.id)
}

const handleClick = () => {
  emit('click', props.post.id)
}
</script>

<template>
  <div
    class="bg-dark-800 border border-dark-700 rounded-lg p-5 hover:border-primary-500 transition-colors cursor-pointer"
    @click="handleClick"
  >
    <!-- Header -->
    <div class="flex items-start justify-between mb-3">
      <div class="flex-1">
        <h3 class="text-lg font-semibold text-white mb-1 hover:text-primary-400 transition-colors">
          {{ post.title }}
        </h3>
        <div class="flex items-center gap-3 text-sm text-dark-400">
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
            {{ post.author }}
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
            r/{{ post.subreddit.name }}
          </span>
        </div>
      </div>

      <!-- Botón favorito -->
      <button
        @click="handleToggleFavorite"
        class="ml-3 p-2 rounded-lg transition-colors"
        :class="
          post.is_favorite
            ? 'text-accent hover:bg-accent/10'
            : 'text-dark-500 hover:bg-dark-700 hover:text-accent'
        "
        :title="post.is_favorite ? 'Quitar de favoritos' : 'Añadir a favoritos'"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-6 w-6"
          :fill="post.is_favorite ? 'currentColor' : 'none'"
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

    <!-- Contenido -->
    <p class="text-dark-300 text-sm mb-4 line-clamp-3">
      {{ truncatedContent }}
    </p>

    <!-- Footer -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4 text-sm">
        <!-- Score -->
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
          {{ post.score }}
        </span>

        <!-- Fecha -->
        <span class="text-dark-500">{{ formattedDate }}</span>
      </div>

      <!-- Badge de análisis -->
      <div v-if="post.summary" class="flex items-center gap-2">
        <span
          class="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-primary-500/10 text-primary-400 text-xs font-medium"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-3 w-3"
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
          Analizado
        </span>
      </div>
    </div>
  </div>
</template>
