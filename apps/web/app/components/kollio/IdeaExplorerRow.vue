<script setup lang="ts">
import type { IdeaSummaryResponse } from '@kollio/api-client'

defineProps<{
  idea: IdeaSummaryResponse
  number: string
  to: string
  stageLabel: string
  dateLabel: string
}>()
</script>

<template>
  <NuxtLink
    :to="to"
    class="explorer-row"
  >
    <span class="explorer-row-number">{{ number }}</span>

    <span class="explorer-row-copy">
      <strong>{{ idea.title }}</strong>
      <span class="explorer-row-pitch">{{ idea.pitch }}</span>
    </span>

    <span class="explorer-row-meta">
      <span>{{ stageLabel }}</span>
      <time :datetime="idea.created_at">{{ dateLabel }}</time>
    </span>

    <span class="explorer-row-arrow" aria-hidden="true">
      <svg viewBox="0 0 24 24"><path d="M5 12h14m-5-5 5 5-5 5" /></svg>
    </span>
  </NuxtLink>
</template>

<style scoped>
.explorer-row { position: relative; display: grid; width: 100%; min-height: 122px; grid-template-columns: 32px minmax(0, 1fr) minmax(108px, 136px) 24px; align-items: center; gap: 20px; overflow: hidden; border-bottom: 1px solid var(--ui-border); padding: 20px 26px; text-align: left; transition: background 180ms ease; }
.explorer-row:hover, .explorer-row:focus-visible { background: color-mix(in srgb, var(--kollio-wash) 16%, var(--ui-bg-elevated)); }
.explorer-row:focus-visible { outline: 2px solid color-mix(in srgb, var(--kollio-active-ink) 58%, transparent); outline-offset: -3px; }
.explorer-row-number { align-self: start; padding-top: 4px; color: var(--ui-text-muted); font-size: .68rem; font-variant-numeric: tabular-nums; }
.explorer-row-copy { min-width: 0; }
.explorer-row strong { display: block; color: var(--kollio-heading); font-size: clamp(1rem, 1.25vw, 1.14rem); font-weight: 610; letter-spacing: -.025em; line-height: 1.28; }
.explorer-row-pitch { display: -webkit-box; overflow: hidden; margin-top: 8px; color: var(--ui-text-muted); font-size: .79rem; line-height: 1.5; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }
.explorer-row-meta { display: grid; gap: 9px; color: var(--ui-text-muted); font-size: .69rem; }
.explorer-row-meta span { color: var(--kollio-active-ink); font-weight: 570; }
.explorer-row-arrow { position: relative; z-index: 1; color: var(--ui-text-muted); font-size: 1.05rem; transition: color 180ms ease, transform 180ms cubic-bezier(.16, 1, .3, 1); }
.explorer-row-arrow svg { width: 17px; fill: none; stroke: currentColor; stroke-linecap: round; stroke-linejoin: round; stroke-width: 1.7; }
.explorer-row:hover .explorer-row-arrow { color: var(--kollio-active-ink); transform: translateX(3px); }
@media (max-width: 840px) {
  .explorer-row { min-height: 128px; grid-template-columns: 24px minmax(0, 1fr) 20px; gap: 14px; padding: 20px 18px; }
  .explorer-row-meta { display: none; }
}
@media (max-width: 480px) {
  .explorer-row { grid-template-columns: minmax(0, 1fr) 20px; }
  .explorer-row-number { display: none; }
}
</style>
