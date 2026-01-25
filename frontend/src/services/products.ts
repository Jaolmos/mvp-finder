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
}

export default new ProductService()
