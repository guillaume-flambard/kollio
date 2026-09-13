<script setup lang="ts">
defineProps<{
  name: 'signal' | 'data' | 'idea' | 'evidence' | 'question' | 'decision' | 'context' | 'sparkles' | 'search'
}>()
</script>

<template>
  <svg class="landing-glyph" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <template v-if="name === 'signal'">
      <path d="M3 12h4l2.2-6 4.1 12 2.1-6H21" />
    </template>
    <template v-else-if="name === 'data'">
      <ellipse cx="12" cy="5" rx="7" ry="3" /><path d="M5 5v6c0 1.7 3.1 3 7 3s7-1.3 7-3V5M5 11v6c0 1.7 3.1 3 7 3s7-1.3 7-3v-6" />
    </template>
    <template v-else-if="name === 'idea'">
      <path d="M9 18h6M10 21h4M8.3 15.5A7 7 0 1 1 15.7 15.5C14.8 16.2 14 17 14 18h-4c0-1-.8-1.8-1.7-2.5Z" />
    </template>
    <template v-else-if="name === 'evidence'">
      <path d="M6 3h9l3 3v15H6zM14 3v4h4M9 11h6M9 15h6" />
    </template>
    <template v-else-if="name === 'question'">
      <circle cx="12" cy="12" r="9" /><path d="M9.8 9a2.4 2.4 0 0 1 4.6 1c0 1.7-2.4 2-2.4 3.7M12 17.5h.01" />
    </template>
    <template v-else-if="name === 'decision'">
      <circle cx="12" cy="12" r="9" /><path d="m8 12 2.5 2.5L16 9" />
    </template>
    <template v-else-if="name === 'context'">
      <circle cx="8" cy="8" r="3" /><circle cx="16" cy="16" r="3" /><path d="m10.2 10.2 3.6 3.6M16 5v3M5 16h3" />
    </template>
    <template v-else-if="name === 'sparkles'">
      <path d="m12 3 1.2 3.8L17 8l-3.8 1.2L12 13l-1.2-3.8L7 8l3.8-1.2ZM18 14l.7 2.3L21 17l-2.3.7L18 20l-.7-2.3L15 17l2.3-.7Z" />
    </template>
    <template v-else>
      <circle cx="10.5" cy="10.5" r="6" /><path d="m15 15 5 5" />
    </template>
  </svg>
</template>

<style scoped>
.landing-glyph { display: block; width: 1em; height: 1em; }
</style>
