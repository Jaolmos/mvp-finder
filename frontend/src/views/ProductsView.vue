<script setup lang="ts">
import { onMounted, ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import ProductCard from '@/components/ProductCard.vue'
import { useProductsStore } from '@/stores/products'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const route = useRoute()
const productsStore = useProductsStore()
const toast = useToast()

// Filtros locales
const searchQuery = ref('')
const selectedTopic = ref<number | undefined>(undefined)
const minPotential = ref<number | undefined>(undefined)
const selectedOrdering = ref<string>('-created_at_source')
const showOnlyFavorites = ref(false)
const showOnlyAnalyzed = ref(false)

// Opciones de ordenamiento
const orderingOptions = [
  { value: '-created_at_source', label: 'Más recientes' },
  { value: 'created_at_source', label: 'Más antiguos' },
  { value: '-potential_score', label: 'Mayor potencial' },
  { value: 'potential_score', label: 'Menor potencial' },
  { value: '-votes_count', label: 'Más votos' },
  { value: 'votes_count', label: 'Menos votos' }
]

// Lista única de topics disponibles
const availableTopics = computed(() => {
  const topics = new Map<number, string>()
  productsStore.products.forEach((product) => {
    topics.set(product.topic.id, product.topic.name)
  })
  return Array.from(topics.entries()).sort((a, b) => a[1].localeCompare(b[1]))
})

// Cargar productos al montar el componente
onMounted(async () => {
  // Leer query params al montar
  if (route.query.analyzed === 'true') {
    showOnlyAnalyzed.value = true
  }
  if (route.query.topic) {
    const topicId = parseInt(route.query.topic as string)
    if (!isNaN(topicId)) {
      selectedTopic.value = topicId
    }
  }
  if (route.query.search) {
    searchQuery.value = route.query.search as string
  }
  if (route.query.favorites === 'true') {
    showOnlyFavorites.value = true
  }
  if (route.query.min_potential) {
    const potential = parseInt(route.query.min_potential as string)
    if (!isNaN(potential)) {
      minPotential.value = potential
    }
  }
  if (route.query.ordering) {
    const ordering = route.query.ordering as string
    if (orderingOptions.some(opt => opt.value === ordering)) {
      selectedOrdering.value = ordering
    }
  }

  // Aplicar filtros desde query params
  await productsStore.fetchProducts({
    analyzed: showOnlyAnalyzed.value || undefined,
    topic: selectedTopic.value || undefined,
    search: searchQuery.value || undefined,
    is_favorite: showOnlyFavorites.value || undefined,
    min_potential: minPotential.value || undefined,
    ordering: selectedOrdering.value
  })
})

// Observar cambios en query params (solo para navegación futura)
watch(() => route.query, async (newQuery) => {
  // Sincronizar filtros locales con query params
  showOnlyAnalyzed.value = newQuery.analyzed === 'true'
  showOnlyFavorites.value = newQuery.favorites === 'true'
  searchQuery.value = (newQuery.search as string) || ''

  const topicId = newQuery.topic ? parseInt(newQuery.topic as string) : undefined
  selectedTopic.value = topicId && !isNaN(topicId) ? topicId : undefined

  const potential = newQuery.min_potential ? parseInt(newQuery.min_potential as string) : undefined
  minPotential.value = potential && !isNaN(potential) ? potential : undefined

  const ordering = newQuery.ordering as string
  if (ordering && orderingOptions.some(opt => opt.value === ordering)) {
    selectedOrdering.value = ordering
  } else {
    selectedOrdering.value = '-created_at_source'
  }

  // Recargar productos con los nuevos filtros
  await productsStore.fetchProducts({
    analyzed: showOnlyAnalyzed.value || undefined,
    topic: selectedTopic.value || undefined,
    search: searchQuery.value || undefined,
    is_favorite: showOnlyFavorites.value || undefined,
    min_potential: minPotential.value || undefined,
    ordering: selectedOrdering.value
  })
}, { deep: true })

// Aplicar filtros
const applyFilters = async () => {
  await productsStore.fetchProducts({
    search: searchQuery.value || undefined,
    topic: selectedTopic.value || undefined,
    min_potential: minPotential.value || undefined,
    ordering: selectedOrdering.value,
    is_favorite: showOnlyFavorites.value || undefined,
    analyzed: showOnlyAnalyzed.value || undefined,
    page: 1 // Resetear a página 1 cuando se aplican filtros
  })
}

// Limpiar filtros
const clearFilters = async () => {
  searchQuery.value = ''
  selectedTopic.value = undefined
  minPotential.value = undefined
  selectedOrdering.value = '-created_at_source'
  showOnlyFavorites.value = false
  showOnlyAnalyzed.value = false
  productsStore.resetFilters()
  await productsStore.fetchProducts({ ordering: '-created_at_source' })
}

// Manejar toggle de favorito
const handleToggleFavorite = async (id: number) => {
  await productsStore.toggleFavorite(id)
  const product = productsStore.products.find(p => p.id === id)
  toast.success(product?.is_favorite ? 'Añadido a favoritos' : 'Eliminado de favoritos')
}

// Navegar al detalle del producto
const handleProductClick = (id: number) => {
  router.push({ name: 'product-detail', params: { id } })
}

// Cambiar de página
const handlePageChange = async (page: number) => {
  productsStore.goToPage(page)
}

// Generador de números de página para mostrar (desktop)
const pageNumbers = computed(() => {
  const total = productsStore.totalPages
  const current = productsStore.currentPage
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

// Generador de números de página para móvil (simplificado)
const pageNumbersMobile = computed(() => {
  const total = productsStore.totalPages
  const current = productsStore.currentPage
  const pages: (number | string)[] = []

  if (total <= 3) {
    // Mostrar todas si son 3 o menos
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    // Mostrar: primera, actual, última (con ... si es necesario)
    pages.push(1)

    if (current > 2) {
      pages.push('...')
    }

    if (current !== 1 && current !== total) {
      pages.push(current)
    }

    if (current < total - 1) {
      pages.push('...')
    }

    pages.push(total)
  }

  return pages
})
</script>

<template>
  <AppLayout>
    <div>
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-6">
        <h1 class="text-xl md:text-2xl font-bold text-white">Productos de Product Hunt</h1>
        <div class="text-sm text-dark-400">
          {{ productsStore.pagination.count }} productos encontrados
        </div>
      </div>

      <!-- Filtros -->
      <div class="bg-dark-700 rounded-lg p-4 border border-dark-600 mb-6 shadow-lg">
        <div class="flex flex-col md:flex-row md:flex-wrap gap-3">
          <!-- Búsqueda (full width en móvil) -->
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar en título o contenido..."
            class="w-full md:flex-1 md:min-w-[250px] px-4 py-2 bg-dark-800 border border-dark-600 rounded-lg text-white placeholder-dark-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            @keyup.enter="applyFilters"
          />

          <!-- Topic (full width en móvil) -->
          <select
            v-model="selectedTopic"
            class="w-full md:w-auto px-4 py-2 bg-dark-800 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option :value="undefined">Todos los topics</option>
            <option v-for="[id, name] in availableTopics" :key="id" :value="id">
              {{ name }}
            </option>
          </select>

          <!-- Potencial mínimo -->
          <select
            v-model="minPotential"
            class="w-full md:w-auto px-4 py-2 bg-dark-800 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option :value="undefined">Potencial</option>
            <option :value="5">Potencial ≥ 5</option>
            <option :value="7">Potencial ≥ 7</option>
            <option :value="8">Potencial ≥ 8</option>
          </select>

          <!-- Ordenamiento -->
          <select
            v-model="selectedOrdering"
            class="w-full md:w-auto px-4 py-2 bg-dark-800 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option
              v-for="option in orderingOptions"
              :key="option.value"
              :value="option.value"
            >
              {{ option.label }}
            </option>
          </select>

          <!-- Checkboxes (en fila en móvil) -->
          <div class="flex gap-3 flex-wrap">
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
          </div>

          <!-- Botones (full width en móvil) -->
          <div class="flex gap-3 w-full md:w-auto">
            <button
              @click="applyFilters"
              class="flex-1 md:flex-none px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-colors"
            >
              Aplicar
            </button>

            <button
              @click="clearFilters"
              class="flex-1 md:flex-none px-4 py-2 bg-dark-700 hover:bg-dark-600 text-white rounded-lg font-medium transition-colors"
            >
              Limpiar
            </button>
          </div>
        </div>
      </div>

      <!-- Loading state -->
      <div v-if="productsStore.loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>

      <!-- Error state -->
      <div
        v-else-if="productsStore.error"
        class="bg-red-500/10 border border-red-500/50 rounded-lg p-4 mb-6"
      >
        <p class="text-red-400">{{ productsStore.error }}</p>
      </div>

      <!-- Empty state -->
      <div
        v-else-if="productsStore.products.length === 0"
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
        <h3 class="text-lg font-semibold text-white mb-2">No hay productos</h3>
        <p class="text-dark-400">No se encontraron productos con los filtros aplicados.</p>
      </div>

      <!-- Products grid -->
      <div v-else class="grid gap-4 mb-6">
        <ProductCard
          v-for="product in productsStore.filteredProducts"
          :key="product.id"
          :product="product"
          @toggle-favorite="handleToggleFavorite"
          @click="handleProductClick"
        />
      </div>

      <!-- Paginación -->
      <div
        v-if="productsStore.totalPages > 1 && !productsStore.loading"
        class="bg-dark-800 rounded-lg p-4 border border-dark-700"
      >
        <!-- Desktop: layout horizontal -->
        <div class="hidden md:flex items-center justify-between">
          <div class="text-sm text-dark-400">
            Página {{ productsStore.currentPage }} de {{ productsStore.totalPages }}
          </div>

          <div class="flex items-center gap-2">
            <!-- Botón anterior -->
            <button
              @click="productsStore.previousPage()"
              :disabled="!productsStore.hasPreviousPage"
              class="px-3 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              :class="
                productsStore.hasPreviousPage
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
                  page === productsStore.currentPage
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
              @click="productsStore.nextPage()"
              :disabled="!productsStore.hasNextPage"
              class="px-3 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              :class="
                productsStore.hasNextPage
                  ? 'bg-dark-700 hover:bg-dark-600 text-white'
                  : 'bg-dark-800 text-dark-600'
              "
            >
              Siguiente
            </button>
          </div>
        </div>

        <!-- Móvil: layout vertical simplificado -->
        <div class="md:hidden space-y-3">
          <!-- Indicador de página -->
          <div class="text-sm text-dark-400 text-center">
            Página {{ productsStore.currentPage }} de {{ productsStore.totalPages }}
          </div>

          <!-- Botones Anterior/Siguiente -->
          <div class="flex gap-2">
            <button
              @click="productsStore.previousPage()"
              :disabled="!productsStore.hasPreviousPage"
              class="flex-1 px-4 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              :class="
                productsStore.hasPreviousPage
                  ? 'bg-dark-700 hover:bg-dark-600 text-white'
                  : 'bg-dark-800 text-dark-600'
              "
            >
              ← Anterior
            </button>

            <button
              @click="productsStore.nextPage()"
              :disabled="!productsStore.hasNextPage"
              class="flex-1 px-4 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              :class="
                productsStore.hasNextPage
                  ? 'bg-dark-700 hover:bg-dark-600 text-white'
                  : 'bg-dark-800 text-dark-600'
              "
            >
              Siguiente →
            </button>
          </div>

          <!-- Números de página (simplificados) -->
          <div class="flex items-center justify-center gap-2">
            <template v-for="(page, index) in pageNumbersMobile" :key="index">
              <button
                v-if="typeof page === 'number'"
                @click="handlePageChange(page)"
                class="px-3 py-2 rounded-lg font-medium transition-colors min-w-[2.5rem]"
                :class="
                  page === productsStore.currentPage
                    ? 'bg-primary-500 text-white'
                    : 'bg-dark-700 hover:bg-dark-600 text-white'
                "
              >
                {{ page }}
              </button>
              <span v-else class="px-1 text-dark-500 text-sm">...</span>
            </template>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
