import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { useDebounce } from '../useDebounce'

describe('useDebounce', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.clearAllTimers()
  })

  it('devuelve debounce, cancel y flush', () => {
    const callback = vi.fn()
    const result = useDebounce(callback, 300)

    expect(result.debounce).toBeDefined()
    expect(result.cancel).toBeDefined()
    expect(result.flush).toBeDefined()
  })

  it('ejecuta callback después del delay', () => {
    const callback = vi.fn()
    const { debounce } = useDebounce(callback, 500)

    debounce('test value')
    expect(callback).not.toHaveBeenCalled()

    vi.advanceTimersByTime(500)
    expect(callback).toHaveBeenCalledWith('test value')
    expect(callback).toHaveBeenCalledTimes(1)
  })

  it('reinicia timer en llamadas múltiples (solo última ejecución)', () => {
    const callback = vi.fn()
    const { debounce } = useDebounce(callback, 500)

    debounce('first')
    vi.advanceTimersByTime(200)

    debounce('second')
    vi.advanceTimersByTime(200)

    debounce('third')
    vi.advanceTimersByTime(500)

    // Solo la última llamada debe ejecutarse
    expect(callback).toHaveBeenCalledTimes(1)
    expect(callback).toHaveBeenCalledWith('third')
  })

  it('usa delay por defecto de 300ms', () => {
    const callback = vi.fn()
    const { debounce } = useDebounce(callback) // Sin especificar delay

    debounce('test')

    vi.advanceTimersByTime(299)
    expect(callback).not.toHaveBeenCalled()

    vi.advanceTimersByTime(1)
    expect(callback).toHaveBeenCalledWith('test')
  })

  it('usa delay customizado cuando se provee', () => {
    const callback = vi.fn()
    const { debounce } = useDebounce(callback, 1000)

    debounce('test')

    vi.advanceTimersByTime(999)
    expect(callback).not.toHaveBeenCalled()

    vi.advanceTimersByTime(1)
    expect(callback).toHaveBeenCalledWith('test')
  })

  it('cancel() previene ejecución pendiente', () => {
    const callback = vi.fn()
    const { debounce, cancel } = useDebounce(callback, 500)

    debounce('test')
    vi.advanceTimersByTime(200)

    cancel()
    vi.advanceTimersByTime(500)

    expect(callback).not.toHaveBeenCalled()
  })

  it('flush() cancela pendiente sin ejecutar', () => {
    const callback = vi.fn()
    const { debounce, flush } = useDebounce(callback, 500)

    debounce('test')
    vi.advanceTimersByTime(200)

    flush()
    vi.advanceTimersByTime(500)

    // El callback no debe ejecutarse después de flush
    expect(callback).not.toHaveBeenCalled()
  })

  it('funciona con diferentes tipos de valores', () => {
    // String
    const stringCallback = vi.fn()
    const stringDebounce = useDebounce(stringCallback, 300)
    stringDebounce.debounce('hello')
    vi.advanceTimersByTime(300)
    expect(stringCallback).toHaveBeenCalledWith('hello')

    vi.clearAllTimers()

    // Number
    const numberCallback = vi.fn()
    const numberDebounce = useDebounce(numberCallback, 300)
    numberDebounce.debounce(42)
    vi.advanceTimersByTime(300)
    expect(numberCallback).toHaveBeenCalledWith(42)

    vi.clearAllTimers()

    // Object
    const objectCallback = vi.fn()
    const objectDebounce = useDebounce(objectCallback, 300)
    const testObj = { key: 'value' }
    objectDebounce.debounce(testObj)
    vi.advanceTimersByTime(300)
    expect(objectCallback).toHaveBeenCalledWith(testObj)
  })
})

// Ejecutar: cd frontend && npm run test -- useDebounce.spec.ts
