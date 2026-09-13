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
      <KollioIcon :name="modelValue ? 'chevron-up' : 'chevron-down'" class="size-4" />
    </button>
  </div>
</template>
