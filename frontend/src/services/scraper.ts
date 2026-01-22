import api from './api'

export interface SyncRequest {
  topic_ids?: number[]
  limit?: number
}

export interface TaskResponse {
  task_id: string
  message: string
  status?: string
}

class ScraperService {
  /**
   * Sincronizar posts de Product Hunt
   * - Sin topic_ids: sincroniza todos los topics activos
   * - Con topic_ids: sincroniza solo esos topics
   */
  async syncPosts(data?: SyncRequest): Promise<TaskResponse> {
    const response = await api.post<TaskResponse>('/scraper/sync/', data || {})
    return response.data
  }

  /**
   * Probar conexión con Product Hunt API
   */
  async testConnection(): Promise<TaskResponse> {
    const response = await api.post<TaskResponse>('/scraper/test-connection/')
    return response.data
  }
}

export default new ScraperService()
