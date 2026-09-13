<script setup lang="ts">
withDefaults(defineProps<{
  size?: 'hero' | 'compact'
}>(), {
  size: 'compact',
})
</script>

<template>
  <span class="felt-mark" :class="`felt-mark--${size}`">
    <span class="felt-mark__content"><slot /></span>
    <svg viewBox="0 0 100 14" preserveAspectRatio="none" aria-hidden="true">
      <path d="M2 7C19 4 35 5 49 6c17 1 31-2 49 0l-1 6c-16 1-31-1-47 0-18 1-32-1-47 1Z" />
      <path class="felt-mark__grain" d="M4 9c19-2 34 0 48-1 17-1 29 1 44 0" pathLength="1" />
    </svg>
  </span>
</template>

<style scoped>
.felt-mark { position: relative; display: inline-block; isolation: isolate; }
.felt-mark__content { position: relative; z-index: 1; }
.felt-mark svg { position: absolute; z-index: 0; right: -2%; bottom: -.08em; width: 104%; height: .42em; overflow: visible; }
.felt-mark path:first-child { fill: color-mix(in srgb, var(--kollio-wash) 72%, transparent); opacity: .78; }
.felt-mark__grain { fill: none; stroke: color-mix(in srgb, white 34%, var(--kollio-wash)); stroke-dasharray: .03 .055; stroke-linecap: round; stroke-width: 1.3; opacity: .42; }
.felt-mark--compact svg { bottom: -.22em; height: .58em; }
</style>
