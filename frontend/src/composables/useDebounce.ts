import { ref } from 'vue'

/**
 * Composable para debouncing de funciones.
 * Útil para reducir llamadas API mientras el usuario escribe.
 *
 * @param callback - Función a ejecutar después del delay
 * @param delay - Delay en milisegundos (default: 300ms)
 * @returns Objeto con métodos debounce, cancel, flush
 *
 * @example
 * ```typescript
 * const debouncedSearch = useDebounce(() => {
 *   performSearch()
 * }, 400)
 *
 * watch(searchQuery, () => {
 *   debouncedSearch.debounce('')
 * })
 *
 * onUnmounted(() => {
 *   debouncedSearch.cancel()
 * })
 * ```
 */
export function useDebounce<T>(callback: (value: T) => void, delay: number = 300) {
  const timeoutId = ref<NodeJS.Timeout | null>(null)

  const debounce = (value: T) => {
    // Limpiar timeout anterior si existe
    if (timeoutId.value !== null) {
      clearTimeout(timeoutId.value)
    }

    // Crear nuevo timeout
    timeoutId.value = setTimeout(() => {
      callback(value)
      timeoutId.value = null
    }, delay)
  }

  const cancel = () => {
    if (timeoutId.value !== null) {
      clearTimeout(timeoutId.value)
      timeoutId.value = null
    }
  }

  const flush = () => {
    if (timeoutId.value !== null) {
      clearTimeout(timeoutId.value)
      timeoutId.value = null
    }
  }

  return {
    debounce,
    cancel,
    flush,
  }
}
