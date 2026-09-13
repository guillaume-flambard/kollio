<script setup lang="ts">
import type { TimelineView } from '../../utils/timeline'

defineProps<{
  view: TimelineView
  title: string
  countLabel: string
  emptyLabel: string
  importedLabel?: string
  branchLabel?: (name: string) => string
}>()
</script>

<template>
  <section class="idea-iterations" aria-labelledby="iterations-title">
    <div class="idea-section-heading">
      <h2 id="iterations-title">{{ title }}</h2>
      <span>{{ countLabel }}</span>
    </div>
    <p v-if="importedLabel" class="iteration-imported">{{ importedLabel }}</p>
    <ol v-if="view.main.length || view.branches.length" class="iteration-timeline">
      <li v-for="entry in view.main" :key="entry.key" class="iteration-entry" data-line="main">
        <time :datetime="entry.dateLabel">{{ entry.dateLabel }}</time>
        <div>
          <p class="iteration-entry-title">{{ entry.message }}</p>
          <p class="iteration-entry-meta">
            <span>{{ entry.authorLabel }}</span>
            <span aria-hidden="true" class="idea-dot" />
            <span class="break-all">{{ entry.hash }}</span>
            <span v-if="entry.analysisLabel" class="iteration-analysis">{{ entry.analysisLabel }}</span>
          </p>
        </div>
      </li>
      <li
        v-for="branch in view.branches"
        :key="branch.key"
        class="iteration-entry iteration-entry-branch"
        data-line="branch"
      >
        <span v-if="branchLabel">{{ branchLabel(branch.name) }}</span>
        <div>
          <p
            v-for="entry in branch.entries"
            :key="entry.key"
            class="iteration-entry-title"
            :data-status="entry.statusLabel ?? undefined"
          >
            {{ entry.message }}
            <span v-if="entry.statusLabel" class="iteration-status">{{ entry.statusLabel }}</span>
            <span v-if="entry.analysisLabel" class="iteration-analysis">{{ entry.analysisLabel }}</span>
          </p>
          <p class="iteration-entry-meta">
            <span>{{ branch.entries[branch.entries.length - 1]?.authorLabel }}</span>
            <span aria-hidden="true" class="idea-dot" />
            <span class="break-all">{{ branch.entries[branch.entries.length - 1]?.hash }}</span>
          </p>
        </div>
      </li>
    </ol>
    <p v-else-if="!importedLabel" class="iteration-empty">{{ emptyLabel }}</p>
  </section>
</template>

<style scoped>
.idea-iterations { display: grid; gap: 14px; }
.idea-section-heading { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; }
.idea-section-heading h2 { margin: 0; font-size: 1.375rem; font-weight: 600; letter-spacing: -0.025em; }
.idea-section-heading span { color: var(--ui-text-muted); font-size: .8rem; }
.iteration-imported { margin: 0; color: var(--ui-text-muted); font-size: .82rem; }
.iteration-timeline { display: grid; gap: 0; margin: 0; padding: 0 0 0 18px; list-style: none; border-left: 2px solid var(--ui-border); }
.iteration-entry { position: relative; display: grid; grid-template-columns: 110px 1fr; gap: 14px; padding: 14px 0; }
.iteration-entry::before { position: absolute; top: 20px; left: -23px; width: 8px; height: 8px; border-radius: 50%; background: var(--kollio-active-ink); content: ''; }
.iteration-entry time { color: var(--ui-text-muted); font-size: .78rem; }
.iteration-entry-branch::before { background: var(--question-clay, #D47A70); }
.iteration-entry-title { margin: 0; font-size: .92rem; font-weight: 570; display: flex; flex-wrap: wrap; gap: 8px; align-items: baseline; }
.iteration-entry-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin: 4px 0 0; color: var(--ui-text-muted); font-size: .78rem; }
.iteration-status { border-radius: 999px; padding: 2px 10px; background: var(--ui-bg-inverted); color: var(--ui-text-inverted); font-size: .68rem; font-weight: 600; }
.iteration-analysis { color: var(--kollio-active-ink); font-weight: 600; }
.iteration-empty { margin: 0; color: var(--ui-text-muted); font-size: .85rem; }
</style>
