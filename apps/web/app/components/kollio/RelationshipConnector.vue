<script setup lang="ts">
withDefaults(defineProps<{
  path: string
  startX: number
  startY: number
  endX: number
  endY: number
  muted?: boolean
  showStart?: boolean
  showEnd?: boolean
}>(), {
  muted: false,
  showStart: true,
  showEnd: true,
})
</script>

<template>
  <svg class="relationship-connector" :class="{ 'relationship-connector--muted': muted }" viewBox="0 0 1426 348" preserveAspectRatio="none" aria-hidden="true">
    <path :d="path" pathLength="1" />
    <circle v-if="showStart" :cx="startX" :cy="startY" r="4" />
    <circle v-if="showEnd" :cx="endX" :cy="endY" r="4" />
  </svg>
</template>

<style scoped>
.relationship-connector { position: absolute; z-index: 0; inset: 0; width: 100%; height: 100%; overflow: visible; pointer-events: none; }
.relationship-connector path { fill: none; stroke: var(--kollio-connector); stroke-linecap: round; stroke-width: 1.65; vector-effect: non-scaling-stroke; }
.relationship-connector circle { fill: var(--kollio-connector); }
.relationship-connector--muted { opacity: .22; }
@media (prefers-reduced-motion: no-preference) { .relationship-connector path { stroke-dasharray: 1; animation: connector-draw 760ms 320ms cubic-bezier(.16, 1, .3, 1) both; } }
@keyframes connector-draw { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
</style>
