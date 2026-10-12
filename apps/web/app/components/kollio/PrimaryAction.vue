<script setup lang="ts">
import type { RouteLocationRaw } from 'vue-router'

defineProps<{
  label: string
  to?: RouteLocationRaw
  href?: string
  disabled?: boolean
}>()

defineEmits<{
  click: [event: MouseEvent]
}>()
</script>

<template>
  <a v-if="href" :href="href" class="primary-action">
    {{ label }}
    <KollioIcon class="primary-action-arrow" name="arrow-right" />
  </a>
  <NuxtLink v-else-if="to" :to="to" class="primary-action">
    {{ label }}
    <KollioIcon class="primary-action-arrow" name="arrow-right" />
  </NuxtLink>
  <button v-else type="button" class="primary-action" :disabled="disabled" @click="$emit('click', $event)">
    {{ label }}
    <KollioIcon class="primary-action-arrow" name="arrow-right" />
  </button>
</template>
