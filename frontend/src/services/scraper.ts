import api from './api'

export interface SyncRequest {
  topic_ids?: number[]
  limit?: number
}

export interface AnalyzeRequest {
  product_ids?: number[]
  limit?: number
}

export interface TaskResponse {
  task_id: string
  message: string
  status?: string
}

export interface OllamaStatus {
  host: string
  model: string
  ollama_available: boolean
  model_available: boolean
  ready: boolean
}

class ScraperService {
  /**
   * Sincronizar productos de Product Hunt
   * - Sin topic_ids: sincroniza todos los topics activos
   * - Con topic_ids: sincroniza solo esos topics
   */
  async syncProducts(data?: SyncRequest): Promise<TaskResponse> {
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

  /**
   * Analizar productos con Ollama IA
   * - Sin product_ids: analiza productos no analizados
   * - Con product_ids: analiza solo esos productos
   */
  async analyzeProducts(data?: AnalyzeRequest): Promise<TaskResponse> {
    const response = await api.post<TaskResponse>('/scraper/analyze/', data || {})
    return response.data
  }

  /**
   * Obtener estado de Ollama
   */
  async getOllamaStatus(): Promise<OllamaStatus> {
    const response = await api.get<OllamaStatus>('/scraper/ollama-status/')
    return response.data
  }

  /**
   * Descargar modelo de Ollama
   */
  async pullModel(): Promise<TaskResponse> {
    const response = await api.post<TaskResponse>('/scraper/pull-model/')
    return response.data
  }
}

export default new ScraperService()
