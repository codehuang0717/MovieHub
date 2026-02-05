<template>
  <div class="app-layout">
    <Navigation />
    <slot />
    <AIChat />
  </div>
</template>

<script setup lang="ts">
import Navigation from '@/components/Navigation.vue'
import AIChat from '@/components/AIChat.vue'
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  background: #0d1117;
}
</style>