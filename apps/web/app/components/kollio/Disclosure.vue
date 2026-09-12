<script setup lang="ts">
defineProps<{
  modelValue: boolean
  contentId: string
  expandLabel: string
  collapseLabel: string
}>()

defineEmits<{
  'update:modelValue': [expanded: boolean]
}>()
</script>

<template>
  <div class="kollio-disclosure" :class="{ 'is-expanded': modelValue }">
    <div :id="contentId" class="kollio-disclosure-content">
      <slot />
    </div>
    <button
      type="button"
      class="kollio-disclosure-toggle"
      :aria-controls="contentId"
      :aria-expanded="modelValue"
      @click="$emit('update:modelValue', !modelValue)"
    >
      <span>{{ modelValue ? collapseLabel : expandLabel }}</span>
      <svg aria-hidden="true" viewBox="0 0 20 20" class="size-4" fill="none" stroke="currentColor" stroke-width="1.6">
        <path :d="modelValue ? 'm5 12 5-5 5 5' : 'm5 8 5 5 5-5'" />
      </svg>
    </button>
  </div>
</template>
