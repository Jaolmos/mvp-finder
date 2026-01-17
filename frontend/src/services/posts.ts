import api from './api'

export interface Post {
  id: number
  title: string
  content: string
  author: string
  score: number
  url: string
  created_at: string
  subreddit: string
  category?: Category
  summary?: string
  is_favorite: boolean
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
  next: string | null
  previous: string | null
  results: Post[]
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
