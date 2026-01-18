<script setup lang="ts">
import AppLayout from '@/layouts/AppLayout.vue'
</script>

<template>
  <AppLayout>
    <div>
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold text-white">Subreddits</h1>
        <button class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg transition-colors">
          Añadir Subreddit
        </button>
      </div>

      <!-- Subreddits list placeholder -->
      <div class="bg-slate-800 rounded-lg border border-slate-700">
        <div class="p-6 text-center text-slate-400">
          No hay subreddits configurados.
        </div>
      </div>
    </div>
  </AppLayout>
</template>
