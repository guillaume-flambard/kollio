<script setup lang="ts">
withDefaults(defineProps<{
  direction?: 'down-right' | 'down-left'
}>(), {
  direction: 'down-right',
})
</script>

<template>
  <svg class="hand-arrow" :class="`hand-arrow--${direction}`" viewBox="0 0 80 84" aria-hidden="true">
    <template v-if="direction === 'down-right'">
      <path class="hand-arrow__main" d="M8 7C10 31 25 51 68 61" pathLength="1" />
      <path class="hand-arrow__echo" d="M9 8C12 32 27 50 67 60" pathLength="1" />
      <path class="hand-arrow__head" d="m57 52 12 9-14 5" />
    </template>
    <template v-else>
      <path class="hand-arrow__main" d="M60 6C74 28 71 52 51 72" pathLength="1" />
      <path class="hand-arrow__echo" d="M59 7C72 29 69 51 50 71" pathLength="1" />
      <path class="hand-arrow__head" d="m58 60-7 13 14-2" />
    </template>
  </svg>
</template>

<style scoped>
.hand-arrow { overflow: visible; color: var(--kollio-active-ink); }
.hand-arrow path { fill: none; stroke: currentColor; stroke-linecap: round; stroke-linejoin: round; }
.hand-arrow__main { stroke-width: 1.55; }
.hand-arrow__echo { stroke-dasharray: 5 7; stroke-width: .75; opacity: .28; }
.hand-arrow__head { stroke-width: 1.55; }
@media (prefers-reduced-motion: no-preference) { .hand-arrow__main, .hand-arrow__head { stroke-dasharray: 1; animation: hand-arrow-draw 650ms 520ms cubic-bezier(.16, 1, .3, 1) both; } }
@keyframes hand-arrow-draw { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
</style>
