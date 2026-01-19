import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { usePostsStore } from '../posts'
import type { Post, PostListResponse, Category } from '@/services/posts'

// Mock del PostService
vi.mock('@/services/posts', () => ({
  default: {
    list: vi.fn(),
    get: vi.fn(),
    toggleFavorite: vi.fn(),
    listCategories: vi.fn()
  }
}))

import postService from '@/services/posts'

describe('usePostsStore', () => {
  const mockPost: Post = {
    id: 1,
    reddit_id: 'abc123',
    title: 'Test Post',
    content: 'Test content',
    author: 'testuser',
    score: 100,
    url: 'https://reddit.com/test',
    created_at_reddit: '2024-01-01T00:00:00Z',
    subreddit: { id: 1, name: 'TestSubreddit' },
    analyzed: false,
    is_favorite: false
  }

  const mockPostListResponse: PostListResponse = {
    count: 1,
    items: [mockPost]
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
      const store = usePostsStore()

      expect(store.posts).toEqual([])
      expect(store.currentPost).toBeNull()
      expect(store.categories).toEqual([])
      expect(store.filters).toEqual({ page: 1, page_size: 20 })
      expect(store.pagination).toEqual({ count: 0 })
      expect(store.loading).toBe(false)
      expect(store.error).toBeNull()
    })
  })

  describe('getters', () => {
    it('filteredPosts retorna los posts', () => {
      const store = usePostsStore()
      store.posts = [mockPost]

      expect(store.filteredPosts).toEqual([mockPost])
    })

    it('favoriteCount cuenta los posts favoritos', () => {
      const store = usePostsStore()
      store.posts = [
        { ...mockPost, id: 1, is_favorite: true },
        { ...mockPost, id: 2, is_favorite: false },
        { ...mockPost, id: 3, is_favorite: true }
      ]

      expect(store.favoriteCount).toBe(2)
    })

    it('hasNextPage es true cuando hay más páginas', () => {
      const store = usePostsStore()
      store.pagination.count = 50
      store.filters.page = 1
      store.filters.page_size = 20

      expect(store.hasNextPage).toBe(true)
    })

    it('hasNextPage es false cuando estamos en la última página', () => {
      const store = usePostsStore()
      store.pagination.count = 20
      store.filters.page = 1
      store.filters.page_size = 20

      expect(store.hasNextPage).toBe(false)
    })

    it('hasPreviousPage es true cuando hay página anterior', () => {
      const store = usePostsStore()
      store.filters.page = 2

      expect(store.hasPreviousPage).toBe(true)
    })

    it('hasPreviousPage es false cuando estamos en página 1', () => {
      const store = usePostsStore()
      store.filters.page = 1

      expect(store.hasPreviousPage).toBe(false)
    })

    it('currentPage retorna la página actual', () => {
      const store = usePostsStore()
      store.filters.page = 3

      expect(store.currentPage).toBe(3)
    })

    it('totalPages calcula correctamente el total de páginas', () => {
      const store = usePostsStore()
      store.pagination.count = 45
      store.filters.page_size = 20

      expect(store.totalPages).toBe(3)
    })
  })

  describe('fetchPosts', () => {
    it('carga posts correctamente', async () => {
      vi.mocked(postService.list).mockResolvedValue(mockPostListResponse)

      const store = usePostsStore()
      await store.fetchPosts()

      expect(store.posts).toEqual([mockPost])
      expect(store.pagination.count).toBe(1)
      expect(store.error).toBeNull()
    })

    it('combina filtros nuevos con existentes', async () => {
      vi.mocked(postService.list).mockResolvedValue(mockPostListResponse)

      const store = usePostsStore()
      await store.fetchPosts({ subreddit: 'test', search: 'query' })

      expect(store.filters).toEqual({
        page: 1,
        page_size: 20,
        subreddit: 'test',
        search: 'query'
      })
      expect(postService.list).toHaveBeenCalledWith(store.filters)
    })

    it('maneja errores al cargar posts', async () => {
      vi.mocked(postService.list).mockRejectedValue(new Error('Error de red'))

      const store = usePostsStore()
      await store.fetchPosts()

      expect(store.posts).toEqual([])
      expect(store.error).toBe('Error de red')
    })

    it('muestra loading durante la carga', async () => {
      vi.mocked(postService.list).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve(mockPostListResponse), 100))
      )

      const store = usePostsStore()

      expect(store.loading).toBe(false)
      const fetchPromise = store.fetchPosts()
      expect(store.loading).toBe(true)

      await fetchPromise
      expect(store.loading).toBe(false)
    })
  })

  describe('fetchPost', () => {
    it('carga un post correctamente', async () => {
      vi.mocked(postService.get).mockResolvedValue(mockPost)

      const store = usePostsStore()
      await store.fetchPost(1)

      expect(store.currentPost).toEqual(mockPost)
      expect(store.error).toBeNull()
    })

    it('maneja errores al cargar un post', async () => {
      vi.mocked(postService.get).mockRejectedValue(new Error('Post no encontrado'))

      const store = usePostsStore()
      await store.fetchPost(999)

      expect(store.currentPost).toBeNull()
      expect(store.error).toBe('Post no encontrado')
    })
  })

  describe('toggleFavorite', () => {
    it('marca un post como favorito', async () => {
      vi.mocked(postService.toggleFavorite).mockResolvedValue({ is_favorite: true })

      const store = usePostsStore()
      store.posts = [mockPost]

      const result = await store.toggleFavorite(1)

      expect(result).toBe(true)
      expect(store.posts[0]?.is_favorite).toBe(true)
    })

    it('desmarca un post como favorito', async () => {
      vi.mocked(postService.toggleFavorite).mockResolvedValue({ is_favorite: false })

      const store = usePostsStore()
      store.posts = [{ ...mockPost, is_favorite: true }]

      const result = await store.toggleFavorite(1)

      expect(result).toBe(false)
      expect(store.posts[0]?.is_favorite).toBe(false)
    })

    it('actualiza currentPost si está cargado', async () => {
      vi.mocked(postService.toggleFavorite).mockResolvedValue({ is_favorite: true })

      const store = usePostsStore()
      store.currentPost = mockPost

      await store.toggleFavorite(1)

      expect(store.currentPost?.is_favorite).toBe(true)
    })

    it('maneja errores al marcar favorito', async () => {
      vi.mocked(postService.toggleFavorite).mockRejectedValue(new Error('Error de servidor'))

      const store = usePostsStore()
      const result = await store.toggleFavorite(1)

      expect(result).toBe(false)
      expect(store.error).toBe('Error de servidor')
    })
  })

  describe('fetchCategories', () => {
    it('carga categorías correctamente', async () => {
      vi.mocked(postService.listCategories).mockResolvedValue([mockCategory])

      const store = usePostsStore()
      await store.fetchCategories()

      expect(store.categories).toEqual([mockCategory])
      expect(store.error).toBeNull()
    })

    it('maneja errores al cargar categorías', async () => {
      vi.mocked(postService.listCategories).mockRejectedValue(new Error('Error de red'))

      const store = usePostsStore()
      await store.fetchCategories()

      expect(store.categories).toEqual([])
      expect(store.error).toBe('Error de red')
    })
  })

  describe('setFilters', () => {
    it('actualiza los filtros correctamente', () => {
      const store = usePostsStore()

      store.setFilters({ subreddit: 'test', search: 'query' })

      expect(store.filters).toEqual({
        page: 1,
        page_size: 20,
        subreddit: 'test',
        search: 'query'
      })
    })
  })

  describe('resetFilters', () => {
    it('resetea los filtros a valores por defecto', () => {
      const store = usePostsStore()
      store.filters = { page: 5, page_size: 50, subreddit: 'test' }

      store.resetFilters()

      expect(store.filters).toEqual({ page: 1, page_size: 20 })
    })
  })

  describe('paginación', () => {
    beforeEach(() => {
      vi.mocked(postService.list).mockResolvedValue(mockPostListResponse)
    })

    it('nextPage incrementa la página si hay siguiente', async () => {
      const store = usePostsStore()
      store.pagination.count = 50
      store.filters.page = 1
      store.filters.page_size = 20

      store.nextPage()

      expect(store.filters.page).toBe(2)
    })

    it('nextPage no hace nada si no hay página siguiente', async () => {
      const store = usePostsStore()
      store.pagination.count = 20
      store.filters.page = 1
      store.filters.page_size = 20

      store.nextPage()

      expect(store.filters.page).toBe(1)
      expect(postService.list).not.toHaveBeenCalled()
    })

    it('previousPage decrementa la página si hay anterior', async () => {
      const store = usePostsStore()
      store.filters.page = 2

      store.previousPage()

      expect(store.filters.page).toBe(1)
    })

    it('previousPage no hace nada si está en página 1', async () => {
      const store = usePostsStore()
      store.filters.page = 1

      store.previousPage()

      expect(store.filters.page).toBe(1)
      expect(postService.list).not.toHaveBeenCalled()
    })

    it('goToPage va a una página específica', async () => {
      const store = usePostsStore()
      store.pagination.count = 100
      store.filters.page_size = 20

      store.goToPage(3)

      expect(store.filters.page).toBe(3)
    })

    it('goToPage no hace nada si la página es inválida', async () => {
      const store = usePostsStore()
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
      const store = usePostsStore()
      store.error = 'Algún error'

      store.clearError()

      expect(store.error).toBeNull()
    })
  })

  describe('clearCurrentPost', () => {
    it('limpia el post actual', () => {
      const store = usePostsStore()
      store.currentPost = mockPost

      store.clearCurrentPost()

      expect(store.currentPost).toBeNull()
    })
  })
})

// Ejecutar este test:
//   cd frontend && npm run test -- src/stores/__tests__/posts.spec.ts
//
// Ejecutar todos los tests:
//   cd frontend && npm run test
