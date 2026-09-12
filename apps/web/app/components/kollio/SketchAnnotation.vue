<script setup lang="ts">
withDefaults(defineProps<{
  kind?: 'loop' | 'swash' | 'arrow' | 'bracket'
  active?: boolean
  animated?: boolean
}>(), {
  kind: 'loop',
  active: true,
  animated: true,
})
</script>

<template>
  <span
    class="sketch-annotation"
    :class="[
      `sketch-annotation--${kind}`,
      { 'is-active': active, 'is-animated': animated },
    ]"
  >
    <span class="sketch-annotation-content"><slot /></span>

    <svg
      v-if="kind === 'loop'"
      class="sketch-annotation-art"
      viewBox="0 0 120 48"
      preserveAspectRatio="none"
      aria-hidden="true"
    >
      <path class="sketch-wash" d="M8 26C9 13 29 8 60 8c31 0 52 5 53 17 1 11-20 16-53 16S7 37 8 26Z" />
      <path class="sketch-line" pathLength="1" d="M4 25C5 9 29 4 61 5c34 0 55 7 55 21 0 13-23 18-57 17C25 43 3 38 4 25Z" />
      <path class="sketch-line sketch-line-secondary" pathLength="1" d="M7 27C8 12 31 6 62 7c31 0 51 6 51 18 0 12-22 16-53 16C29 41 6 37 7 27Z" />
    </svg>

    <svg
      v-else-if="kind === 'swash'"
      class="sketch-annotation-art"
      viewBox="0 0 120 30"
      preserveAspectRatio="none"
      aria-hidden="true"
    >
      <path class="sketch-wash sketch-wash-solid" d="M3 16C23 12 43 13 62 12c21 0 39 1 55 5l-2 9c-22 1-40-1-58 0-20 0-37 2-53-1Z" />
      <path class="sketch-line sketch-swash-edge" pathLength="1" d="M4 24c23-2 42 0 61-1 20-1 35 1 51-1" />
    </svg>

    <svg
      v-else-if="kind === 'arrow'"
      class="sketch-annotation-arrow"
      viewBox="0 0 54 34"
      aria-hidden="true"
    >
      <path class="sketch-line" pathLength="1" d="M3 6c10 1 15 2 22 7 7 4 10 10 17 11" />
      <path class="sketch-line" pathLength="1" d="m36 17 7 7-9 4" />
    </svg>

    <svg
      v-else
      class="sketch-annotation-art sketch-annotation-bracket"
      viewBox="0 0 120 48"
      preserveAspectRatio="none"
      aria-hidden="true"
    >
      <path class="sketch-wash sketch-bracket-wash" d="M3 5c20-2 49-2 76-1 17 1 28 1 38 4v36c-32 1-78 1-114-1Z" />
      <path class="sketch-line" pathLength="1" d="M7 4C4 12 4 34 8 42c24 3 77 2 108 1" />
      <path class="sketch-line sketch-line-secondary" pathLength="1" d="M9 6c-2 9-2 26 1 34 23 2 73 2 104 1" />
    </svg>
  </span>
</template>

<style scoped>
.sketch-annotation {
  --sketch-ink: var(--kollio-active-ink, #493b57);
  --sketch-wash: var(--kollio-wash, #ddd3e8);
  --sketch-opacity: .68;
  --sketch-secondary-opacity: .2;
  --sketch-stroke: 1.45px;
  position: relative;
  z-index: 0;
  display: inline-flex;
  min-width: 0;
  align-items: center;
  isolation: isolate;
}

.sketch-annotation-content {
  position: relative;
  z-index: 1;
}

.sketch-annotation--loop {
  width: max-content;
  min-height: 44px;
  justify-self: start;
  padding: 8px 17px;
}

.sketch-annotation--swash {
  width: max-content;
  justify-self: start;
  padding-inline: 3px;
  vertical-align: middle;
}

.sketch-annotation--arrow {
  width: max-content;
  gap: 5px;
  justify-self: start;
  padding-right: 43px;
}

.sketch-annotation--bracket {
  display: flex;
  width: 100%;
  padding: 18px 20px;
}

.sketch-annotation-art,
.sketch-annotation-arrow {
  pointer-events: none;
}

.sketch-annotation-art {
  position: absolute;
  z-index: 0;
  inset: 0;
  width: 100%;
  height: 100%;
  overflow: visible;
}

.sketch-annotation-arrow {
  position: absolute;
  top: 50%;
  right: 0;
  width: 38px;
  height: 26px;
  overflow: visible;
  transform: translateY(-48%);
}

.sketch-line {
  fill: none;
  stroke: var(--sketch-ink);
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: var(--sketch-stroke);
  vector-effect: non-scaling-stroke;
  opacity: 0;
}

.sketch-line-secondary {
  stroke-width: calc(var(--sketch-stroke) * .72);
  opacity: 0;
}

.sketch-wash {
  fill: var(--sketch-wash);
  opacity: 0;
}

.sketch-wash-solid {
  opacity: 0;
}

.sketch-swash-edge {
  stroke-width: calc(var(--sketch-stroke) * .68);
}

.sketch-bracket-wash {
  opacity: 0;
}

.is-active .sketch-line {
  opacity: var(--sketch-opacity);
}

.is-active .sketch-line-secondary {
  opacity: var(--sketch-secondary-opacity);
}

.is-active .sketch-wash {
  opacity: .2;
}

.is-active .sketch-wash-solid {
  opacity: .46;
}

.is-active .sketch-bracket-wash {
  opacity: .15;
}

.is-animated .sketch-line {
  clip-path: inset(0 100% 0 0);
  transition: clip-path 240ms cubic-bezier(.16, 1, .3, 1), opacity 160ms ease;
}

.is-animated.is-active .sketch-line {
  clip-path: inset(0 0 0 0);
}

.is-animated .sketch-wash {
  transform: scaleX(.82);
  transform-origin: left center;
  transition: transform 200ms cubic-bezier(.16, 1, .3, 1), opacity 160ms ease;
}

.is-animated.is-active .sketch-wash {
  transform: scaleX(1);
}

@media (prefers-reduced-motion: reduce) {
  .sketch-line,
  .sketch-wash {
    transition: none !important;
  }

  .sketch-line {
    clip-path: none !important;
  }
}
</style>
