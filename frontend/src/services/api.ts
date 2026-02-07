import axios, { type AxiosInstance, type InternalAxiosRequestConfig } from 'axios'

// URL base de la API
// En desarrollo: Vite proxy /api → localhost:8000
// En producción: Host Nginx proxy /api → backend:8000
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

// Crear instancia de Axios
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor de request: añadir token JWT si existe
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token')

    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor de response: manejar errores de autenticación
api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config

    // Si el error es 401 (no autorizado) y no es un retry
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const refreshToken = localStorage.getItem('refresh_token')

      if (refreshToken) {
        try {
          // Intentar refrescar el token
          const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
            refresh: refreshToken,
          })

          const { access } = response.data

          // Guardar nuevo token
          localStorage.setItem('access_token', access)

          // Reintentar la petición original con el nuevo token
          originalRequest.headers.Authorization = `Bearer ${access}`
          return api(originalRequest)
        } catch (refreshError) {
          // Si falla el refresh, limpiar tokens y redirigir a login
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
          return Promise.reject(refreshError)
        }
      } else {
        // No hay refresh token, redirigir a login
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

export default api
