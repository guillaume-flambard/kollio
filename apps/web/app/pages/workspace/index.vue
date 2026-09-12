<script setup lang="ts">
import type { IdeaPageResponse, WorkspaceResponse } from '@kollio/api-client'
import { motion, useReducedMotion } from 'motion-v'

definePageMeta({ layout: 'workspace', middleware: 'authenticated' })

const { t, locale } = useI18n()
const route = useRoute()
const requestFetch = useRequestFetch()
const localePath = useLocalePath()
const reducedMotion = useReducedMotion()
const pageSize = 12

const { data: workspaces } = await useAsyncData('workspaces', () =>
  requestFetch<WorkspaceResponse[]>('/api/workspaces'),
)

const activeWorkspace = computed(() => {
  const requestedId = typeof route.query.workspace === 'string' ? route.query.workspace : undefined
  return workspaces.value?.find(workspace => workspace.id === requestedId) ?? workspaces.value?.[0]
})

const currentPage = computed(() => {
  const value = Number(route.query.page ?? 1)
  return Number.isInteger(value) && value > 0 ? value : 1
})

const { data: ideaPage, status, error } = await useAsyncData(
  'workspace-ideas',
  async () => {
    if (!activeWorkspace.value) return undefined
    return requestFetch<IdeaPageResponse>(
      `/api/workspaces/${encodeURIComponent(activeWorkspace.value.id)}/ideas`,
      { query: { limit: pageSize, offset: (currentPage.value - 1) * pageSize } },
    )
  },
  { watch: [activeWorkspace, currentPage] },
)

const totalPages = computed(() => Math.max(1, Math.ceil((ideaPage.value?.total ?? 0) / pageSize)))
const dateFormatter = computed(() =>
  new Intl.DateTimeFormat(locale.value, { day: 'numeric', month: 'short', year: 'numeric' }),
)

function pageLocation(page: number) {
  return {
    path: localePath('/workspace'),
    query: {
      ...(activeWorkspace.value ? { workspace: activeWorkspace.value.id } : {}),
      ...(page > 1 ? { page: String(page) } : {}),
    },
  }
}

useSeoMeta({ title: () => t('workspace.metaTitle') })
</script>

<template>
  <div>
    <section v-if="!activeWorkspace" class="mx-auto max-w-2xl py-24 text-center">
    <div class="mx-auto flex size-12 items-center justify-center rounded-2xl border border-default bg-elevated shadow-xs">
      <svg aria-hidden="true" viewBox="0 0 24 24" class="size-5" fill="none" stroke="currentColor" stroke-width="1.7">
        <path d="M4 7.5h16M7.5 4v7M16.5 4v7M5 11.5h14v8H5z" />
      </svg>
    </div>
    <h1 class="font-display mt-6 text-4xl font-bold tracking-tight">{{ t('workspace.empty.title') }}</h1>
    <p class="mx-auto mt-3 max-w-lg leading-relaxed text-muted">{{ t('workspace.empty.description') }}</p>
    </section>

    <template v-else>
    <motion.section
      :initial="{ opacity: 0, y: reducedMotion ? 0 : 10 }"
      :animate="{ opacity: 1, y: 0 }"
      :transition="{ duration: reducedMotion ? 0 : 0.35 }"
      class="border-b border-default pb-9"
    >
      <div class="flex flex-wrap items-end justify-between gap-6">
        <div>
          <div class="mb-4 flex items-center gap-2 text-sm text-muted">
            <span class="size-2 rounded-full bg-success" aria-hidden="true" />
            <span>{{ t(`workspace.role.${activeWorkspace.role}`) }}</span>
          </div>
          <h1 class="font-display text-4xl font-bold tracking-tight sm:text-5xl">{{ activeWorkspace.name }}</h1>
          <p class="mt-3 max-w-2xl text-base leading-relaxed text-muted">{{ t('workspace.description') }}</p>
        </div>
        <div class="rounded-2xl border border-default bg-elevated px-5 py-4 shadow-xs">
          <p class="font-mono text-2xl font-semibold tabular-nums">{{ ideaPage?.total ?? 0 }}</p>
          <p class="mt-1 text-xs font-medium tracking-wide text-muted uppercase">{{ t('workspace.ideaLabel') }}</p>
        </div>
      </div>
    </motion.section>

    <section class="pt-9" :aria-labelledby="'idea-list-title'">
      <div class="mb-6 flex items-center justify-between gap-4">
        <div>
          <p class="text-xs font-semibold tracking-[0.14em] text-primary uppercase">{{ t('ideas.eyebrow') }}</p>
          <h2 id="idea-list-title" class="font-display mt-1 text-2xl font-semibold">{{ t('ideas.title') }}</h2>
        </div>
        <p v-if="ideaPage" class="text-sm text-muted">
          {{ t('ideas.page', { current: currentPage, total: totalPages }) }}
        </p>
      </div>

      <div v-if="status === 'pending'" class="grid gap-4 md:grid-cols-2 xl:grid-cols-3" aria-live="polite">
        <div v-for="index in 6" :key="index" class="h-64 animate-pulse rounded-2xl border border-default bg-elevated" />
      </div>

      <div v-else-if="error" class="rounded-2xl border border-error/30 bg-error/5 p-6">
        <h3 class="font-display text-xl font-semibold">{{ t('ideas.error.title') }}</h3>
        <p class="mt-2 text-sm text-muted">{{ t('ideas.error.description') }}</p>
      </div>

      <div v-else-if="ideaPage?.items.length" class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <motion.article
          v-for="(idea, index) in ideaPage.items"
          :key="idea.id"
          :initial="{ opacity: 0, y: reducedMotion ? 0 : 8 }"
          :animate="{ opacity: 1, y: 0 }"
          :transition="{ duration: reducedMotion ? 0 : 0.28, delay: reducedMotion ? 0 : index * 0.025 }"
          class="group relative flex min-h-64 flex-col rounded-2xl border border-default bg-elevated p-6 shadow-xs transition-[border-color,transform] hover:-translate-y-0.5 hover:border-primary/35"
        >
          <div class="flex items-center justify-between gap-3">
            <span class="rounded-full bg-muted px-2.5 py-1 text-xs font-semibold text-muted">
              {{ t(`ideas.stage.${idea.stage}`) }}
            </span>
            <span class="font-mono text-xs text-muted uppercase">{{ idea.lang }}</span>
          </div>
          <h3 class="font-display mt-5 text-xl leading-snug font-semibold tracking-tight">
            <NuxtLink :to="$localePath(`/workspace/ideas/${idea.id}`)" class="after:absolute after:inset-0">
              {{ idea.title }}
            </NuxtLink>
          </h3>
          <p class="mt-3 line-clamp-3 text-sm leading-relaxed text-muted">{{ idea.pitch }}</p>
          <div class="mt-auto flex items-center justify-between border-t border-default pt-5 text-xs text-muted">
            <time :datetime="idea.created_at">{{ dateFormatter.format(new Date(idea.created_at)) }}</time>
            <svg aria-hidden="true" viewBox="0 0 24 24" class="size-4 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M5 12h14m-5-5 5 5-5 5" />
            </svg>
          </div>
        </motion.article>
      </div>

      <div v-else class="rounded-2xl border border-dashed border-default py-16 text-center">
        <h3 class="font-display text-xl font-semibold">{{ t('ideas.empty.title') }}</h3>
        <p class="mt-2 text-sm text-muted">{{ t('ideas.empty.description') }}</p>
      </div>

      <nav v-if="ideaPage && totalPages > 1" class="mt-9 flex items-center justify-between border-t border-default pt-6" :aria-label="t('ideas.pagination')">
        <NuxtLink
          v-if="currentPage > 1"
          :to="pageLocation(currentPage - 1)"
          class="inline-flex items-center gap-2 rounded-lg border border-default bg-elevated px-4 py-2 text-sm font-medium shadow-xs hover:bg-accented"
        >
          <svg aria-hidden="true" viewBox="0 0 24 24" class="size-4" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m15 18-6-6 6-6" /></svg>
          {{ t('ideas.previous') }}
        </NuxtLink>
        <span v-else />
        <NuxtLink
          v-if="currentPage < totalPages"
          :to="pageLocation(currentPage + 1)"
          class="inline-flex items-center gap-2 rounded-lg border border-default bg-elevated px-4 py-2 text-sm font-medium shadow-xs hover:bg-accented"
        >
          {{ t('ideas.next') }}
          <svg aria-hidden="true" viewBox="0 0 24 24" class="size-4" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m9 18 6-6-6-6" /></svg>
        </NuxtLink>
      </nav>
    </section>
    </template>
  </div>
</template>
