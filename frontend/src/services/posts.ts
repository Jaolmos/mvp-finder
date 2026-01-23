import api from './api'

export interface Topic {
  id: number
  name: string
}

export interface Post {
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

export interface PostFilters {
  topic?: number
  analyzed?: boolean
  min_score?: number
  search?: string
  is_favorite?: boolean
  page?: number
}

export interface PostListResponse {
  count: number
  items: Post[]
}

export interface PostStats {
  total_posts: number
  analyzed_posts: number
  favorites_count: number
}

class PostService {
  /**
   * Listar posts con filtros
   */
  async list(filters?: PostFilters): Promise<PostListResponse> {
    const response = await api.get<PostListResponse>('/posts/', {
      params: filters,
    })
    return response.data
  }

  /**
   * Obtener detalle de un post
   */
  async get(id: number): Promise<Post> {
    const response = await api.get<Post>(`/posts/${id}/`)
    return response.data
  }

  /**
   * Marcar/desmarcar post como favorito
   */
  async toggleFavorite(id: number): Promise<{ is_favorite: boolean }> {
    const response = await api.post<{ is_favorite: boolean }>(`/posts/${id}/favorite/`)
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
   * Obtener estadísticas globales de posts
   */
  async getStats(): Promise<PostStats> {
    const response = await api.get<PostStats>('/posts/stats/')
    return response.data
  }
}

export default new PostService()
