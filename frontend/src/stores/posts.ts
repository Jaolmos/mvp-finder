import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import postService, {
  type Post,
  type PostFilters,
  type PostListResponse,
  type Category
} from '@/services/posts'

export const usePostsStore = defineStore('posts', () => {
  // State
  const posts = ref<Post[]>([])
  const currentPost = ref<Post | null>(null)
  const categories = ref<Category[]>([])
  const filters = ref<PostFilters>({
    page: 1,
    page_size: 20
  })
  const pagination = ref({
    count: 0,
    next: null as string | null,
    previous: null as string | null
  })
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const filteredPosts = computed(() => {
    // Los posts ya vienen filtrados del backend
    return posts.value
  })

  const favoriteCount = computed(() => {
    return posts.value.filter((post) => post.is_favorite).length
  })

  const hasNextPage = computed(() => !!pagination.value.next)
  const hasPreviousPage = computed(() => !!pagination.value.previous)
  const currentPage = computed(() => filters.value.page || 1)
  const totalPages = computed(() => {
    const pageSize = filters.value.page_size || 20
    return Math.ceil(pagination.value.count / pageSize)
  })

  // Actions
  async function fetchPosts(newFilters?: Partial<PostFilters>): Promise<void> {
    loading.value = true
    error.value = null

    try {
      // Combinar nuevos filtros con los existentes
      if (newFilters) {
        filters.value = { ...filters.value, ...newFilters }
      }

      const response: PostListResponse = await postService.list(filters.value)
      posts.value = response.results
      pagination.value = {
        count: response.count,
        next: response.next,
        previous: response.previous
      }
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Error al cargar posts'
      error.value = errorMessage
      posts.value = []
    } finally {
      loading.value = false
    }
  }

  async function fetchPost(id: number): Promise<void> {
    loading.value = true
    error.value = null

    try {
      currentPost.value = await postService.get(id)
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Error al cargar el post'
      error.value = errorMessage
      currentPost.value = null
    } finally {
      loading.value = false
    }
  }

  async function toggleFavorite(id: number): Promise<boolean> {
    try {
      const result = await postService.toggleFavorite(id)

      // Actualizar el post en la lista
      const postIndex = posts.value.findIndex((p) => p.id === id)
      if (postIndex !== -1) {
        posts.value[postIndex].is_favorite = result.is_favorite
      }

      // Actualizar el post actual si está cargado
      if (currentPost.value?.id === id) {
        currentPost.value.is_favorite = result.is_favorite
      }

      return result.is_favorite
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Error al marcar favorito'
      error.value = errorMessage
      return false
    }
  }

  async function fetchCategories(): Promise<void> {
    try {
      categories.value = await postService.listCategories()
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Error al cargar categorías'
      error.value = errorMessage
      categories.value = []
    }
  }

  function setFilters(newFilters: Partial<PostFilters>): void {
    filters.value = { ...filters.value, ...newFilters }
  }

  function resetFilters(): void {
    filters.value = {
      page: 1,
      page_size: 20
    }
  }

  function nextPage(): void {
    if (hasNextPage.value) {
      filters.value.page = (filters.value.page || 1) + 1
      fetchPosts()
    }
  }

  function previousPage(): void {
    if (hasPreviousPage.value && (filters.value.page || 1) > 1) {
      filters.value.page = (filters.value.page || 1) - 1
      fetchPosts()
    }
  }

  function goToPage(page: number): void {
    if (page > 0 && page <= totalPages.value) {
      filters.value.page = page
      fetchPosts()
    }
  }

  function clearError(): void {
    error.value = null
  }

  function clearCurrentPost(): void {
    currentPost.value = null
  }

  return {
    // State
    posts,
    currentPost,
    categories,
    filters,
    pagination,
    loading,
    error,
    // Getters
    filteredPosts,
    favoriteCount,
    hasNextPage,
    hasPreviousPage,
    currentPage,
    totalPages,
    // Actions
    fetchPosts,
    fetchPost,
    toggleFavorite,
    fetchCategories,
    setFilters,
    resetFilters,
    nextPage,
    previousPage,
    goToPage,
    clearError,
    clearCurrentPost
  }
})
