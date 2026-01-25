import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useProductsStore } from '../products'
import type { Product, ProductListResponse, Category } from '@/services/products'

// Mock del ProductService
vi.mock('@/services/products', () => ({
  default: {
    list: vi.fn(),
    get: vi.fn(),
    toggleFavorite: vi.fn(),
    listCategories: vi.fn()
  }
}))

import productService from '@/services/products'

describe('useProductsStore', () => {
  const mockProduct: Product = {
    id: 1,
    external_id: 'abc123',
    title: 'Test Product',
    tagline: 'Test tagline',
    content: 'Test content',
    author: 'testuser',
    score: 100,
    votes_count: 100,
    comments_count: 10,
    url: 'https://producthunt.com/test',
    website: 'https://example.com',
    created_at_source: '2024-01-01T00:00:00Z',
    topic: { id: 1, name: 'artificial-intelligence' },
    analyzed: false,
    is_favorite: false
  }

  const mockProductListResponse: ProductListResponse = {
    count: 1,
    items: [mockProduct]
  }

  const mockCategory: Category = {
    id: 1,
    name: 'Test Category',
    description: 'Test description'
  }

  beforeEach(() => {
    vi.clearAllMocks()
    setActivePinia(createPinia())
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('estado inicial', () => {
    it('tiene valores por defecto correctos', () => {
      const store = useProductsStore()

      expect(store.products).toEqual([])
      expect(store.currentProduct).toBeNull()
      expect(store.categories).toEqual([])
      expect(store.filters).toEqual({ page: 1, page_size: 20 })
      expect(store.pagination).toEqual({ count: 0 })
      expect(store.loading).toBe(false)
      expect(store.error).toBeNull()
    })
  })

  describe('getters', () => {
    it('filteredProducts retorna los productos', () => {
      const store = useProductsStore()
      store.products = [mockProduct]

      expect(store.filteredProducts).toEqual([mockProduct])
    })

    it('favoriteCount cuenta los productos favoritos', () => {
      const store = useProductsStore()
      store.products = [
        { ...mockProduct, id: 1, is_favorite: true },
        { ...mockProduct, id: 2, is_favorite: false },
        { ...mockProduct, id: 3, is_favorite: true }
      ]

      expect(store.favoriteCount).toBe(2)
    })

    it('hasNextPage es true cuando hay más páginas', () => {
      const store = useProductsStore()
      store.pagination.count = 50
      store.filters.page = 1
      store.filters.page_size = 20

      expect(store.hasNextPage).toBe(true)
    })

    it('hasNextPage es false cuando estamos en la última página', () => {
      const store = useProductsStore()
      store.pagination.count = 20
      store.filters.page = 1
      store.filters.page_size = 20

      expect(store.hasNextPage).toBe(false)
    })

    it('hasPreviousPage es true cuando hay página anterior', () => {
      const store = useProductsStore()
      store.filters.page = 2

      expect(store.hasPreviousPage).toBe(true)
    })

    it('hasPreviousPage es false cuando estamos en página 1', () => {
      const store = useProductsStore()
      store.filters.page = 1

      expect(store.hasPreviousPage).toBe(false)
    })

    it('currentPage retorna la página actual', () => {
      const store = useProductsStore()
      store.filters.page = 3

      expect(store.currentPage).toBe(3)
    })

    it('totalPages calcula correctamente el total de páginas', () => {
      const store = useProductsStore()
      store.pagination.count = 45
      store.filters.page_size = 20

      expect(store.totalPages).toBe(3)
    })
  })

  describe('fetchProducts', () => {
    it('carga productos correctamente', async () => {
      vi.mocked(productService.list).mockResolvedValue(mockProductListResponse)

      const store = useProductsStore()
      await store.fetchProducts()

      expect(store.products).toEqual([mockProduct])
      expect(store.pagination.count).toBe(1)
      expect(store.error).toBeNull()
    })

    it('combina filtros nuevos con existentes', async () => {
      vi.mocked(productService.list).mockResolvedValue(mockProductListResponse)

      const store = useProductsStore()
      await store.fetchProducts({ topic: 'test', search: 'query' })

      expect(store.filters).toEqual({
        page: 1,
        page_size: 20,
        topic: 'test',
        search: 'query'
      })
      expect(productService.list).toHaveBeenCalledWith(store.filters)
    })

    it('maneja errores al cargar productos', async () => {
      vi.mocked(productService.list).mockRejectedValue(new Error('Error de red'))

      const store = useProductsStore()
      await store.fetchProducts()

      expect(store.products).toEqual([])
      expect(store.error).toBe('Error de red')
    })

    it('muestra loading durante la carga', async () => {
      vi.mocked(productService.list).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve(mockProductListResponse), 100))
      )

      const store = useProductsStore()

      expect(store.loading).toBe(false)
      const fetchPromise = store.fetchProducts()
      expect(store.loading).toBe(true)

      await fetchPromise
      expect(store.loading).toBe(false)
    })
  })

  describe('fetchProduct', () => {
    it('carga un producto correctamente', async () => {
      vi.mocked(productService.get).mockResolvedValue(mockProduct)

      const store = useProductsStore()
      await store.fetchProduct(1)

      expect(store.currentProduct).toEqual(mockProduct)
      expect(store.error).toBeNull()
    })

    it('maneja errores al cargar un producto', async () => {
      vi.mocked(productService.get).mockRejectedValue(new Error('Producto no encontrado'))

      const store = useProductsStore()
      await store.fetchProduct(999)

      expect(store.currentProduct).toBeNull()
      expect(store.error).toBe('Producto no encontrado')
    })
  })

  describe('toggleFavorite', () => {
    it('marca un producto como favorito', async () => {
      vi.mocked(productService.toggleFavorite).mockResolvedValue({ is_favorite: true })

      const store = useProductsStore()
      store.products = [mockProduct]

      const result = await store.toggleFavorite(1)

      expect(result).toBe(true)
      expect(store.products[0]?.is_favorite).toBe(true)
    })

    it('desmarca un producto como favorito', async () => {
      vi.mocked(productService.toggleFavorite).mockResolvedValue({ is_favorite: false })

      const store = useProductsStore()
      store.products = [{ ...mockProduct, is_favorite: true }]

      const result = await store.toggleFavorite(1)

      expect(result).toBe(false)
      expect(store.products[0]?.is_favorite).toBe(false)
    })

    it('actualiza currentProduct si está cargado', async () => {
      vi.mocked(productService.toggleFavorite).mockResolvedValue({ is_favorite: true })

      const store = useProductsStore()
      store.currentProduct = mockProduct

      await store.toggleFavorite(1)

      expect(store.currentProduct?.is_favorite).toBe(true)
    })

    it('maneja errores al marcar favorito', async () => {
      vi.mocked(productService.toggleFavorite).mockRejectedValue(new Error('Error de servidor'))

      const store = useProductsStore()
      const result = await store.toggleFavorite(1)

      expect(result).toBe(false)
      expect(store.error).toBe('Error de servidor')
    })
  })

  describe('fetchCategories', () => {
    it('carga categorías correctamente', async () => {
      vi.mocked(productService.listCategories).mockResolvedValue([mockCategory])

      const store = useProductsStore()
      await store.fetchCategories()

      expect(store.categories).toEqual([mockCategory])
      expect(store.error).toBeNull()
    })

    it('maneja errores al cargar categorías', async () => {
      vi.mocked(productService.listCategories).mockRejectedValue(new Error('Error de red'))

      const store = useProductsStore()
      await store.fetchCategories()

      expect(store.categories).toEqual([])
      expect(store.error).toBe('Error de red')
    })
  })

  describe('setFilters', () => {
    it('actualiza los filtros correctamente', () => {
      const store = useProductsStore()

      store.setFilters({ topic: 'test', search: 'query' })

      expect(store.filters).toEqual({
        page: 1,
        page_size: 20,
        topic: 'test',
        search: 'query'
      })
    })
  })

  describe('resetFilters', () => {
    it('resetea los filtros a valores por defecto', () => {
      const store = useProductsStore()
      store.filters = { page: 5, page_size: 50, topic: 'test' }

      store.resetFilters()

      expect(store.filters).toEqual({ page: 1, page_size: 20 })
    })
  })

  describe('paginación', () => {
    beforeEach(() => {
      vi.mocked(productService.list).mockResolvedValue(mockProductListResponse)
    })

    it('nextPage incrementa la página si hay siguiente', async () => {
      const store = useProductsStore()
      store.pagination.count = 50
      store.filters.page = 1
      store.filters.page_size = 20

      store.nextPage()

      expect(store.filters.page).toBe(2)
    })

    it('nextPage no hace nada si no hay página siguiente', async () => {
      const store = useProductsStore()
      store.pagination.count = 20
      store.filters.page = 1
      store.filters.page_size = 20

      store.nextPage()

      expect(store.filters.page).toBe(1)
      expect(productService.list).not.toHaveBeenCalled()
    })

    it('previousPage decrementa la página si hay anterior', async () => {
      const store = useProductsStore()
      store.filters.page = 2

      store.previousPage()

      expect(store.filters.page).toBe(1)
    })

    it('previousPage no hace nada si está en página 1', async () => {
      const store = useProductsStore()
      store.filters.page = 1

      store.previousPage()

      expect(store.filters.page).toBe(1)
      expect(productService.list).not.toHaveBeenCalled()
    })

    it('goToPage va a una página específica', async () => {
      const store = useProductsStore()
      store.pagination.count = 100
      store.filters.page_size = 20

      store.goToPage(3)

      expect(store.filters.page).toBe(3)
    })

    it('goToPage no hace nada si la página es inválida', async () => {
      const store = useProductsStore()
      store.pagination.count = 100
      store.filters.page_size = 20
      store.filters.page = 2

      store.goToPage(0)
      expect(store.filters.page).toBe(2)

      store.goToPage(10)
      expect(store.filters.page).toBe(2)
    })
  })

  describe('clearError', () => {
    it('limpia el error', () => {
      const store = useProductsStore()
      store.error = 'Algún error'

      store.clearError()

      expect(store.error).toBeNull()
    })
  })

  describe('clearCurrentProduct', () => {
    it('limpia el producto actual', () => {
      const store = useProductsStore()
      store.currentProduct = mockProduct

      store.clearCurrentProduct()

      expect(store.currentProduct).toBeNull()
    })
  })
})

// Ejecutar: cd frontend && npm run test -- src/stores/__tests__/products.spec.ts
