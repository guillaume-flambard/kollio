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
      <span aria-hidden="true">{{ initials(person.display_name) }}</span>
      <span class="sr-only">{{ person.display_name }}</span>
    </li>
  </ul>
</template>

<style scoped>
.avatar-stack { display: flex; align-items: center; padding-left: 8px; }
.avatar-stack li { display: grid; width: 30px; height: 30px; place-items: center; margin-left: -8px; border: 2px solid var(--ui-bg-elevated); border-radius: 50%; background: var(--kollio-wash); color: var(--kollio-heading); font-size: .61rem; font-weight: 720; letter-spacing: -.02em; }
.avatar-stack li[data-avatar='rose'] { background: color-mix(in srgb, var(--kollio-question-wash) 72%, white); }
.avatar-stack li[data-avatar='ochre'] { background: color-mix(in srgb, var(--ui-warning) 28%, white); }
.avatar-stack li[data-avatar='citron'] { background: color-mix(in srgb, var(--kollio-verified) 34%, white); }
.avatar-stack li[data-avatar='coral'] { background: color-mix(in srgb, var(--ui-error) 16%, white); }
.avatar-stack li[data-avatar='sage'] { background: color-mix(in srgb, var(--ui-success) 18%, white); }
</style>
