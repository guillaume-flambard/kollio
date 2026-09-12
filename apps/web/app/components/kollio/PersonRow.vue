<script setup lang="ts">
withDefaults(defineProps<{
  name: string
  meta: string
  initials?: string
  imageUrl?: string
  online?: boolean
}>(), {
  initials: '',
  imageUrl: undefined,
  online: false,
})
</script>

<template>
  <div class="person-row">
    <span class="person-row-avatar" aria-hidden="true">
      <img v-if="imageUrl" :src="imageUrl" alt="">
      <span v-else>{{ initials || name.charAt(0) }}</span>
    </span>
    <span class="min-w-0 flex-1">
      <strong class="person-row-name">
        {{ name }}
        <span v-if="online" class="person-row-online" aria-hidden="true" />
      </strong>
      <span class="person-row-meta">{{ meta }}</span>
    </span>
  </div>
</template>
