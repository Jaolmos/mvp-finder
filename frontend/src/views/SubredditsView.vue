<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import AppLayout from '@/layouts/AppLayout.vue'
import { useSubredditsStore } from '@/stores/subreddits'

const subredditsStore = useSubredditsStore()

// Estado del modal
const showModal = ref(false)
const modalMode = ref<'create' | 'edit'>('create')
const editingId = ref<number | null>(null)

// Formulario
const formData = ref({
  name: '',
  is_active: true
})

// Cargar subreddits al montar
onMounted(async () => {
  await subredditsStore.fetchSubreddits()
})

// Computed para obtener listas de subreddits
const subreddits = computed(() => subredditsStore.subreddits)
const loading = computed(() => subredditsStore.loading)
const error = computed(() => subredditsStore.error)

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
    name: name.replace(/^r\//, ''), // Quitar r/ si existe
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
  subredditsStore.clearError()
}

// Guardar (crear o editar)
const handleSave = async () => {
  // Validar nombre
  const name = formData.value.name.trim()
  if (!name) {
    return
  }

  // Asegurar formato r/nombre
  const subredditName = name.startsWith('r/') ? name.slice(2) : name

  let success = false
  if (modalMode.value === 'create') {
    success = await subredditsStore.createSubreddit(subredditName, formData.value.is_active)
  } else if (editingId.value !== null) {
    success = await subredditsStore.updateSubreddit(editingId.value, {
      name: subredditName,
      is_active: formData.value.is_active
    })
  }

  if (success) {
    closeModal()
  }
}

// Toggle activo/inactivo
const handleToggleActive = async (id: number) => {
  await subredditsStore.toggleActive(id)
}

// Eliminar subreddit
const handleDelete = async (id: number, name: string) => {
  if (confirm(`¿Estás seguro de eliminar r/${name}?`)) {
    await subredditsStore.deleteSubreddit(id)
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
</script>

<template>
  <AppLayout>
    <div>
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 mb-6">
        <h1 class="text-xl md:text-2xl font-bold text-white">Subreddits</h1>
        <button
          @click="openCreateModal"
          class="w-full sm:w-auto px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white font-medium rounded-lg transition-colors"
        >
          + Añadir Subreddit
        </button>
      </div>

      <!-- Estado de carga -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="text-dark-400">Cargando subreddits...</div>
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
        v-else-if="subreddits.length === 0"
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
          <p class="text-lg mb-2">No hay subreddits configurados</p>
          <p class="text-sm">Añade subreddits para comenzar a monitorear posts de Reddit</p>
        </div>
      </div>

      <!-- Tabla de subreddits -->
      <div v-else class="bg-dark-700 rounded-lg border border-dark-600 shadow-lg overflow-hidden">
        <!-- Wrapper con scroll horizontal en móvil -->
        <div class="overflow-x-auto">
        <table class="w-full min-w-[640px]">
          <thead class="bg-dark-800">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-dark-300 uppercase tracking-wider">
                Subreddit
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
              v-for="subreddit in subreddits"
              :key="subreddit.id"
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
                      d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"
                    />
                  </svg>
                  <span class="text-white font-medium">r/{{ subreddit.name }}</span>
                </div>
              </td>

              <!-- Estado -->
              <td class="px-6 py-4 whitespace-nowrap">
                <button
                  @click="handleToggleActive(subreddit.id)"
                  class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium transition-colors"
                  :class="
                    subreddit.is_active
                      ? 'bg-green-500/20 text-green-400 hover:bg-green-500/30'
                      : 'bg-dark-600 text-dark-400 hover:bg-dark-500'
                  "
                >
                  <span
                    class="w-2 h-2 rounded-full mr-2"
                    :class="subreddit.is_active ? 'bg-green-400' : 'bg-dark-400'"
                  ></span>
                  {{ subreddit.is_active ? 'Activo' : 'Inactivo' }}
                </button>
              </td>

              <!-- Última sincronización -->
              <td class="px-6 py-4 whitespace-nowrap text-sm text-dark-300">
                {{ subreddit.last_sync ? formatDate(subreddit.last_sync) : 'Nunca' }}
              </td>

              <!-- Creado -->
              <td class="px-6 py-4 whitespace-nowrap text-sm text-dark-400">
                {{ formatDate(subreddit.created_at) }}
              </td>

              <!-- Acciones -->
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button
                  @click="openEditModal(subreddit.id, subreddit.name, subreddit.is_active)"
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
                  @click="handleDelete(subreddit.id, subreddit.name)"
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
                {{ modalMode === 'create' ? 'Añadir Subreddit' : 'Editar Subreddit' }}
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
                  Nombre del Subreddit
                </label>
                <div class="relative">
                  <span class="absolute left-3 top-2 text-dark-400">r/</span>
                  <input
                    id="name"
                    v-model="formData.name"
                    type="text"
                    required
                    placeholder="ejemplo: SomebodyMakeThis"
                    class="w-full pl-10 pr-4 py-2 bg-dark-800 border border-dark-600 rounded-lg text-white placeholder-dark-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                <p class="mt-1 text-xs text-dark-400">
                  Nombre sin el prefijo r/ (se añadirá automáticamente)
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
                  Los subreddits activos se sincronizarán automáticamente
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
