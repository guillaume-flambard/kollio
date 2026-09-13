<script setup lang="ts">
type ArtworkName =
  | 'shared-context'
  | 'explainable-decisions'
  | 'controlled-ai'
  | 'decision-memory'
  | 'team-alignment'

const props = withDefaults(defineProps<{
  name: ArtworkName
  eager?: boolean
}>(), {
  eager: false,
})

const sources: Record<ArtworkName, string> = {
  'shared-context': '/images/landing/shared-context.svg',
  'explainable-decisions': '/images/landing/explainable-decisions.svg',
  'controlled-ai': '/images/landing/controlled-ai.svg',
  'decision-memory': '/images/landing/decision-memory.svg',
  'team-alignment': '/images/landing/team-alignment.svg',
}

const dimensions: Record<ArtworkName, { width: number, height: number }> = {
  'shared-context': { width: 256, height: 256 },
  'explainable-decisions': { width: 256, height: 256 },
  'controlled-ai': { width: 256, height: 256 },
  'decision-memory': { width: 480, height: 300 },
  'team-alignment': { width: 320, height: 220 },
}
</script>

<template>
  <img
    class="kollio-artwork"
    :src="sources[props.name]"
    :data-artwork="props.name"
    alt=""
    aria-hidden="true"
    :width="dimensions[props.name].width"
    :height="dimensions[props.name].height"
    :loading="props.eager ? 'eager' : 'lazy'"
    decoding="async"
  >
</template>

<style scoped>
.kollio-artwork {
  display: block;
  object-fit: contain;
}
</style>
