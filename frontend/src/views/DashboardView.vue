<script setup lang="ts">
import AppLayout from '@/layouts/AppLayout.vue'
</script>

<template>
  <AppLayout>
    <div>
      <h1 class="text-2xl font-bold text-white mb-6">Dashboard</h1>

      <!-- Stats cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <div class="text-slate-400 text-sm mb-1">Total Posts</div>
          <div class="text-3xl font-bold text-white">-</div>
        </div>

        <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <div class="text-slate-400 text-sm mb-1">Posts Analizados</div>
          <div class="text-3xl font-bold text-cyan-400">-</div>
        </div>

        <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <div class="text-slate-400 text-sm mb-1">Subreddits Activos</div>
          <div class="text-3xl font-bold text-purple-400">-</div>
        </div>
      </div>

      <!-- Placeholder content -->
      <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h2 class="text-lg font-semibold text-white mb-4">Posts Recientes</h2>
        <p class="text-slate-400">No hay posts todavía. Configura tus subreddits y sincroniza.</p>
      </div>
    </div>
  </AppLayout>
</template>
