import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { createRouter, createMemoryHistory } from 'vue-router'
import LoginView from '../LoginView.vue'
import { useAuthStore } from '@/stores/auth'

// Mock de las rutas
const routes = [
  { path: '/login', name: 'login', component: LoginView },
  { path: '/', name: 'dashboard', component: { template: '<div>Dashboard</div>' } }
]

describe('LoginView', () => {
  let router: ReturnType<typeof createRouter>

  beforeEach(() => {
    router = createRouter({
      history: createMemoryHistory(),
      routes
    })
  })

  function mountLoginView() {
    return mount(LoginView, {
      global: {
        plugins: [
          router,
          createTestingPinia({
            createSpy: vi.fn
          })
        ]
      }
    })
  }

  it('renderiza el formulario de login', () => {
    const wrapper = mountLoginView()

    expect(wrapper.find('h2').text()).toBe('Iniciar sesión')
    expect(wrapper.find('input#username').exists()).toBe(true)
    expect(wrapper.find('input#password').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
  })

  it('muestra los labels correctos', () => {
    const wrapper = mountLoginView()

    expect(wrapper.find('label[for="username"]').text()).toBe('Usuario')
    expect(wrapper.find('label[for="password"]').text()).toBe('Contraseña')
  })

  it('el botón muestra "Iniciar sesión" por defecto', () => {
    const wrapper = mountLoginView()

    expect(wrapper.find('button[type="submit"]').text()).toBe('Iniciar sesión')
  })

  it('actualiza los v-model al escribir', async () => {
    const wrapper = mountLoginView()

    const usernameInput = wrapper.find('input#username')
    const passwordInput = wrapper.find('input#password')

    await usernameInput.setValue('testuser')
    await passwordInput.setValue('testpass')

    expect((usernameInput.element as HTMLInputElement).value).toBe('testuser')
    expect((passwordInput.element as HTMLInputElement).value).toBe('testpass')
  })

  it('llama a login del store al enviar el formulario', async () => {
    const wrapper = mountLoginView()
    const authStore = useAuthStore()

    vi.mocked(authStore.login).mockResolvedValue(true)

    await wrapper.find('input#username').setValue('testuser')
    await wrapper.find('input#password').setValue('testpass')
    await wrapper.find('form').trigger('submit')

    expect(authStore.login).toHaveBeenCalledWith({
      username: 'testuser',
      password: 'testpass'
    })
  })

  it('muestra el error del store si existe', async () => {
    const wrapper = mount(LoginView, {
      global: {
        plugins: [
          router,
          createTestingPinia({
            createSpy: vi.fn,
            initialState: {
              auth: {
                error: 'Credenciales inválidas'
              }
            }
          })
        ]
      }
    })

    expect(wrapper.text()).toContain('Credenciales inválidas')
  })

  it('muestra estado de carga cuando loading es true', async () => {
    const wrapper = mount(LoginView, {
      global: {
        plugins: [
          router,
          createTestingPinia({
            createSpy: vi.fn,
            initialState: {
              auth: {
                loading: true
              }
            }
          })
        ]
      }
    })

    expect(wrapper.find('button[type="submit"]').text()).toContain('Iniciando sesión...')
    expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeDefined()
  })

  it('redirige al dashboard después de login exitoso', async () => {
    await router.push('/login')
    await router.isReady()

    const wrapper = mount(LoginView, {
      global: {
        plugins: [
          router,
          createTestingPinia({
            createSpy: vi.fn,
            stubActions: false
          })
        ]
      }
    })

    const authStore = useAuthStore()
    vi.mocked(authStore.login).mockResolvedValue(true)

    await wrapper.find('input#username').setValue('testuser')
    await wrapper.find('input#password').setValue('testpass')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(router.currentRoute.value.path).toBe('/')
  })

  it('no redirige si el login falla', async () => {
    await router.push('/login')
    await router.isReady()

    const wrapper = mount(LoginView, {
      global: {
        plugins: [
          router,
          createTestingPinia({
            createSpy: vi.fn,
            stubActions: false
          })
        ]
      }
    })

    const authStore = useAuthStore()
    vi.mocked(authStore.login).mockResolvedValue(false)

    await wrapper.find('input#username').setValue('testuser')
    await wrapper.find('input#password').setValue('testpass')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('redirige a la URL de redirect si existe', async () => {
    await router.push('/login?redirect=/posts')
    await router.isReady()

    const wrapper = mount(LoginView, {
      global: {
        plugins: [
          router,
          createTestingPinia({
            createSpy: vi.fn,
            stubActions: false
          })
        ]
      }
    })

    const authStore = useAuthStore()
    vi.mocked(authStore.login).mockResolvedValue(true)

    await wrapper.find('input#username').setValue('testuser')
    await wrapper.find('input#password').setValue('testpass')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(router.currentRoute.value.path).toBe('/posts')
  })
})

// Ejecutar este test:
//   cd frontend && npm run test:unit -- --run src/views/__tests__/LoginView.spec.ts
//
// Ejecutar todos los tests:
//   cd frontend && npm run test:unit
