<script setup lang="ts">
defineProps<{
  label: string
}>()

defineEmits<{
  activate: []
}>()
</script>

<template>
  <button type="button" class="comment-composer" @click="$emit('activate')">
    <KollioIcon name="message" class="comment-composer-icon" />
    <span>{{ label }}</span>
    <span class="comment-composer-submit" aria-hidden="true">
      <KollioIcon name="arrow-right" />
    </span>
  </button>
</template>
