<script setup lang="ts">
defineProps<{
  title: string
  eyebrow?: string
  summary?: string
}>()
</script>

<template>
  <header class="page-header">
    <div class="page-header__copy">
      <p v-if="eyebrow" class="page-header__eyebrow">{{ eyebrow }}</p>
      <h1>{{ title }}</h1>
      <p v-if="summary" class="page-header__summary">{{ summary }}</p>
    </div>
    <div v-if="$slots.action" class="page-header__action"><slot name="action" /></div>
  </header>
</template>

<style scoped>
.page-header { display: flex; flex-wrap: wrap; align-items: flex-end; justify-content: space-between; gap: var(--kollio-space-lg); }
.page-header__copy { display: grid; max-width: 72ch; gap: var(--kollio-space-sm); }
.page-header__eyebrow { color: var(--kollio-active-ink); font-size: var(--kollio-text-caption); font-weight: var(--kollio-weight-strong); letter-spacing: var(--kollio-tracking-label); text-transform: uppercase; }
.page-header h1 { color: var(--kollio-heading); font-size: var(--kollio-text-headline); font-weight: var(--kollio-weight-display); line-height: var(--kollio-leading-display); }
.page-header__summary { color: var(--ui-text-muted); font-size: var(--kollio-text-lead); line-height: var(--kollio-leading-body); }
.page-header__action { flex: none; }
@media (max-width: 639px) { .page-header__action { width: 100%; } }
</style>
