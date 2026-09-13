<script setup lang="ts">
withDefaults(defineProps<{
  description: string
  title?: string
  actionLabel?: string
  imageSrc?: string
  imageAlt?: string
  tone?: 'neutral' | 'danger'
}>(), {
  title: undefined,
  actionLabel: undefined,
  imageSrc: undefined,
  imageAlt: '',
  tone: 'neutral',
})

defineEmits<{
  action: []
}>()
</script>

<template>
  <div class="kollio-empty-state" :class="`kollio-empty-state--${tone}`">
    <img
      v-if="imageSrc"
      class="kollio-empty-state-image"
      :src="imageSrc"
      :alt="imageAlt"
    >
    <p v-if="title" class="font-medium text-default">{{ title }}</p>
    <p :class="{ 'mt-1': title }">{{ description }}</p>
    <button v-if="actionLabel" type="button" class="kollio-empty-state-action" @click="$emit('action')">
      {{ actionLabel }}
    </button>
  </div>
</template>
