<script setup lang="ts">
withDefaults(defineProps<{
  name: string
  meta: string
  initials?: string
  imageUrl?: string
  avatarKey?: string
  online?: boolean
  to?: string
}>(), {
  initials: '',
  imageUrl: undefined,
  avatarKey: 'lilac',
  online: false,
  to: undefined,
})
</script>

<template>
  <div class="person-row">
    <span class="person-row-avatar" :data-avatar="avatarKey" aria-hidden="true">
      <img v-if="imageUrl" :src="imageUrl" alt="">
      <span v-else>{{ initials || name.charAt(0) }}</span>
    </span>
    <span class="min-w-0 flex-1">
      <NuxtLink v-if="to" :to="to" class="person-row-name">
        {{ name }}
        <span v-if="online" class="person-row-online" aria-hidden="true" />
      </NuxtLink>
      <strong v-else class="person-row-name">
        {{ name }}
        <span v-if="online" class="person-row-online" aria-hidden="true" />
      </strong>
      <span class="person-row-meta">{{ meta }}</span>
    </span>
  </div>
</template>
