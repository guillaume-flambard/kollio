<script setup lang="ts">
defineProps<{
  label: string
}>()

defineEmits<{
  activate: []
}>()
</script>

<template>
  <button type="button" class="comment-composer" @click="$emit('activate')">
    <svg aria-hidden="true" viewBox="0 0 24 24" class="comment-composer-icon" fill="none" stroke="currentColor" stroke-width="1.7">
      <path d="M21 11.5a8.4 8.4 0 0 1-9 8.5 9.5 9.5 0 0 1-4-.9L3 21l1.7-4.4A8.2 8.2 0 0 1 3 11.5a8.4 8.4 0 0 1 9-8.5 8.4 8.4 0 0 1 9 8.5Z" />
    </svg>
    <span>{{ label }}</span>
    <span class="comment-composer-submit" aria-hidden="true">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M5 12h14m-5-5 5 5-5 5" /></svg>
    </span>
  </button>
</template>
