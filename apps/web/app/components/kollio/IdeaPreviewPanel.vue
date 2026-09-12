<script setup lang="ts">
import type { IdeaSummaryResponse } from '@kollio/api-client'

defineProps<{
  idea: IdeaSummaryResponse
  stageLabel: string
  dateLabel: string
  openLabel: string
  previewLabel: string
  domainLabel: string
  languageLabel: string
  closeLabel: string
}>()

defineEmits<{
  close: []
}>()
</script>

<template>
  <aside class="idea-preview" :aria-label="previewLabel">
    <header class="idea-preview-header">
      <span>{{ previewLabel }}</span>
      <button type="button" :aria-label="closeLabel" @click="$emit('close')">
        <svg aria-hidden="true" viewBox="0 0 24 24"><path d="m6 6 12 12M18 6 6 18" /></svg>
      </button>
    </header>

    <div class="idea-preview-body">
      <KollioSketchAnnotation kind="swash"><span>{{ stageLabel }}</span></KollioSketchAnnotation>
      <h2>{{ idea.title }}</h2>
      <p>{{ idea.pitch }}</p>

      <dl>
        <div v-if="idea.domain && idea.domain.length <= 32"><dt>{{ domainLabel }}</dt><dd>{{ idea.domain }}</dd></div>
        <div><dt>{{ languageLabel }}</dt><dd>{{ idea.lang.toUpperCase() }}</dd></div>
        <div><dt>{{ $t('ideas.explorer.updated') }}</dt><dd>{{ dateLabel }}</dd></div>
      </dl>
    </div>

    <footer>
      <KollioPrimaryAction :to="$localePath(`/workspace/ideas/${idea.id}`)" :label="openLabel" />
    </footer>
  </aside>
</template>

<style scoped>
.idea-preview { display: flex; min-width: 0; min-height: 0; flex-direction: column; background: var(--ui-bg-elevated); }
.idea-preview-header { display: flex; min-height: 62px; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--ui-border); padding: 0 22px; color: var(--ui-text-muted); font-size: .72rem; font-weight: 600; }
.idea-preview-header button { display: grid; width: 40px; height: 40px; place-items: center; border-radius: 10px; color: var(--ui-text-muted); }
.idea-preview-header button:hover { background: var(--ui-bg-muted); color: var(--kollio-heading); }
.idea-preview-header svg { width: 18px; fill: none; stroke: currentColor; stroke-linecap: round; stroke-width: 1.6; }
.idea-preview-body { min-height: 0; flex: 1; overflow-y: auto; padding: 28px 26px; }
.idea-preview-body h2 { margin-top: 18px; color: var(--kollio-heading); font-size: clamp(1.55rem, 2.25vw, 2.2rem); font-weight: 620; letter-spacing: -.045em; line-height: 1.08; text-wrap: balance; }
.idea-preview-body > p { margin-top: 22px; color: var(--ui-text-muted); font-size: .88rem; line-height: 1.68; }
.idea-preview dl { display: grid; gap: 15px; margin-top: 30px; border-top: 1px solid var(--ui-border); padding-top: 22px; }
.idea-preview dl div { display: grid; grid-template-columns: 92px minmax(0, 1fr); gap: 12px; font-size: .75rem; }
.idea-preview dt { color: var(--ui-text-muted); }
.idea-preview dd { color: var(--kollio-heading); font-weight: 560; }
.idea-preview footer { border-top: 1px solid var(--ui-border); padding: 18px 22px; }
.idea-preview footer :deep(.primary-action) { width: 100%; justify-content: space-between; }
@media (min-width: 1100px) {
  .idea-preview-header button { display: none; }
}
</style>
