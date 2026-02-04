import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { createRouter, createMemoryHistory } from 'vue-router'
import TopicsView from '../TopicsView.vue'
import AppLayout from '@/layouts/AppLayout.vue'
import { useTopicsStore } from '@/stores/topics'
import type { Topic } from '@/services/topics'

// Mock de AppLayout
vi.mock('@/layouts/AppLayout.vue', () => ({
  default: {
    name: 'AppLayout',
    template: '<div class="app-layout"><slot /></div>'
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
  { path: '/topics', name: 'topics', component: TopicsView },
  { path: '/', name: 'dashboard', component: { template: '<div>Dashboard</div>' } }
]

describe('TopicsView', () => {
  let router: ReturnType<typeof createRouter>

  const mockTopic: Topic = {
    id: 1,
    name: 'artificial-intelligence',
    is_active: true,
    last_sync: '2024-01-01T00:00:00Z',
    created_at: '2024-01-01T00:00:00Z'
  }

  const mockInactiveTopic: Topic = {
    id: 2,
    name: 'developer-tools',
    is_active: false,
    last_sync: null,
    created_at: '2024-01-01T00:00:00Z'
  }

  beforeEach(() => {
    router = createRouter({
      history: createMemoryHistory(),
      routes
    })
  })

  function mountTopicsView(initialState = {}) {
    return mount(TopicsView, {
      global: {
        plugins: [
          router,
          createTestingPinia({
            createSpy: vi.fn,
            initialState: {
              topics: initialState
            }
          })
        ]
      }
    })
  }

  it('renderiza el header con título y botón añadir', () => {
    const wrapper = mountTopicsView()

    expect(wrapper.find('h1').text()).toBe('Topics')
    expect(wrapper.find('button').text()).toContain('Añadir Topic')
  })

  it('muestra estado de carga cuando loading es true', () => {
    const wrapper = mountTopicsView({ loading: true })

    expect(wrapper.text()).toContain('Cargando topics...')
  })

  it('muestra mensaje de error cuando hay error', () => {
    const wrapper = mountTopicsView({ error: 'Error de conexión' })

    expect(wrapper.text()).toContain('Error de conexión')
  })

  it('muestra mensaje cuando no hay topics', () => {
    const wrapper = mountTopicsView({ topics: [] })

    expect(wrapper.text()).toContain('No hay topics configurados')
  })

  it('renderiza tabla con topics', () => {
    const wrapper = mountTopicsView({
      topics: [mockTopic, mockInactiveTopic]
    })

    expect(wrapper.find('table').exists()).toBe(true)
    expect(wrapper.text()).toContain('artificial-intelligence')
    expect(wrapper.text()).toContain('developer-tools')
  })

  it('muestra badge "Activo" para topics activos', () => {
    const wrapper = mountTopicsView({
      topics: [mockTopic]
    })

    expect(wrapper.text()).toContain('Activo')
  })

  it('muestra badge "Inactivo" para topics inactivos', () => {
    const wrapper = mountTopicsView({
      topics: [mockInactiveTopic]
    })

    expect(wrapper.text()).toContain('Inactivo')
  })

  it('muestra "Nunca" cuando last_sync es null', () => {
    const wrapper = mountTopicsView({
      topics: [mockInactiveTopic]
    })

    expect(wrapper.text()).toContain('Nunca')
  })

  it('abre modal al hacer click en "Añadir Topic"', async () => {
    const wrapper = mountTopicsView()

    expect(wrapper.text()).not.toContain('Cancelar')

    await wrapper.find('button').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Añadir Topic')
    expect(wrapper.text()).toContain('Nombre del Topic')
  })

  it('cierra modal al hacer click en cancelar', async () => {
    const wrapper = mountTopicsView()

    // Abrir modal
    await wrapper.find('button').trigger('click')
    await flushPromises()
    expect(wrapper.text()).toContain('Añadir Topic')

    // Cerrar modal
    const buttons = wrapper.findAll('button')
    const cancelButton = buttons.find(btn => btn.text() === 'Cancelar')
    await cancelButton?.trigger('click')
    await flushPromises()

    expect(wrapper.text()).not.toContain('Nombre del Topic')
  })

  it('llama a createTopic del store al enviar formulario de crear', async () => {
    const wrapper = mountTopicsView()
    const store = useTopicsStore()

    vi.mocked(store.createTopic).mockResolvedValue(true)

    // Abrir modal
    await wrapper.find('button').trigger('click')
    await flushPromises()

    // Llenar formulario
    const nameInput = wrapper.find('input#name')
    await nameInput.setValue('new-topic')

    // Enviar formulario
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(store.createTopic).toHaveBeenCalledWith('new-topic', true)
  })

  it('llama a toggleActive al hacer click en badge de estado', async () => {
    const wrapper = mountTopicsView({
      topics: [mockTopic]
    })
    const store = useTopicsStore()

    vi.mocked(store.toggleActive).mockResolvedValue(true)

    // Buscar el botón de toggle (badge "Activo")
    const toggleButtons = wrapper.findAll('button')
    const toggleButton = toggleButtons.find(btn => btn.text().includes('Activo'))

    await toggleButton?.trigger('click')
    await flushPromises()

    expect(store.toggleActive).toHaveBeenCalledWith(1)
  })

  it('muestra confirmación antes de eliminar', async () => {
    const wrapper = mountTopicsView({
      topics: [mockTopic]
    })

    // Mock de window.confirm
    global.confirm = vi.fn(() => true)

    // Buscar botón de eliminar (último botón de la fila)
    const deleteButtons = wrapper.findAll('button[title="Eliminar"]')
    await deleteButtons[0]?.trigger('click')

    expect(global.confirm).toHaveBeenCalledWith('¿Estás seguro de eliminar "artificial-intelligence"?')
  })

  it('llama a deleteTopic si se confirma la eliminación', async () => {
    const wrapper = mountTopicsView({
      topics: [mockTopic]
    })
    const store = useTopicsStore()

    vi.mocked(store.deleteTopic).mockResolvedValue(true)
    global.confirm = vi.fn(() => true)

    const deleteButtons = wrapper.findAll('button[title="Eliminar"]')
    await deleteButtons[0]?.trigger('click')
    await flushPromises()

    expect(store.deleteTopic).toHaveBeenCalledWith(1)
  })

  it('no llama a deleteTopic si se cancela la confirmación', async () => {
    const wrapper = mountTopicsView({
      topics: [mockTopic]
    })
    const store = useTopicsStore()

    global.confirm = vi.fn(() => false)

    const deleteButtons = wrapper.findAll('button[title="Eliminar"]')
    await deleteButtons[0]?.trigger('click')
    await flushPromises()

    expect(store.deleteTopic).not.toHaveBeenCalled()
  })

  it('llama a fetchTopics al montar el componente', () => {
    const wrapper = mountTopicsView()
    const store = useTopicsStore()

    expect(store.fetchTopics).toHaveBeenCalled()
  })
})

// Ejecutar este test:
//   cd frontend && npm run test:unit -- --run src/views/__tests__/TopicsView.spec.ts
//
// Ejecutar todos los tests:
//   cd frontend && npm run test:unit
