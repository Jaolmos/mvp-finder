import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { createRouter, createMemoryHistory } from 'vue-router'
import PostDetailView from '../PostDetailView.vue'
import { usePostsStore } from '@/stores/posts'
import { scraperService } from '@/services'
import type { PostDetail } from '@/services/posts'

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
    analyzePosts: vi.fn()
  }
}))

// Mock de las rutas
const routes = [
  { path: '/posts/:id', name: 'post-detail', component: PostDetailView },
  { path: '/posts', name: 'posts', component: { template: '<div>Posts</div>' } }
]

describe('PostDetailView', () => {
  let router: ReturnType<typeof createRouter>

  const mockPost: PostDetail = {
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

  const mockAnalyzedPost: PostDetail = {
    ...mockPost,
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

  async function mountPostDetailView(
    initialState = {},
    ollamaStatus = mockOllamaReady
  ) {
    vi.mocked(scraperService.getOllamaStatus).mockResolvedValue(ollamaStatus)

    await router.push('/posts/1')
    await router.isReady()

    const wrapper = mount(PostDetailView, {
      global: {
        plugins: [
          router,
          createTestingPinia({
            createSpy: vi.fn,
            initialState: {
              posts: initialState
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
      const wrapper = await mountPostDetailView({ loading: true })

      expect(wrapper.find('.animate-spin').exists()).toBe(true)
    })

    it('muestra error cuando hay error en el store', async () => {
      const wrapper = await mountPostDetailView({ error: 'Post no encontrado' })

      expect(wrapper.text()).toContain('Error al cargar el post')
      expect(wrapper.text()).toContain('Post no encontrado')
    })

    it('muestra el título del post', async () => {
      const wrapper = await mountPostDetailView({ currentPost: mockPost })

      expect(wrapper.find('h1').text()).toBe('Test Product')
    })

    it('muestra botón "Volver a posts"', async () => {
      const wrapper = await mountPostDetailView({ currentPost: mockPost })

      expect(wrapper.text()).toContain('Volver a posts')
    })
  })

  describe('Análisis IA - Post no analizado', () => {
    it('muestra card de análisis cuando post no está analizado y Ollama está listo', async () => {
      const wrapper = await mountPostDetailView(
        { currentPost: mockPost },
        mockOllamaReady
      )

      expect(wrapper.text()).toContain('Análisis IA')
      expect(wrapper.text()).toContain('Extrae insights del producto con inteligencia artificial')
    })

    it('muestra botón "Analizar con IA" cuando Ollama está listo', async () => {
      const wrapper = await mountPostDetailView(
        { currentPost: mockPost },
        mockOllamaReady
      )

      const analyzeButton = wrapper.find('button').wrapperElement
      const buttons = wrapper.findAll('button')
      const analyzeBtn = buttons.find(btn => btn.text().includes('Analizar con IA'))

      expect(analyzeBtn?.exists()).toBe(true)
    })

    it('muestra "Modelo no disponible" cuando Ollama no está listo', async () => {
      const wrapper = await mountPostDetailView(
        { currentPost: mockPost },
        mockOllamaNotReady
      )

      expect(wrapper.text()).toContain('Modelo no disponible')
      expect(wrapper.text()).toContain('Ollama no está disponible')
    })

    it('no muestra botón "Analizar con IA" cuando Ollama no está listo', async () => {
      const wrapper = await mountPostDetailView(
        { currentPost: mockPost },
        mockOllamaNotReady
      )

      const buttons = wrapper.findAll('button')
      const analyzeBtn = buttons.find(btn => btn.text().includes('Analizar con IA'))

      expect(analyzeBtn).toBeUndefined()
    })
  })

  describe('Análisis IA - Post ya analizado', () => {
    it('no muestra card de "Analizar con IA" cuando post ya está analizado', async () => {
      const wrapper = await mountPostDetailView(
        { currentPost: mockAnalyzedPost },
        mockOllamaReady
      )

      const buttons = wrapper.findAll('button')
      const analyzeBtn = buttons.find(btn => btn.text().includes('Analizar con IA'))

      expect(analyzeBtn).toBeUndefined()
    })

    it('muestra sección de análisis completado con resumen', async () => {
      const wrapper = await mountPostDetailView(
        { currentPost: mockAnalyzedPost },
        mockOllamaReady
      )

      expect(wrapper.text()).toContain('Resumen')
      expect(wrapper.text()).toContain('Este es un resumen del producto')
    })

    it('muestra problema que resuelve', async () => {
      const wrapper = await mountPostDetailView(
        { currentPost: mockAnalyzedPost },
        mockOllamaReady
      )

      expect(wrapper.text()).toContain('Problema que resuelve')
      expect(wrapper.text()).toContain('Resuelve el problema de testing')
    })

    it('muestra idea de MVP', async () => {
      const wrapper = await mountPostDetailView(
        { currentPost: mockAnalyzedPost },
        mockOllamaReady
      )

      expect(wrapper.text()).toContain('Idea de MVP')
      expect(wrapper.text()).toContain('Crear una versión simplificada')
    })

    it('muestra público objetivo', async () => {
      const wrapper = await mountPostDetailView(
        { currentPost: mockAnalyzedPost },
        mockOllamaReady
      )

      expect(wrapper.text()).toContain('Público objetivo')
      expect(wrapper.text()).toContain('Desarrolladores')
    })

    it('muestra score de potencial con color verde para score >= 7', async () => {
      const wrapper = await mountPostDetailView(
        { currentPost: mockAnalyzedPost },
        mockOllamaReady
      )

      expect(wrapper.text()).toContain('Potencial:')
      expect(wrapper.text()).toContain('8/10')
    })

    it('muestra tags separados', async () => {
      const wrapper = await mountPostDetailView(
        { currentPost: mockAnalyzedPost },
        mockOllamaReady
      )

      expect(wrapper.text()).toContain('Tags')
      expect(wrapper.text()).toContain('testing')
      expect(wrapper.text()).toContain('automation')
      expect(wrapper.text()).toContain('devtools')
    })
  })

  describe('Interacción de análisis', () => {
    it('llama a scraperService.analyzePosts al hacer click en "Analizar con IA"', async () => {
      vi.mocked(scraperService.analyzePosts).mockResolvedValue({
        task_id: 'task-123',
        message: 'Análisis iniciado'
      })

      const wrapper = await mountPostDetailView(
        { currentPost: mockPost },
        mockOllamaReady
      )

      const buttons = wrapper.findAll('button')
      const analyzeBtn = buttons.find(btn => btn.text().includes('Analizar con IA'))

      await analyzeBtn?.trigger('click')
      await flushPromises()

      expect(scraperService.analyzePosts).toHaveBeenCalledWith({ post_ids: [1] })
    })

    it('muestra "Analizando..." mientras se procesa', async () => {
      vi.mocked(scraperService.analyzePosts).mockResolvedValue({
        task_id: 'task-123',
        message: 'Análisis iniciado'
      })

      const wrapper = await mountPostDetailView(
        { currentPost: mockPost },
        mockOllamaReady
      )

      const buttons = wrapper.findAll('button')
      const analyzeBtn = buttons.find(btn => btn.text().includes('Analizar con IA'))

      await analyzeBtn?.trigger('click')
      await flushPromises()

      expect(wrapper.text()).toContain('Analizando...')
    })

    it('deshabilita botón mientras analiza', async () => {
      vi.mocked(scraperService.analyzePosts).mockResolvedValue({
        task_id: 'task-123',
        message: 'Análisis iniciado'
      })

      const wrapper = await mountPostDetailView(
        { currentPost: mockPost },
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

    it('muestra error si falla el análisis', async () => {
      vi.mocked(scraperService.analyzePosts).mockRejectedValue({
        response: { data: { message: 'Error de conexión con Ollama' } }
      })

      const wrapper = await mountPostDetailView(
        { currentPost: mockPost },
        mockOllamaReady
      )

      const buttons = wrapper.findAll('button')
      const analyzeBtn = buttons.find(btn => btn.text().includes('Analizar con IA'))

      await analyzeBtn?.trigger('click')
      await flushPromises()

      expect(wrapper.text()).toContain('Error de conexión con Ollama')
    })
  })

  describe('Carga de estado de Ollama', () => {
    it('llama a scraperService.getOllamaStatus al montar', async () => {
      await mountPostDetailView({ currentPost: mockPost })

      expect(scraperService.getOllamaStatus).toHaveBeenCalled()
    })

    it('no muestra card de análisis si ollamaStatus es null', async () => {
      vi.mocked(scraperService.getOllamaStatus).mockRejectedValue(new Error('Network error'))

      await router.push('/posts/1')
      await router.isReady()

      const wrapper = mount(PostDetailView, {
        global: {
          plugins: [
            router,
            createTestingPinia({
              createSpy: vi.fn,
              initialState: {
                posts: { currentPost: mockPost }
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
//   cd frontend && npm run test:unit -- --run src/views/__tests__/PostDetailView.spec.ts
//
// Ejecutar todos los tests:
//   cd frontend && npm run test:unit
