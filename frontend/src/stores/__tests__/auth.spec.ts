import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../auth'

// Mock del AuthService
vi.mock('@/services/auth', () => ({
  default: {
    login: vi.fn(),
    logout: vi.fn(),
    getCurrentUser: vi.fn(),
    isAuthenticated: vi.fn(),
    getAccessToken: vi.fn()
  }
}))

import authService from '@/services/auth'

describe('useAuthStore', () => {
  beforeEach(() => {
    // Limpiar localStorage antes de cada test
    localStorage.clear()
    vi.clearAllMocks()
    setActivePinia(createPinia())
  })

  afterEach(() => {
    localStorage.clear()
  })

  describe('estado inicial', () => {
    it('tiene valores por defecto correctos', () => {
      const store = useAuthStore()

      expect(store.user).toBeNull()
      expect(store.accessToken).toBeNull()
      expect(store.refreshToken).toBeNull()
      expect(store.loading).toBe(false)
      expect(store.error).toBeNull()
      expect(store.isAuthenticated).toBe(false)
    })

    it('carga tokens desde localStorage si existen', () => {
      // Configurar localStorage ANTES de crear el store
      localStorage.setItem('access_token', 'stored_access_token')
      localStorage.setItem('refresh_token', 'stored_refresh_token')

      // Crear nuevo pinia para que se recargue
      setActivePinia(createPinia())
      const store = useAuthStore()

      expect(store.accessToken).toBe('stored_access_token')
      expect(store.refreshToken).toBe('stored_refresh_token')
      expect(store.isAuthenticated).toBe(true)
    })
  })

  describe('login', () => {
    it('hace login correctamente y obtiene el usuario', async () => {
      const mockTokens = { access: 'access_123', refresh: 'refresh_123' }
      const mockUser = { id: 1, username: 'testuser', email: 'test@test.com' }

      vi.mocked(authService.login).mockResolvedValue(mockTokens)
      vi.mocked(authService.getCurrentUser).mockResolvedValue(mockUser)

      const store = useAuthStore()
      const result = await store.login({ username: 'testuser', password: 'password' })

      expect(result).toBe(true)
      expect(store.accessToken).toBe('access_123')
      expect(store.refreshToken).toBe('refresh_123')
      expect(store.user).toEqual(mockUser)
      expect(store.isAuthenticated).toBe(true)
      expect(store.error).toBeNull()
    })

    it('maneja errores de login', async () => {
      vi.mocked(authService.login).mockRejectedValue(new Error('Credenciales inválidas'))

      const store = useAuthStore()
      const result = await store.login({ username: 'bad', password: 'bad' })

      expect(result).toBe(false)
      expect(store.error).toBe('Credenciales inválidas')
      expect(store.isAuthenticated).toBe(false)
      expect(store.user).toBeNull()
    })

    it('muestra loading durante el login', async () => {
      vi.mocked(authService.login).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve({ access: 'a', refresh: 'r' }), 100))
      )
      vi.mocked(authService.getCurrentUser).mockResolvedValue({
        id: 1,
        username: 'test',
        email: 'test@test.com'
      })

      const store = useAuthStore()

      expect(store.loading).toBe(false)
      const loginPromise = store.login({ username: 'test', password: 'test' })
      expect(store.loading).toBe(true)

      await loginPromise
      expect(store.loading).toBe(false)
    })
  })

  describe('logout', () => {
    it('limpia el estado al hacer logout', async () => {
      const store = useAuthStore()

      // Simular estado autenticado
      store.user = { id: 1, username: 'test', email: 'test@test.com' }
      store.accessToken = 'token'
      store.refreshToken = 'refresh'

      vi.mocked(authService.logout).mockResolvedValue()

      await store.logout()

      expect(store.user).toBeNull()
      expect(store.accessToken).toBeNull()
      expect(store.refreshToken).toBeNull()
      expect(store.isAuthenticated).toBe(false)
    })

    it('limpia el estado aunque falle la llamada al servidor', async () => {
      const store = useAuthStore()

      store.user = { id: 1, username: 'test', email: 'test@test.com' }
      store.accessToken = 'token'

      vi.mocked(authService.logout).mockRejectedValue(new Error('Network error'))

      // No debe lanzar excepción
      await store.logout()

      expect(store.user).toBeNull()
      expect(store.accessToken).toBeNull()
      expect(store.isAuthenticated).toBe(false)
    })
  })

  describe('fetchUser', () => {
    it('obtiene el usuario cuando hay token', async () => {
      const mockUser = { id: 1, username: 'testuser', email: 'test@test.com' }
      vi.mocked(authService.getCurrentUser).mockResolvedValue(mockUser)

      const store = useAuthStore()
      store.accessToken = 'valid_token'

      await store.fetchUser()

      expect(store.user).toEqual(mockUser)
    })

    it('no hace nada si no hay token', async () => {
      const store = useAuthStore()
      // Asegurar que no hay token
      store.accessToken = null

      await store.fetchUser()

      expect(authService.getCurrentUser).not.toHaveBeenCalled()
      expect(store.user).toBeNull()
    })

    it('hace logout si el token es inválido', async () => {
      vi.mocked(authService.getCurrentUser).mockRejectedValue(new Error('Unauthorized'))
      vi.mocked(authService.logout).mockResolvedValue()

      const store = useAuthStore()
      store.accessToken = 'invalid_token'

      await store.fetchUser()

      expect(store.accessToken).toBeNull()
      expect(store.user).toBeNull()
    })
  })

  describe('checkAuth', () => {
    it('retorna true si el usuario está autenticado', async () => {
      const mockUser = { id: 1, username: 'test', email: 'test@test.com' }
      vi.mocked(authService.getCurrentUser).mockResolvedValue(mockUser)

      const store = useAuthStore()
      store.accessToken = 'valid_token'

      const result = await store.checkAuth()

      expect(result).toBe(true)
      expect(store.user).toEqual(mockUser)
    })

    it('retorna false si no hay token', async () => {
      const store = useAuthStore()
      // Asegurar que no hay token
      store.accessToken = null

      const result = await store.checkAuth()

      expect(result).toBe(false)
    })

    it('retorna false si el token es inválido', async () => {
      vi.mocked(authService.getCurrentUser).mockRejectedValue(new Error('Unauthorized'))
      vi.mocked(authService.logout).mockResolvedValue()

      const store = useAuthStore()
      store.accessToken = 'invalid_token'

      const result = await store.checkAuth()

      expect(result).toBe(false)
    })
  })

  describe('clearError', () => {
    it('limpia el error', () => {
      const store = useAuthStore()
      store.error = 'Algún error'

      store.clearError()

      expect(store.error).toBeNull()
    })
  })
})

// Ejecutar este test:
//   cd frontend && npm run test:unit -- --run src/stores/__tests__/auth.spec.ts
//
// Ejecutar todos los tests:
//   cd frontend && npm run test:unit
