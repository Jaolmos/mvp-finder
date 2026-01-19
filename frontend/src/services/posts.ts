import api from './api'

export interface Subreddit {
  id: number
  name: string
}

export interface Post {
  id: number
  reddit_id: string
  subreddit: Subreddit
  title: string
  content?: string // Solo en detalle
  author: string
  score: number
  url: string
  created_at_reddit: string
  created_at?: string // Solo en detalle
  updated_at?: string // Solo en detalle
  analyzed: boolean
  summary?: string
  problem?: string // Solo en detalle
  mvp_idea?: string // Solo en detalle
  target_audience?: string // Solo en detalle
  potential_score?: number | null
  tags?: string
  analyzed_at?: string | null // Solo en detalle
  is_favorite?: boolean
}

export interface Category {
  id: number
  name: string
  description: string
}

export interface PostFilters {
  subreddit?: string
  category?: number
  search?: string
  is_favorite?: boolean
  ordering?: string
  page?: number
  page_size?: number
}

export interface PostListResponse {
  count: number
  items: Post[]
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
}

export default new PostService()
