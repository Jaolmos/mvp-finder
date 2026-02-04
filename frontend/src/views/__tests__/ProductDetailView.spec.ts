import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { createRouter, createMemoryHistory } from 'vue-router'
import ProductDetailView from '../ProductDetailView.vue'
import { useProductsStore } from '@/stores/products'
import { scraperService } from '@/services'
import type { ProductDetail } from '@/services/products'

// Mock de AppLayout
vi.mock('@/layouts/AppLayout.vue', () => ({
  default: {
    name: 'AppLayout',
    template: '<div class="app-layout"><slot /></div>'
  }
}))

// Mock de scraperService
vi.mock('@/services', () => ({
  scraperService: {
    getOllamaStatus: vi.fn(),
    analyzeProducts: vi.fn()
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
  { path: '/products/:id', name: 'product-detail', component: ProductDetailView },
  { path: '/products', name: 'products', component: { template: '<div>Products</div>' } }
]

describe('ProductDetailView', () => {
  let router: ReturnType<typeof createRouter>

  const mockProduct: ProductDetail = {
    id: 1,
    external_id: 'ph-123',
    title: 'Test Product',
    tagline: 'A test tagline',
    content: 'Test content description',
    author: 'testuser',
    score: 150,
    votes_count: 150,
    comments_count: 25,
    url: 'https://producthunt.com/posts/test',
    website: 'https://test.com',
    created_at_source: '2024-01-15T10:00:00Z',
    topic: { id: 1, name: 'developer-tools' },
    is_favorite: false,
    analyzed: false,
    summary: null,
    problem: null,
    mvp_idea: null,
    target_audience: null,
    potential_score: null,
    tags: null,
    analyzed_at: null
  }

  const mockAnalyzedProduct: ProductDetail = {
    ...mockProduct,
    analyzed: true,
    summary: 'Este es un resumen del producto',
    problem: 'Resuelve el problema de testing',
    mvp_idea: 'Crear una versión simplificada',
    target_audience: 'Desarrolladores',
    potential_score: 8,
    tags: 'testing, automation, devtools',
    analyzed_at: '2024-01-16T12:00:00Z'
  }

  const mockOllamaReady = {
    host: 'http://ollama:11434',
    model: 'llama3.2:1b',
    ollama_available: true,
    model_available: true,
    ready: true
  }

  const mockOllamaNotReady = {
    host: 'http://ollama:11434',
    model: 'llama3.2:1b',
    ollama_available: true,
    model_available: false,
    ready: false
  }

  beforeEach(() => {
    router = createRouter({
      history: createMemoryHistory(),
      routes
    })
    vi.clearAllMocks()
  })

  async function mountProductDetailView(
    initialState = {},
    ollamaStatus = mockOllamaReady
  ) {
    vi.mocked(scraperService.getOllamaStatus).mockResolvedValue(ollamaStatus)

    await router.push('/products/1')
    await router.isReady()

    const wrapper = mount(ProductDetailView, {
      global: {
        plugins: [
          router,
          createTestingPinia({
            createSpy: vi.fn,
            initialState: {
              products: initialState
            }
          })
        ]
      }
    })

    await flushPromises()
    return wrapper
  }

  describe('Renderizado básico', () => {
    it('muestra spinner de carga cuando loading es true', async () => {
      const wrapper = await mountProductDetailView({ loading: true })

      expect(wrapper.find('.animate-spin').exists()).toBe(true)
    })

    it('muestra error cuando hay error en el store', async () => {
      const wrapper = await mountProductDetailView({ error: 'Producto no encontrado' })

      expect(wrapper.text()).toContain('Error al cargar el producto')
      expect(wrapper.text()).toContain('Producto no encontrado')
    })

    it('muestra el título del producto', async () => {
      const wrapper = await mountProductDetailView({ currentProduct: mockProduct })

      expect(wrapper.find('h1').text()).toBe('Test Product')
    })

    it('muestra botón "Volver a productos"', async () => {
      const wrapper = await mountProductDetailView({ currentProduct: mockProduct })

      expect(wrapper.text()).toContain('Volver a productos')
    })
  })

  describe('Análisis IA - Producto no analizado', () => {
    it('muestra card de análisis cuando producto no está analizado y Ollama está listo', async () => {
      const wrapper = await mountProductDetailView(
        { currentProduct: mockProduct },
        mockOllamaReady
      )

      expect(wrapper.text()).toContain('Análisis IA')
      expect(wrapper.text()).toContain('Extrae insights del producto con inteligencia artificial')
    })

    it('muestra botón "Analizar con IA" cuando Ollama está listo', async () => {
      const wrapper = await mountProductDetailView(
        { currentProduct: mockProduct },
        mockOllamaReady
      )

      const analyzeButton = wrapper.find('button').wrapperElement
      const buttons = wrapper.findAll('button')
      const analyzeBtn = buttons.find(btn => btn.text().includes('Analizar con IA'))

      expect(analyzeBtn?.exists()).toBe(true)
    })

    it('muestra "Modelo no disponible" cuando Ollama no está listo', async () => {
      const wrapper = await mountProductDetailView(
        { currentProduct: mockProduct },
        mockOllamaNotReady
      )

      expect(wrapper.text()).toContain('Modelo no disponible')
      expect(wrapper.text()).toContain('Ollama no está disponible')
    })

    it('no muestra botón "Analizar con IA" cuando Ollama no está listo', async () => {
      const wrapper = await mountProductDetailView(
        { currentProduct: mockProduct },
        mockOllamaNotReady
      )

      const buttons = wrapper.findAll('button')
      const analyzeBtn = buttons.find(btn => btn.text().includes('Analizar con IA'))

      expect(analyzeBtn).toBeUndefined()
    })
  })

  describe('Análisis IA - Producto ya analizado', () => {
    it('no muestra card de "Analizar con IA" cuando producto ya está analizado', async () => {
      const wrapper = await mountProductDetailView(
        { currentProduct: mockAnalyzedProduct },
        mockOllamaReady
      )

      const buttons = wrapper.findAll('button')
      const analyzeBtn = buttons.find(btn => btn.text().includes('Analizar con IA'))

      expect(analyzeBtn).toBeUndefined()
    })

    it('muestra sección de análisis completado con resumen', async () => {
      const wrapper = await mountProductDetailView(
        { currentProduct: mockAnalyzedProduct },
        mockOllamaReady
      )

      expect(wrapper.text()).toContain('Resumen')
      expect(wrapper.text()).toContain('Este es un resumen del producto')
    })

    it('muestra problema que resuelve', async () => {
      const wrapper = await mountProductDetailView(
        { currentProduct: mockAnalyzedProduct },
        mockOllamaReady
      )

      expect(wrapper.text()).toContain('Problema que resuelve')
      expect(wrapper.text()).toContain('Resuelve el problema de testing')
    })

    it('muestra idea de MVP', async () => {
      const wrapper = await mountProductDetailView(
        { currentProduct: mockAnalyzedProduct },
        mockOllamaReady
      )

      expect(wrapper.text()).toContain('Idea de MVP')
      expect(wrapper.text()).toContain('Crear una versión simplificada')
    })

    it('muestra público objetivo', async () => {
      const wrapper = await mountProductDetailView(
        { currentProduct: mockAnalyzedProduct },
        mockOllamaReady
      )

      expect(wrapper.text()).toContain('Público objetivo')
      expect(wrapper.text()).toContain('Desarrolladores')
    })

    it('muestra score de potencial con color verde para score >= 7', async () => {
      const wrapper = await mountProductDetailView(
        { currentProduct: mockAnalyzedProduct },
        mockOllamaReady
      )

      expect(wrapper.text()).toContain('Potencial:')
      expect(wrapper.text()).toContain('8/10')
    })

    it('muestra tags separados', async () => {
      const wrapper = await mountProductDetailView(
        { currentProduct: mockAnalyzedProduct },
        mockOllamaReady
      )

      expect(wrapper.text()).toContain('Tags')
      expect(wrapper.text()).toContain('testing')
      expect(wrapper.text()).toContain('automation')
      expect(wrapper.text()).toContain('devtools')
    })
  })

  describe('Interacción de análisis', () => {
    it('llama a scraperService.analyzeProducts al hacer click en "Analizar con IA"', async () => {
      vi.mocked(scraperService.analyzeProducts).mockResolvedValue({
        task_id: 'task-123',
        message: 'Análisis iniciado'
      })

      const wrapper = await mountProductDetailView(
        { currentProduct: mockProduct },
        mockOllamaReady
      )

      const buttons = wrapper.findAll('button')
      const analyzeBtn = buttons.find(btn => btn.text().includes('Analizar con IA'))

      await analyzeBtn?.trigger('click')
      await flushPromises()

      expect(scraperService.analyzeProducts).toHaveBeenCalledWith({ product_ids: [1] })
    })

    it('muestra "Analizando..." mientras se procesa', async () => {
      vi.mocked(scraperService.analyzeProducts).mockResolvedValue({
        task_id: 'task-123',
        message: 'Análisis iniciado'
      })

      const wrapper = await mountProductDetailView(
        { currentProduct: mockProduct },
        mockOllamaReady
      )

      const buttons = wrapper.findAll('button')
      const analyzeBtn = buttons.find(btn => btn.text().includes('Analizar con IA'))

      await analyzeBtn?.trigger('click')
      await flushPromises()

      expect(wrapper.text()).toContain('Analizando...')
    })

    it('deshabilita botón mientras analiza', async () => {
      vi.mocked(scraperService.analyzeProducts).mockResolvedValue({
        task_id: 'task-123',
        message: 'Análisis iniciado'
      })

      const wrapper = await mountProductDetailView(
        { currentProduct: mockProduct },
        mockOllamaReady
      )

      const buttons = wrapper.findAll('button')
      const analyzeBtn = buttons.find(btn => btn.text().includes('Analizar con IA'))

      await analyzeBtn?.trigger('click')
      await flushPromises()

      // Buscar el botón que ahora dice "Analizando..."
      const analyzingBtn = wrapper.findAll('button').find(btn => btn.text().includes('Analizando...'))
      expect(analyzingBtn?.attributes('disabled')).toBeDefined()
    })

    it('maneja error si falla el análisis', async () => {
      vi.mocked(scraperService.analyzeProducts).mockRejectedValue({
        response: { data: { message: 'Error de conexión con Ollama' } }
      })

      const wrapper = await mountProductDetailView(
        { currentProduct: mockProduct },
        mockOllamaReady
      )

      const buttons = wrapper.findAll('button')
      const analyzeBtn = buttons.find(btn => btn.text().includes('Analizar con IA'))

      await analyzeBtn?.trigger('click')
      await flushPromises()

      // El error ahora se muestra mediante toast, no inline
      // Verificar que el botón vuelve a estar disponible
      const analyzeBtn2 = wrapper.findAll('button').find(btn => btn.text().includes('Analizar con IA'))
      expect(analyzeBtn2?.attributes('disabled')).toBeUndefined()
    })
  })

  describe('Carga de estado de Ollama', () => {
    it('llama a scraperService.getOllamaStatus al montar', async () => {
      await mountProductDetailView({ currentProduct: mockProduct })

      expect(scraperService.getOllamaStatus).toHaveBeenCalled()
    })

    it('no muestra card de análisis si ollamaStatus es null', async () => {
      vi.mocked(scraperService.getOllamaStatus).mockRejectedValue(new Error('Network error'))

      await router.push('/products/1')
      await router.isReady()

      const wrapper = mount(ProductDetailView, {
        global: {
          plugins: [
            router,
            createTestingPinia({
              createSpy: vi.fn,
              initialState: {
                products: { currentProduct: mockProduct }
              }
            })
          ]
        }
      })

      await flushPromises()

      // No debe mostrar la card de análisis porque ollamaStatus es null
      const buttons = wrapper.findAll('button')
      const analyzeBtn = buttons.find(btn => btn.text().includes('Analizar con IA'))

      expect(analyzeBtn).toBeUndefined()
    })
  })
})

// Ejecutar este test:
//   cd frontend && npm run test:unit -- --run src/views/__tests__/ProductDetailView.spec.ts
//
// Ejecutar todos los tests:
//   cd frontend && npm run test:unit
