import api from './api'

export interface Topic {
  id: number
  name: string
}

export interface Product {
  id: number
  external_id: string
  topic: Topic
  title: string
  tagline: string
  content?: string
  author: string
  score: number
  votes_count: number
  comments_count: number
  url: string
  website?: string | null
  created_at_source: string
  created_at?: string
  updated_at?: string
  analyzed: boolean
  summary?: string
  problem?: string
  mvp_idea?: string
  target_audience?: string
  potential_score?: number | null
  tags?: string
  analyzed_at?: string | null
  is_favorite?: boolean
  has_note?: boolean
}

export interface Category {
  id: number
  name: string
  description: string
}

export interface ProductFilters {
  topic?: number
  analyzed?: boolean
  min_score?: number
  min_potential?: number
  search?: string
  is_favorite?: boolean
  ordering?: string
  tag?: string
  page?: number
  page_size?: number
}

export interface ProductListResponse {
  count: number
  items: Product[]
}

export interface ProductStats {
  total_products: number
  analyzed_products: number
  favorites_count: number
}

export interface ProductNote {
  id: number
  content: string
  created_at: string
  updated_at: string
}

export interface NoteCreatePayload {
  content: string
}

export interface NoteUpdatePayload {
  content: string
}

export interface NoteResponse {
  success: boolean
  message: string
  note: ProductNote
}

class ProductService {
  /**
   * Listar productos con filtros
   */
  async list(filters?: ProductFilters): Promise<ProductListResponse> {
    const response = await api.get<ProductListResponse>('/products/', {
      params: filters,
    })
    return response.data
  }

  /**
   * Obtener detalle de un producto
   */
  async get(id: number): Promise<Product> {
    const response = await api.get<Product>(`/products/${id}/`)
    return response.data
  }

  /**
   * Marcar/desmarcar producto como favorito
   */
  async toggleFavorite(id: number): Promise<{ is_favorite: boolean }> {
    const response = await api.post<{ is_favorite: boolean }>(`/products/${id}/favorite/`)
    return response.data
  }

  /**
   * Eliminar un producto
   */
  async delete(id: number): Promise<{ success: boolean; message: string }> {
    const response = await api.delete<{ success: boolean; message: string }>(`/products/${id}/`)
    return response.data
  }

  /**
   * Listar categorías
   */
  async listCategories(): Promise<Category[]> {
    const response = await api.get<Category[]>('/categories/')
    return response.data
  }

  /**
   * Obtener estadísticas globales de productos
   */
  async getStats(): Promise<ProductStats> {
    const response = await api.get<ProductStats>('/products/stats/')
    return response.data
  }

  /**
   * Obtener nota de un producto
   */
  async getNote(productId: number): Promise<ProductNote | null> {
    try {
      const response = await api.get<ProductNote>(`/products/${productId}/note/`)
      return response.data
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null // No hay nota
      }
      throw error
    }
  }

  /**
   * Crear nota para un producto
   */
  async createNote(productId: number, payload: NoteCreatePayload): Promise<NoteResponse> {
    const response = await api.post<NoteResponse>(`/products/${productId}/note/`, payload)
    return response.data
  }

  /**
   * Actualizar nota de un producto
   */
  async updateNote(productId: number, payload: NoteUpdatePayload): Promise<NoteResponse> {
    const response = await api.put<NoteResponse>(`/products/${productId}/note/`, payload)
    return response.data
  }

  /**
   * Eliminar nota de un producto
   */
  async deleteNote(productId: number): Promise<{ message: string }> {
    const response = await api.delete<{ message: string }>(`/products/${productId}/note/`)
    return response.data
  }
}

export default new ProductService()
