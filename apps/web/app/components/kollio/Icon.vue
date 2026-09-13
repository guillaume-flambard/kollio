<script setup lang="ts">
const paths = {
  plus: 'M12 5v14M5 12h14',
  'chevron-up': 'm6 15 6-6 6 6',
  'chevron-down': 'm6 9 6 6 6-6',
  'chevron-right': 'm9 18 6-6-6-6',
  'arrow-right': 'M5 12h14m-5-5 5 5-5 5',
  message:
    'M21 11.5a8.4 8.4 0 0 1-9 8.5 9.5 9.5 0 0 1-4-.9L3 21l1.7-4.4A8.2 8.2 0 0 1 3 11.5a8.4 8.4 0 0 1 9-8.5 8.4 8.4 0 0 1 9 8.5Z',
} as const

export type KollioIconName = keyof typeof paths | 'ellipsis' | 'search'

defineProps<{
  name: KollioIconName
}>()
</script>

<template>
  <svg
    aria-hidden="true"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.8"
    stroke-linecap="round"
    stroke-linejoin="round"
  >
    <template v-if="name === 'ellipsis'">
      <circle cx="5" cy="12" r="1.5" fill="currentColor" stroke="none" />
      <circle cx="12" cy="12" r="1.5" fill="currentColor" stroke="none" />
      <circle cx="19" cy="12" r="1.5" fill="currentColor" stroke="none" />
    </template>
    <template v-if="name === 'search'">
      <circle cx="11" cy="11" r="7" />
      <path d="m16 16 5 5" />
    </template>
    <path v-else-if="name in paths" :d="paths[name as keyof typeof paths]" />
  </svg>
</template>
