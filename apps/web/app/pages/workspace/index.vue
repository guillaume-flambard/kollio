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
  <div class="mx-auto max-w-5xl">
    <section v-if="!activeWorkspace" class="py-24 text-center">
      <h1 class="text-3xl font-semibold tracking-[-0.03em]">{{ t('workspace.empty.title') }}</h1>
      <p class="mx-auto mt-3 max-w-lg leading-relaxed text-muted">{{ t('workspace.empty.description') }}</p>
    </section>

    <template v-else>
      <motion.header
        :initial="{ opacity: 0, y: reducedMotion ? 0 : 8 }"
        :animate="{ opacity: 1, y: 0 }"
        :transition="{ duration: reducedMotion ? 0 : 0.28 }"
        class="mb-10 flex flex-wrap items-end justify-between gap-6"
      >
        <div>
          <p class="mb-2 flex items-center gap-2 text-sm text-muted">
            <span class="size-2 rounded-full bg-success" aria-hidden="true" />
            {{ t(`workspace.role.${activeWorkspace.role}`) }}
          </p>
          <h1 class="text-4xl font-semibold tracking-[-0.035em] sm:text-5xl">{{ activeWorkspace.name }}</h1>
          <p class="mt-3 max-w-2xl leading-relaxed text-muted">{{ t('workspace.description') }}</p>
        </div>
        <p class="text-sm text-muted">
          <strong class="font-semibold text-default tabular-nums">{{ ideaPage?.total ?? 0 }}</strong>
          {{ t('workspace.ideaLabel') }}
        </p>
      </motion.header>

      <section class="kollio-surface overflow-hidden" aria-labelledby="idea-list-title">
        <header class="flex items-center justify-between gap-4 border-b border-default px-5 py-4 sm:px-6">
          <h2 id="idea-list-title" class="text-lg font-semibold">{{ t('ideas.title') }}</h2>
          <p v-if="ideaPage" class="text-sm text-muted">{{ t('ideas.page', { current: currentPage, total: totalPages }) }}</p>
        </header>

        <div v-if="status === 'pending'" class="divide-y divide-default" aria-live="polite">
          <div v-for="index in 6" :key="index" class="h-32 animate-pulse bg-muted/60" />
        </div>

        <div v-else-if="error" class="p-8">
          <h3 class="text-lg font-semibold">{{ t('ideas.error.title') }}</h3>
          <p class="mt-2 text-sm text-muted">{{ t('ideas.error.description') }}</p>
        </div>

        <div v-else-if="ideaPage?.items.length" class="divide-y divide-default">
          <motion.article
            v-for="(idea, index) in ideaPage.items"
            :key="idea.id"
            :initial="{ opacity: 0, y: reducedMotion ? 0 : 5 }"
            :animate="{ opacity: 1, y: 0 }"
            :transition="{ duration: reducedMotion ? 0 : 0.24, delay: reducedMotion ? 0 : index * 0.02 }"
            class="group relative grid gap-3 px-5 py-5 transition-colors hover:bg-muted/45 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-center sm:px-6"
          >
            <div class="min-w-0">
              <div class="mb-2 flex flex-wrap items-center gap-2 text-xs text-muted">
                <KollioFeltMark active>{{ t(`ideas.stage.${idea.stage}`) }}</KollioFeltMark>
                <span aria-hidden="true" class="size-1 rounded-full bg-muted" />
                <span class="uppercase">{{ idea.lang }}</span>
                <span aria-hidden="true" class="size-1 rounded-full bg-muted" />
                <time :datetime="idea.created_at">{{ dateFormatter.format(new Date(idea.created_at)) }}</time>
              </div>
              <h3 class="text-lg font-semibold tracking-[-0.015em]">
                <NuxtLink :to="$localePath(`/workspace/ideas/${idea.id}`)" class="after:absolute after:inset-0">
                  {{ idea.title }}
                </NuxtLink>
              </h3>
              <p class="mt-2 line-clamp-2 max-w-3xl text-sm leading-relaxed text-muted">{{ idea.pitch }}</p>
            </div>
            <svg aria-hidden="true" viewBox="0 0 24 24" class="size-5 text-muted transition-transform duration-200 group-hover:translate-x-1 group-hover:text-default" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M5 12h14m-5-5 5 5-5 5" />
            </svg>
          </motion.article>
        </div>

        <div v-else class="p-12 text-center">
          <h3 class="text-lg font-semibold">{{ t('ideas.empty.title') }}</h3>
          <p class="mt-2 text-sm text-muted">{{ t('ideas.empty.description') }}</p>
        </div>
      </section>

      <nav v-if="ideaPage && totalPages > 1" class="mt-6 flex items-center justify-between" :aria-label="t('ideas.pagination')">
        <NuxtLink v-if="currentPage > 1" :to="pageLocation(currentPage - 1)" class="min-h-11 rounded-xl border border-default bg-elevated px-4 text-sm font-medium leading-11 hover:bg-muted">
          {{ t('ideas.previous') }}
        </NuxtLink>
        <span v-else />
        <KollioPrimaryAction
          v-if="currentPage < totalPages"
          :to="pageLocation(currentPage + 1)"
          :label="t('ideas.next')"
        />
      </nav>
    </template>
  </div>
</template>
