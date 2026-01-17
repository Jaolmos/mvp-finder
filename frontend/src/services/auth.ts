import api from './api'

export interface LoginCredentials {
  username: string
  password: string
}

export interface AuthTokens {
  access: string
  refresh: string
}

export interface User {
  id: number
  username: string
  email: string
}

class AuthService {
  /**
   * Login de usuario
   */
  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    const response = await api.post<AuthTokens>('/auth/login/', credentials)

    // Guardar tokens en localStorage
    localStorage.setItem('access_token', response.data.access)
    localStorage.setItem('refresh_token', response.data.refresh)

    return response.data
  }

  /**
   * Logout de usuario
   */
  async logout(): Promise<void> {
    try {
      await api.post('/auth/logout/')
    } finally {
      // Limpiar tokens independientemente del resultado
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }

  /**
   * Obtener información del usuario actual
   */
  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/auth/me/')
    return response.data
  }

  /**
   * Verificar si el usuario está autenticado
   */
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token')
  }

  /**
   * Obtener el token de acceso
   */
  getAccessToken(): string | null {
    return localStorage.getItem('access_token')
  }
}

export default new AuthService()
