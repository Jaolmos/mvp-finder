import api from './api'

export interface Topic {
  id: number
  name: string
  is_active: boolean
  last_sync: string | null
  created_at: string
}

export interface TopicCreate {
  name: string
  is_active?: boolean
}

export interface TopicUpdate {
  name?: string
  is_active?: boolean
}

class TopicService {
  /**
   * Listar todos los topics
   */
  async list(): Promise<Topic[]> {
    const response = await api.get<Topic[]>('/topics/')
    return response.data
  }

  /**
   * Obtener detalle de un topic
   */
  async get(id: number): Promise<Topic> {
    const response = await api.get<Topic>(`/topics/${id}/`)
    return response.data
  }

  /**
   * Crear nuevo topic
   */
  async create(data: TopicCreate): Promise<Topic> {
    const response = await api.post<Topic>('/topics/', data)
    return response.data
  }

  /**
   * Actualizar topic
   */
  async update(id: number, data: TopicUpdate): Promise<Topic> {
    const response = await api.patch<Topic>(`/topics/${id}/`, data)
    return response.data
  }

  /**
   * Eliminar topic
   */
  async delete(id: number): Promise<void> {
    await api.delete(`/topics/${id}/`)
  }

  /**
   * Activar/desactivar topic
   */
  async toggleActive(id: number): Promise<Topic> {
    const topic = await this.get(id)
    return this.update(id, { is_active: !topic.is_active })
  }
}

export default new TopicService()
