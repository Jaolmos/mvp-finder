<script setup lang="ts">
import AppLayout from '@/layouts/AppLayout.vue'
</script>

<template>
  <AppLayout>
    <div>
      <h1 class="text-2xl font-bold text-white mb-6">Posts</h1>

      <!-- Filters placeholder -->
      <div class="bg-slate-800 rounded-lg p-4 border border-slate-700 mb-6">
        <div class="flex flex-wrap gap-4">
          <input
            type="text"
            placeholder="Buscar posts..."
            class="px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
          <select class="px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500">
            <option value="">Todos los subreddits</option>
          </select>
        </div>
      </div>

      <!-- Posts list placeholder -->
      <div class="bg-slate-800 rounded-lg border border-slate-700">
        <div class="p-6 text-center text-slate-400">
          No hay posts todavía.
        </div>
      </div>
    </div>
  </AppLayout>
</template>
