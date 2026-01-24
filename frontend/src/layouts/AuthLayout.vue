<script setup lang="ts">
</script>

<template>
  <div class="min-h-screen bg-dark-900 flex items-center justify-center px-4">
    <div class="w-full max-w-md">
      <!-- Logo -->
      <div class="text-center mb-6 sm:mb-8">
        <h1 class="text-2xl sm:text-3xl font-bold text-primary-400">MVP Finder</h1>
        <p class="text-sm sm:text-base text-dark-400 mt-2">Descubre oportunidades de negocio</p>
      </div>

      <!-- Content -->
      <slot />
    </div>
  </div>
</template>
