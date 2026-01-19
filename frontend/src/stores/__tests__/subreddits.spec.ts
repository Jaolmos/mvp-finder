import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useSubredditsStore } from '../subreddits'
import type { Subreddit } from '@/services/subreddits'

// Mock del SubredditService
vi.mock('@/services/subreddits', () => ({
  default: {
    list: vi.fn(),
    get: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    toggleActive: vi.fn()
  }
}))

import subredditService from '@/services/subreddits'

describe('useSubredditsStore', () => {
  const mockSubreddit: Subreddit = {
    id: 1,
    name: 'SomebodyMakeThis',
    is_active: true,
    last_sync: '2024-01-01T00:00:00Z',
    created_at: '2024-01-01T00:00:00Z'
  }

  const mockInactiveSubreddit: Subreddit = {
    id: 2,
    name: 'AppIdeas',
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
      const store = useSubredditsStore()

      expect(store.subreddits).toEqual([])
      expect(store.currentSubreddit).toBeNull()
      expect(store.loading).toBe(false)
      expect(store.error).toBeNull()
    })
  })

  describe('getters', () => {
    it('activeSubreddits retorna solo subreddits activos', () => {
      const store = useSubredditsStore()
      store.subreddits = [mockSubreddit, mockInactiveSubreddit]

      expect(store.activeSubreddits).toEqual([mockSubreddit])
    })

    it('inactiveSubreddits retorna solo subreddits inactivos', () => {
      const store = useSubredditsStore()
      store.subreddits = [mockSubreddit, mockInactiveSubreddit]

      expect(store.inactiveSubreddits).toEqual([mockInactiveSubreddit])
    })

    it('totalCount retorna el total de subreddits', () => {
      const store = useSubredditsStore()
      store.subreddits = [mockSubreddit, mockInactiveSubreddit]

      expect(store.totalCount).toBe(2)
    })

    it('activeCount retorna el número de subreddits activos', () => {
      const store = useSubredditsStore()
      store.subreddits = [mockSubreddit, mockInactiveSubreddit]

      expect(store.activeCount).toBe(1)
    })
  })

  describe('fetchSubreddits', () => {
    it('carga subreddits correctamente', async () => {
      vi.mocked(subredditService.list).mockResolvedValue([mockSubreddit, mockInactiveSubreddit])

      const store = useSubredditsStore()
      await store.fetchSubreddits()

      expect(store.subreddits).toEqual([mockSubreddit, mockInactiveSubreddit])
      expect(store.error).toBeNull()
    })

    it('maneja errores al cargar subreddits', async () => {
      vi.mocked(subredditService.list).mockRejectedValue(new Error('Error de red'))

      const store = useSubredditsStore()
      await store.fetchSubreddits()

      expect(store.subreddits).toEqual([])
      expect(store.error).toBe('Error de red')
    })

    it('muestra loading durante la carga', async () => {
      vi.mocked(subredditService.list).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve([mockSubreddit]), 100))
      )

      const store = useSubredditsStore()

      expect(store.loading).toBe(false)
      const fetchPromise = store.fetchSubreddits()
      expect(store.loading).toBe(true)

      await fetchPromise
      expect(store.loading).toBe(false)
    })
  })

  describe('fetchSubreddit', () => {
    it('carga un subreddit correctamente', async () => {
      vi.mocked(subredditService.get).mockResolvedValue(mockSubreddit)

      const store = useSubredditsStore()
      await store.fetchSubreddit(1)

      expect(store.currentSubreddit).toEqual(mockSubreddit)
      expect(store.error).toBeNull()
    })

    it('maneja errores al cargar un subreddit', async () => {
      vi.mocked(subredditService.get).mockRejectedValue(new Error('Subreddit no encontrado'))

      const store = useSubredditsStore()
      await store.fetchSubreddit(999)

      expect(store.currentSubreddit).toBeNull()
      expect(store.error).toBe('Subreddit no encontrado')
    })
  })

  describe('createSubreddit', () => {
    it('crea un subreddit correctamente', async () => {
      const newSubreddit = { ...mockSubreddit, id: 3, name: 'NewSubreddit' }
      vi.mocked(subredditService.create).mockResolvedValue(newSubreddit)

      const store = useSubredditsStore()
      const result = await store.createSubreddit('NewSubreddit', true)

      expect(result).toBe(true)
      expect(store.subreddits).toContainEqual(newSubreddit)
      expect(store.error).toBeNull()
    })

    it('usa is_active=true por defecto', async () => {
      const newSubreddit = { ...mockSubreddit, id: 3, name: 'NewSubreddit' }
      vi.mocked(subredditService.create).mockResolvedValue(newSubreddit)

      const store = useSubredditsStore()
      await store.createSubreddit('NewSubreddit')

      expect(subredditService.create).toHaveBeenCalledWith({
        name: 'NewSubreddit',
        is_active: true
      })
    })

    it('maneja errores al crear subreddit', async () => {
      vi.mocked(subredditService.create).mockRejectedValue(new Error('Error al crear'))

      const store = useSubredditsStore()
      const result = await store.createSubreddit('NewSubreddit')

      expect(result).toBe(false)
      expect(store.error).toBe('Error al crear')
      expect(store.subreddits).toEqual([])
    })
  })

  describe('updateSubreddit', () => {
    it('actualiza un subreddit correctamente', async () => {
      const updatedSubreddit = { ...mockSubreddit, name: 'UpdatedName' }
      vi.mocked(subredditService.update).mockResolvedValue(updatedSubreddit)

      const store = useSubredditsStore()
      store.subreddits = [mockSubreddit]

      const result = await store.updateSubreddit(1, { name: 'UpdatedName' })

      expect(result).toBe(true)
      expect(store.subreddits[0]).toEqual(updatedSubreddit)
      expect(store.error).toBeNull()
    })

    it('actualiza currentSubreddit si está cargado', async () => {
      const updatedSubreddit = { ...mockSubreddit, name: 'UpdatedName' }
      vi.mocked(subredditService.update).mockResolvedValue(updatedSubreddit)

      const store = useSubredditsStore()
      store.currentSubreddit = mockSubreddit

      await store.updateSubreddit(1, { name: 'UpdatedName' })

      expect(store.currentSubreddit).toEqual(updatedSubreddit)
    })

    it('maneja errores al actualizar subreddit', async () => {
      vi.mocked(subredditService.update).mockRejectedValue(new Error('Error al actualizar'))

      const store = useSubredditsStore()
      store.subreddits = [mockSubreddit]

      const result = await store.updateSubreddit(1, { name: 'UpdatedName' })

      expect(result).toBe(false)
      expect(store.error).toBe('Error al actualizar')
    })
  })

  describe('deleteSubreddit', () => {
    it('elimina un subreddit correctamente', async () => {
      vi.mocked(subredditService.delete).mockResolvedValue()

      const store = useSubredditsStore()
      store.subreddits = [mockSubreddit, mockInactiveSubreddit]

      const result = await store.deleteSubreddit(1)

      expect(result).toBe(true)
      expect(store.subreddits).toEqual([mockInactiveSubreddit])
      expect(store.error).toBeNull()
    })

    it('limpia currentSubreddit si se elimina', async () => {
      vi.mocked(subredditService.delete).mockResolvedValue()

      const store = useSubredditsStore()
      store.subreddits = [mockSubreddit]
      store.currentSubreddit = mockSubreddit

      await store.deleteSubreddit(1)

      expect(store.currentSubreddit).toBeNull()
    })

    it('maneja errores al eliminar subreddit', async () => {
      vi.mocked(subredditService.delete).mockRejectedValue(new Error('Error al eliminar'))

      const store = useSubredditsStore()
      store.subreddits = [mockSubreddit]

      const result = await store.deleteSubreddit(1)

      expect(result).toBe(false)
      expect(store.error).toBe('Error al eliminar')
      expect(store.subreddits).toEqual([mockSubreddit])
    })
  })

  describe('toggleActive', () => {
    it('cambia un subreddit activo a inactivo', async () => {
      const toggledSubreddit = { ...mockSubreddit, is_active: false }
      vi.mocked(subredditService.update).mockResolvedValue(toggledSubreddit)

      const store = useSubredditsStore()
      store.subreddits = [mockSubreddit]

      const result = await store.toggleActive(1)

      expect(result).toBe(true)
      expect(store.subreddits[0]?.is_active).toBe(false)
    })

    it('cambia un subreddit inactivo a activo', async () => {
      const toggledSubreddit = { ...mockInactiveSubreddit, is_active: true }
      vi.mocked(subredditService.update).mockResolvedValue(toggledSubreddit)

      const store = useSubredditsStore()
      store.subreddits = [mockInactiveSubreddit]

      const result = await store.toggleActive(2)

      expect(result).toBe(true)
      expect(store.subreddits[0]?.is_active).toBe(true)
    })

    it('retorna false si el subreddit no existe', async () => {
      const store = useSubredditsStore()
      store.subreddits = [mockSubreddit]

      const result = await store.toggleActive(999)

      expect(result).toBe(false)
      expect(store.error).toBe('Subreddit no encontrado')
    })

    it('maneja errores al hacer toggle', async () => {
      vi.mocked(subredditService.update).mockRejectedValue(new Error('Error de servidor'))

      const store = useSubredditsStore()
      store.subreddits = [mockSubreddit]

      const result = await store.toggleActive(1)

      expect(result).toBe(false)
      expect(store.error).toBe('Error de servidor')
    })
  })

  describe('clearError', () => {
    it('limpia el error', () => {
      const store = useSubredditsStore()
      store.error = 'Algún error'

      store.clearError()

      expect(store.error).toBeNull()
    })
  })

  describe('clearCurrentSubreddit', () => {
    it('limpia el subreddit actual', () => {
      const store = useSubredditsStore()
      store.currentSubreddit = mockSubreddit

      store.clearCurrentSubreddit()

      expect(store.currentSubreddit).toBeNull()
    })
  })
})

// Ejecutar este test:
//   cd frontend && npm run test -- src/stores/__tests__/subreddits.spec.ts
//
// Ejecutar todos los tests:
//   cd frontend && npm run test
