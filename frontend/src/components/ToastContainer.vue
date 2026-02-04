<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useToastStore } from '@/stores/toast'
import type { ToastType } from '@/types/toast'

const toastStore = useToastStore()
const { toasts } = storeToRefs(toastStore)

const toastClasses = (type: ToastType) => {
  const baseClasses = 'bg-white shadow-lg border rounded-lg px-4 py-3 min-w-[320px] max-w-[400px]'
  const typeClasses = {
    success: 'border-green-500 bg-green-50 text-green-800',
    error: 'border-red-500 bg-red-50 text-red-800',
    info: 'border-blue-500 bg-blue-50 text-blue-800',
    warning: 'border-amber-500 bg-amber-50 text-amber-800',
  }
  return `${baseClasses} ${typeClasses[type]}`
}

const iconColor = (type: ToastType) => {
  const colors = {
    success: '#22c55e',
    error: '#ef4444',
    info: '#3b82f6',
    warning: '#f59e0b',
  }
  return colors[type]
}

const ariaLive = (type: ToastType) => {
  return type === 'error' || type === 'warning' ? 'assertive' : 'polite'
}
</script>

<template>
  <div class="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
    <TransitionGroup name="toast">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="toastClasses(toast.type)"
        class="toast-item pointer-events-auto"
        role="alert"
        :aria-live="ariaLive(toast.type)"
      >
        <div class="flex items-center gap-3">
          <!-- Icono según tipo -->
          <div class="flex-shrink-0">
            <!-- Success: CheckCircle -->
            <svg
              v-if="toast.type === 'success'"
              class="w-5 h-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              :style="{ color: iconColor(toast.type) }"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>

            <!-- Error: XCircle -->
            <svg
              v-else-if="toast.type === 'error'"
              class="w-5 h-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              :style="{ color: iconColor(toast.type) }"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>

            <!-- Info: InformationCircle -->
            <svg
              v-else-if="toast.type === 'info'"
              class="w-5 h-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              :style="{ color: iconColor(toast.type) }"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>

            <!-- Warning: ExclamationTriangle -->
            <svg
              v-else-if="toast.type === 'warning'"
              class="w-5 h-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              :style="{ color: iconColor(toast.type) }"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>

          <!-- Mensaje -->
          <p class="flex-1 text-sm font-medium">{{ toast.message }}</p>

          <!-- Botón cerrar -->
          <button
            @click="toastStore.removeToast(toast.id)"
            class="flex-shrink-0 hover:opacity-70 transition-opacity"
            aria-label="Cerrar notificación"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
/* Animaciones de entrada */
.toast-enter-active {
  animation: toast-in 0.3s ease-out;
}

/* Animaciones de salida */
.toast-leave-active {
  animation: toast-out 0.3s ease-in;
}

@keyframes toast-in {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes toast-out {
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(100%);
    opacity: 0;
  }
}

/* Responsive mobile */
@media (max-width: 640px) {
  .toast-item {
    min-width: 280px;
    max-width: calc(100vw - 2rem);
  }
}
</style>
