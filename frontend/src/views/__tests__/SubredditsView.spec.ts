import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { createRouter, createMemoryHistory } from 'vue-router'
import SubredditsView from '../SubredditsView.vue'
import AppLayout from '@/layouts/AppLayout.vue'
import { useSubredditsStore } from '@/stores/subreddits'
import type { Subreddit } from '@/services/subreddits'

// Mock de AppLayout
vi.mock('@/layouts/AppLayout.vue', () => ({
  default: {
    name: 'AppLayout',
    template: '<div class="app-layout"><slot /></div>'
  }
}))

// Mock de las rutas
const routes = [
  { path: '/subreddits', name: 'subreddits', component: SubredditsView },
  { path: '/', name: 'dashboard', component: { template: '<div>Dashboard</div>' } }
]

describe('SubredditsView', () => {
  let router: ReturnType<typeof createRouter>

  const mockSubreddit: Subreddit = {
    id: 1,
    name: 'SomebodyMakeThis',
    is_active: true,
    last_sync: '2024-01-01T00:00:00Z',
    created_at: '2024-01-01T00:00:00Z'
  }

  const mockInactiveSubreddit: Subreddit = {
    id: 2,
    name: 'AppIdeas',
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

  function mountSubredditsView(initialState = {}) {
    return mount(SubredditsView, {
      global: {
        plugins: [
          router,
          createTestingPinia({
            createSpy: vi.fn,
            initialState: {
              subreddits: initialState
            }
          })
        ]
      }
    })
  }

  it('renderiza el header con título y botón añadir', () => {
    const wrapper = mountSubredditsView()

    expect(wrapper.find('h1').text()).toBe('Subreddits')
    expect(wrapper.find('button').text()).toContain('Añadir Subreddit')
  })

  it('muestra estado de carga cuando loading es true', () => {
    const wrapper = mountSubredditsView({ loading: true })

    expect(wrapper.text()).toContain('Cargando subreddits...')
  })

  it('muestra mensaje de error cuando hay error', () => {
    const wrapper = mountSubredditsView({ error: 'Error de conexión' })

    expect(wrapper.text()).toContain('Error de conexión')
  })

  it('muestra mensaje cuando no hay subreddits', () => {
    const wrapper = mountSubredditsView({ subreddits: [] })

    expect(wrapper.text()).toContain('No hay subreddits configurados')
  })

  it('renderiza tabla con subreddits', () => {
    const wrapper = mountSubredditsView({
      subreddits: [mockSubreddit, mockInactiveSubreddit]
    })

    expect(wrapper.find('table').exists()).toBe(true)
    expect(wrapper.text()).toContain('r/SomebodyMakeThis')
    expect(wrapper.text()).toContain('r/AppIdeas')
  })

  it('muestra badge "Activo" para subreddits activos', () => {
    const wrapper = mountSubredditsView({
      subreddits: [mockSubreddit]
    })

    expect(wrapper.text()).toContain('Activo')
  })

  it('muestra badge "Inactivo" para subreddits inactivos', () => {
    const wrapper = mountSubredditsView({
      subreddits: [mockInactiveSubreddit]
    })

    expect(wrapper.text()).toContain('Inactivo')
  })

  it('muestra "Nunca" cuando last_sync es null', () => {
    const wrapper = mountSubredditsView({
      subreddits: [mockInactiveSubreddit]
    })

    expect(wrapper.text()).toContain('Nunca')
  })

  it('abre modal al hacer click en "Añadir Subreddit"', async () => {
    const wrapper = mountSubredditsView()

    expect(wrapper.text()).not.toContain('Nombre del Subreddit')

    await wrapper.find('button').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Añadir Subreddit')
    expect(wrapper.text()).toContain('Nombre del Subreddit')
  })

  it('cierra modal al hacer click en cancelar', async () => {
    const wrapper = mountSubredditsView()

    // Abrir modal
    await wrapper.find('button').trigger('click')
    await flushPromises()
    expect(wrapper.text()).toContain('Añadir Subreddit')

    // Cerrar modal
    const buttons = wrapper.findAll('button')
    const cancelButton = buttons.find(btn => btn.text() === 'Cancelar')
    await cancelButton?.trigger('click')
    await flushPromises()

    expect(wrapper.text()).not.toContain('Nombre del Subreddit')
  })

  it('llama a createSubreddit del store al enviar formulario de crear', async () => {
    const wrapper = mountSubredditsView()
    const store = useSubredditsStore()

    vi.mocked(store.createSubreddit).mockResolvedValue(true)

    // Abrir modal
    await wrapper.find('button').trigger('click')
    await flushPromises()

    // Llenar formulario
    const nameInput = wrapper.find('input#name')
    await nameInput.setValue('NewSubreddit')

    // Enviar formulario
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(store.createSubreddit).toHaveBeenCalledWith('NewSubreddit', true)
  })

  it('llama a toggleActive al hacer click en badge de estado', async () => {
    const wrapper = mountSubredditsView({
      subreddits: [mockSubreddit]
    })
    const store = useSubredditsStore()

    vi.mocked(store.toggleActive).mockResolvedValue(true)

    // Buscar el botón de toggle (badge "Activo")
    const toggleButtons = wrapper.findAll('button')
    const toggleButton = toggleButtons.find(btn => btn.text().includes('Activo'))

    await toggleButton?.trigger('click')
    await flushPromises()

    expect(store.toggleActive).toHaveBeenCalledWith(1)
  })

  it('muestra confirmación antes de eliminar', async () => {
    const wrapper = mountSubredditsView({
      subreddits: [mockSubreddit]
    })

    // Mock de window.confirm
    global.confirm = vi.fn(() => true)

    // Buscar botón de eliminar (último botón de la fila)
    const deleteButtons = wrapper.findAll('button[title="Eliminar"]')
    await deleteButtons[0]?.trigger('click')

    expect(global.confirm).toHaveBeenCalledWith('¿Estás seguro de eliminar r/SomebodyMakeThis?')
  })

  it('llama a deleteSubreddit si se confirma la eliminación', async () => {
    const wrapper = mountSubredditsView({
      subreddits: [mockSubreddit]
    })
    const store = useSubredditsStore()

    vi.mocked(store.deleteSubreddit).mockResolvedValue(true)
    global.confirm = vi.fn(() => true)

    const deleteButtons = wrapper.findAll('button[title="Eliminar"]')
    await deleteButtons[0]?.trigger('click')
    await flushPromises()

    expect(store.deleteSubreddit).toHaveBeenCalledWith(1)
  })

  it('no llama a deleteSubreddit si se cancela la confirmación', async () => {
    const wrapper = mountSubredditsView({
      subreddits: [mockSubreddit]
    })
    const store = useSubredditsStore()

    global.confirm = vi.fn(() => false)

    const deleteButtons = wrapper.findAll('button[title="Eliminar"]')
    await deleteButtons[0]?.trigger('click')
    await flushPromises()

    expect(store.deleteSubreddit).not.toHaveBeenCalled()
  })

  it('llama a fetchSubreddits al montar el componente', () => {
    const wrapper = mountSubredditsView()
    const store = useSubredditsStore()

    expect(store.fetchSubreddits).toHaveBeenCalled()
  })
})

// Ejecutar este test:
//   cd frontend && npm run test:unit -- --run src/views/__tests__/SubredditsView.spec.ts
//
// Ejecutar todos los tests:
//   cd frontend && npm run test:unit
