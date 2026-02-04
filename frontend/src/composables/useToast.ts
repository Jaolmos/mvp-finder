import { useToastStore } from '@/stores/toast'

export function useToast() {
  const store = useToastStore()

  return {
    success: (message: string) => store.addToast('success', message, 3000),
    error: (message: string) => store.addToast('error', message, 5000),
    info: (message: string) => store.addToast('info', message, 3000),
    warning: (message: string) => store.addToast('warning', message, 5000),
  }
}
