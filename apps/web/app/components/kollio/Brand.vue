<script setup lang="ts">
withDefaults(defineProps<{
  compact?: boolean
}>(), {
  compact: false,
})

const { t } = useI18n()
</script>

<template>
  <span class="brand" :class="{ 'brand--compact': compact }">
    <img class="brand__mark" src="/brand/kollio-mark.svg" alt="" width="32" height="32">
    <span v-if="!compact" class="brand__wordmark">{{ t('brand') }}</span>
  </span>
</template>

<style scoped>
.brand {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  color: var(--kollio-heading);
}

.brand__mark {
  width: 1.9rem;
  height: 1.9rem;
  flex: none;
}

.brand__wordmark {
  font-family: var(--font-sans);
  font-size: var(--kollio-text-title);
  font-weight: var(--kollio-weight-display);
  letter-spacing: -0.045em;
  line-height: 1;
}

.brand--compact .brand__mark {
  width: 1.75rem;
  height: 1.75rem;
}
</style>
