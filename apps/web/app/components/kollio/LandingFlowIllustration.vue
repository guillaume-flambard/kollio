<script setup lang="ts">
withDefaults(defineProps<{
  stage: 'signal' | 'evidence' | 'question' | 'decision'
  format?: 'icon' | 'thumbnail'
}>(), {
  format: 'icon',
})
</script>

<template>
  <span class="flow-art" :class="`flow-art--${format}`" aria-hidden="true">
    <svg v-if="stage === 'signal'" viewBox="0 0 48 48" role="presentation">
      <path class="paper-muted" d="M6 13h22v25H6z" />
      <path class="paper" d="M13 8h28v29H13z" />
      <path class="ink-line" d="m18 29 6-7 5 3 7-10" />
      <circle class="ink-fill" cx="18" cy="29" r="2" />
      <circle class="ink-fill" cx="36" cy="15" r="2" />
      <path class="marker marker-coral" d="M18 33c5-1 12-1 18 0" />
    </svg>

    <svg v-else-if="stage === 'evidence'" viewBox="0 0 48 48" role="presentation">
      <path class="paper-muted" d="M7 12h26v29H7z" />
      <path class="paper" d="M14 7h27v31H14z" />
      <path class="soft-line" d="M20 15h14M20 21h10M20 27h14" />
      <path class="marker marker-lilac" d="M19 31c6-1 12-1 17 0" />
      <circle class="verified-fill" cx="38" cy="35" r="6" />
      <path class="check" d="m35 35 2 2 4-5" />
    </svg>

    <svg v-else-if="stage === 'question'" viewBox="0 0 48 48" role="presentation">
      <path class="paper" d="M8 9h32v30H8z" />
      <path class="soft-line" d="M14 30h20M14 34h13" />
      <path class="ink-line" d="M20 19c0-4 8-5 9-1 1 5-5 4-5 9" />
      <circle class="ink-fill" cx="24" cy="31" r="1.7" />
      <path class="marker marker-lilac" d="M15 36c7-1 13-1 19 0" />
    </svg>

    <svg v-else viewBox="0 0 48 48" role="presentation">
      <path class="paper" d="M6 9h35v30H6z" />
      <circle class="target" cx="17" cy="21" r="8" />
      <circle class="target" cx="17" cy="21" r="3" />
      <path class="soft-line" d="M29 17h7M29 22h7M12 32h23" />
      <path class="marker marker-olive" d="M11 35c7-1 16-1 24 0" />
      <circle class="question-fill" cx="40" cy="30" r="3" />
    </svg>
  </span>
</template>

<style scoped>
.flow-art { display: inline-grid; width: 28px; height: 28px; flex: none; place-items: center; }
.flow-art--thumbnail { width: 66px; height: 54px; padding: 3px; border: 1px solid color-mix(in srgb, var(--ui-border) 80%, transparent); border-radius: var(--kollio-radius-sm); background: color-mix(in srgb, var(--kollio-wash) 18%, white); box-shadow: 0 5px 14px color-mix(in srgb, var(--kollio-active-ink) 9%, transparent); transform: rotate(-2deg); }
svg { width: 100%; height: 100%; overflow: visible; }
.paper { fill: color-mix(in srgb, white 92%, var(--kollio-wash)); stroke: color-mix(in srgb, var(--kollio-active-ink) 30%, var(--ui-border)); stroke-linejoin: round; stroke-width: 1.2; }
.paper-muted { fill: color-mix(in srgb, var(--kollio-wash) 34%, white); stroke: color-mix(in srgb, var(--kollio-active-ink) 12%, var(--ui-border)); stroke-width: 1; transform: rotate(-4deg); transform-origin: center; }
.ink-line, .soft-line, .target { fill: none; stroke-linecap: round; stroke-linejoin: round; }
.ink-line, .target { stroke: var(--kollio-active-ink); stroke-width: 2; }
.soft-line { stroke: color-mix(in srgb, var(--kollio-active-ink) 49%, transparent); stroke-width: 1.5; }
.ink-fill { fill: var(--kollio-active-ink); }
.verified-fill { fill: var(--kollio-verified); }
.question-fill { fill: var(--kollio-question); }
.check { fill: none; stroke: white; stroke-linecap: round; stroke-linejoin: round; stroke-width: 1.6; }
.marker { fill: none; stroke-linecap: round; stroke-width: 4; opacity: .58; }
.marker-coral { stroke: var(--kollio-question-wash); }
.marker-lilac { stroke: var(--kollio-wash); }
.marker-olive { stroke: color-mix(in srgb, var(--kollio-verified) 42%, transparent); }
</style>
