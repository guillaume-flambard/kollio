<script setup lang="ts">
import type { IdeaResponse, IterationResponse, ProfileResponse } from '@kollio/api-client'
import type { TimelineView } from '~/utils/timeline'

definePageMeta({ layout: 'workspace', middleware: 'authenticated' })

const { t, locale } = useI18n()
const route = useRoute()
const requestFetch = useRequestFetch()
const localePath = useLocalePath()
const ideaId = String(route.params.ideaId)
const activePanel = ref<'team' | 'questions' | 'evidence'>('team')
const descriptionExpanded = ref(false)
const canvasRef = ref<HTMLElement>()
const documentRef = ref<HTMLElement>()
const annotationRef = ref<HTMLElement>()
const relationshipTargetRef = ref<HTMLElement>()
const connection = reactive({ path: '', width: 1, height: 1, startX: 0, startY: 0 })
let canvasObserver: ResizeObserver | undefined

const { data: idea, error, status, refresh } = useLazyAsyncData(`idea-${ideaId}`, () =>
  requestFetch<IdeaResponse>(`/api/ideas/${encodeURIComponent(ideaId)}`),
)

function personLink(id: string) {
  return localePath({ name: 'workspace-people-userId', params: { userId: id } })
}

const dateFormatter = computed(() =>
  new Intl.DateTimeFormat(locale.value, { day: 'numeric', month: 'long', year: 'numeric' }),
)

const grantableParticipations = ['decision_maker', 'contributor', 'observer'] as const
const ownerMemberId = ref('')
const ownerParticipation = ref<(typeof grantableParticipations)[number]>('contributor')
const ownerFunction = ref<(typeof teamFunctions)[number]>('product')
const ownerMembers = ref<{ id: string, display_name: string }[]>([])
const ownerAdding = ref(false)
const ownerAdded = ref(false)
const ownerAddError = ref(false)

async function loadOwnerMembers() {
  const workspaceId = idea.value?.workspace_id
  if (!workspaceId) return
  try {
    ownerMembers.value = await requestFetch(`/api/workspaces/${encodeURIComponent(workspaceId)}/members`)
  } catch {
    ownerMembers.value = []
  }
}

async function addOwnerParticipant() {
  if (!ownerMemberId.value || ownerAdding.value) return
  ownerAdding.value = true
  ownerAddError.value = false
  ownerAdded.value = false
  try {
    await requestFetch(`/api/ideas/${encodeURIComponent(ideaId)}/members`, {
      method: 'POST',
      body: {
        user_id: ownerMemberId.value,
        participation: ownerParticipation.value,
        function: ownerFunction.value,
      },
    })
    ownerMemberId.value = ''
    ownerAdded.value = true
    await refresh()
  } catch {
    ownerAddError.value = true
  } finally {
    ownerAdding.value = false
  }
}

const teamFunctions = ['marketing', 'sales', 'finance', 'product', 'engineering', 'customer_success', 'operations', 'legal', 'hr', 'data', 'direction', 'other'] as const
const joinRequests = computed(() => idea.value?.join_requests ?? [])
const soughtRoles = computed(() => idea.value?.sought_roles ?? [])
const sessionSubject = computed(() => sessionData?.value?.subject)
const isOwner = computed(() => !!idea.value && !!sessionSubject.value && sessionSubject.value === idea.value.owner_id)
const applyRole = ref<(typeof teamFunctions)[number] | ''>('')
const applyNote = ref('')
const teamBusy = ref(false)
const teamError = ref(false)
const teamApplied = ref(false)
const rejectTarget = ref<string | null>(null)
const rejectRationale = ref('')

const { data: sessionData } = await useAsyncData('idea-session', () =>
  requestFetch<{ signedIn: boolean; subject?: string }>('/api/session'),
)

async function retryTeamRefresh() {
  teamError.value = false
  try {
    await refresh()
  }
  catch {
    teamError.value = true
  }
}

async function applyJoin() {
  if (!applyRole.value || !applyNote.value.trim() || teamBusy.value) return
  teamBusy.value = true
  teamError.value = false
  try {
    await requestFetch(`/api/ideas/${encodeURIComponent(ideaId)}/join-requests`, {
      method: 'POST',
      body: { role: applyRole.value, note: applyNote.value.trim() },
    })
    applyRole.value = ''
    applyNote.value = ''
    teamApplied.value = true
    await retryTeamRefresh()
  }
  catch {
    teamError.value = true
  }
  finally {
    teamBusy.value = false
  }
}

async function resolveJoin(requestId: string, action: 'accept' | 'reject') {
  if (teamBusy.value) return
  if (action === 'reject' && rejectTarget.value !== requestId) {
    rejectTarget.value = requestId
    rejectRationale.value = ''
    return
  }
  const rationale = rejectRationale.value
  rejectTarget.value = null
  rejectRationale.value = ''
  teamBusy.value = true
  teamError.value = false
  try {
    await requestFetch(
      `/api/ideas/${encodeURIComponent(ideaId)}/join-requests/${encodeURIComponent(requestId)}/${action}`,
      { method: 'POST', body: action === 'reject' ? { rationale } : undefined },
    )
    await retryTeamRefresh()
  }
  catch {
    teamError.value = true
  }
  finally {
    teamBusy.value = false
  }
}

async function leaveTeam() {
  teamBusy.value = true
  teamError.value = false
  try {
    await requestFetch(`/api/ideas/${encodeURIComponent(ideaId)}/team/leave`, { method: 'POST' })
    await retryTeamRefresh()
  }
  catch {
    teamError.value = true
  }
  finally {
    teamBusy.value = false
  }
}

async function removeTeamMember(memberId: string) {
  teamBusy.value = true
  teamError.value = false
  try {
    await requestFetch(
      `/api/ideas/${encodeURIComponent(ideaId)}/team/remove/${encodeURIComponent(memberId)}`,
      { method: 'POST' },
    )
    await retryTeamRefresh()
  }
  catch {
    teamError.value = true
  }
  finally {
    teamBusy.value = false
  }
}

const actionError = computed(() => teamError.value ? t('ideas.detail.team.error') : '')
watch(isOwner, (owner) => { if (owner) loadOwnerMembers() }, { immediate: true })
const panels = ['team', 'questions', 'evidence'] as const
const pitchParagraphs = computed(() => idea.value?.pitch.split(/\n\s*\n/).filter(Boolean) ?? [])
const pitchSentences = computed(() => idea.value?.pitch.split(/(?<=[.!?])\s+(?=[A-ZÀ-ÖØ-Þ])/).map(sentence => sentence.trim()).filter(Boolean) ?? [])
const ideaSummary = computed(() => pitchSentences.value[0] ?? pitchParagraphs.value[0] ?? '')
const collaborators = computed(() => idea.value?.collaborators ?? [])
const isMember = computed(() => isOwner.value || collaborators.value.some(member => member.id === sessionSubject.value))
const detailParagraphs = computed(() => pitchSentences.value.length > 1 ? pitchSentences.value.slice(1) : pitchParagraphs.value)
const legacyTopics = computed(() => idea.value?.legacy_context?.domain?.split('·').map(topic => topic.trim()).filter(Boolean) ?? [])

const { data: iterations, refresh: refreshIterations } = await useAsyncData(`idea-${ideaId}-iterations`, async () => {
  if (!idea.value) return [] as IterationResponse[]
  return requestFetch<IterationResponse[]>(`/api/ideas/${encodeURIComponent(ideaId)}/iterations`)
}, { watch: [idea] })

const { data: ownerProfile } = await useAsyncData(`idea-${ideaId}-owner`, async () => {
  const ownerId = idea.value?.owner_id
  if (!ownerId) return null
  try {
    return await requestFetch<ProfileResponse>(`/api/users/${encodeURIComponent(ownerId)}`)
  }
  catch {
    return null
  }
}, { watch: [idea] })

const authorNames = computed(() => {
  const names = new Map<string, string>()
  for (const member of collaborators.value) names.set(member.id, member.display_name)
  if (ownerProfile.value && idea.value) names.set(idea.value.owner_id, ownerProfile.value.display_name)
  return names
})

function authorLabel(id: string) {
  return authorNames.value.get(id) ?? id.slice(0, 8)
}

function analysisLabel(analysis: IterationResponse['analysis']) {
  if (!analysis) return undefined
  if (analysis.state === 'resolved' && analysis.realism_score != null)
    return t('ideas.iterations.analysisResolved')
  if (analysis.state === 'abstained') return t('ideas.iterations.analysisAbstained')
  if (analysis.state === 'running') return t('ideas.iterations.analysisRunning')
  return undefined
}

const timelineView = computed<TimelineView>(() => toTimelineView(buildTimeline(iterations.value ?? []), {
  authorName: authorLabel,
  formatDate: iso => dateFormatter.value.format(new Date(iso)),
  statusLabel: status => t(`ideas.iterations.${status}`),
  analysisLabel,
}))

const mainHead = computed(() => headEntry(buildTimeline(iterations.value ?? [])))
const proposing = ref(false)
const proposeOpen = ref(false)
const proposeError = ref<'conflict' | 'other' | ''>('')
const proposeForm = reactive({ message: '', title: '', pitch: '', stage: 'seed' as 'seed' | 'iterating' | 'team_formed' })

function openPropose() {
  proposeOpen.value = true
  proposeError.value = ''
  proposeForm.title = idea.value?.title ?? ''
  proposeForm.pitch = idea.value?.pitch ?? ''
  proposeForm.stage = (idea.value?.stage ?? 'seed') as typeof proposeForm.stage
  proposeForm.message = ''
}

function branchSlug(message: string) {
  const stem = message.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 40)
  return `proposal/${stem || 'change'}`
}

async function submitProposal() {  if (!proposeForm.message.trim() || !proposeForm.title.trim() || !proposeForm.pitch.trim() || proposing.value) return
  proposing.value = true
  proposeError.value = ''
  try {
    await requestFetch(`/api/ideas/${encodeURIComponent(ideaId)}/iterations`, {
      method: 'POST',
      body: {
        message: proposeForm.message.trim(),
        lang: idea.value?.lang ?? 'en',
        snapshot: { title: proposeForm.title.trim(), pitch: proposeForm.pitch.trim(), stage: proposeForm.stage },
        branch: branchSlug(proposeForm.message),
        expected_parent_id: mainHead.value?.id ?? null,
      },
    })
    proposeOpen.value = false
    await refreshIterations()
  }
  catch (error: unknown) {
    proposeError.value = (error as { statusCode?: number })?.statusCode === 409 ? 'conflict' : 'other'
  }
  finally {
    proposing.value = false
  }
}

const typeOptions = useInitiativeTypeOptions()

const typeError = ref(false)

async function changeInitiativeType(event: Event) {
  const value = (event.target as HTMLSelectElement).value
  typeError.value = false
  try {
    await requestFetch(`/api/ideas/${encodeURIComponent(ideaId)}`, {
      method: 'PATCH',
      body: { initiative_type: value },
    })
    await refresh()
  }
  catch {
    typeError.value = true
  }
}

const canManageIterations = computed(() => isOwner.value)
const iterationsActionsError = ref(false)

async function acceptProposal(id: string) {
  iterationsActionsError.value = false
  try {
    await requestFetch(`/api/ideas/${encodeURIComponent(ideaId)}/iterations/${encodeURIComponent(id)}/accept`, {
      method: 'POST',
      body: { expected_parent_id: mainHead.value?.id ?? null },
    })
    await Promise.all([refreshIterations(), refresh()])
  }
  catch {
    iterationsActionsError.value = true
  }
}

async function rejectProposal(payload: { id: string, rationale: string }) {
  iterationsActionsError.value = false
  try {
    await requestFetch(`/api/ideas/${encodeURIComponent(ideaId)}/iterations/${encodeURIComponent(payload.id)}/reject`, {
      method: 'POST',
      body: { rationale: payload.rationale },
    })
    await refreshIterations()
  }
  catch {
    iterationsActionsError.value = true
  }
}

async function rollbackTo(target: { key: string, hash: string }) {
  iterationsActionsError.value = false
  try {
    await requestFetch(`/api/ideas/${encodeURIComponent(ideaId)}/iterations/${encodeURIComponent(target.key)}/rollback`, {
      method: 'POST',
      body: {
        message: t('ideas.iterations.rollbackMessage', { hash: target.hash }),
        lang: idea.value?.lang ?? 'en',
        expected_parent_id: mainHead.value?.id ?? null,
      },
    })
    await Promise.all([refreshIterations(), refresh()])
  }
  catch {
    iterationsActionsError.value = true
  }
}

const problemAnnotation = computed(() => {
  const paragraph = detailParagraphs.value[0] ?? ''
  if (!idea.value?.legacy_context || !paragraph) return undefined
  const words = paragraph.split(/\s+/)
  if (words.length < 8) return { before: '', highlight: paragraph, after: '' }
  const start = Math.min(words.length - 4, Math.floor(words.length * 0.38))
  const end = Math.min(words.length, start + 4)
  return {
    before: `${words.slice(0, start).join(' ')} `,
    highlight: words.slice(start, end).join(' '),
    after: ` ${words.slice(end).join(' ')}`,
  }
})
const legacySourceLabel = computed(() => idea.value?.legacy_context?.source === 'prospecteur' ? 'Prospecteur' : idea.value?.legacy_context?.source)
const errorTitle = computed(() => error.value?.statusCode === 404 ? t('ideas.detail.notFound') : t('ideas.detail.loadError.title'))
const errorDescription = computed(() => error.value?.statusCode === 404 ? t('ideas.detail.notFoundDescription') : t('ideas.detail.loadError.description'))

function updateConnection() {
  const canvas = canvasRef.value
  const documentSurface = documentRef.value
  const annotation = annotationRef.value
  const target = relationshipTargetRef.value
  if (activePanel.value !== 'team' || !canvas || !documentSurface || !annotation || !target) {
    connection.path = ''
    return
  }
  const canvasRect = canvas.getBoundingClientRect()
  const annotationRect = annotation.getBoundingClientRect()
  const targetRect = target.getBoundingClientRect()
  const annotationVisible = annotationRect.bottom > 0 && annotationRect.top < window.innerHeight
  const targetVisible = targetRect.bottom > 0 && targetRect.top < window.innerHeight
  if (!annotationVisible || !targetVisible) {
    connection.path = ''
    return
  }
  const startX = annotationRect.right - canvasRect.left + 8
  const startY = annotationRect.top + annotationRect.height / 2 - canvasRect.top
  const endX = targetRect.left - canvasRect.left
  const endY = targetRect.top + Math.min(42, targetRect.height / 2) - canvasRect.top
  const horizontalSpan = Math.max(1, endX - startX)
  const curveSpan = Math.min(220, horizontalSpan)
  const curveStartX = endX - curveSpan
  const controlOffset = Math.max(34, curveSpan * 0.45)
  connection.width = canvasRect.width
  connection.height = canvas.scrollHeight
  connection.startX = startX
  connection.startY = startY
  connection.path = `M ${startX} ${startY} L ${curveStartX} ${startY} C ${curveStartX + controlOffset} ${startY}, ${endX - controlOffset} ${endY}, ${endX} ${endY}`
}

function selectPanel(panel: string) {
  if (!panels.includes(panel as typeof panels[number])) return
  const nextPanel = panel as typeof panels[number]
  activePanel.value = nextPanel
  nextTick(() => requestAnimationFrame(updateConnection))
}

function handleRelationshipTarget(target?: HTMLElement) {
  relationshipTargetRef.value = target
  nextTick(() => requestAnimationFrame(updateConnection))
}

watch(activePanel, () => nextTick(() => requestAnimationFrame(updateConnection)))
onMounted(() => {
  window.addEventListener('resize', updateConnection)
  window.addEventListener('scroll', updateConnection, { passive: true })
  canvasObserver = new ResizeObserver(updateConnection)
  if (canvasRef.value) canvasObserver.observe(canvasRef.value)
  requestAnimationFrame(updateConnection)
})
onBeforeUnmount(() => {
  window.removeEventListener('resize', updateConnection)
  window.removeEventListener('scroll', updateConnection)
  canvasObserver?.disconnect()
})

useSeoMeta({ title: () => idea.value ? `${idea.value.title} | Kollio` : t('ideas.detail.metaTitle') })
</script>

<template>
  <KollioIdeaDetailSkeleton v-if="status === 'pending' || status === 'idle'" :label="t('ideas.detail.loading')" />
  <KollioIdeaDetailError
    v-else-if="error"
    :title="errorTitle"
    :description="errorDescription"
    :reassurance="t('ideas.detail.loadError.reassurance')"
    :retry-label="t('ideas.detail.retry')"
    :back-label="t('ideas.detail.explore')"
    :back-to="$localePath('/workspace/ideas')"
    @retry="refresh"
  />
  <article
    v-else-if="idea"
    class="idea-enter w-full"
  >
    <div ref="canvasRef" class="idea-layout relative grid min-w-0">
      <svg v-if="connection.path" aria-hidden="true" class="pointer-events-none absolute inset-0 z-40 hidden overflow-visible lg:block" :viewBox="`0 0 ${connection.width} ${connection.height}`" preserveAspectRatio="none">
        <path class="relationship-path" :d="connection.path" pathLength="1" fill="none" stroke="var(--kollio-connector)" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" />
        <circle :cx="connection.startX" :cy="connection.startY" r="4.5" fill="var(--kollio-connector)" />
      </svg>

      <div ref="documentRef" class="kollio-surface idea-document relative z-10 min-w-0 p-5 sm:p-7 lg:p-7 xl:p-9">
        <header class="idea-header">
          <NuxtLink :to="$localePath('/workspace/ideas')" class="idea-breadcrumb inline-flex items-center gap-2 text-sm font-medium text-muted hover:text-default">
            {{ t('navigation.ideas') }}
            <svg aria-hidden="true" viewBox="0 0 24 24" class="size-4" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m9 18 6-6-6-6" /></svg>
            {{ t(`ideas.stage.${idea.stage}`) }}
          </NuxtLink>
          <div class="idea-header-actions flex items-center gap-3">
            <KollioPrimaryAction :label="t('ideas.detail.advance')" @click="selectPanel('questions')" />
            <button type="button" class="idea-more-action" :aria-label="t('ideas.detail.moreActions')">
              <svg aria-hidden="true" viewBox="0 0 24 24" class="size-5" fill="currentColor"><circle cx="5" cy="12" r="1.5" /><circle cx="12" cy="12" r="1.5" /><circle cx="19" cy="12" r="1.5" /></svg>
            </button>
          </div>
          <h1 class="idea-title max-w-[630px]">{{ idea.title }}</h1>
          <div class="idea-topics flex flex-wrap items-center gap-x-5 gap-y-3 text-sm text-muted">
            <KollioSketchAnnotation active kind="swash">{{ t(`ideas.stage.${idea.stage}`) }}</KollioSketchAnnotation>
            <label class="initiative-type">
              <span class="text-muted">{{ t('ideas.initiativeTypeLabel') }}</span>
              <select
                v-if="isOwner"
                :value="idea.initiative_type"
                name="initiative-type"
                @change="changeInitiativeType"
              >
                <option v-for="(label, value) in typeOptions" :key="value" :value="value">{{ label }}</option>
              </select>
              <strong v-else>{{ t(`ideas.initiativeType.${idea.initiative_type}`) }}</strong>
            </label>
            <p v-if="typeError" role="alert" class="text-sm text-red-500">{{ t('ideas.detail.typeError') }}</p>
            <template v-for="topic in legacyTopics" :key="topic">
              <span class="inline-flex items-center gap-5">
                <span aria-hidden="true" class="idea-dot" />
                <span class="first-letter:uppercase">{{ topic }}</span>
              </span>
            </template>
            <button type="button" class="idea-topic-add" :aria-label="t('ideas.detail.enrich')" @click="selectPanel('questions')">
              <svg aria-hidden="true" viewBox="0 0 24 24" class="size-5" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 5v14M5 12h14" /></svg>
            </button>
          </div>
          <p class="idea-summary line-clamp-2 max-w-[70ch] text-muted">{{ ideaSummary }}</p>
          <div class="idea-stats flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-muted">
            <KollioAvatarStack
              v-if="collaborators.length"
              :people="collaborators"
              :profile-links="true"
              :label="t('ideas.detail.stats.contributors', { count: collaborators.length })"
            />
            <span>{{ t('ideas.detail.stats.contributors', { count: collaborators.length }) }}</span>
            <span aria-hidden="true" class="size-1 rounded-full bg-muted" />
            <button type="button" class="transition-colors hover:text-default" @click="selectPanel('questions')">{{ t('ideas.detail.stats.questions', { count: 0 }) }}</button>
            <span aria-hidden="true" class="size-1 rounded-full bg-muted" />
            <button type="button" class="transition-colors hover:text-default" @click="selectPanel('evidence')">{{ t('ideas.detail.stats.evidence', { count: 0 }) }}</button>
            <span aria-hidden="true" class="size-1 rounded-full bg-muted" />
            <time :datetime="idea.created_at">{{ dateFormatter.format(new Date(idea.created_at)) }}</time>
          </div>
        </header>

        <section id="description" class="idea-description mt-11 rounded-2xl border border-default p-5 sm:p-6" :aria-labelledby="'idea-pitch-title'">
          <h2 id="idea-pitch-title" class="text-[length:var(--kollio-text-title)] font-semibold tracking-[-0.025em]">{{ t('ideas.detail.pitchTitle') }}</h2>
          <KollioDisclosure
            v-model="descriptionExpanded"
            content-id="idea-description-content"
            :expand-label="t('ideas.detail.showFull')"
            :collapse-label="t('ideas.detail.showLess')"
            class="mt-4 max-w-[72ch]"
          >
            <div class="idea-prose space-y-5 text-muted">
              <p v-if="problemAnnotation">
                {{ problemAnnotation.before }}<button ref="annotationRef" type="button" class="linked-passage text-left" :aria-label="t('ideas.detail.annotation.provenance', { excerpt: problemAnnotation.highlight })" :aria-pressed="activePanel === 'team'" @click="selectPanel('team')"><KollioSketchAnnotation active kind="swash">{{ problemAnnotation.highlight }}</KollioSketchAnnotation></button><br class="linked-passage-break">{{ problemAnnotation.after }}
              </p>
              <p v-else-if="detailParagraphs[0]">{{ detailParagraphs[0] }}</p>
              <p v-for="(paragraph, index) in detailParagraphs.slice(1)" :key="index">{{ paragraph }}</p>
            </div>
          </KollioDisclosure>
          <button type="button" class="idea-writing-prompt mt-6 w-full text-left" @click="selectPanel('questions')">{{ t('ideas.detail.writeToEnrich') }}</button>
        </section>

        <KollioIterationTimeline
          :view="timelineView"
          :count-label="t('ideas.detail.iterations.count', { count: iterations?.length ?? 0 })"
          :title="t('ideas.detail.iterations.title')"
          :empty-label="t('ideas.detail.iterations.empty')"
          :imported-label="legacySourceLabel ? t('ideas.detail.iterations.imported') : undefined"
          :branch-label="name => t('ideas.iterations.branch', { name })"
          :can-manage="canManageIterations"
          :accept-label="t('ideas.iterations.accept')"
          :reject-label="t('ideas.iterations.reject')"
          :rationale-placeholder="t('ideas.iterations.rationalePlaceholder')"
          :rollback-label="t('ideas.iterations.rollback')"
          @accept="acceptProposal"
          @reject="rejectProposal"
          @rollback="rollbackTo"
        />
        <p v-if="iterationsActionsError" role="alert" class="text-sm text-red-500">{{ t('ideas.iterations.actionsError') }}</p>

        <div class="mt-6">
          <button v-if="!proposeOpen" type="button" class="team-link" @click="openPropose()">{{ t('ideas.iterations.propose') }}</button>
          <p v-if="!proposeOpen" class="mt-2 text-sm text-muted">{{ t('ideas.iterations.proposeHint') }}</p>
          <form v-else class="mt-4 grid max-w-[560px] gap-3" @submit.prevent="submitProposal">
            <label class="grid gap-1 text-sm font-medium">{{ t('ideas.iterations.message') }}
              <input v-model="proposeForm.message" type="text" required maxlength="500" name="iteration-message" class="rounded-xl border border-default bg-elevated px-3 py-2 text-sm font-normal">
            </label>
            <label class="grid gap-1 text-sm font-medium">{{ t('ideas.iterations.titleField') }}
              <input v-model="proposeForm.title" type="text" required maxlength="240" name="iteration-title" class="rounded-xl border border-default bg-elevated px-3 py-2 text-sm font-normal">
            </label>
            <label class="grid gap-1 text-sm font-medium">{{ t('ideas.iterations.pitchField') }}
              <textarea v-model="proposeForm.pitch" rows="4" required maxlength="12000" name="iteration-pitch" class="rounded-xl border border-default bg-elevated px-3 py-2 text-sm font-normal" />
            </label>
            <label class="grid gap-1 text-sm font-medium">{{ t('ideas.iterations.stageField') }}
              <select v-model="proposeForm.stage" name="iteration-stage" class="w-fit rounded-xl border border-default bg-elevated px-3 py-2 text-sm font-normal">
                <option v-for="stage in ['seed', 'iterating', 'team_formed']" :key="stage" :value="stage">{{ t(`ideas.iterations.stages.${stage}`) }}</option>
              </select>
            </label>
            <p v-if="proposeError === 'conflict'" role="alert" class="text-sm text-red-500">{{ t('ideas.iterations.conflict') }}</p>
            <p v-else-if="proposeError" role="alert" class="text-sm text-red-500">{{ t('ideas.iterations.error') }}</p>
            <div class="flex items-center gap-3">
              <button type="button" class="team-link" @click="proposeOpen = false">{{ t('ideas.iterations.cancel') }}</button>
              <button type="submit" class="team-link" :disabled="proposing">{{ proposing ? t('ideas.iterations.sending') : t('ideas.iterations.send') }}</button>
            </div>
          </form>
        </div>

        <KollioExperimentLoop
          :idea-id="ideaId"
          :is-member="isMember"
        />

        <section id="team" class="idea-team mt-11 rounded-2xl border border-default p-5 sm:p-6" :aria-labelledby="'idea-team-title'">
          <h2 id="idea-team-title" class="text-[length:var(--kollio-text-title)] font-semibold tracking-[-0.025em]">{{ t('ideas.detail.team.title') }}</h2>

          <div class="mt-4 grid gap-2 sm:grid-cols-[2fr_1fr]">
            <div>
              <h3 class="text-sm font-medium text-muted">{{ t('ideas.detail.team.membersTitle') }}</h3>
              <ul class="mt-2 grid gap-1" role="list">
                <li v-for="member in collaborators" :key="member.id" class="flex items-center justify-between gap-3">
                  <KollioPersonRow :name="member.display_name" :meta="`${t(`ideas.participation.${member.participation}`)} · ${t(`ideas.function.${member.business_function}`)}`" :avatar-key="member.avatar_key ?? 'lilac'" :to="personLink(member.id)" />
                  <button v-if="isOwner && member.id !== idea.owner_id" type="button" class="team-link" @click="removeTeamMember(member.id)">
                    {{ t('ideas.detail.team.remove') }}
                  </button>
                  <button v-else-if="!isOwner" type="button" class="team-link" @click="leaveTeam()">
                    {{ t('ideas.detail.team.leave') }}
                  </button>
                </li>
              </ul>
              <p v-if="!collaborators.length" class="text-sm text-muted">{{ t('ideas.detail.foundationNote') }}</p>
            </div>
            <div>
              <h3 class="text-sm font-medium text-muted">{{ t('ideas.detail.team.soughtTitle') }}</h3>
              <ul class="mt-2 flex flex-wrap gap-1">
                <li v-for="role in soughtRoles" :key="role" class="team-role-pill">{{ t(`ideas.function.${role}`) }}</li>
              </ul>
            </div>
          </div>

          <div v-if="joinRequests.length" class="team-requests mt-4 grid gap-2">
            <div v-for="request in joinRequests" :key="request.id" class="team-request rounded-xl border border-default p-3" :data-status="request.status">
              <p class="text-sm font-medium">{{ request.note }}</p>
              <p class="text-sm text-muted">{{ t('ideas.function.' + request.business_function) }}</p>
              <p v-if="request.status === 'rejected' && request.rationale">
                {{ t('ideas.detail.team.rejected', { rationale: request.rationale }) }}
              </p>
              <p v-else-if="request.status === 'pending'">{{ t('ideas.detail.team.pending') }}</p>
              <div v-if="isOwner && request.status === 'pending'" class="flex gap-2">
                <button v-if="rejectTarget !== request.id" type="button" class="team-link" @click="resolveJoin(request.id, 'accept')">
                  {{ t('ideas.detail.team.accept') }}
                </button>
                <button type="button" class="team-link" @click="resolveJoin(request.id, 'reject')">
                  {{ t('ideas.detail.team.reject') }}
                </button>
              </div>
              <form v-if="rejectTarget === request.id" @submit.prevent="resolveJoin(request.id, 'reject')">
                <input v-model="rejectRationale" type="text" :placeholder="t('ideas.detail.team.rejectReason')" required>
                <button type="submit" class="team-link">{{ t('ideas.detail.team.reject') }}</button>
              </form>
            </div>
          </div>

          <form v-if="isOwner" class="team-add mt-4 grid gap-2" @submit.prevent="addOwnerParticipant">
            <label class="text-sm font-medium" for="team-add-member">{{ t('ideas.detail.team.addTitle') }}</label>
            <select id="team-add-member" v-model="ownerMemberId" required>
              <option value="" disabled>{{ t('ideas.detail.team.addPick') }}</option>
              <option v-for="member in ownerMembers" :key="member.id" :value="member.id">{{ member.display_name }}</option>
            </select>
            <div class="flex flex-wrap gap-2">
              <select v-model="ownerParticipation" :aria-label="t('ideas.detail.team.addParticipation')">
                <option v-for="value in grantableParticipations" :key="value" :value="value">{{ t(`ideas.participation.${value}`) }}</option>
              </select>
              <select v-model="ownerFunction" :aria-label="t('ideas.detail.team.addFunction')">
                <option v-for="role in teamFunctions" :key="role" :value="role">{{ t(`ideas.function.${role}`) }}</option>
              </select>
            </div>
            <p v-if="ownerAddError" role="alert">{{ t('ideas.detail.team.addError') }}</p>
            <button type="submit" class="team-link" :disabled="ownerAdding || !ownerMemberId">
              {{ ownerAdding ? t('ideas.detail.team.sending') : t('ideas.detail.team.add') }}
            </button>
            <p v-if="ownerAdded" class="text-sm text-muted">{{ t('ideas.detail.team.added') }}</p>
          </form>

          <form v-if="!isOwner && !joinRequests.length" class="team-apply mt-4 grid gap-2" @submit.prevent="applyJoin">
            <div class="flex flex-wrap items-center gap-2">
              <label class="text-sm font-medium" for="team-apply-role">{{ t('ideas.detail.team.applyRole') }}</label>
              <select id="team-apply-role" v-model="applyRole" required>
                <option v-for="role in teamFunctions" :key="role" :value="role">{{ t(`ideas.function.${role}`) }}</option>
              </select>
            </div>
            <label class="grid gap-1 text-sm font-medium" for="team-apply-note">
              {{ t('ideas.detail.team.applyNote') }}
              <textarea id="team-apply-note" v-model="applyNote" rows="2" required />
            </label>
            <p v-if="actionError" role="alert">{{ actionError }}</p>
            <button type="submit" class="team-link" :disabled="teamBusy">
              {{ teamBusy ? t('ideas.detail.team.sending') : t('ideas.detail.team.apply') }}
            </button>
            <p v-if="teamApplied" class="text-sm text-muted">{{ t('ideas.detail.team.applied') }}</p>
          </form>
        </section>

        <KollioCommentComposer :label="t('ideas.detail.comment')" @activate="selectPanel('team')" />
      </div>

      <KollioIdeaCompanion
        :idea="idea"
        :active-panel="activePanel"
        @update:active-panel="selectPanel"
        @target-ready="handleRelationshipTarget"
      />
    </div>
  </article>
</template>

<style scoped>
.initiative-type {
  display: inline-flex;
  align-items: baseline;
  gap: var(--kollio-space-sm);
}
</style>
