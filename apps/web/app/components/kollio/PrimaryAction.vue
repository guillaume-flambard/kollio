<script setup lang="ts">
import type { RouteLocationRaw } from 'vue-router'

defineProps<{
  label: string
  to?: RouteLocationRaw
  disabled?: boolean
}>()

defineEmits<{
  click: [event: MouseEvent]
}>()
</script>

<template>
  <NuxtLink v-if="to" :to="to" class="primary-action">
    {{ label }}
    <svg aria-hidden="true" viewBox="0 0 24 24" class="primary-action-arrow size-4" fill="none" stroke="currentColor" stroke-width="1.8">
      <path d="M5 12h14m-5-5 5 5-5 5" />
    </svg>
  </NuxtLink>
  <button v-else type="button" class="primary-action" :disabled="disabled" @click="$emit('click', $event)">
    {{ label }}
    <svg aria-hidden="true" viewBox="0 0 24 24" class="primary-action-arrow size-4" fill="none" stroke="currentColor" stroke-width="1.8">
      <path d="M5 12h14m-5-5 5 5-5 5" />
    </svg>
  </button>
</template>
