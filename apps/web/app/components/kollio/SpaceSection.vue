<script setup lang="ts">
defineProps<{ title: string, body: string }>()

const { t } = useI18n()
</script>

<template>
  <section class="space-section">
    <h2>{{ title }}</h2>
    <p>{{ body }}</p>
    <p class="pending">{{ t('decisionSpaces.section.pending') }}</p>
  </section>
</template>

<style scoped>
.space-section { display: flex; min-height: 300px; max-width: 62ch; flex-direction: column; justify-content: center; }
.space-section h2 { color: var(--kollio-heading); font-size: var(--kollio-text-title); font-weight: var(--kollio-weight-display); }
.space-section p { margin-top: 10px; color: var(--ui-text-muted); font-size: var(--kollio-text-small); line-height: var(--kollio-leading-body); }
.space-section .pending { color: var(--kollio-active-ink); font-weight: var(--kollio-weight-strong); }
</style>
