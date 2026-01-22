// Exportar todos los servicios desde un punto centralizado
export { default as api } from './api'
export { default as authService } from './auth'
export { default as postService } from './posts'
export { default as topicService } from './topics'
export { default as scraperService } from './scraper'

// Exportar tipos
export type { LoginCredentials, AuthTokens, User } from './auth'
export type { Post, Category, PostFilters, PostListResponse } from './posts'
export type { Topic, TopicCreate, TopicUpdate } from './topics'
export type { SyncRequest, TaskResponse } from './scraper'
