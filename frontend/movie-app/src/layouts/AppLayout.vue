<template>
  <div class="app-layout">
    <Navigation />
    <slot />
  </div>
</template>

<script setup lang="ts">
import Navigation from '@/components/Navigation.vue'
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  background: #0d1117;
}
</style>