import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import subredditService, { type Subreddit } from '@/services/subreddits'

export const useSubredditsStore = defineStore('subreddits', () => {
  // State
  const subreddits = ref<Subreddit[]>([])
  const currentSubreddit = ref<Subreddit | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const activeSubreddits = computed(() => {
    return subreddits.value.filter((s) => s.is_active)
  })

  const inactiveSubreddits = computed(() => {
    return subreddits.value.filter((s) => !s.is_active)
  })

  const totalCount = computed(() => subreddits.value.length)
  const activeCount = computed(() => activeSubreddits.value.length)

  // Actions
  async function fetchSubreddits(): Promise<void> {
    loading.value = true
    error.value = null

    try {
      subreddits.value = await subredditService.list()
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Error al cargar subreddits'
      error.value = errorMessage
      subreddits.value = []
    } finally {
      loading.value = false
    }
  }

  async function fetchSubreddit(id: number): Promise<void> {
    loading.value = true
    error.value = null

    try {
      currentSubreddit.value = await subredditService.get(id)
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Error al cargar el subreddit'
      error.value = errorMessage
      currentSubreddit.value = null
    } finally {
      loading.value = false
    }
  }

  async function createSubreddit(name: string, is_active: boolean = true): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      const newSubreddit = await subredditService.create({ name, is_active })
      subreddits.value.push(newSubreddit)
      return true
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Error al crear subreddit'
      error.value = errorMessage
      return false
    } finally {
      loading.value = false
    }
  }

  async function updateSubreddit(id: number, data: { name?: string; is_active?: boolean }): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      const updated = await subredditService.update(id, data)

      // Actualizar en la lista
      const index = subreddits.value.findIndex((s) => s.id === id)
      if (index !== -1) {
        subreddits.value[index] = updated
      }

      // Actualizar el subreddit actual si está cargado
      if (currentSubreddit.value?.id === id) {
        currentSubreddit.value = updated
      }

      return true
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Error al actualizar subreddit'
      error.value = errorMessage
      return false
    } finally {
      loading.value = false
    }
  }

  async function deleteSubreddit(id: number): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      await subredditService.delete(id)

      // Eliminar de la lista
      subreddits.value = subreddits.value.filter((s) => s.id !== id)

      // Limpiar el subreddit actual si es el eliminado
      if (currentSubreddit.value?.id === id) {
        currentSubreddit.value = null
      }

      return true
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Error al eliminar subreddit'
      error.value = errorMessage
      return false
    } finally {
      loading.value = false
    }
  }

  async function toggleActive(id: number): Promise<boolean> {
    const subreddit = subreddits.value.find((s) => s.id === id)
    if (!subreddit) {
      error.value = 'Subreddit no encontrado'
      return false
    }

    return await updateSubreddit(id, { is_active: !subreddit.is_active })
  }

  function clearError(): void {
    error.value = null
  }

  function clearCurrentSubreddit(): void {
    currentSubreddit.value = null
  }

  return {
    // State
    subreddits,
    currentSubreddit,
    loading,
    error,
    // Getters
    activeSubreddits,
    inactiveSubreddits,
    totalCount,
    activeCount,
    // Actions
    fetchSubreddits,
    fetchSubreddit,
    createSubreddit,
    updateSubreddit,
    deleteSubreddit,
    toggleActive,
    clearError,
    clearCurrentSubreddit
  }
})
