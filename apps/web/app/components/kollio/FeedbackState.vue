<script setup lang="ts">
defineProps<{
  title: string
  body?: string
  actionLabel?: string
  tone?: 'empty' | 'error'
}>()

defineEmits<{ action: [] }>()
</script>

<template>
  <section class="feedback-state" :class="`feedback-state--${tone ?? 'empty'}`">
    <p class="feedback-state__eyebrow">{{ tone === 'error' ? '!' : '·' }}</p>
    <h2>{{ title }}</h2>
    <p v-if="body">{{ body }}</p>
    <button v-if="actionLabel" type="button" @click="$emit('action')">{{ actionLabel }}</button>
  </section>
</template>

<style scoped>
.feedback-state { display: grid; max-width: 62ch; gap: var(--kollio-space-sm); padding: var(--kollio-space-2xl) 0; }
.feedback-state__eyebrow { color: var(--kollio-active-ink); font-weight: var(--kollio-weight-display); }
.feedback-state h2 { color: var(--kollio-heading); font-size: var(--kollio-text-title); font-weight: var(--kollio-weight-display); line-height: var(--kollio-leading-heading); }
.feedback-state > p:not(.feedback-state__eyebrow) { color: var(--ui-text-muted); font-size: var(--kollio-text-small); line-height: var(--kollio-leading-body); }
.feedback-state button { justify-self: start; min-height: var(--kollio-control-height); border-radius: var(--kollio-radius-md); background: var(--kollio-action); padding: 0 var(--kollio-space-lg); color: var(--kollio-on-action); font-size: var(--kollio-text-caption); font-weight: var(--kollio-weight-strong); }
.feedback-state--error .feedback-state__eyebrow { color: var(--kollio-question); }
</style>
