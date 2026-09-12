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
      <path class="sketch-line sketch-line-secondary sketch-loop-echo" pathLength="1" d="M18 10C40 3 82 4 103 12" />
    </svg>

    <svg
      v-else-if="kind === 'swash'"
      class="sketch-annotation-art"
      viewBox="0 0 120 30"
      preserveAspectRatio="none"
      aria-hidden="true"
    >
      <path class="sketch-wash sketch-wash-solid" d="M2 12C25 7 45 10 64 8c20 0 38 2 54 7l-3 13c-22-1-40-2-58 0-20-1-38 2-54-2Z" />
    </svg>

    <svg
      v-else-if="kind === 'arrow'"
      class="sketch-annotation-arrow"
      viewBox="0 0 54 34"
      aria-hidden="true"
    >
      <path class="sketch-line" pathLength="1" d="M2 5c11 0 18 2 26 7 7 4 10 9 16 12" />
      <path class="sketch-line" pathLength="1" d="m37 16 8 8-10 5" />
    </svg>

    <svg
      v-else
      class="sketch-annotation-art sketch-annotation-bracket"
      viewBox="0 0 120 48"
      preserveAspectRatio="none"
      aria-hidden="true"
    >
      <path class="sketch-wash sketch-bracket-wash" d="M5 4c27-2 76-1 112 4v35c-37 2-81 1-112-1Z" />
      <path class="sketch-line sketch-bracket-line" pathLength="1" d="M12 5C7 15 7 33 12 42c8 2 17 2 26 2" />
    </svg>
  </span>
</template>

<style scoped>
.sketch-annotation {
  --sketch-ink: var(--kollio-active-ink, #493b57);
  --sketch-wash: var(--kollio-wash, #ddd3e8);
  --sketch-opacity: .54;
  --sketch-secondary-opacity: .12;
  --sketch-stroke: 1.3px;
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
  stroke-width: calc(var(--sketch-stroke) * .66);
  opacity: 0;
}

.sketch-wash {
  fill: var(--sketch-wash);
  opacity: 0;
}

.sketch-wash-solid {
  opacity: 0;
}

.sketch-loop-echo {
  transform: rotate(-1deg);
  transform-origin: center;
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
  opacity: .38;
}

.is-active .sketch-bracket-wash {
  opacity: .12;
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
