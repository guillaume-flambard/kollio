<script setup lang="ts">
import type { LegacyIdeaContext } from '@kollio/api-client'

defineProps<{
  context?: LegacyIdeaContext | null
  createdAt: string
  dateLabel: string
  countLabel: string
  title: string
  importedLabel: string
  emptyLabel: string
  sourceLabel?: string
}>()
</script>

<template>
  <section class="idea-iterations" aria-labelledby="iterations-title">
    <div class="idea-section-heading">
      <h2 id="iterations-title">{{ title }}</h2>
      <span>{{ countLabel }}</span>
    </div>
    <ol v-if="context" class="iteration-timeline">
      <li class="iteration-entry">
        <time :datetime="createdAt">{{ dateLabel }}</time>
        <div>
          <p class="iteration-entry-title">{{ importedLabel }}</p>
          <p class="iteration-entry-meta">
            <span>{{ sourceLabel }}</span>
            <span aria-hidden="true" class="idea-dot" />
            <span class="break-all">{{ context.source_id }}</span>
          </p>
        </div>
      </li>
    </ol>
    <KollioEmptyState v-else class="mt-3" :description="emptyLabel" />
  </section>
</template>
