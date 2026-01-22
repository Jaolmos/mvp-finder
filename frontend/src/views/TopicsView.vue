<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import AppLayout from '@/layouts/AppLayout.vue'
import { useTopicsStore } from '@/stores/topics'
import { scraperService } from '@/services'

const topicsStore = useTopicsStore()

// Estado del modal
const showModal = ref(false)
const modalMode = ref<'create' | 'edit'>('create')
const editingId = ref<number | null>(null)

// Estado de sincronización
const syncingTopicId = ref<number | null>(null)
const syncMessage = ref('')
const syncError = ref('')

// Formulario
const formData = ref({
  name: '',
  is_active: true
})

// Cargar topics al montar
onMounted(async () => {
  await topicsStore.fetchTopics()
})

// Computed para obtener listas de topics
const topics = computed(() => topicsStore.topics)
const loading = computed(() => topicsStore.loading)
const error = computed(() => topicsStore.error)

// Abrir modal para crear
const openCreateModal = () => {
  modalMode.value = 'create'
  editingId.value = null
  formData.value = {
    name: '',
    is_active: true
  }
  showModal.value = true
}

// Abrir modal para editar
const openEditModal = (id: number, name: string, is_active: boolean) => {
  modalMode.value = 'edit'
  editingId.value = id
  formData.value = {
    name: name,
    is_active
  }
  showModal.value = true
}

// Cerrar modal
const closeModal = () => {
  showModal.value = false
  formData.value = {
    name: '',
    is_active: true
  }
  editingId.value = null
  topicsStore.clearError()
}

// Guardar (crear o editar)
const handleSave = async () => {
  // Validar nombre
  const name = formData.value.name.trim()
  if (!name) {
    return
  }

  let success = false
  if (modalMode.value === 'create') {
    success = await topicsStore.createTopic(name, formData.value.is_active)
  } else if (editingId.value !== null) {
    success = await topicsStore.updateTopic(editingId.value, {
      name: name,
      is_active: formData.value.is_active
    })
  }

  if (success) {
    closeModal()
  }
}

// Toggle activo/inactivo
const handleToggleActive = async (id: number) => {
  await topicsStore.toggleActive(id)
}

// Eliminar topic
const handleDelete = async (id: number, name: string) => {
  if (confirm(`¿Estás seguro de eliminar "${name}"?`)) {
    await topicsStore.deleteTopic(id)
  }
}

// Formatear fecha
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// Sincronizar topic individual
const handleSyncTopic = async (topicId: number) => {
  try {
    syncingTopicId.value = topicId
    syncError.value = ''
    syncMessage.value = ''

    const response = await scraperService.syncPosts({ topic_ids: [topicId] })
    syncMessage.value = response.message

    // Esperar 3 segundos y recargar topics para actualizar last_sync
    setTimeout(async () => {
      await topicsStore.fetchTopics()
      syncMessage.value = 'Sincronización completada'

      // Limpiar mensaje después de 3 segundos
      setTimeout(() => {
        syncMessage.value = ''
      }, 3000)
    }, 3000)
  } catch (error: any) {
    syncError.value = error.response?.data?.message || 'Error al sincronizar topic'

    // Limpiar error después de 5 segundos
    setTimeout(() => {
      syncError.value = ''
    }, 5000)
  } finally {
    syncingTopicId.value = null
  }
}
</script>

<template>
  <AppLayout>
    <div>
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 mb-6">
        <h1 class="text-xl md:text-2xl font-bold text-white">Topics</h1>
        <button
          @click="openCreateModal"
          class="w-full sm:w-auto px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white font-medium rounded-lg transition-colors"
        >
          + Añadir Topic
        </button>
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

      <!-- Estado de carga -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="text-dark-400">Cargando topics...</div>
      </div>

      <!-- Error -->
      <div
        v-else-if="error"
        class="bg-red-500/10 border border-red-500 rounded-lg p-4 mb-6"
      >
        <p class="text-red-400">{{ error }}</p>
      </div>

      <!-- Lista vacía -->
      <div
        v-else-if="topics.length === 0"
        class="bg-dark-700 rounded-lg border border-dark-600 shadow-lg"
      >
        <div class="p-12 text-center text-dark-400">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-16 w-16 mx-auto mb-4 text-dark-500"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
            />
          </svg>
          <p class="text-lg mb-2">No hay topics configurados</p>
          <p class="text-sm">Añade topics de Product Hunt para comenzar a monitorear productos</p>
        </div>
      </div>

      <!-- Tabla de topics -->
      <div v-else class="bg-dark-700 rounded-lg border border-dark-600 shadow-lg overflow-hidden">
        <!-- Wrapper con scroll horizontal en móvil -->
        <div class="overflow-x-auto">
        <table class="w-full min-w-[640px]">
          <thead class="bg-dark-800">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-dark-300 uppercase tracking-wider">
                Topic
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-dark-300 uppercase tracking-wider">
                Estado
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-dark-300 uppercase tracking-wider">
                Última sincronización
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-dark-300 uppercase tracking-wider">
                Creado
              </th>
              <th class="px-6 py-3 text-right text-xs font-medium text-dark-300 uppercase tracking-wider">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-dark-600">
            <tr
              v-for="topic in topics"
              :key="topic.id"
              class="hover:bg-dark-600 transition-colors"
            >
              <!-- Nombre -->
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-5 w-5 text-secondary-400 mr-2"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
                    />
                  </svg>
                  <span class="text-white font-medium">{{ topic.name }}</span>
                </div>
              </td>

              <!-- Estado -->
              <td class="px-6 py-4 whitespace-nowrap">
                <button
                  @click="handleToggleActive(topic.id)"
                  class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium transition-colors"
                  :class="
                    topic.is_active
                      ? 'bg-green-500/20 text-green-400 hover:bg-green-500/30'
                      : 'bg-dark-600 text-dark-400 hover:bg-dark-500'
                  "
                >
                  <span
                    class="w-2 h-2 rounded-full mr-2"
                    :class="topic.is_active ? 'bg-green-400' : 'bg-dark-400'"
                  ></span>
                  {{ topic.is_active ? 'Activo' : 'Inactivo' }}
                </button>
              </td>

              <!-- Última sincronización -->
              <td class="px-6 py-4 whitespace-nowrap text-sm text-dark-300">
                {{ topic.last_sync ? formatDate(topic.last_sync) : 'Nunca' }}
              </td>

              <!-- Creado -->
              <td class="px-6 py-4 whitespace-nowrap text-sm text-dark-400">
                {{ formatDate(topic.created_at) }}
              </td>

              <!-- Acciones -->
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button
                  @click="handleSyncTopic(topic.id)"
                  :disabled="syncingTopicId === topic.id"
                  class="text-accent hover:text-accent/80 mr-4 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Sincronizar topic"
                >
                  <svg
                    v-if="syncingTopicId !== topic.id"
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
                      d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                    />
                  </svg>
                  <div
                    v-else
                    class="animate-spin rounded-full h-5 w-5 border-b-2 border-accent"
                  ></div>
                </button>
                <button
                  @click="openEditModal(topic.id, topic.name, topic.is_active)"
                  class="text-primary-400 hover:text-primary-300 mr-4 transition-colors"
                  title="Editar"
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
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                    />
                  </svg>
                </button>
                <button
                  @click="handleDelete(topic.id, topic.name)"
                  class="text-red-400 hover:text-red-300 transition-colors"
                  title="Eliminar"
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
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        </div>
      </div>

      <!-- Modal Crear/Editar -->
      <div
        v-if="showModal"
        class="fixed inset-0 z-50 overflow-y-auto"
        @click.self="closeModal"
      >
        <div class="flex items-center justify-center min-h-screen px-4 py-6">
          <!-- Overlay -->
          <div class="fixed inset-0 bg-black/70 transition-opacity"></div>

          <!-- Modal -->
          <div class="relative bg-dark-700 rounded-lg shadow-xl w-full max-w-md p-4 sm:p-6 border border-dark-600">
            <!-- Header -->
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-xl font-semibold text-white">
                {{ modalMode === 'create' ? 'Añadir Topic' : 'Editar Topic' }}
              </h3>
              <button
                @click="closeModal"
                class="text-dark-400 hover:text-white transition-colors"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>

            <!-- Error -->
            <div
              v-if="error"
              class="bg-red-500/10 border border-red-500 rounded-lg p-3 mb-4"
            >
              <p class="text-red-400 text-sm">{{ error }}</p>
            </div>

            <!-- Formulario -->
            <form @submit.prevent="handleSave">
              <!-- Nombre -->
              <div class="mb-4">
                <label for="name" class="block text-sm font-medium text-dark-300 mb-2">
                  Nombre del Topic
                </label>
                <input
                  id="name"
                  v-model="formData.name"
                  type="text"
                  required
                  placeholder="ejemplo: artificial-intelligence"
                  class="w-full px-4 py-2 bg-dark-800 border border-dark-600 rounded-lg text-white placeholder-dark-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
                <p class="mt-1 text-xs text-dark-400">
                  Slug del topic de Product Hunt (ej: artificial-intelligence, developer-tools)
                </p>
              </div>

              <!-- Estado activo -->
              <div class="mb-6">
                <label class="flex items-center cursor-pointer">
                  <input
                    v-model="formData.is_active"
                    type="checkbox"
                    class="w-4 h-4 text-primary-500 bg-dark-800 border-dark-600 rounded focus:ring-primary-500 focus:ring-2"
                  />
                  <span class="ml-2 text-sm text-white">Activar inmediatamente</span>
                </label>
                <p class="mt-1 text-xs text-dark-400">
                  Los topics activos se sincronizarán automáticamente
                </p>
              </div>

              <!-- Botones -->
              <div class="flex flex-col sm:flex-row sm:justify-end gap-3">
                <button
                  type="button"
                  @click="closeModal"
                  class="w-full sm:w-auto px-4 py-2 bg-dark-600 hover:bg-dark-500 text-white rounded-lg transition-colors order-2 sm:order-1"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  class="w-full sm:w-auto px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-colors order-1 sm:order-2"
                >
                  {{ modalMode === 'create' ? 'Crear' : 'Guardar' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
