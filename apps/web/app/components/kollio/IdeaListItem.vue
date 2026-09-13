<script setup lang="ts">
import type { IdeaSummaryResponse } from '@kollio/api-client'
import type { RouteLocationRaw } from 'vue-router'

defineProps<{
  idea: IdeaSummaryResponse
  to: RouteLocationRaw
  stageLabel: string
  dateLabel: string
}>()
</script>

<template>
  <article class="idea-list-item group">
    <div class="idea-list-item-meta">
      <KollioFeltMark active variant="status">{{ stageLabel }}</KollioFeltMark>
      <div class="idea-list-item-context">
        <span class="uppercase">{{ idea.lang }}</span>
        <time :datetime="idea.created_at">{{ dateLabel }}</time>
      </div>
    </div>

    <div class="idea-list-item-content">
      <h3>
        <NuxtLink :to="to" class="after:absolute after:inset-0">
          {{ idea.title }}
        </NuxtLink>
      </h3>
      <p>{{ idea.pitch }}</p>
    </div>

    <span class="idea-list-item-arrow" aria-hidden="true">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
        <path d="M5 12h14m-5-5 5 5-5 5" />
      </svg>
    </span>
  </article>
</template>
