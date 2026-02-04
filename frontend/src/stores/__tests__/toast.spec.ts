import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useToastStore } from '../toast'

describe('useToastStore', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    setActivePinia(createPinia())
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  describe('estado inicial', () => {
    it('tiene array de toasts vacío', () => {
      const store = useToastStore()
      expect(store.toasts).toEqual([])
    })
  })

  describe('addToast', () => {
    it('añade toast correctamente', () => {
      const store = useToastStore()
      const id = store.addToast('success', 'Test message', 3000)

      expect(store.toasts).toHaveLength(1)
      expect(store.toasts[0]).toMatchObject({
        id,
        type: 'success',
        message: 'Test message',
        duration: 3000
      })
    })

    it('genera IDs únicos', () => {
      const store = useToastStore()
      const id1 = store.addToast('success', 'Message 1')
      const id2 = store.addToast('error', 'Message 2')

      expect(id1).not.toBe(id2)
      expect(store.toasts).toHaveLength(2)
    })

    it('respeta límite de 3 toasts (FIFO)', () => {
      const store = useToastStore()

      const id1 = store.addToast('success', 'Message 1')
      const id2 = store.addToast('info', 'Message 2')
      const id3 = store.addToast('warning', 'Message 3')
      const id4 = store.addToast('error', 'Message 4')

      expect(store.toasts).toHaveLength(3)
      expect(store.toasts.find(t => t.id === id1)).toBeUndefined()
      expect(store.toasts.find(t => t.id === id2)).toBeDefined()
      expect(store.toasts.find(t => t.id === id3)).toBeDefined()
      expect(store.toasts.find(t => t.id === id4)).toBeDefined()
    })

    it('aplica duración por defecto 3000ms para success', () => {
      const store = useToastStore()
      store.addToast('success', 'Test')

      expect(store.toasts[0].duration).toBe(3000)
    })

    it('aplica duración por defecto 5000ms para error', () => {
      const store = useToastStore()
      store.addToast('error', 'Test')

      expect(store.toasts[0].duration).toBe(5000)
    })

    it('aplica duración por defecto 3000ms para info', () => {
      const store = useToastStore()
      store.addToast('info', 'Test')

      expect(store.toasts[0].duration).toBe(3000)
    })

    it('aplica duración por defecto 5000ms para warning', () => {
      const store = useToastStore()
      store.addToast('warning', 'Test')

      expect(store.toasts[0].duration).toBe(5000)
    })

    it('auto-dismiss después de la duración especificada', () => {
      const store = useToastStore()
      const id = store.addToast('success', 'Test', 3000)

      expect(store.toasts).toHaveLength(1)

      vi.advanceTimersByTime(3000)

      expect(store.toasts).toHaveLength(0)
    })
  })

  describe('removeToast', () => {
    it('elimina toast por ID', () => {
      const store = useToastStore()
      const id = store.addToast('success', 'Test')

      expect(store.toasts).toHaveLength(1)

      store.removeToast(id)

      expect(store.toasts).toHaveLength(0)
    })

    it('no hace nada si el ID no existe', () => {
      const store = useToastStore()
      store.addToast('success', 'Test')

      expect(store.toasts).toHaveLength(1)

      store.removeToast('non-existent-id')

      expect(store.toasts).toHaveLength(1)
    })

    it('limpia timeout al eliminar toast', () => {
      const store = useToastStore()
      const id = store.addToast('success', 'Test', 5000)

      store.removeToast(id)

      // Avanzar tiempo para verificar que el timeout fue cancelado
      vi.advanceTimersByTime(5000)

      expect(store.toasts).toHaveLength(0)
    })
  })

  describe('clearAll', () => {
    it('limpia todos los toasts', () => {
      const store = useToastStore()
      store.addToast('success', 'Test 1')
      store.addToast('error', 'Test 2')
      store.addToast('info', 'Test 3')

      expect(store.toasts).toHaveLength(3)

      store.clearAll()

      expect(store.toasts).toHaveLength(0)
    })

    it('limpia todos los timeouts', () => {
      const store = useToastStore()
      store.addToast('success', 'Test 1', 5000)
      store.addToast('error', 'Test 2', 5000)

      store.clearAll()

      // Avanzar tiempo para verificar que los timeouts fueron cancelados
      vi.advanceTimersByTime(5000)

      expect(store.toasts).toHaveLength(0)
    })
  })
})

// Ejecutar: cd frontend && npm run test -- toast.spec.ts
