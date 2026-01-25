import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import productService, {
  type Product,
  type ProductFilters,
  type ProductListResponse,
  type Category
} from '@/services/products'

export const useProductsStore = defineStore('products', () => {
  // State
  const products = ref<Product[]>([])
  const currentProduct = ref<Product | null>(null)
  const categories = ref<Category[]>([])
  const filters = ref<ProductFilters>({
    page: 1,
    page_size: 20
  })
  const pagination = ref({
    count: 0
  })
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const filteredProducts = computed(() => {
    // Los productos ya vienen filtrados del backend
    return products.value
  })

  const favoriteCount = computed(() => {
    return products.value.filter((product) => product.is_favorite).length
  })

  const hasNextPage = computed(() => {
    const pageSize = filters.value.page_size || 20
    const currentPageNum = filters.value.page || 1
    return currentPageNum * pageSize < pagination.value.count
  })
  const hasPreviousPage = computed(() => (filters.value.page || 1) > 1)
  const currentPage = computed(() => filters.value.page || 1)
  const totalPages = computed(() => {
    const pageSize = filters.value.page_size || 20
    return Math.ceil(pagination.value.count / pageSize)
  })

  // Actions
  async function fetchProducts(newFilters?: Partial<ProductFilters>): Promise<void> {
    loading.value = true
    error.value = null

    try {
      // Combinar nuevos filtros con los existentes
      if (newFilters) {
        filters.value = { ...filters.value, ...newFilters }
      }

      const response: ProductListResponse = await productService.list(filters.value)
      products.value = response.items
      pagination.value = {
        count: response.count
      }
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Error al cargar productos'
      error.value = errorMessage
      products.value = []
    } finally {
      loading.value = false
    }
  }

  async function fetchProduct(id: number): Promise<void> {
    loading.value = true
    error.value = null

    try {
      currentProduct.value = await productService.get(id)
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Error al cargar el producto'
      error.value = errorMessage
      currentProduct.value = null
    } finally {
      loading.value = false
    }
  }

  async function toggleFavorite(id: number): Promise<boolean> {
    try {
      const result = await productService.toggleFavorite(id)

      // Actualizar el producto en la lista
      const productIndex = products.value.findIndex((p) => p.id === id)
      if (productIndex !== -1 && products.value[productIndex]) {
        products.value[productIndex].is_favorite = result.is_favorite
      }

      // Actualizar el producto actual si está cargado
      if (currentProduct.value?.id === id) {
        currentProduct.value.is_favorite = result.is_favorite
      }

      return result.is_favorite
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Error al marcar favorito'
      error.value = errorMessage
      return false
    }
  }

  async function deleteProduct(id: number): Promise<boolean> {
    try {
      await productService.delete(id)

      // Eliminar de la lista local
      products.value = products.value.filter((p) => p.id !== id)

      // Limpiar producto actual si es el eliminado
      if (currentProduct.value?.id === id) {
        currentProduct.value = null
      }

      return true
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Error al eliminar el producto'
      error.value = errorMessage
      return false
    }
  }

  async function fetchCategories(): Promise<void> {
    try {
      categories.value = await productService.listCategories()
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Error al cargar categorías'
      error.value = errorMessage
      categories.value = []
    }
  }

  function setFilters(newFilters: Partial<ProductFilters>): void {
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
      fetchProducts()
    }
  }

  function previousPage(): void {
    if (hasPreviousPage.value && (filters.value.page || 1) > 1) {
      filters.value.page = (filters.value.page || 1) - 1
      fetchProducts()
    }
  }

  function goToPage(page: number): void {
    if (page > 0 && page <= totalPages.value) {
      filters.value.page = page
      fetchProducts()
    }
  }

  function clearError(): void {
    error.value = null
  }

  function clearCurrentProduct(): void {
    currentProduct.value = null
  }

  return {
    // State
    products,
    currentProduct,
    categories,
    filters,
    pagination,
    loading,
    error,
    // Getters
    filteredProducts,
    favoriteCount,
    hasNextPage,
    hasPreviousPage,
    currentPage,
    totalPages,
    // Actions
    fetchProducts,
    fetchProduct,
    deleteProduct,
    toggleFavorite,
    fetchCategories,
    setFilters,
    resetFilters,
    nextPage,
    previousPage,
    goToPage,
    clearError,
    clearCurrentProduct
  }
})
