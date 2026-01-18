<script setup lang="ts">
import { useRoute } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'

const route = useRoute()
const postId = route.params.id
</script>

<template>
  <AppLayout>
    <div>
      <h1 class="text-2xl font-bold text-white mb-6">Detalle del Post #{{ postId }}</h1>

      <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <p class="text-slate-400">Cargando post...</p>
      </div>
    </div>
  </AppLayout>
</template>
