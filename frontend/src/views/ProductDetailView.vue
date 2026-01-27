<script setup lang="ts">
import { onMounted, computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import { useProductsStore } from '@/stores/products'
import { scraperService } from '@/services'
import type { OllamaStatus } from '@/services/scraper'

const route = useRoute()
const router = useRouter()
const productsStore = useProductsStore()

const productId = computed(() => parseInt(route.params.id as string))

// Estado de análisis IA
const isAnalyzing = ref(false)
const analyzeError = ref('')
const analyzeSuccess = ref('')
const ollamaStatus = ref<OllamaStatus | null>(null)

// Cargar estado de Ollama
const loadOllamaStatus = async () => {
  try {
    ollamaStatus.value = await scraperService.getOllamaStatus()
  } catch (error) {
    console.error('Error al cargar estado de Ollama:', error)
    ollamaStatus.value = null
  }
}

// Analizar este producto con IA
const handleAnalyzeProduct = async () => {
  if (!productId.value || isAnalyzing.value) return

  try {
    isAnalyzing.value = true
    analyzeError.value = ''
    analyzeSuccess.value = ''

    await scraperService.analyzeProducts({ product_ids: [productId.value] })

    // Esperar un poco para que el análisis se complete
    analyzeSuccess.value = 'Analizando...'

    // Polling para verificar cuando termine el análisis
    const maxAttempts = 20
    let attempts = 0

    const checkAnalysis = async () => {
      attempts++
      await productsStore.fetchProduct(productId.value)

      if (productsStore.currentProduct?.analyzed) {
        isAnalyzing.value = false
        analyzeSuccess.value = 'Análisis completado'
        setTimeout(() => {
          analyzeSuccess.value = ''
        }, 3000)
        return
      }

      if (attempts < maxAttempts) {
        setTimeout(checkAnalysis, 3000)
      } else {
        isAnalyzing.value = false
        analyzeSuccess.value = ''
        analyzeError.value = 'El análisis está tardando más de lo esperado. Recarga la página para ver el resultado.'
        setTimeout(() => {
          analyzeError.value = ''
        }, 5000)
      }
    }

    setTimeout(checkAnalysis, 5000)
  } catch (error: any) {
    isAnalyzing.value = false
    analyzeError.value = error.response?.data?.message || 'Error al analizar el producto'
    setTimeout(() => {
      analyzeError.value = ''
    }, 5000)
  }
}

// Cargar producto, estado de Ollama y nota al montar
onMounted(async () => {
  await Promise.all([
    productId.value ? productsStore.fetchProduct(productId.value) : Promise.resolve(),
    productId.value ? productsStore.fetchNote(productId.value) : Promise.resolve(),
    loadOllamaStatus()
  ])

  // Inicializar contenido si existe nota
  if (productsStore.currentNote) {
    noteContent.value = productsStore.currentNote.content
  }
})

// Formatear fecha
const formattedDate = computed(() => {
  if (!productsStore.currentProduct) return ''
  const date = new Date(productsStore.currentProduct.created_at_source)
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
  if (productsStore.currentProduct) {
    await productsStore.toggleFavorite(productsStore.currentProduct.id)
  }
}

// Volver atrás
const goBack = () => {
  router.push({ name: 'products' })
}

// Abrir en Product Hunt
const openInProductHunt = () => {
  if (productsStore.currentProduct) {
    window.open(productsStore.currentProduct.url, '_blank')
  }
}

// Estado de eliminación
const showDeleteConfirm = ref(false)
const isDeleting = ref(false)

// Estado de notas
const isEditingNote = ref(false)
const noteContent = ref('')
const noteSaveSuccess = ref(false)
const noteSaveError = ref('')

// Eliminar producto
const handleDeleteProduct = async () => {
  if (!productsStore.currentProduct || isDeleting.value) return

  isDeleting.value = true
  const success = await productsStore.deleteProduct(productsStore.currentProduct.id)

  if (success) {
    router.push({ name: 'products' })
  } else {
    isDeleting.value = false
    showDeleteConfirm.value = false
  }
}

// Funciones de notas
const handleCreateNote = async () => {
  if (!productId.value || !noteContent.value.trim()) return

  noteSaveError.value = ''
  noteSaveSuccess.value = false

  const success = await productsStore.createNote(productId.value, noteContent.value.trim())

  if (success) {
    noteSaveSuccess.value = true
    isEditingNote.value = false
    setTimeout(() => (noteSaveSuccess.value = false), 3000)
  } else {
    noteSaveError.value = productsStore.noteError || 'Error al guardar nota'
  }
}

const handleUpdateNote = async () => {
  if (!productId.value || !noteContent.value.trim()) return

  noteSaveError.value = ''
  noteSaveSuccess.value = false

  const success = await productsStore.updateNote(productId.value, noteContent.value.trim())

  if (success) {
    noteSaveSuccess.value = true
    isEditingNote.value = false
    setTimeout(() => (noteSaveSuccess.value = false), 3000)
  } else {
    noteSaveError.value = productsStore.noteError || 'Error al actualizar nota'
  }
}

const handleDeleteNote = async () => {
  if (!productId.value || !confirm('¿Estás seguro de eliminar esta nota?')) return

  noteSaveError.value = ''

  const success = await productsStore.deleteNote(productId.value)

  if (success) {
    noteContent.value = ''
    isEditingNote.value = false
  } else {
    noteSaveError.value = productsStore.noteError || 'Error al eliminar nota'
  }
}

const handleCancelEdit = () => {
  if (productsStore.currentNote) {
    noteContent.value = productsStore.currentNote.content
  } else {
    noteContent.value = ''
  }
  isEditingNote.value = false
  noteSaveError.value = ''
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
        Volver a productos
      </button>

      <!-- Loading state -->
      <div v-if="productsStore.loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>

      <!-- Error state -->
      <div
        v-else-if="productsStore.error"
        class="bg-red-500/10 border border-red-500/50 rounded-lg p-6"
      >
        <h2 class="text-xl font-semibold text-red-400 mb-2">Error al cargar el producto</h2>
        <p class="text-red-300">{{ productsStore.error }}</p>
      </div>

      <!-- Product detail -->
      <div v-else-if="productsStore.currentProduct" class="space-y-4 md:space-y-6">
        <!-- Header card -->
        <div class="bg-dark-800 rounded-lg p-4 sm:p-6 border border-dark-700">
          <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-4">
            <div class="flex-1">
              <h1 class="text-2xl sm:text-3xl font-bold text-white mb-4">
                {{ productsStore.currentProduct.title }}
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
                      d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"
                    />
                  </svg>
                  {{ productsStore.currentProduct.topic.name }}
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
                  {{ productsStore.currentProduct.score }} puntos
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
              class="sm:ml-4 p-3 rounded-lg transition-colors self-start sm:self-auto"
              :class="
                productsStore.currentProduct.is_favorite
                  ? 'bg-accent/10 text-accent hover:bg-accent/20'
                  : 'bg-dark-700 text-dark-400 hover:bg-dark-600 hover:text-accent'
              "
              :title="
                productsStore.currentProduct.is_favorite ? 'Quitar de favoritos' : 'Añadir a favoritos'
              "
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-6 w-6"
                :fill="productsStore.currentProduct.is_favorite ? 'currentColor' : 'none'"
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

          <!-- Botones de acción -->
          <div class="flex flex-col sm:flex-row gap-3">
            <button
              @click="openInProductHunt"
              class="flex-1 sm:flex-none flex items-center justify-center gap-2 px-4 py-2 bg-secondary-500 hover:bg-secondary-600 text-white rounded-lg font-medium transition-colors"
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
              Ver en Product Hunt
            </button>

            <button
              @click="showDeleteConfirm = true"
              class="flex-1 sm:flex-none flex items-center justify-center gap-2 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/50 rounded-lg font-medium transition-colors"
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
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
              Eliminar
            </button>
          </div>
        </div>

        <!-- Content card -->
        <div class="bg-dark-800 rounded-lg p-4 sm:p-6 border border-dark-700">
          <h2 class="text-lg sm:text-xl font-semibold text-white mb-4">Contenido</h2>
          <div class="prose prose-invert max-w-none">
            <p class="text-dark-200 whitespace-pre-wrap leading-relaxed">
              {{ productsStore.currentProduct.content }}
            </p>
          </div>
        </div>

        <!-- Mensajes de análisis -->
        <div v-if="analyzeError || analyzeSuccess" class="space-y-3">
          <div
            v-if="analyzeSuccess"
            class="bg-primary-500/20 border border-primary-500 text-primary-300 px-4 py-3 rounded-lg flex items-center gap-3"
          >
            <div v-if="isAnalyzing" class="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-400"></div>
            {{ analyzeSuccess }}
          </div>
          <div
            v-if="analyzeError"
            class="bg-red-500/20 border border-red-500 text-red-300 px-4 py-3 rounded-lg"
          >
            {{ analyzeError }}
          </div>
        </div>

        <!-- Card para analizar con IA (cuando no está analizado) -->
        <div
          v-if="!productsStore.currentProduct.analyzed && ollamaStatus"
          class="bg-dark-800 rounded-lg p-4 sm:p-6 border border-dark-700"
        >
          <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div class="flex items-center gap-3">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-8 w-8 text-primary-400"
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
              <div>
                <h3 class="text-lg font-semibold text-white">Análisis IA</h3>
                <p class="text-dark-400 text-sm">
                  {{ ollamaStatus.ready ? 'Extrae insights del producto con inteligencia artificial' : 'Ollama no está disponible' }}
                </p>
              </div>
            </div>
            <button
              v-if="ollamaStatus.ready"
              @click="handleAnalyzeProduct"
              :disabled="isAnalyzing"
              class="w-full sm:w-auto flex items-center justify-center gap-2 px-6 py-3 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div v-if="isAnalyzing" class="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              <svg
                v-else
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
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                />
              </svg>
              {{ isAnalyzing ? 'Analizando...' : 'Analizar con IA' }}
            </button>
            <div v-else class="text-yellow-400 text-sm flex items-center gap-2">
              <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
              Modelo no disponible
            </div>
          </div>
        </div>

        <!-- AI Analysis card (si existe) -->
        <div
          v-if="productsStore.currentProduct.analyzed"
          class="bg-gradient-to-br from-primary-500/10 to-secondary-500/10 rounded-lg p-4 sm:p-6 border border-primary-500/30"
        >
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-2">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-5 w-5 sm:h-6 sm:w-6 text-primary-400"
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
              <h2 class="text-lg sm:text-xl font-semibold text-white">Análisis IA</h2>
            </div>
            <!-- Potential Score Badge -->
            <div
              v-if="productsStore.currentProduct.potential_score"
              class="flex items-center gap-1 px-3 py-1 rounded-full"
              :class="{
                'bg-green-500/20 text-green-300': productsStore.currentProduct.potential_score >= 7,
                'bg-yellow-500/20 text-yellow-300': productsStore.currentProduct.potential_score >= 4 && productsStore.currentProduct.potential_score < 7,
                'bg-red-500/20 text-red-300': productsStore.currentProduct.potential_score < 4
              }"
            >
              <span class="text-sm font-medium">Potencial:</span>
              <span class="text-lg font-bold">{{ productsStore.currentProduct.potential_score }}/10</span>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Summary -->
            <div v-if="productsStore.currentProduct.summary" class="bg-dark-800/50 rounded-lg p-4">
              <h3 class="text-sm font-medium text-primary-300 mb-2">Resumen</h3>
              <p class="text-white">{{ productsStore.currentProduct.summary }}</p>
            </div>

            <!-- Problem -->
            <div v-if="productsStore.currentProduct.problem" class="bg-dark-800/50 rounded-lg p-4">
              <h3 class="text-sm font-medium text-red-300 mb-2">Problema que resuelve</h3>
              <p class="text-white">{{ productsStore.currentProduct.problem }}</p>
            </div>

            <!-- MVP Idea -->
            <div v-if="productsStore.currentProduct.mvp_idea" class="bg-dark-800/50 rounded-lg p-4 md:col-span-2">
              <h3 class="text-sm font-medium text-accent mb-2">Idea de MVP</h3>
              <p class="text-white">{{ productsStore.currentProduct.mvp_idea }}</p>
            </div>

            <!-- Target Audience -->
            <div v-if="productsStore.currentProduct.target_audience" class="bg-dark-800/50 rounded-lg p-4">
              <h3 class="text-sm font-medium text-secondary-300 mb-2">Público objetivo</h3>
              <p class="text-white">{{ productsStore.currentProduct.target_audience }}</p>
            </div>

            <!-- Tags -->
            <div v-if="productsStore.currentProduct.tags" class="bg-dark-800/50 rounded-lg p-4">
              <h3 class="text-sm font-medium text-dark-300 mb-2">Tags</h3>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="tag in productsStore.currentProduct.tags.split(',')"
                  :key="tag"
                  class="px-2 py-1 bg-dark-700 text-dark-200 rounded text-sm"
                >
                  {{ tag.trim() }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Mis Notas -->
        <div class="bg-dark-800 rounded-lg p-4 sm:p-6 border border-dark-700">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg sm:text-xl font-semibold text-white flex items-center gap-2">
              <span>📝</span>
              Mis Notas
            </h3>

            <!-- Botones de acción -->
            <div class="flex gap-2" v-if="!isEditingNote && productsStore.currentNote">
              <button
                @click="isEditingNote = true"
                class="px-3 py-1 text-sm bg-primary hover:bg-primary/80 text-white rounded transition-colors"
              >
                Editar
              </button>
              <button
                @click="handleDeleteNote"
                class="px-3 py-1 text-sm bg-red-600 hover:bg-red-700 text-white rounded transition-colors"
                :disabled="productsStore.noteLoading"
              >
                Eliminar
              </button>
            </div>
          </div>

          <!-- Mostrar nota existente (modo lectura) -->
          <div v-if="productsStore.currentNote && !isEditingNote" class="space-y-2">
            <p class="text-gray-300 whitespace-pre-wrap">{{ productsStore.currentNote.content }}</p>
            <p class="text-sm text-gray-500">
              Última edición: {{ new Date(productsStore.currentNote.updated_at).toLocaleString('es-ES') }}
            </p>
          </div>

          <!-- Formulario de edición/creación -->
          <div v-else-if="isEditingNote || !productsStore.currentNote" class="space-y-3">
            <textarea
              v-model="noteContent"
              placeholder="Escribe tus notas, ideas o reflexiones sobre este producto..."
              rows="6"
              class="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
            ></textarea>

            <!-- Mensajes de éxito/error -->
            <div v-if="noteSaveSuccess" class="text-sm text-green-400">
              ✓ Nota guardada correctamente
            </div>
            <div v-if="noteSaveError" class="text-sm text-red-400">
              {{ noteSaveError }}
            </div>

            <!-- Botones -->
            <div class="flex gap-2">
              <button
                @click="productsStore.currentNote ? handleUpdateNote() : handleCreateNote()"
                :disabled="!noteContent.trim() || productsStore.noteLoading"
                class="px-4 py-2 bg-primary hover:bg-primary/80 text-white rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ productsStore.noteLoading ? 'Guardando...' : 'Guardar' }}
              </button>
              <button
                v-if="isEditingNote || productsStore.currentNote"
                @click="handleCancelEdit"
                :disabled="productsStore.noteLoading"
                class="px-4 py-2 bg-dark-700 hover:bg-dark-600 text-white rounded transition-colors"
              >
                Cancelar
              </button>
            </div>
          </div>

          <!-- Estado vacío -->
          <div v-if="!productsStore.currentNote && !isEditingNote" class="text-center py-8">
            <p class="text-gray-500 mb-4">Aún no tienes notas para este producto</p>
            <button
              @click="isEditingNote = true"
              class="px-4 py-2 bg-primary hover:bg-primary/80 text-white rounded transition-colors"
            >
              Agregar Nota
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de confirmación de eliminación -->
    <div
      v-if="showDeleteConfirm"
      class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
      @click.self="showDeleteConfirm = false"
    >
      <div class="bg-dark-800 rounded-lg p-6 max-w-md w-full border border-dark-700">
        <h3 class="text-xl font-semibold text-white mb-4">Eliminar producto</h3>
        <p class="text-dark-300 mb-6">
          ¿Estás seguro de que quieres eliminar
          <span class="text-white font-medium">"{{ productsStore.currentProduct?.title }}"</span>?
          Esta acción no se puede deshacer.
        </p>
        <div class="flex gap-3 justify-end">
          <button
            @click="showDeleteConfirm = false"
            :disabled="isDeleting"
            class="px-4 py-2 bg-dark-700 hover:bg-dark-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            Cancelar
          </button>
          <button
            @click="handleDeleteProduct"
            :disabled="isDeleting"
            class="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50 flex items-center gap-2"
          >
            <div v-if="isDeleting" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            {{ isDeleting ? 'Eliminando...' : 'Eliminar' }}
          </button>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
