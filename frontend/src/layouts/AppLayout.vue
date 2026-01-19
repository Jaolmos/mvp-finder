<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

// Estado del sidebar para móvil
const isSidebarOpen = ref(false)

async function handleLogout() {
  await authStore.logout()
  router.push({ name: 'login' })
}

// Toggle sidebar en móvil
const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

// Cerrar sidebar al navegar (móvil)
const closeSidebar = () => {
  isSidebarOpen.value = false
}

// Cerrar sidebar al hacer click en un link
router.afterEach(() => {
  closeSidebar()
})
</script>

<template>
  <div class="min-h-screen bg-slate-900">
    <!-- Backdrop móvil (solo visible cuando sidebar está abierto) -->
    <div
      v-if="isSidebarOpen"
      @click="closeSidebar"
      class="fixed inset-0 bg-black/50 z-30 md:hidden"
    ></div>

    <!-- Sidebar -->
    <aside
      class="fixed inset-y-0 left-0 w-64 bg-slate-800 border-r border-slate-700 z-40 transition-transform duration-300"
      :class="isSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'"
    >
      <!-- Logo -->
      <div class="h-16 flex items-center px-6 border-b border-slate-700">
        <h1 class="text-xl font-bold text-purple-400">Reddit MVP Finder</h1>
      </div>

      <!-- Navigation -->
      <nav class="p-4 space-y-2">
        <RouterLink
          to="/"
          class="flex items-center px-4 py-2 rounded-lg text-slate-300 hover:bg-slate-700 hover:text-white transition-colors"
          active-class="bg-purple-600 text-white hover:bg-purple-600"
        >
          <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          Dashboard
        </RouterLink>

        <RouterLink
          to="/posts"
          class="flex items-center px-4 py-2 rounded-lg text-slate-300 hover:bg-slate-700 hover:text-white transition-colors"
          active-class="bg-purple-600 text-white hover:bg-purple-600"
        >
          <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
          </svg>
          Posts
        </RouterLink>

        <RouterLink
          to="/subreddits"
          class="flex items-center px-4 py-2 rounded-lg text-slate-300 hover:bg-slate-700 hover:text-white transition-colors"
          active-class="bg-purple-600 text-white hover:bg-purple-600"
        >
          <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A2 2 0 013 12V7a4 4 0 014-4z" />
          </svg>
          Subreddits
        </RouterLink>
      </nav>
    </aside>

    <!-- Main content -->
    <div class="md:pl-64">
      <!-- Header -->
      <header class="h-16 bg-slate-800 border-b border-slate-700 flex items-center justify-between px-4 md:px-6">
        <!-- Botón hamburguesa (solo móvil) -->
        <button
          @click="toggleSidebar"
          class="p-2 text-slate-300 hover:text-white hover:bg-slate-700 rounded-lg transition-colors md:hidden"
          aria-label="Toggle menu"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>

        <!-- User info y logout -->
        <div class="flex items-center space-x-4 ml-auto">
          <span class="text-slate-300 text-sm md:text-base">{{ authStore.user?.username }}</span>
          <button
            @click="handleLogout"
            class="px-3 py-2 md:px-4 text-sm text-slate-300 hover:text-white hover:bg-slate-700 rounded-lg transition-colors"
          >
            Cerrar sesión
          </button>
        </div>
      </header>

      <!-- Page content -->
      <main class="p-4 md:p-6">
        <slot />
      </main>
    </div>
  </div>
</template>
