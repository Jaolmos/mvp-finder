import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import topicService, { type Topic } from '@/services/topics'

export const useTopicsStore = defineStore('topics', () => {
  // State
  const topics = ref<Topic[]>([])
  const currentTopic = ref<Topic | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const activeTopics = computed(() => {
    return topics.value.filter((t) => t.is_active)
  })

  const inactiveTopics = computed(() => {
    return topics.value.filter((t) => !t.is_active)
  })

  const totalCount = computed(() => topics.value.length)
  const activeCount = computed(() => activeTopics.value.length)

  // Actions
  async function fetchTopics(): Promise<void> {
    loading.value = true
    error.value = null

    try {
      topics.value = await topicService.list()
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Error al cargar topics'
      error.value = errorMessage
      topics.value = []
    } finally {
      loading.value = false
    }
  }

  async function fetchTopic(id: number): Promise<void> {
    loading.value = true
    error.value = null

    try {
      currentTopic.value = await topicService.get(id)
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Error al cargar el topic'
      error.value = errorMessage
      currentTopic.value = null
    } finally {
      loading.value = false
    }
  }

  async function createTopic(name: string, is_active: boolean = true): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      const newTopic = await topicService.create({ name, is_active })
      topics.value.push(newTopic)
      return true
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Error al crear topic'
      error.value = errorMessage
      return false
    } finally {
      loading.value = false
    }
  }

  async function updateTopic(id: number, data: { name?: string; is_active?: boolean }): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      const updated = await topicService.update(id, data)

      // Actualizar en la lista
      const index = topics.value.findIndex((t) => t.id === id)
      if (index !== -1) {
        topics.value[index] = updated
      }

      // Actualizar el topic actual si está cargado
      if (currentTopic.value?.id === id) {
        currentTopic.value = updated
      }

      return true
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Error al actualizar topic'
      error.value = errorMessage
      return false
    } finally {
      loading.value = false
    }
  }

  async function deleteTopic(id: number): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      await topicService.delete(id)

      // Eliminar de la lista
      topics.value = topics.value.filter((t) => t.id !== id)

      // Limpiar el topic actual si es el eliminado
      if (currentTopic.value?.id === id) {
        currentTopic.value = null
      }

      return true
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Error al eliminar topic'
      error.value = errorMessage
      return false
    } finally {
      loading.value = false
    }
  }

  async function toggleActive(id: number): Promise<boolean> {
    const topic = topics.value.find((t) => t.id === id)
    if (!topic) {
      error.value = 'Topic no encontrado'
      return false
    }

    return await updateTopic(id, { is_active: !topic.is_active })
  }

  function clearError(): void {
    error.value = null
  }

  function clearCurrentTopic(): void {
    currentTopic.value = null
  }

  return {
    // State
    topics,
    currentTopic,
    loading,
    error,
    // Getters
    activeTopics,
    inactiveTopics,
    totalCount,
    activeCount,
    // Actions
    fetchTopics,
    fetchTopic,
    createTopic,
    updateTopic,
    deleteTopic,
    toggleActive,
    clearError,
    clearCurrentTopic
  }
})
