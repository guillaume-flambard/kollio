<script setup lang="ts">
import type { IdeaSummaryResponse } from '@kollio/api-client'

defineProps<{
  idea: IdeaSummaryResponse
  selected: boolean
  stageLabel: string
  dateLabel: string
}>()

defineEmits<{
  select: []
}>()
</script>

<template>
  <button
    type="button"
    class="explorer-row"
    :class="{ 'is-selected': selected }"
    :aria-pressed="selected"
    @click="$emit('select')"
  >
    <KollioSketchAnnotation v-if="selected" kind="bracket" class="explorer-row-selection">
      <span class="sr-only">{{ stageLabel }}</span>
    </KollioSketchAnnotation>

    <span class="explorer-row-copy">
      <span class="explorer-row-meta">
        <KollioSketchAnnotation kind="swash"><span>{{ stageLabel }}</span></KollioSketchAnnotation>
        <span v-if="idea.domain && idea.domain.length <= 32">{{ idea.domain }}</span>
        <time :datetime="idea.created_at">{{ dateLabel }}</time>
      </span>
      <strong>{{ idea.title }}</strong>
    </span>

    <span class="explorer-row-arrow" aria-hidden="true">
      <svg viewBox="0 0 24 24"><path d="M5 12h14m-5-5 5 5-5 5" /></svg>
    </span>
  </button>
</template>

<style scoped>
.explorer-row { position: relative; display: grid; width: 100%; min-height: 100px; grid-template-columns: minmax(0, 1fr) 28px; align-items: center; gap: 20px; overflow: hidden; border-bottom: 1px solid var(--ui-border); padding: 18px 24px; text-align: left; transition: background 180ms ease; }
.explorer-row:hover, .explorer-row:focus-visible, .explorer-row.is-selected { background: color-mix(in srgb, var(--kollio-wash) 16%, var(--ui-bg-elevated)); }
.explorer-row:focus-visible { outline: 2px solid color-mix(in srgb, var(--kollio-active-ink) 58%, transparent); outline-offset: -3px; }
.explorer-row-selection { position: absolute; z-index: 0; inset: 5px 8px; width: auto; height: calc(100% - 10px); padding: 0; }
.explorer-row-copy { position: relative; z-index: 1; min-width: 0; }
.explorer-row-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 7px 12px; color: var(--ui-text-muted); font-size: .69rem; }
.explorer-row-meta > * + *::before { margin-right: 12px; color: var(--ui-border-accented); content: '·'; }
.explorer-row strong { display: block; margin-top: 12px; color: var(--kollio-heading); font-size: clamp(.98rem, 1.25vw, 1.12rem); font-weight: 620; letter-spacing: -.022em; line-height: 1.28; }
.explorer-row-arrow { position: relative; z-index: 1; color: var(--ui-text-muted); font-size: 1.05rem; transition: color 180ms ease, transform 180ms cubic-bezier(.16, 1, .3, 1); }
.explorer-row-arrow svg { width: 17px; fill: none; stroke: currentColor; stroke-linecap: round; stroke-linejoin: round; stroke-width: 1.7; }
.explorer-row:hover .explorer-row-arrow, .explorer-row.is-selected .explorer-row-arrow { color: var(--kollio-active-ink); transform: translateX(3px); }
</style>
