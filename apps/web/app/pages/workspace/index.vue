<script setup lang="ts">
import type { IdeaPageResponse, IdeaSummaryResponse, WorkspaceResponse } from '@kollio/api-client'
import { motion, useReducedMotion } from 'motion-v'

definePageMeta({ layout: 'workspace', middleware: 'authenticated' })

const { t, locale } = useI18n()
const route = useRoute()
const router = useRouter()
const requestFetch = useRequestFetch()
const localePath = useLocalePath()
const reducedMotion = useReducedMotion()
const pageSize = 6
const validStages = ['seed', 'iterating', 'team_formed'] as const
const searchInput = ref(typeof route.query.q === 'string' ? route.query.q : '')
const selectedIdeaId = ref<string>()
const previewOpen = ref(false)
let searchTimer: ReturnType<typeof setTimeout> | undefined

const { data: workspaces } = await useAsyncData('workspaces', () => requestFetch<WorkspaceResponse[]>('/api/workspaces'))

const activeWorkspace = computed(() => {
  const requestedId = typeof route.query.workspace === 'string' ? route.query.workspace : undefined
  return workspaces.value?.find(workspace => workspace.id === requestedId) ?? workspaces.value?.[0]
})
const currentPage = computed(() => {
  const value = Number(route.query.page ?? 1)
  return Number.isInteger(value) && value > 0 ? value : 1
})
const queryText = computed(() => typeof route.query.q === 'string' ? route.query.q.trim() : '')
const activeStage = computed(() => {
  const stage = typeof route.query.stage === 'string' ? route.query.stage : undefined
  return validStages.includes(stage as typeof validStages[number]) ? stage : undefined
})
const activeDomain = computed(() => typeof route.query.domain === 'string' ? route.query.domain : undefined)

const { data: ideaPage, status, error, refresh } = await useAsyncData(
  'workspace-ideas',
  async () => {
    if (!activeWorkspace.value) return undefined
    return requestFetch<IdeaPageResponse>(`/api/workspaces/${encodeURIComponent(activeWorkspace.value.id)}/ideas`, {
      query: {
        limit: pageSize,
        offset: (currentPage.value - 1) * pageSize,
        ...(queryText.value ? { q: queryText.value } : {}),
        ...(activeStage.value ? { stage: activeStage.value } : {}),
        ...(activeDomain.value ? { domain: activeDomain.value } : {}),
      },
    })
  },
  { watch: [activeWorkspace, currentPage, queryText, activeStage, activeDomain] },
)

const totalPages = computed(() => Math.max(1, Math.ceil((ideaPage.value?.total ?? 0) / pageSize)))
const dateFormatter = computed(() => new Intl.DateTimeFormat(locale.value, { day: 'numeric', month: 'short', year: 'numeric' }))
const selectedIdea = computed(() => ideaPage.value?.items.find(idea => idea.id === selectedIdeaId.value) ?? ideaPage.value?.items[0])
const visibleDomains = computed(() => Array.from(new Set(
  ideaPage.value?.items.map(idea => idea.domain).filter(
    (domain): domain is string => Boolean(domain && domain.length <= 32),
  ) ?? [],
)).slice(0, 6))

watch(() => route.query.q, value => {
  searchInput.value = typeof value === 'string' ? value : ''
})
watch(() => ideaPage.value?.items, items => {
  if (!items?.some(idea => idea.id === selectedIdeaId.value)) selectedIdeaId.value = items?.[0]?.id
}, { immediate: true })

function replaceFilters(updates: Record<string, string | undefined>) {
  const nextQuery = Object.fromEntries(
    Object.entries({ ...route.query, ...updates }).filter(([key, value]) => key !== 'page' && Boolean(value)),
  )
  void router.replace({ path: localePath('/workspace'), query: nextQuery })
}
function scheduleSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => replaceFilters({ q: searchInput.value.trim() || undefined }), 280)
}
function selectIdea(idea: IdeaSummaryResponse) {
  selectedIdeaId.value = idea.id
  previewOpen.value = true
}
function pageLocation(page: number) {
  return {
    path: localePath('/workspace'),
    query: {
      ...route.query,
      ...(activeWorkspace.value ? { workspace: activeWorkspace.value.id } : {}),
      ...(page > 1 ? { page: String(page) } : {}),
    },
  }
}

onBeforeUnmount(() => clearTimeout(searchTimer))
useSeoMeta({ title: () => t('workspace.metaTitle') })
</script>

<template>
  <div class="ideas-explorer">
    <section v-if="!activeWorkspace" class="py-24 text-center">
      <h1 class="text-3xl font-semibold tracking-[-0.03em]">{{ t('workspace.empty.title') }}</h1>
      <p class="mx-auto mt-3 max-w-lg leading-relaxed text-muted">{{ t('workspace.empty.description') }}</p>
    </section>

    <template v-else>
      <motion.header
        :initial="{ opacity: 0, y: reducedMotion ? 0 : 7 }"
        :animate="{ opacity: 1, y: 0 }"
        :transition="{ duration: reducedMotion ? 0 : 0.26 }"
        class="ideas-explorer-header"
      >
        <div>
          <p>{{ activeWorkspace.name }}</p>
          <h1>{{ t('ideas.title') }}</h1>
          <span>{{ t('ideas.explorer.description') }}</span>
        </div>
        <label class="ideas-search">
          <svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7" /><path d="m16 16 5 5" /></svg>
          <input v-model="searchInput" type="search" :placeholder="t('ideas.explorer.search')" @input="scheduleSearch">
        </label>
      </motion.header>

      <section class="ideas-explorer-shell" :aria-label="t('ideas.explorer.library')">
        <aside class="ideas-filter-rail">
          <p>{{ t('ideas.explorer.explore') }}</p>
          <button type="button" :aria-pressed="!activeStage" @click="replaceFilters({ stage: undefined })">
            <KollioSketchAnnotation :active="!activeStage" kind="swash">{{ t('ideas.explorer.all') }}</KollioSketchAnnotation>
            <span v-if="!activeStage">{{ ideaPage?.total ?? 0 }}</span>
          </button>
          <button v-for="stage in validStages" :key="stage" type="button" :aria-pressed="activeStage === stage" @click="replaceFilters({ stage })">
            <KollioSketchAnnotation :active="activeStage === stage" kind="swash">{{ t(`ideas.stage.${stage}`) }}</KollioSketchAnnotation>
          </button>

          <template v-if="visibleDomains.length">
            <hr>
            <p>{{ t('ideas.explorer.domains') }}</p>
            <button
              v-for="domain in visibleDomains"
              :key="domain"
              type="button"
              class="domain-filter"
              :aria-pressed="activeDomain === domain"
              @click="replaceFilters({ domain: activeDomain === domain ? undefined : domain })"
            >
              <KollioSketchAnnotation :active="activeDomain === domain" kind="swash">{{ domain }}</KollioSketchAnnotation>
            </button>
          </template>
        </aside>

        <main class="ideas-results">
          <header class="ideas-results-header">
            <span>{{ t('ideas.explorer.results', { count: ideaPage?.total ?? 0 }) }}</span>
            <span>{{ t('ideas.page', { current: currentPage, total: totalPages }) }}</span>
          </header>

          <div v-if="status === 'pending'" aria-live="polite">
            <div v-for="index in pageSize" :key="index" class="explorer-row-skeleton">
              <span class="skeleton-line w-20" /><span class="skeleton-line mt-5 w-3/4" /><span class="skeleton-line mt-3 w-full" />
            </div>
          </div>
          <div v-else-if="error" class="ideas-results-feedback">
            <h2>{{ t('ideas.error.title') }}</h2><p>{{ t('ideas.error.description') }}</p>
            <KollioPrimaryAction :label="t('ideas.retry')" @click="() => refresh()" />
          </div>
          <div v-else-if="ideaPage?.items.length">
            <KollioIdeaExplorerRow
              v-for="idea in ideaPage.items"
              :key="idea.id"
              :idea="idea"
              :selected="selectedIdea?.id === idea.id"
              :stage-label="t(`ideas.stage.${idea.stage}`)"
              :date-label="dateFormatter.format(new Date(idea.created_at))"
              @select="selectIdea(idea)"
            />
          </div>
          <div v-else class="ideas-results-feedback">
            <h2>{{ t('ideas.empty.title') }}</h2><p>{{ t('ideas.explorer.noResults') }}</p>
          </div>

          <nav v-if="ideaPage && totalPages > 1" class="ideas-results-pagination" :aria-label="t('ideas.pagination')">
            <NuxtLink v-if="currentPage > 1" :to="pageLocation(currentPage - 1)">{{ t('ideas.previous') }}</NuxtLink><span v-else />
            <NuxtLink v-if="currentPage < totalPages" :to="pageLocation(currentPage + 1)">{{ t('ideas.next') }}</NuxtLink>
          </nav>
        </main>

        <KollioIdeaPreviewPanel
          v-if="selectedIdea"
          class="ideas-preview-panel"
          :class="{ 'is-open': previewOpen }"
          :idea="selectedIdea"
          :stage-label="t(`ideas.stage.${selectedIdea.stage}`)"
          :date-label="dateFormatter.format(new Date(selectedIdea.created_at))"
          :open-label="t('ideas.explorer.open')"
          :preview-label="t('ideas.explorer.preview')"
          :domain-label="t('ideas.explorer.domain')"
          :language-label="t('ideas.explorer.language')"
          :close-label="t('ideas.explorer.closePreview')"
          @close="previewOpen = false"
        />
      </section>

      <button v-if="previewOpen" class="ideas-preview-backdrop" type="button" :aria-label="t('ideas.explorer.closePreview')" @click="previewOpen = false" />
    </template>
  </div>
</template>

<style scoped>
.ideas-explorer { width: 100%; padding: clamp(22px, 3vw, 46px); }
.ideas-explorer-header { display: grid; grid-template-columns: minmax(320px, .85fr) minmax(360px, 1.15fr); align-items: end; gap: clamp(30px, 4vw, 70px); margin-bottom: 28px; }
.ideas-explorer-header > div > p { color: var(--kollio-active-ink); font-size: .72rem; font-weight: 650; letter-spacing: .05em; text-transform: uppercase; }
.ideas-explorer-header h1 { margin-top: 9px; color: var(--kollio-heading); font-size: clamp(2.35rem, 3.6vw, 3.8rem); font-weight: 620; letter-spacing: -.062em; line-height: .96; }
.ideas-explorer-header > div > span { display: block; max-width: 560px; margin-top: 14px; color: var(--ui-text-muted); font-size: .94rem; line-height: 1.55; }
.ideas-search { display: flex; min-height: 58px; align-items: center; gap: 13px; border: 1px solid var(--ui-border); border-radius: 18px; background: var(--ui-bg-elevated); padding: 0 19px; box-shadow: 0 14px 42px color-mix(in srgb, var(--kollio-active-ink) 5%, transparent); }
.ideas-search:focus-within { border-color: color-mix(in srgb, var(--kollio-active-ink) 45%, var(--ui-border)); }
.ideas-search svg { width: 20px; flex: none; fill: none; stroke: var(--ui-text-muted); stroke-linecap: round; stroke-width: 1.7; }
.ideas-search input { min-width: 0; flex: 1; outline: 0; background: transparent; color: var(--kollio-heading); font-size: .88rem; }
.ideas-explorer-shell { display: grid; min-height: 680px; grid-template-columns: minmax(168px, 210px) minmax(420px, 1fr) minmax(300px, 360px); overflow: hidden; border: 1px solid var(--ui-border); border-radius: 24px; background: var(--ui-bg-elevated); }
.ideas-filter-rail { border-right: 1px solid var(--ui-border); padding: 24px 16px; }
.ideas-filter-rail > p { margin: 0 11px 10px; color: var(--ui-text-muted); font-size: .66rem; font-weight: 680; letter-spacing: .075em; text-transform: uppercase; }
.ideas-filter-rail button { display: flex; width: 100%; min-height: 48px; align-items: center; justify-content: space-between; color: var(--ui-text-muted); font-size: .78rem; text-align: left; }
.ideas-filter-rail button[aria-pressed='true'] { color: var(--kollio-heading); font-weight: 620; }
.ideas-filter-rail button > span { padding-right: 9px; font-size: .66rem; }
.ideas-filter-rail :deep(.sketch-annotation--swash) { min-height: 32px; margin-left: -3px; padding: 4px 7px; }
.ideas-filter-rail .domain-filter { min-height: 39px; padding-inline: 11px; }
.ideas-filter-rail hr { margin: 20px 10px; border-color: var(--ui-border); }
.ideas-results { min-width: 0; border-right: 1px solid var(--ui-border); }
.ideas-results-header { display: flex; min-height: 62px; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--ui-border); padding: 0 24px; color: var(--ui-text-muted); font-size: .71rem; }
.explorer-row-skeleton { min-height: 100px; border-bottom: 1px solid var(--ui-border); padding: 22px 24px; }
.ideas-results-feedback { display: flex; min-height: 360px; align-items: flex-start; flex-direction: column; justify-content: center; padding: 42px; }
.ideas-results-feedback h2 { color: var(--kollio-heading); font-size: 1.25rem; font-weight: 620; }
.ideas-results-feedback p { margin: 9px 0 22px; color: var(--ui-text-muted); font-size: .82rem; }
.ideas-results-pagination { display: flex; min-height: 68px; align-items: center; justify-content: space-between; padding: 0 24px; }
.ideas-results-pagination a { min-height: 40px; border-radius: 10px; padding: 11px 13px; color: var(--kollio-active-ink); font-size: .75rem; font-weight: 600; }
.ideas-results-pagination a:hover { background: var(--ui-bg-muted); }
.ideas-preview-panel { min-width: 0; }
.ideas-preview-backdrop { display: none; }
@media (max-width: 1099px) {
  .ideas-explorer-shell { grid-template-columns: minmax(170px, 210px) minmax(0, 1fr); }
  .ideas-results { border-right: 0; }
  .ideas-preview-panel { position: fixed; z-index: 55; top: 72px; right: 16px; bottom: 16px; width: min(430px, calc(100vw - 32px)); border: 1px solid var(--ui-border); border-radius: 22px; box-shadow: 0 24px 70px rgb(37 34 41 / 18%); opacity: 0; pointer-events: none; transform: translateX(24px); transition: opacity 180ms ease, transform 220ms cubic-bezier(.16, 1, .3, 1); }
  .ideas-preview-panel.is-open { opacity: 1; pointer-events: auto; transform: translateX(0); }
  .ideas-preview-backdrop { position: fixed; z-index: 50; inset: 0; display: block; background: rgb(37 34 41 / 16%); }
}
@media (max-width: 720px) {
  .ideas-explorer { padding: 24px 14px 50px; }
  .ideas-explorer-header { grid-template-columns: 1fr; gap: 24px; }
  .ideas-explorer-header h1 { font-size: clamp(2.4rem, 13vw, 3.5rem); }
  .ideas-explorer-shell { display: block; height: auto; min-height: 0; overflow: visible; border-radius: 20px; }
  .ideas-filter-rail { display: flex; overflow-x: auto; border-right: 0; border-bottom: 1px solid var(--ui-border); padding: 10px 13px; scrollbar-width: none; }
  .ideas-filter-rail > p, .ideas-filter-rail hr, .ideas-filter-rail .domain-filter { display: none; }
  .ideas-filter-rail button { width: auto; min-width: max-content; padding-right: 8px; }
  .ideas-filter-rail button > span { display: none; }
  .ideas-results-header { padding-inline: 18px; }
}
</style>
