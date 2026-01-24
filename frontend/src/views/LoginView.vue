<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AuthLayout from '@/layouts/AuthLayout.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')

async function handleSubmit() {
  const success = await authStore.login({
    username: username.value,
    password: password.value
  })

  if (success) {
    const redirect = route.query.redirect as string || '/'
    router.push(redirect)
  }
}
</script>

<template>
  <AuthLayout>
    <form @submit.prevent="handleSubmit" class="bg-dark-800 rounded-lg p-6 sm:p-8 shadow-xl border border-dark-700">
      <h2 class="text-xl sm:text-2xl font-semibold text-white mb-6 text-center">Iniciar sesión</h2>

      <!-- Error message -->
      <div
        v-if="authStore.error"
        class="mb-4 p-3 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400 text-sm"
      >
        {{ authStore.error }}
      </div>

      <!-- Username -->
      <div class="mb-4">
        <label for="username" class="block text-sm font-medium text-dark-300 mb-2">
          Usuario
        </label>
        <input
          id="username"
          v-model="username"
          type="text"
          required
          autocomplete="username"
          class="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white placeholder-dark-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          placeholder="Tu nombre de usuario"
        />
      </div>

      <!-- Password -->
      <div class="mb-6">
        <label for="password" class="block text-sm font-medium text-dark-300 mb-2">
          Contraseña
        </label>
        <input
          id="password"
          v-model="password"
          type="password"
          required
          autocomplete="current-password"
          class="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white placeholder-dark-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          placeholder="Tu contraseña"
        />
      </div>

      <!-- Submit button -->
      <button
        type="submit"
        :disabled="authStore.loading"
        class="w-full py-2 px-4 bg-primary-600 hover:bg-primary-700 disabled:bg-primary-600/50 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-offset-dark-800"
      >
        <span v-if="authStore.loading" class="flex items-center justify-center">
          <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Iniciando sesión...
        </span>
        <span v-else>Iniciar sesión</span>
      </button>
    </form>
  </AuthLayout>
</template>
