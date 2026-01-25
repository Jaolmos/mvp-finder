// Exportar todos los servicios desde un punto centralizado
export { default as api } from './api'
export { default as authService } from './auth'
export { default as productService } from './products'
export { default as topicService } from './topics'
export { default as scraperService } from './scraper'

// Exportar tipos
export type { LoginCredentials, AuthTokens, User } from './auth'
export type { Product, Category, ProductFilters, ProductListResponse } from './products'
export type { Topic, TopicCreate, TopicUpdate } from './topics'
export type { SyncRequest, TaskResponse } from './scraper'
