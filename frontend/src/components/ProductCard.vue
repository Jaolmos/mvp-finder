<script setup lang="ts">
import { computed } from 'vue'
import type { Product } from '@/services/products'

const props = defineProps<{
  product: Product
}>()

const emit = defineEmits<{
  toggleFavorite: [id: number]
  click: [id: number]
}>()

const formattedDate = computed(() => {
  const date = new Date(props.product.created_at_source)
  return date.toLocaleDateString('es-ES', {
    month: 'short',
    day: 'numeric'
  })
})

// Autor mostrado (Anónimo si es [REDACTED] o vacío)
const displayAuthor = computed(() => {
  const author = props.product.author
  return (!author || author === '[REDACTED]') ? 'Anónimo' : author
})

// Color del badge de score según valor
const scoreColorClass = computed(() => {
  const score = props.product.score
  if (score >= 100) return 'bg-emerald-500/15 text-emerald-400 ring-emerald-500/20'
  if (score >= 50) return 'bg-amber-500/15 text-amber-400 ring-amber-500/20'
  return 'bg-dark-600 text-dark-300 ring-dark-500/20'
})

const handleToggleFavorite = (e: Event) => {
  e.stopPropagation()
  emit('toggleFavorite', props.product.id)
}

const handleClick = () => {
  emit('click', props.product.id)
}
</script>

<template>
  <article
    class="group relative bg-dark-800/80 border border-dark-700/50 rounded-xl p-4 cursor-pointer transition-all duration-300 ease-out hover:bg-dark-800 hover:border-dark-600 hover:shadow-xl hover:shadow-primary-500/5 hover:-translate-y-0.5"
    @click="handleClick"
  >
    <!-- Gradient accent line -->
    <div
      class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-primary-500/50 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100"
    />

    <!-- Header: Title + Favorite -->
    <div class="flex items-start gap-3 mb-2">
      <div class="flex-1 min-w-0">
        <h3
          class="text-[15px] font-semibold text-dark-100 leading-snug tracking-tight transition-colors duration-200 group-hover:text-white line-clamp-2"
        >
          {{ product.title }}
        </h3>
      </div>

      <!-- Favorite button -->
      <button
        @click="handleToggleFavorite"
        class="shrink-0 p-1.5 -m-1.5 rounded-lg transition-all duration-200"
        :class="
          product.is_favorite
            ? 'text-accent-400 hover:text-accent-300 hover:bg-accent-500/10'
            : 'text-dark-500 opacity-0 group-hover:opacity-100 hover:text-accent-400 hover:bg-dark-700'
        "
        :title="product.is_favorite ? 'Quitar de favoritos' : 'Añadir a favoritos'"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5 transition-transform duration-200"
          :class="product.is_favorite ? 'scale-100' : 'scale-90 group-hover:scale-100'"
          :fill="product.is_favorite ? 'currentColor' : 'none'"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="2"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
          />
        </svg>
      </button>
    </div>

    <!-- Tagline -->
    <p
      v-if="product.tagline"
      class="text-sm text-dark-400 leading-relaxed mb-3 line-clamp-1"
    >
      {{ product.tagline }}
    </p>

    <!-- Meta row: Topic + Author -->
    <div class="flex items-center gap-2 mb-3 text-xs text-dark-400">
      <span
        class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-primary-500/10 text-primary-400 font-medium"
      >
        <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A2 2 0 013 12V7a4 4 0 014-4z" />
        </svg>
        {{ product.topic.name }}
      </span>
      <span class="text-dark-600">·</span>
      <span class="truncate">{{ displayAuthor }}</span>
    </div>

    <!-- Footer: Score + Date + Analyzed -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <!-- Score badge -->
        <span
          class="inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-semibold ring-1 ring-inset"
          :class="scoreColorClass"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 15l7-7 7 7" />
          </svg>
          {{ product.score }}
        </span>

        <!-- Date -->
        <span class="text-xs text-dark-500">{{ formattedDate }}</span>
      </div>

      <!-- Analyzed badge -->
      <div
        v-if="product.analyzed"
        class="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-secondary-500/10 text-secondary-400 text-xs font-medium"
      >
        <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
          />
        </svg>
        IA
      </div>
    </div>
  </article>
</template>
