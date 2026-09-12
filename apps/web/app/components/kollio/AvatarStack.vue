<script setup lang="ts">
import type { CollaboratorResponse } from '@kollio/api-client'

defineProps<{
  people: CollaboratorResponse[]
  label: string
}>()

function initials(name: string) {
  return name.split(/\s+/).slice(0, 2).map(part => part.charAt(0)).join('').toUpperCase()
}
</script>

<template>
  <ul class="avatar-stack" :aria-label="label">
    <li v-for="person in people.slice(0, 4)" :key="person.id" :data-avatar="person.avatar_key || 'lilac'">
      <span class="avatar-stack-fallback" aria-hidden="true">{{ initials(person.display_name) }}</span>
      <span class="sr-only">{{ person.display_name }}</span>
    </li>
  </ul>
</template>

<style scoped>
.avatar-stack { display: flex; align-items: center; padding-left: 8px; }
.avatar-stack li { display: grid; width: 32px; height: 32px; place-items: center; margin-left: -8px; overflow: hidden; border: 2px solid var(--ui-bg-elevated); border-radius: 50%; background-color: var(--kollio-wash); background-image: url('/avatars/collaborator-sprite.webp'); background-position: 0 0; background-size: 300% 200%; color: var(--kollio-heading); font-size: .61rem; font-weight: 720; letter-spacing: -.02em; }
.avatar-stack li[data-avatar='rose'] { background-position: 50% 0; }
.avatar-stack li[data-avatar='ochre'] { background-position: 100% 0; }
.avatar-stack li[data-avatar='citron'] { background-position: 0 100%; }
.avatar-stack li[data-avatar='coral'] { background-position: 50% 100%; }
.avatar-stack li[data-avatar='sage'] { background-position: 100% 100%; }
.avatar-stack-fallback { opacity: 0; }
</style>
