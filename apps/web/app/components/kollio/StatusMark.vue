<script setup lang="ts">
withDefaults(defineProps<{ label: string, tone?: 'active' | 'verified' | 'question' }>(), { tone: 'active' })
</script>

<template>
  <span class="status-mark" :class="`status-mark--${tone}`" :aria-label="label">{{ label }}</span>
</template>

<style scoped>
.status-mark { display: inline-flex; min-height: var(--kollio-control-height); align-items: center; border-radius: var(--kollio-radius-md); padding: 0 var(--kollio-space-md); font-size: var(--kollio-text-caption); font-weight: var(--kollio-weight-strong); }
.status-mark--active { background: var(--kollio-active-wash); color: var(--kollio-active-ink); }
.status-mark--verified { background: color-mix(in srgb, var(--kollio-verified) 20%, transparent); color: var(--kollio-verified); }
.status-mark--question { background: var(--kollio-question-wash); color: var(--kollio-question); }
</style>
