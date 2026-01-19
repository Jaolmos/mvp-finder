<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import PostCard from '@/components/PostCard.vue'
import { usePostsStore } from '@/stores/posts'

const router = useRouter()
const postsStore = usePostsStore()

// Filtros locales
const searchQuery = ref('')
const selectedSubreddit = ref('')
const showOnlyFavorites = ref(false)
const showOnlyAnalyzed = ref(false)

// Lista única de subreddits disponibles
const availableSubreddits = computed(() => {
  const subreddits = new Set<string>()
  postsStore.posts.forEach((post) => {
    subreddits.add(post.subreddit.name)
  })
  return Array.from(subreddits).sort()
})

// Cargar posts al montar el componente
onMounted(async () => {
  await postsStore.fetchPosts()
})

// Aplicar filtros
const applyFilters = async () => {
  await postsStore.fetchPosts({
    search: searchQuery.value || undefined,
    subreddit: selectedSubreddit.value || undefined,
    is_favorite: showOnlyFavorites.value || undefined,
    page: 1 // Resetear a página 1 cuando se aplican filtros
  })
}

// Limpiar filtros
const clearFilters = async () => {
  searchQuery.value = ''
  selectedSubreddit.value = ''
  showOnlyFavorites.value = false
  showOnlyAnalyzed.value = false
  postsStore.resetFilters()
  await postsStore.fetchPosts()
}

// Manejar toggle de favorito
const handleToggleFavorite = async (id: number) => {
  await postsStore.toggleFavorite(id)
}

// Navegar al detalle del post
const handlePostClick = (id: number) => {
  router.push({ name: 'post-detail', params: { id } })
}

// Cambiar de página
const handlePageChange = async (page: number) => {
  postsStore.goToPage(page)
}

// Generador de números de página para mostrar
const pageNumbers = computed(() => {
  const total = postsStore.totalPages
  const current = postsStore.currentPage
  const pages: (number | string)[] = []

  if (total <= 7) {
    // Mostrar todas las páginas si son pocas
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    // Siempre mostrar primera página
    pages.push(1)

    if (current > 3) {
      pages.push('...')
    }

    // Páginas alrededor de la actual
    for (let i = Math.max(2, current - 1); i <= Math.min(total - 1, current + 1); i++) {
      pages.push(i)
    }

    if (current < total - 2) {
      pages.push('...')
    }

    // Siempre mostrar última página
    if (total > 1) {
      pages.push(total)
    }
  }

  return pages
})
</script>

<template>
  <AppLayout>
    <div>
      <!-- Header -->
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold text-white">Posts de Reddit</h1>
        <div class="text-sm text-dark-400">
          {{ postsStore.pagination.count }} posts encontrados
        </div>
      </div>

      <!-- Filtros -->
      <div class="bg-dark-700 rounded-lg p-4 border border-dark-600 mb-6 shadow-lg">
        <div class="flex flex-wrap gap-4">
          <!-- Búsqueda -->
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar en título o contenido..."
            class="flex-1 min-w-[250px] px-4 py-2 bg-dark-800 border border-dark-600 rounded-lg text-white placeholder-dark-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            @keyup.enter="applyFilters"
          />

          <!-- Subreddit -->
          <select
            v-model="selectedSubreddit"
            class="px-4 py-2 bg-dark-800 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="">Todos los subreddits</option>
            <option v-for="subreddit in availableSubreddits" :key="subreddit" :value="subreddit">
              r/{{ subreddit }}
            </option>
          </select>

          <!-- Checkboxes -->
          <label class="flex items-center gap-2 px-3 py-2 bg-dark-800 rounded-lg cursor-pointer hover:bg-dark-600 transition-colors">
            <input
              v-model="showOnlyFavorites"
              type="checkbox"
              class="w-4 h-4 text-primary-500 bg-dark-900 border-dark-600 rounded focus:ring-primary-500 focus:ring-2"
            />
            <span class="text-sm text-white">Solo favoritos</span>
          </label>

          <label class="flex items-center gap-2 px-3 py-2 bg-dark-800 rounded-lg cursor-pointer hover:bg-dark-600 transition-colors">
            <input
              v-model="showOnlyAnalyzed"
              type="checkbox"
              class="w-4 h-4 text-primary-500 bg-dark-800 border-dark-600 rounded focus:ring-primary-500 focus:ring-2"
            />
            <span class="text-sm text-white">Solo analizados</span>
          </label>

          <!-- Botones -->
          <button
            @click="applyFilters"
            class="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-colors"
          >
            Aplicar
          </button>

          <button
            @click="clearFilters"
            class="px-4 py-2 bg-dark-700 hover:bg-dark-600 text-white rounded-lg font-medium transition-colors"
          >
            Limpiar
          </button>
        </div>
      </div>

      <!-- Loading state -->
      <div v-if="postsStore.loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>

      <!-- Error state -->
      <div
        v-else-if="postsStore.error"
        class="bg-red-500/10 border border-red-500/50 rounded-lg p-4 mb-6"
      >
        <p class="text-red-400">{{ postsStore.error }}</p>
      </div>

      <!-- Empty state -->
      <div
        v-else-if="postsStore.posts.length === 0"
        class="bg-dark-800 rounded-lg border border-dark-700 p-12 text-center"
      >
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
        <p class="text-dark-400">No se encontraron posts con los filtros aplicados.</p>
      </div>

      <!-- Posts grid -->
      <div v-else class="grid gap-4 mb-6">
        <PostCard
          v-for="post in postsStore.filteredPosts"
          :key="post.id"
          :post="post"
          @toggle-favorite="handleToggleFavorite"
          @click="handlePostClick"
        />
      </div>

      <!-- Paginación -->
      <div
        v-if="postsStore.totalPages > 1 && !postsStore.loading"
        class="flex items-center justify-between bg-dark-800 rounded-lg p-4 border border-dark-700"
      >
        <div class="text-sm text-dark-400">
          Página {{ postsStore.currentPage }} de {{ postsStore.totalPages }}
        </div>

        <div class="flex items-center gap-2">
          <!-- Botón anterior -->
          <button
            @click="postsStore.previousPage()"
            :disabled="!postsStore.hasPreviousPage"
            class="px-3 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            :class="
              postsStore.hasPreviousPage
                ? 'bg-dark-700 hover:bg-dark-600 text-white'
                : 'bg-dark-800 text-dark-600'
            "
          >
            Anterior
          </button>

          <!-- Números de página -->
          <template v-for="(page, index) in pageNumbers" :key="index">
            <button
              v-if="typeof page === 'number'"
              @click="handlePageChange(page)"
              class="px-3 py-2 rounded-lg font-medium transition-colors"
              :class="
                page === postsStore.currentPage
                  ? 'bg-primary-500 text-white'
                  : 'bg-dark-700 hover:bg-dark-600 text-white'
              "
            >
              {{ page }}
            </button>
            <span v-else class="px-2 text-dark-500">...</span>
          </template>

          <!-- Botón siguiente -->
          <button
            @click="postsStore.nextPage()"
            :disabled="!postsStore.hasNextPage"
            class="px-3 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            :class="
              postsStore.hasNextPage
                ? 'bg-dark-700 hover:bg-dark-600 text-white'
                : 'bg-dark-800 text-dark-600'
            "
          >
            Siguiente
          </button>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
