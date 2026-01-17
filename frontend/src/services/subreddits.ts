import api from './api'

export interface Subreddit {
  id: number
  name: string
  is_active: boolean
  last_sync: string | null
  created_at: string
}

export interface SubredditCreate {
  name: string
  is_active?: boolean
}

export interface SubredditUpdate {
  name?: string
  is_active?: boolean
}

class SubredditService {
  /**
   * Listar todos los subreddits
   */
  async list(): Promise<Subreddit[]> {
    const response = await api.get<Subreddit[]>('/subreddits/')
    return response.data
  }

  /**
   * Obtener detalle de un subreddit
   */
  async get(id: number): Promise<Subreddit> {
    const response = await api.get<Subreddit>(`/subreddits/${id}/`)
    return response.data
  }

  /**
   * Crear nuevo subreddit
   */
  async create(data: SubredditCreate): Promise<Subreddit> {
    const response = await api.post<Subreddit>('/subreddits/', data)
    return response.data
  }

  /**
   * Actualizar subreddit
   */
  async update(id: number, data: SubredditUpdate): Promise<Subreddit> {
    const response = await api.patch<Subreddit>(`/subreddits/${id}/`, data)
    return response.data
  }

  /**
   * Eliminar subreddit
   */
  async delete(id: number): Promise<void> {
    await api.delete(`/subreddits/${id}/`)
  }

  /**
   * Activar/desactivar subreddit
   */
  async toggleActive(id: number): Promise<Subreddit> {
    const subreddit = await this.get(id)
    return this.update(id, { is_active: !subreddit.is_active })
  }
}

export default new SubredditService()
