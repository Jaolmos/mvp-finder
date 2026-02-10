import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { createRouter, createMemoryHistory } from 'vue-router'
import ProductsView from '../ProductsView.vue'
import { useProductsStore } from '@/stores/products'
import type { ProductListItem } from '@/services/products'

// Mock de AppLayout
vi.mock('@/layouts/AppLayout.vue', () => ({
  default: {
    name: 'AppLayout',
    template: '<div class="app-layout"><slot /></div>'
  }
}))

// Mock de ProductCard
vi.mock('@/components/ProductCard.vue', () => ({
  default: {
    name: 'ProductCard',
    template: '<div class="product-card">{{ product.title }}</div>',
    props: ['product']
  }
}))

// Mock de useToast
vi.mock('@/composables/useToast', () => ({
  useToast: () => ({
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
    warning: vi.fn()
  })
}))

// Mock de las rutas
const routes = [
  { path: '/products', name: 'products', component: ProductsView },
  { path: '/products/:id', name: 'product-detail', component: { template: '<div>Detail</div>' } }
]

describe('ProductsView - Búsqueda en tiempo real', () => {
  let router: ReturnType<typeof createRouter>

  const mockProducts: ProductListItem[] = [
    {
      id: 1,
      external_id: 'ph-123',
      title: 'Test Product AI',
      tagline: 'AI assistant',
      content: 'An AI product',
      author: 'testuser',
      score: 150,
      votes_count: 150,
      comments_count: 25,
      url: 'https://producthunt.com/posts/test',
      website: 'https://test.com',
      created_at_source: '2024-01-15T10:00:00Z',
      topic: { id: 1, name: 'artificial-intelligence' },
      is_favorite: false,
      analyzed: false,
      potential_score: null,
      has_note: false
    }
  ]

  beforeEach(() => {
    vi.useFakeTimers()

    router = createRouter({
      history: createMemoryHistory(),
      routes
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.clearAllTimers()
  })

  it('typing dispara búsqueda debounced después de 400ms', async () => {
    const wrapper = mount(ProductsView, {
      global: {
        plugins: [
          createTestingPinia({
            createSpy: vi.fn,
            initialState: {
              products: {
                products: mockProducts,
                totalProducts: 1,
                totalPages: 1,
                currentPage: 1
              }
            }
          }),
          router
        ]
      }
    })

    await router.isReady()
    await flushPromises()

    const store = useProductsStore()
    const spy = vi.spyOn(store, 'fetchProducts')

    // Limpiar llamadas del mount/watch inicial
    spy.mockClear()

    // Encontrar el input de búsqueda
    const searchInput = wrapper.find('input[type="text"]')
    expect(searchInput.exists()).toBe(true)

    // Escribir en el input
    await searchInput.setValue('ai assistant')

    // No debe dispararse inmediatamente
    expect(spy).not.toHaveBeenCalled()

    // Avanzar 399ms - aún no debe dispararse
    vi.advanceTimersByTime(399)
    await flushPromises()
    expect(spy).not.toHaveBeenCalled()

    // Avanzar 1ms más (total 400ms) - debe dispararse
    vi.advanceTimersByTime(1)
    await flushPromises()
    expect(spy).toHaveBeenCalled()
    expect(spy).toHaveBeenCalledWith(expect.objectContaining({
      search: 'ai assistant'
    }))
  })

  it('typing rápido solo dispara una búsqueda (debounce funciona)', async () => {
    const wrapper = mount(ProductsView, {
      global: {
        plugins: [
          createTestingPinia({
            createSpy: vi.fn,
            initialState: {
              products: {
                products: mockProducts,
                totalProducts: 1,
                totalPages: 1,
                currentPage: 1
              }
            }
          }),
          router
        ]
      }
    })

    await router.isReady()
    await flushPromises()

    const store = useProductsStore()
    const spy = vi.spyOn(store, 'fetchProducts')

    // Limpiar llamadas del mount/watch inicial
    spy.mockClear()

    const searchInput = wrapper.find('input[type="text"]')

    // Escribir múltiples veces rápido
    await searchInput.setValue('a')
    vi.advanceTimersByTime(100)

    await searchInput.setValue('ai')
    vi.advanceTimersByTime(100)

    await searchInput.setValue('ai ')
    vi.advanceTimersByTime(100)

    await searchInput.setValue('ai assistant')

    // No debe haberse disparado aún
    expect(spy).not.toHaveBeenCalled()

    // Avanzar 400ms desde la última escritura
    vi.advanceTimersByTime(400)
    await flushPromises()

    // Solo debe haberse llamado una vez con el valor final
    expect(spy).toHaveBeenCalledTimes(1)
    expect(spy).toHaveBeenCalledWith(expect.objectContaining({
      search: 'ai assistant'
    }))
  })

  it('presionar Enter bypasea debounce (búsqueda inmediata)', async () => {
    const wrapper = mount(ProductsView, {
      global: {
        plugins: [
          createTestingPinia({
            createSpy: vi.fn,
            initialState: {
              products: {
                products: mockProducts,
                totalProducts: 1,
                totalPages: 1,
                currentPage: 1
              }
            }
          }),
          router
        ]
      }
    })

    await router.isReady()
    await flushPromises()

    const store = useProductsStore()
    const spy = vi.spyOn(store, 'fetchProducts')

    const searchInput = wrapper.find('input[type="text"]')

    // Escribir en el input
    await searchInput.setValue('productivity')

    // Presionar Enter inmediatamente
    await searchInput.trigger('keyup.enter')
    await flushPromises()

    // Debe dispararse inmediatamente sin esperar debounce
    expect(spy).toHaveBeenCalled()
    expect(spy).toHaveBeenCalledWith(expect.objectContaining({
      search: 'productivity'
    }))
  })

  it('cambiar otros filtros no usa debounce (inmediato)', async () => {
    const wrapper = mount(ProductsView, {
      global: {
        plugins: [
          createTestingPinia({
            createSpy: vi.fn,
            initialState: {
              products: {
                products: mockProducts,
                totalProducts: 1,
                totalPages: 1,
                currentPage: 1
              }
            }
          }),
          router
        ]
      }
    })

    await router.isReady()
    await flushPromises()

    const store = useProductsStore()
    const spy = vi.spyOn(store, 'fetchProducts')

    // Encontrar checkbox de "Solo analizados"
    const analyzedCheckbox = wrapper.find('input[type="checkbox"]')
    expect(analyzedCheckbox.exists()).toBe(true)

    // Cambiar checkbox
    await analyzedCheckbox.setValue(true)
    await flushPromises()

    // Debe dispararse inmediatamente sin debounce
    expect(spy).toHaveBeenCalled()

    // No necesita avanzar tiempo - se dispara inmediatamente
    // Si hubiera debounce, necesitaríamos vi.advanceTimersByTime(400)
  })

  it('muestra badge de tag activo cuando hay query param tag', async () => {
    await router.push('/products?tag=productividad')
    await router.isReady()

    const wrapper = mount(ProductsView, {
      global: {
        plugins: [
          createTestingPinia({
            createSpy: vi.fn,
            initialState: {
              products: {
                products: mockProducts,
                totalProducts: 1,
                totalPages: 1,
                currentPage: 1
              }
            }
          }),
          router
        ]
      }
    })

    await flushPromises()

    expect(wrapper.text()).toContain('Filtrando por tag:')
    expect(wrapper.text()).toContain('productividad')
  })

  it('pasa el tag como filtro al store al cargar con query param', async () => {
    await router.push('/products?tag=ia')
    await router.isReady()

    const wrapper = mount(ProductsView, {
      global: {
        plugins: [
          createTestingPinia({
            createSpy: vi.fn,
            initialState: {
              products: {
                products: mockProducts,
                totalProducts: 1,
                totalPages: 1,
                currentPage: 1
              }
            }
          }),
          router
        ]
      }
    })

    await flushPromises()

    const store = useProductsStore()
    expect(store.fetchProducts).toHaveBeenCalledWith(
      expect.objectContaining({ tag: 'ia' })
    )
  })
})

// Ejecutar: cd frontend && npm run test -- ProductsView.spec.ts
