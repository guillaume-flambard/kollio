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
const pageSize = 5
const validStages = ['seed', 'iterating', 'team_formed'] as const
const searchInput = ref(typeof route.query.q === 'string' ? route.query.q : '')
const selectedIdeaId = ref<string>()
const previewOpen = ref(false)
const glyphs = Object.freeze({ plus: '＋', down: '⌄' })
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
const activeSoughtRole = computed(() => typeof route.query.role === 'string' ? route.query.role : undefined)
const activeRealism = computed(() => {
  const value = Number(route.query.realism_min)
  return Number.isInteger(value) && value >= 1 && value <= 99 ? value : undefined
})

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
        ...(activeSoughtRole.value ? { sought_role: activeSoughtRole.value } : {}),
        ...(activeRealism.value ? { realism_min: activeRealism.value } : {}),
      },
    })
  },
  { watch: [activeWorkspace, currentPage, queryText, activeStage, activeSoughtRole, activeRealism] },
)

const selectedIdea = computed(() => ideaPage.value?.items.find(idea => idea.id === selectedIdeaId.value) ?? ideaPage.value?.items[0])
const totalPages = computed(() => Math.max(1, Math.ceil((ideaPage.value?.total ?? 0) / pageSize)))
const relativeFormatter = computed(() => new Intl.RelativeTimeFormat(locale.value, { numeric: 'auto' }))
const teamRoles = ['marketing', 'sales', 'finance', 'product', 'engineering', 'customer_success', 'operations', 'legal', 'hr', 'data', 'direction', 'other'] as const

watch(() => route.query.q, value => {
  searchInput.value = typeof value === 'string' ? value : ''
})
watch(() => ideaPage.value?.items, items => {
  if (!items?.length) {
    selectedIdeaId.value = undefined
    return
  }
  if (!items.some(idea => idea.id === selectedIdeaId.value)) selectedIdeaId.value = items[0]?.id
}, { immediate: true })

function replaceFilters(updates: Record<string, string | undefined>) {
  const nextQuery = Object.fromEntries(Object.entries({ ...route.query, ...updates }).filter(([key, value]) => key !== 'page' && Boolean(value)))
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
function relativeDate(date: string) {
  const days = Math.round((new Date(date).getTime() - Date.now()) / 86_400_000)
  if (Math.abs(days) < 1) {
    const hours = Math.round((new Date(date).getTime() - Date.now()) / 3_600_000)
    return relativeFormatter.value.format(hours, 'hour')
  }
  return relativeFormatter.value.format(days, 'day')
}
function pageLocation(page: number) {
  return {
    path: localePath('/workspace'),
    query: { ...route.query, ...(activeWorkspace.value ? { workspace: activeWorkspace.value.id } : {}), page: page > 1 ? String(page) : undefined },
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
      <motion.header :initial="{ opacity: 0, y: reducedMotion ? 0 : 7 }" :animate="{ opacity: 1, y: 0 }" :transition="{ duration: reducedMotion ? 0 : 0.26 }" class="ideas-explorer-header">
        <div>
          <h1>{{ t('ideas.title') }}</h1>
          <p>{{ t('ideas.explorer.description') }}</p>
        </div>
        <NuxtLink type="button" class="ideas-create-action" :to="localePath({ name: 'workspace-deposit' })">
          {{ t('ideas.explorer.create') }}<span aria-hidden="true" v-text="glyphs.plus" />
        </NuxtLink>
        <label class="ideas-search">
          <svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7" /><path d="m16 16 5 5" /></svg>
          <input v-model="searchInput" type="search" :placeholder="t('ideas.explorer.search')" @input="scheduleSearch">
          <span class="ideas-filter-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M4 7h10m4 0h2M4 17h2m4 0h10M14 4v6M7 14v6" /></svg></span>
        </label>
      </motion.header>

      <section class="ideas-explorer-shell" :aria-label="t('ideas.explorer.library')">
        <aside class="ideas-filter-rail">
          <nav :aria-label="t('ideas.explorer.explore')">
            <button type="button" :aria-pressed="!activeStage && !activeSoughtRole && !activeRealism" @click="replaceFilters({ stage: undefined, role: undefined, realism_min: undefined })">
              <KollioSketchAnnotation :active="!activeStage && !activeSoughtRole && !activeRealism" kind="loop">
                <span class="filter-annotation-content"><svg aria-hidden="true" viewBox="0 0 24 24"><path d="m12 3 1.7 5.3L19 10l-5.3 1.7L12 17l-1.7-5.3L5 10l5.3-1.7L12 3Z" /></svg>{{ t('ideas.explorer.forYou') }}</span>
              </KollioSketchAnnotation>
            </button>
            <button type="button" :aria-pressed="activeStage === 'seed'" @click="replaceFilters({ stage: activeStage === 'seed' ? undefined : 'seed' })">
              <svg aria-hidden="true" viewBox="0 0 24 24"><path d="M12 21V9m0 0L8 13m4-4 4 4" /></svg>{{ t('ideas.stage.seed') }}
            </button>
            <button type="button" :aria-pressed="activeStage === 'iterating'" @click="replaceFilters({ stage: activeStage === 'iterating' ? undefined : 'iterating' })">
              <svg aria-hidden="true" viewBox="0 0 24 24"><path d="M9 3h6M10 3v5l-5 9a3 3 0 0 0 2.6 4h8.8a3 3 0 0 0 2.6-4l-5-9V3M8 15h8" /></svg>{{ t('ideas.explorer.validation') }}
            </button>
            <button type="button" :aria-pressed="activeStage === 'team_formed'" @click="replaceFilters({ stage: activeStage === 'team_formed' ? undefined : 'team_formed' })">
              <svg aria-hidden="true" viewBox="0 0 24 24"><path d="M16 20a4 4 0 0 0-8 0M12 13a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm7 7a3 3 0 0 0-3-3M5 20a3 3 0 0 1 3-3" /></svg>{{ t('ideas.stage.team_formed') }}
            </button>
          </nav>
          <hr><p>{{ t('ideas.detail.team.soughtTitle') }}</p>
          <select class="rail-select" :value="activeSoughtRole ?? ''" :aria-label="t('ideas.detail.team.soughtTitle')" @change="replaceFilters({ role: ($event.target as HTMLSelectElement).value || undefined })">
            <option value="">{{ t('ideas.explorer.allRoles') }}</option>
            <option v-for="role in teamRoles" :key="role" :value="role">{{ t(`ideas.function.${role}`) }}</option>
          </select>
          <hr><p>{{ t('ideas.explorer.realism.title') }}</p>
          <button type="button" class="domain-filter" :aria-pressed="activeRealism != null" @click="replaceFilters({ realism_min: activeRealism != null ? undefined : '60' })">
            <span>{{ t('ideas.explorer.realism.grounded') }}</span><small>{{ t('ideas.explorer.realism.band') }}</small>
          </button>
        </aside>

        <main class="ideas-results">
          <header class="ideas-results-header">
            <strong>{{ t('ideas.explorer.found', { count: ideaPage?.total ?? 0 }) }}</strong>
            <span>{{ t('ideas.explorer.sortBy') }} <b>{{ t('ideas.explorer.activity') }}</b></span>
          </header>
          <div v-if="status === 'pending'" aria-live="polite">
            <div v-for="index in pageSize" :key="index" class="explorer-row-skeleton"><span class="skeleton-circle" /><span><i class="skeleton-line w-3/4" /><i class="skeleton-line mt-3 w-full" /></span></div>
          </div>
          <div v-else-if="error" class="ideas-results-feedback"><h2>{{ t('ideas.error.title') }}</h2><p>{{ t('ideas.error.description') }}</p><KollioPrimaryAction :label="t('ideas.retry')" @click="() => refresh()" /></div>
          <div v-else-if="ideaPage?.items.length">
            <KollioIdeaExplorerRow
              v-for="idea in ideaPage.items"
              :key="idea.id"
              :idea="idea"
              :selected="selectedIdea?.id === idea.id"
              :stage-label="t(`ideas.stage.${idea.stage}`)"
              :date-label="relativeDate(idea.created_at)"
              :contributor-label="t('ideas.explorer.contributors', { count: idea.collaborators?.length ?? 0 })"
              :avatar-label="t('ideas.explorer.contributors', { count: idea.collaborators?.length ?? 0 })"
              :expertise-label="idea.collaborators?.[0]?.roles[0] ? t(`ideas.role.${idea.collaborators[0].roles[0]}`) : undefined"
              :realism-label="idea.realism_score != null ? t('ideas.explorer.prism', { score: idea.realism_score }) : undefined"
              :roles-label="idea.sought_roles?.length ? idea.sought_roles.map(role => t(`ideas.function.${role}`)).join(' · ') : undefined"
              @select="selectIdea(idea)"
            />
          </div>
          <div v-else class="ideas-results-feedback"><h2>{{ t('ideas.empty.title') }}</h2><p>{{ t('ideas.explorer.noResults') }}</p></div>
          <nav v-if="ideaPage && totalPages > 1" class="ideas-results-pagination" :aria-label="t('ideas.pagination')">
            <NuxtLink v-if="currentPage > 1" :to="pageLocation(currentPage - 1)">{{ t('ideas.previous') }}</NuxtLink><span v-else />
            <NuxtLink v-if="currentPage < totalPages" :to="pageLocation(currentPage + 1)">{{ t('ideas.next') }}</NuxtLink>
          </nav>
        </main>

        <KollioIdeaPreviewPanel
          v-if="selectedIdea"
          :idea="selectedIdea"
          :stage-label="t(`ideas.stage.${selectedIdea.stage}`)"
          :profile-links="true"
          :open-label="t('ideas.explorer.open')"
          :contributor-title="t('ideas.explorer.contributorTitle')"
          :expertise-title="t('ideas.explorer.expertiseTitle')"
          :close-label="t('ideas.explorer.closePreview')"
          :to="localePath(`/workspace/ideas/${selectedIdea.id}`)"
          :mobile-open="previewOpen"
          @close="previewOpen = false"
        />
      </section>
      <button v-if="previewOpen" type="button" class="preview-backdrop" :aria-label="t('ideas.explorer.closePreview')" @click="previewOpen = false" />
    </template>
  </div>
</template>

<style scoped>
.ideas-explorer { width: 100%; padding: 16px 16px 34px; }
.ideas-explorer-header { display: grid; grid-template-columns: minmax(0, 1fr) auto; align-items: center; gap: 22px; margin-bottom: 20px; }
.ideas-explorer-header h1 { color: var(--kollio-heading); font-size: var(--kollio-display-section); font-weight: 650; letter-spacing: -.06em; line-height: .96; }
.ideas-explorer-header p { margin-top: 8px; color: var(--ui-text-muted); font-size: var(--kollio-text-body); }
.ideas-create-action { display: flex; min-height: 48px; align-items: center; gap: 24px; border-radius: var(--kollio-radius-md); background: var(--kollio-heading); padding: 0 20px; color: var(--ui-bg-elevated); font-size: var(--kollio-text-caption); font-weight: 570; box-shadow: 0 8px 22px color-mix(in srgb, var(--kollio-heading) 17%, transparent); transition: transform 180ms ease, box-shadow 180ms ease; }
.ideas-create-action:hover { transform: translateY(-1px); box-shadow: 0 11px 28px color-mix(in srgb, var(--kollio-heading) 22%, transparent); }
.ideas-create-action span { font-size: var(--kollio-text-lead); font-weight: 300; }
.ideas-search { display: flex; min-height: 56px; grid-column: 1 / -1; align-items: center; gap: 13px; border: 1px solid var(--ui-border); border-radius: var(--kollio-radius-md); background: var(--ui-bg-elevated); padding-left: 16px; }
.ideas-search:focus-within { border-color: color-mix(in srgb, var(--kollio-active-ink) 42%, var(--ui-border)); }
.ideas-search > svg { width: 21px; flex: none; fill: none; stroke: var(--kollio-active-ink); stroke-linecap: round; stroke-width: 1.7; }
.ideas-search input { min-width: 0; flex: 1; outline: 0; background: transparent; color: var(--kollio-heading); font-size: var(--kollio-text-small); }
.ideas-filter-icon { display: grid; width: 56px; height: 54px; place-items: center; border-left: 1px solid var(--ui-border); }
.ideas-filter-icon svg { width: 22px; fill: none; stroke: var(--kollio-active-ink); stroke-linecap: round; stroke-width: 1.6; }
.ideas-explorer-shell { display: grid; min-height: 744px; grid-template-columns: minmax(192px, 210px) minmax(470px, 1fr) minmax(330px, 376px); overflow: hidden; border: 1px solid var(--ui-border); border-radius: var(--kollio-radius-lg); background: var(--ui-bg-elevated); box-shadow: 0 22px 72px color-mix(in srgb, var(--kollio-active-ink) 6%, transparent); }
.ideas-filter-rail { border-right: 1px solid var(--ui-border); padding: 16px 15px 26px; }
.ideas-filter-rail nav { display: grid; gap: 1px; }
.ideas-filter-rail button { display: flex; width: 100%; min-height: 52px; align-items: center; gap: 12px; color: var(--ui-text-muted); font-size: var(--kollio-text-small); text-align: left; }
.ideas-filter-rail button[aria-pressed='true'] { color: var(--kollio-heading); font-weight: 620; }
.ideas-filter-rail button svg { width: 21px; flex: none; fill: none; stroke: var(--kollio-active-ink); stroke-linecap: round; stroke-linejoin: round; stroke-width: 1.55; }
.ideas-filter-rail nav :deep(.sketch-annotation--loop) { --sketch-opacity: .72; --sketch-secondary-opacity: .16; --sketch-stroke: 1.45px; width: 100%; min-height: 46px; margin-left: -8px; padding: 8px 12px; }
.filter-annotation-content { display: flex; align-items: center; gap: 12px; }
.ideas-filter-rail hr { margin: 16px 0 22px; border-color: var(--ui-border); }
.ideas-filter-rail > p { margin: 0 8px 9px; color: var(--kollio-heading); font-size: var(--kollio-text-caption); font-weight: 650; }
.ideas-filter-rail .domain-filter { min-height: 38px; justify-content: space-between; padding: 0 8px; }
.ideas-filter-rail .domain-filter small { font-size: var(--kollio-text-micro); }
.ideas-results { min-width: 0; }
.ideas-results-header { display: flex; min-height: 62px; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--ui-border); padding: 0 24px; color: var(--ui-text-muted); font-size: var(--kollio-text-caption); }
.ideas-results-header strong { color: var(--kollio-heading); font-size: var(--kollio-text-small); font-weight: 650; }
.ideas-results-header b { margin: 0 7px; color: var(--kollio-active-ink); font-weight: 570; }
.explorer-row-skeleton { display: grid; min-height: 128px; grid-template-columns: 48px minmax(0, 1fr); align-items: center; gap: 18px; border-bottom: 1px solid var(--ui-border); padding: 20px 22px; }
.explorer-row-skeleton > span:last-child { display: block; }
.skeleton-circle { width: 48px; height: 48px; border-radius: 50%; background: var(--ui-bg-muted); }
.ideas-results-feedback { display: flex; min-height: 420px; align-items: flex-start; flex-direction: column; justify-content: center; padding: 42px; }
.ideas-results-feedback h2 { color: var(--kollio-heading); font-size: var(--kollio-text-title); font-weight: 620; }
.ideas-results-feedback p { margin: 9px 0 22px; color: var(--ui-text-muted); font-size: var(--kollio-text-small); }
.ideas-results-pagination { display: flex; min-height: 58px; align-items: center; justify-content: space-between; padding: 0 22px; }
.ideas-results-pagination a { min-height: 40px; border-radius: var(--kollio-radius-sm); padding: 11px 13px; color: var(--kollio-active-ink); font-size: var(--kollio-text-caption); font-weight: 600; }
.preview-backdrop { display: none; }
@media (max-width: 1180px) {
  .ideas-explorer-shell { grid-template-columns: minmax(184px, 210px) minmax(0, 1fr); }
  .preview-backdrop { position: fixed; z-index: 65; display: block; inset: 0; background: color-mix(in srgb, var(--kollio-heading) 18%, transparent); backdrop-filter: blur(2px); }
}
@media (max-width: 760px) {
  .ideas-explorer { padding: 24px 14px 50px; }
  .ideas-explorer-header { grid-template-columns: 1fr; }
  .ideas-explorer-header h1 { font-size: var(--kollio-display-hero); }
  .ideas-create-action { grid-row: 3; justify-content: space-between; }
  .ideas-search { grid-column: 1; }
  .ideas-explorer-shell { display: block; min-height: 0; overflow: visible; border-radius: var(--kollio-radius-lg); }
  .ideas-filter-rail { display: block; border-right: 0; border-bottom: 1px solid var(--ui-border); padding: 10px 12px 12px; }
  .ideas-filter-rail nav { display: flex; flex-wrap: wrap; gap: 2px 6px; }
  .ideas-filter-rail > p, .ideas-filter-rail hr { display: none; }
  .ideas-filter-rail .domain-filter { display: flex; min-height: 44px; margin-top: 8px; }
  .ideas-filter-rail button { width: auto; min-width: 0; min-height: 44px; padding: 0 10px; }
  .ideas-filter-rail nav :deep(.sketch-annotation--loop) { width: auto; margin-left: 0; }
  .ideas-results-header { padding-inline: 16px; }
  .ideas-results-header > span { display: none; }
}
</style>
