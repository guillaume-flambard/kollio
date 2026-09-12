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

const isIdeasPrototype = computed(() => import.meta.dev && route.query.prototype === 'ideas')

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

const { data: ideaPage, status, error, refresh } = await useAsyncData(
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
  <KollioIdeaLibraryPrototype
    v-if="isIdeasPrototype && activeWorkspace && ideaPage?.items.length"
    :ideas="ideaPage.items"
    :total="ideaPage.total"
  />

  <div v-else class="idea-library">
    <section v-if="!activeWorkspace" class="py-24 text-center">
      <h1 class="text-3xl font-semibold tracking-[-0.03em]">{{ t('workspace.empty.title') }}</h1>
      <p class="mx-auto mt-3 max-w-lg leading-relaxed text-muted">{{ t('workspace.empty.description') }}</p>
    </section>

    <template v-else>
      <motion.header
        :initial="{ opacity: 0, y: reducedMotion ? 0 : 8 }"
        :animate="{ opacity: 1, y: 0 }"
        :transition="{ duration: reducedMotion ? 0 : 0.28 }"
        class="idea-library-hero"
      >
        <div class="idea-library-intro">
          <p class="idea-library-context">
            <span>{{ activeWorkspace.name }}</span>
            <span>{{ t(`workspace.role.${activeWorkspace.role}`) }}</span>
          </p>
          <h1>{{ t('ideas.title') }}</h1>
          <p class="idea-library-description">{{ t('workspace.description') }}</p>
        </div>
        <div class="idea-library-count" aria-live="polite">
          <strong>{{ ideaPage?.total ?? 0 }}</strong>
          <KollioFeltMark active>{{ t('workspace.ideaLabel') }}</KollioFeltMark>
        </div>
      </motion.header>

      <section class="kollio-surface idea-library-surface" aria-labelledby="idea-list-title">
        <header class="idea-library-toolbar">
          <div>
            <p>{{ t('ideas.eyebrow') }}</p>
            <h2 id="idea-list-title">{{ t('ideas.collectionTitle') }}</h2>
          </div>
          <p v-if="ideaPage" class="idea-library-page">{{ t('ideas.page', { current: currentPage, total: totalPages }) }}</p>
        </header>

        <div v-if="status === 'pending'" class="idea-library-grid" aria-live="polite">
          <div v-for="index in 8" :key="index" class="idea-list-skeleton">
            <span class="skeleton-line w-16" />
            <span class="skeleton-line mt-8 w-4/5" />
            <span class="skeleton-line mt-3 w-full" />
            <span class="skeleton-line mt-2 w-2/3" />
          </div>
        </div>

        <div v-else-if="error" class="idea-library-feedback">
          <h3 class="text-lg font-semibold">{{ t('ideas.error.title') }}</h3>
          <p class="mt-2 text-sm text-muted">{{ t('ideas.error.description') }}</p>
          <KollioPrimaryAction class="mt-6" :label="t('ideas.retry')" @click="() => refresh()" />
        </div>

        <div v-else-if="ideaPage?.items.length" class="idea-library-grid">
          <motion.div
            v-for="(idea, index) in ideaPage.items"
            :key="idea.id"
            :initial="{ opacity: 0, y: reducedMotion ? 0 : 5 }"
            :animate="{ opacity: 1, y: 0 }"
            :transition="{ duration: reducedMotion ? 0 : 0.24, delay: reducedMotion ? 0 : index * 0.02 }"
            class="idea-list-entry"
          >
            <KollioIdeaListItem
              :idea="idea"
              :to="$localePath(`/workspace/ideas/${idea.id}`)"
              :stage-label="t(`ideas.stage.${idea.stage}`)"
              :date-label="dateFormatter.format(new Date(idea.created_at))"
            />
          </motion.div>
        </div>

        <div v-else class="idea-library-feedback">
          <h3 class="text-lg font-semibold">{{ t('ideas.empty.title') }}</h3>
          <p class="mt-2 text-sm text-muted">{{ t('ideas.empty.description') }}</p>
        </div>

        <nav v-if="ideaPage && totalPages > 1" class="idea-library-pagination" :aria-label="t('ideas.pagination')">
          <NuxtLink v-if="currentPage > 1" :to="pageLocation(currentPage - 1)" class="idea-library-previous">
            {{ t('ideas.previous') }}
          </NuxtLink>
          <span v-else />
          <KollioPrimaryAction
            v-if="currentPage < totalPages"
            :to="pageLocation(currentPage + 1)"
            :label="t('ideas.next')"
          />
        </nav>
      </section>
    </template>
  </div>
</template>
