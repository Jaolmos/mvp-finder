import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useToast } from '../useToast'
import { useToastStore } from '@/stores/toast'

describe('useToast', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    setActivePinia(createPinia())
  })

  it('devuelve métodos success, error, info, warning', () => {
    const toast = useToast()

    expect(toast.success).toBeDefined()
    expect(toast.error).toBeDefined()
    expect(toast.info).toBeDefined()
    expect(toast.warning).toBeDefined()
  })

  it('success llama addToast con tipo success y duración 3000ms', () => {
    const toast = useToast()
    const store = useToastStore()
    const spy = vi.spyOn(store, 'addToast')

    toast.success('Success message')

    expect(spy).toHaveBeenCalledWith('success', 'Success message', 3000)
  })

  it('error llama addToast con tipo error y duración 5000ms', () => {
    const toast = useToast()
    const store = useToastStore()
    const spy = vi.spyOn(store, 'addToast')

    toast.error('Error message')

    expect(spy).toHaveBeenCalledWith('error', 'Error message', 5000)
  })

  it('info llama addToast con tipo info y duración 3000ms', () => {
    const toast = useToast()
    const store = useToastStore()
    const spy = vi.spyOn(store, 'addToast')

    toast.info('Info message')

    expect(spy).toHaveBeenCalledWith('info', 'Info message', 3000)
  })

  it('warning llama addToast con tipo warning y duración 5000ms', () => {
    const toast = useToast()
    const store = useToastStore()
    const spy = vi.spyOn(store, 'addToast')

    toast.warning('Warning message')

    expect(spy).toHaveBeenCalledWith('warning', 'Warning message', 5000)
  })
})

// Ejecutar: cd frontend && npm run test -- useToast.spec.ts
