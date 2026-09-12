<script setup lang="ts">
defineProps<{
  title: string
  description: string
  retryLabel: string
  backLabel: string
  backTo: string
}>()

defineEmits<{
  retry: []
}>()
</script>

<template>
  <section class="kollio-surface idea-detail-error mx-auto max-w-2xl" role="alert">
    <div class="idea-detail-error-mark" aria-hidden="true">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
        <circle cx="12" cy="12" r="9" />
        <path d="M12 7.5v5M12 16.5h.01" />
      </svg>
    </div>
    <h1>{{ title }}</h1>
    <p>{{ description }}</p>
    <div class="mt-7 flex flex-wrap gap-3">
      <KollioPrimaryAction :label="retryLabel" @click="$emit('retry')" />
      <NuxtLink :to="backTo" class="idea-detail-error-back">{{ backLabel }}</NuxtLink>
    </div>
  </section>
</template>
