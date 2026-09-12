<script setup lang="ts">
withDefaults(defineProps<{
  active?: boolean
  variant?: 'label' | 'passage'
}>(), {
  active: false,
  variant: 'label',
})
</script>

<template>
  <span class="felt-mark" :class="[`felt-mark--${variant}`, { 'is-active': active }]">
    <slot />
  </span>
</template>
