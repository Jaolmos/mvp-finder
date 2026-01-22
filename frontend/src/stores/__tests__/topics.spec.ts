import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useTopicsStore } from '../topics'
import type { Topic } from '@/services/topics'

// Mock del TopicService
vi.mock('@/services/topics', () => ({
  default: {
    list: vi.fn(),
    get: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    toggleActive: vi.fn()
  }
}))

import topicService from '@/services/topics'

describe('useTopicsStore', () => {
  const mockTopic: Topic = {
    id: 1,
    name: 'artificial-intelligence',
    is_active: true,
    last_sync: '2024-01-01T00:00:00Z',
    created_at: '2024-01-01T00:00:00Z'
  }

  const mockInactiveTopic: Topic = {
    id: 2,
    name: 'developer-tools',
    is_active: false,
    last_sync: null,
    created_at: '2024-01-01T00:00:00Z'
  }

  beforeEach(() => {
    vi.clearAllMocks()
    setActivePinia(createPinia())
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('estado inicial', () => {
    it('tiene valores por defecto correctos', () => {
      const store = useTopicsStore()

      expect(store.topics).toEqual([])
      expect(store.currentTopic).toBeNull()
      expect(store.loading).toBe(false)
      expect(store.error).toBeNull()
    })
  })

  describe('getters', () => {
    it('activeTopics retorna solo topics activos', () => {
      const store = useTopicsStore()
      store.topics = [mockTopic, mockInactiveTopic]

      expect(store.activeTopics).toEqual([mockTopic])
    })

    it('inactiveTopics retorna solo topics inactivos', () => {
      const store = useTopicsStore()
      store.topics = [mockTopic, mockInactiveTopic]

      expect(store.inactiveTopics).toEqual([mockInactiveTopic])
    })

    it('totalCount retorna el total de topics', () => {
      const store = useTopicsStore()
      store.topics = [mockTopic, mockInactiveTopic]

      expect(store.totalCount).toBe(2)
    })

    it('activeCount retorna el número de topics activos', () => {
      const store = useTopicsStore()
      store.topics = [mockTopic, mockInactiveTopic]

      expect(store.activeCount).toBe(1)
    })
  })

  describe('fetchTopics', () => {
    it('carga topics correctamente', async () => {
      vi.mocked(topicService.list).mockResolvedValue([mockTopic, mockInactiveTopic])

      const store = useTopicsStore()
      await store.fetchTopics()

      expect(store.topics).toEqual([mockTopic, mockInactiveTopic])
      expect(store.error).toBeNull()
    })

    it('maneja errores al cargar topics', async () => {
      vi.mocked(topicService.list).mockRejectedValue(new Error('Error de red'))

      const store = useTopicsStore()
      await store.fetchTopics()

      expect(store.topics).toEqual([])
      expect(store.error).toBe('Error de red')
    })

    it('muestra loading durante la carga', async () => {
      vi.mocked(topicService.list).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve([mockTopic]), 100))
      )

      const store = useTopicsStore()

      expect(store.loading).toBe(false)
      const fetchPromise = store.fetchTopics()
      expect(store.loading).toBe(true)

      await fetchPromise
      expect(store.loading).toBe(false)
    })
  })

  describe('fetchTopic', () => {
    it('carga un topic correctamente', async () => {
      vi.mocked(topicService.get).mockResolvedValue(mockTopic)

      const store = useTopicsStore()
      await store.fetchTopic(1)

      expect(store.currentTopic).toEqual(mockTopic)
      expect(store.error).toBeNull()
    })

    it('maneja errores al cargar un topic', async () => {
      vi.mocked(topicService.get).mockRejectedValue(new Error('Topic no encontrado'))

      const store = useTopicsStore()
      await store.fetchTopic(999)

      expect(store.currentTopic).toBeNull()
      expect(store.error).toBe('Topic no encontrado')
    })
  })

  describe('createTopic', () => {
    it('crea un topic correctamente', async () => {
      const newTopic = { ...mockTopic, id: 3, name: 'new-topic' }
      vi.mocked(topicService.create).mockResolvedValue(newTopic)

      const store = useTopicsStore()
      const result = await store.createTopic('new-topic', true)

      expect(result).toBe(true)
      expect(store.topics).toContainEqual(newTopic)
      expect(store.error).toBeNull()
    })

    it('usa is_active=true por defecto', async () => {
      const newTopic = { ...mockTopic, id: 3, name: 'new-topic' }
      vi.mocked(topicService.create).mockResolvedValue(newTopic)

      const store = useTopicsStore()
      await store.createTopic('new-topic')

      expect(topicService.create).toHaveBeenCalledWith({
        name: 'new-topic',
        is_active: true
      })
    })

    it('maneja errores al crear topic', async () => {
      vi.mocked(topicService.create).mockRejectedValue(new Error('Error al crear'))

      const store = useTopicsStore()
      const result = await store.createTopic('new-topic')

      expect(result).toBe(false)
      expect(store.error).toBe('Error al crear')
      expect(store.topics).toEqual([])
    })
  })

  describe('updateTopic', () => {
    it('actualiza un topic correctamente', async () => {
      const updatedTopic = { ...mockTopic, name: 'updated-name' }
      vi.mocked(topicService.update).mockResolvedValue(updatedTopic)

      const store = useTopicsStore()
      store.topics = [mockTopic]

      const result = await store.updateTopic(1, { name: 'updated-name' })

      expect(result).toBe(true)
      expect(store.topics[0]).toEqual(updatedTopic)
      expect(store.error).toBeNull()
    })

    it('actualiza currentTopic si está cargado', async () => {
      const updatedTopic = { ...mockTopic, name: 'updated-name' }
      vi.mocked(topicService.update).mockResolvedValue(updatedTopic)

      const store = useTopicsStore()
      store.currentTopic = mockTopic

      await store.updateTopic(1, { name: 'updated-name' })

      expect(store.currentTopic).toEqual(updatedTopic)
    })

    it('maneja errores al actualizar topic', async () => {
      vi.mocked(topicService.update).mockRejectedValue(new Error('Error al actualizar'))

      const store = useTopicsStore()
      store.topics = [mockTopic]

      const result = await store.updateTopic(1, { name: 'updated-name' })

      expect(result).toBe(false)
      expect(store.error).toBe('Error al actualizar')
    })
  })

  describe('deleteTopic', () => {
    it('elimina un topic correctamente', async () => {
      vi.mocked(topicService.delete).mockResolvedValue()

      const store = useTopicsStore()
      store.topics = [mockTopic, mockInactiveTopic]

      const result = await store.deleteTopic(1)

      expect(result).toBe(true)
      expect(store.topics).toEqual([mockInactiveTopic])
      expect(store.error).toBeNull()
    })

    it('limpia currentTopic si se elimina', async () => {
      vi.mocked(topicService.delete).mockResolvedValue()

      const store = useTopicsStore()
      store.topics = [mockTopic]
      store.currentTopic = mockTopic

      await store.deleteTopic(1)

      expect(store.currentTopic).toBeNull()
    })

    it('maneja errores al eliminar topic', async () => {
      vi.mocked(topicService.delete).mockRejectedValue(new Error('Error al eliminar'))

      const store = useTopicsStore()
      store.topics = [mockTopic]

      const result = await store.deleteTopic(1)

      expect(result).toBe(false)
      expect(store.error).toBe('Error al eliminar')
      expect(store.topics).toEqual([mockTopic])
    })
  })

  describe('toggleActive', () => {
    it('cambia un topic activo a inactivo', async () => {
      const toggledTopic = { ...mockTopic, is_active: false }
      vi.mocked(topicService.update).mockResolvedValue(toggledTopic)

      const store = useTopicsStore()
      store.topics = [mockTopic]

      const result = await store.toggleActive(1)

      expect(result).toBe(true)
      expect(store.topics[0]?.is_active).toBe(false)
    })

    it('cambia un topic inactivo a activo', async () => {
      const toggledTopic = { ...mockInactiveTopic, is_active: true }
      vi.mocked(topicService.update).mockResolvedValue(toggledTopic)

      const store = useTopicsStore()
      store.topics = [mockInactiveTopic]

      const result = await store.toggleActive(2)

      expect(result).toBe(true)
      expect(store.topics[0]?.is_active).toBe(true)
    })

    it('retorna false si el topic no existe', async () => {
      const store = useTopicsStore()
      store.topics = [mockTopic]

      const result = await store.toggleActive(999)

      expect(result).toBe(false)
      expect(store.error).toBe('Topic no encontrado')
    })

    it('maneja errores al hacer toggle', async () => {
      vi.mocked(topicService.update).mockRejectedValue(new Error('Error de servidor'))

      const store = useTopicsStore()
      store.topics = [mockTopic]

      const result = await store.toggleActive(1)

      expect(result).toBe(false)
      expect(store.error).toBe('Error de servidor')
    })
  })

  describe('clearError', () => {
    it('limpia el error', () => {
      const store = useTopicsStore()
      store.error = 'Algún error'

      store.clearError()

      expect(store.error).toBeNull()
    })
  })

  describe('clearCurrentTopic', () => {
    it('limpia el topic actual', () => {
      const store = useTopicsStore()
      store.currentTopic = mockTopic

      store.clearCurrentTopic()

      expect(store.currentTopic).toBeNull()
    })
  })
})

// Ejecutar este test:
//   cd frontend && npm run test -- src/stores/__tests__/topics.spec.ts
//
// Ejecutar todos los tests:
//   cd frontend && npm run test
