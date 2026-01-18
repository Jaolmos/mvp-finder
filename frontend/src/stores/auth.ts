import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import authService, { type User, type LoginCredentials } from '@/services/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value)

  // Actions
  async function login(credentials: LoginCredentials): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      const tokens = await authService.login(credentials)
      accessToken.value = tokens.access
      refreshToken.value = tokens.refresh

      // Obtener info del usuario
      await fetchUser()
      return true
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Error de autenticación'
      error.value = errorMessage
      return false
    } finally {
      loading.value = false
    }
  }

  async function logout(): Promise<void> {
    try {
      await authService.logout()
    } catch {
      // Ignorar errores del servidor al hacer logout
    } finally {
      // Limpiar estado
      user.value = null
      accessToken.value = null
      refreshToken.value = null
      error.value = null
    }
  }

  async function fetchUser(): Promise<void> {
    if (!accessToken.value) return

    try {
      user.value = await authService.getCurrentUser()
    } catch {
      // Si falla, probablemente el token expiró
      await logout()
    }
  }

  async function checkAuth(): Promise<boolean> {
    if (!accessToken.value) return false

    try {
      await fetchUser()
      return !!user.value
    } catch {
      return false
    }
  }

  function clearError(): void {
    error.value = null
  }

  return {
    // State
    user,
    accessToken,
    refreshToken,
    loading,
    error,
    // Getters
    isAuthenticated,
    // Actions
    login,
    logout,
    fetchUser,
    checkAuth,
    clearError
  }
})
