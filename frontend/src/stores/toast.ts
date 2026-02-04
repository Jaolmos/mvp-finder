import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { Toast, ToastType } from '@/types/toast'

export const useToastStore = defineStore('toast', () => {
  // State
  const toasts = ref<Toast[]>([])
  const timeouts = new Map<string, number>()

  // Actions
  function addToast(type: ToastType, message: string, duration?: number): string {
    // Generar ID único
    const id = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

    // Determinar duración por defecto según tipo
    const defaultDuration = type === 'error' || type === 'warning' ? 5000 : 3000
    const finalDuration = duration ?? defaultDuration

    // Aplicar límite FIFO: si hay 3 toasts, eliminar el más antiguo
    if (toasts.value.length >= 3) {
      const oldestToast = toasts.value[0]
      removeToast(oldestToast.id)
    }

    // Crear toast
    const toast: Toast = {
      id,
      type,
      message,
      duration: finalDuration,
      createdAt: Date.now(),
    }

    // Añadir al array
    toasts.value.push(toast)

    // Auto-dismiss después de la duración especificada
    const timeout = window.setTimeout(() => {
      removeToast(id)
    }, finalDuration)

    timeouts.set(id, timeout)

    return id
  }

  function removeToast(id: string): void {
    // Limpiar timeout si existe
    const timeout = timeouts.get(id)
    if (timeout) {
      clearTimeout(timeout)
      timeouts.delete(id)
    }

    // Eliminar toast del array
    const index = toasts.value.findIndex(t => t.id === id)
    if (index !== -1) {
      toasts.value.splice(index, 1)
    }
  }

  function clearAll(): void {
    // Limpiar todos los timeouts
    timeouts.forEach(timeout => clearTimeout(timeout))
    timeouts.clear()

    // Vaciar array de toasts
    toasts.value = []
  }

  return {
    toasts,
    addToast,
    removeToast,
    clearAll,
  }
})
