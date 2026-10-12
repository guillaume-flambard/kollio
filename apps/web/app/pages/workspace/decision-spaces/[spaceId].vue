<script setup lang="ts">
import type { DecisionSpaceDetailResponse, WorkspaceMemberResponse, WorkspaceResponse } from '@kollio/api-client'

definePageMeta({ layout: 'workspace', middleware: 'authenticated' })

const { t } = useI18n()
const route = useRoute()
const requestFetch = useRequestFetch()
const localePath = useLocalePath()
const spaceId = String(route.params.spaceId)
const moments = [
  { key: 'frame', sections: ['explore', 'converge'] },
  { key: 'choose', sections: ['options', 'decision'] },
  { key: 'happened', sections: ['experiment', 'learning'] },
] as const

const permitted: Record<string, readonly string[]> = {
  OPEN: ['EXPLORING'],
  EXPLORING: ['CONVERGING'],
  CONVERGING: ['READY_TO_DECIDE'],
  READY_TO_DECIDE: ['DECIDED'],
  DECIDED: ['TESTING', 'REOPENED'],
  TESTING: ['LEARNED', 'REOPENED'],
  LEARNED: ['REOPENED'],
  REOPENED: ['EXPLORING'],
}

const transitionTarget = ref('')
const transitionReason = ref('')
const transitionError = ref<string>()
const transitioning = ref(false)

const { data: workspaces } = await useAsyncData('workspaces', () => requestFetch<WorkspaceResponse[]>('/api/workspaces'))

const workspaceId = computed(() => {
  const requested = typeof route.query.workspace === 'string' ? route.query.workspace : undefined
  return workspaces.value?.find(workspace => workspace.id === requested)?.id ?? workspaces.value?.[0]?.id
})

const { data: space, error, refresh } = await useAsyncData(
  `decision-space-${spaceId}`,
  async () => {
    if (!workspaceId.value) return undefined
    return requestFetch<DecisionSpaceDetailResponse>(
      `/api/workspaces/${encodeURIComponent(workspaceId.value)}/decision-spaces/${encodeURIComponent(spaceId)}`,
    )
  },
  { watch: [workspaceId] },
)

const { data: members } = await useAsyncData(
  `decision-space-members-${spaceId}`,
  async () => {
    if (!workspaceId.value) return undefined
    return requestFetch<WorkspaceMemberResponse[]>(`/api/workspaces/${encodeURIComponent(workspaceId.value)}/members`)
  },
  { watch: [workspaceId] },
)

const offeredTransitions = computed(() => (space.value ? permitted[space.value.status] ?? [] : []))
const currentMomentKey = computed(() => {
  const activeSection = moments.find(moment => moment.sections.some(section => sectionIsActive(section)))
  if (activeSection) return activeSection.key

  if (!space.value) return undefined
  if (['OPEN', 'EXPLORING', 'CONVERGING', 'REOPENED'].includes(space.value.status)) return 'frame'
  if (['READY_TO_DECIDE', 'DECIDED'].includes(space.value.status)) return 'choose'
  return 'happened'
})
const { formatDate } = useFormatters()

function momentIsActive(moment: (typeof moments)[number]) {
  return moment.key === currentMomentKey.value
}

function memberName(userId: string) {
  return members.value?.find(member => member.id === userId)?.display_name ?? userId
}
function deadlineLabel(deadline: string | null | undefined) {
  return deadline ? formatDate(deadline) : t('decisionSpaces.list.noDeadline')
}
function sectionLink(section: string) {
  return {
    path: localePath(`/workspace/decision-spaces/${spaceId}/${section}`),
    query: route.query.workspace ? { workspace: route.query.workspace } : undefined,
  }
}
function sectionLabel(section: string) {
  return t(`decisionSpaces.section.${section}.label`)
}
function sectionIsActive(section: string) {
  return route.path === localePath(`/workspace/decision-spaces/${spaceId}/${section}`)
}

watch(offeredTransitions, targets => {
  if (!targets.includes(transitionTarget.value)) transitionTarget.value = targets[0] ?? ''
}, { immediate: true })

async function applyTransition() {
  const current = space.value
  if (!current || !transitionTarget.value) return
  if (transitionTarget.value === 'REOPENED' && !transitionReason.value.trim()) {
    transitionError.value = t('decisionSpaces.transition.reasonRequired')
    return
  }
  transitioning.value = true
  transitionError.value = undefined
  try {
    await $fetch(
      `/api/workspaces/${encodeURIComponent(current.workspace_id)}/decision-spaces/${encodeURIComponent(current.id)}/transitions`,
      {
        method: 'POST',
        body: { to_status: transitionTarget.value, reason: transitionReason.value.trim() || null },
      },
    )
    transitionReason.value = ''
    await refresh()
  } catch {
    transitionError.value = t('decisionSpaces.transition.failed')
  } finally {
    transitioning.value = false
  }
}

useSeoMeta({ title: () => space.value?.question ?? t('decisionSpaces.metaTitle') })
</script>

<template>
  <div class="space">
    <div v-if="error" class="space-feedback">
      <KollioFeedbackState
        :title="t('decisionSpaces.notFound.title')"
        :body="t('decisionSpaces.notFound.description')"
        tone="error"
      />
    </div>

    <template v-else-if="space">
      <NuxtLink class="space-back" :to="localePath('/workspace')">
        <KollioIcon class="space-back__icon" name="arrow-right" />
        {{ t('decisionSpaces.back') }}
      </NuxtLink>

      <KollioPageHeader
        class="space-header"
        :title="space.question"
        :summary="space.description ?? undefined"
      >
        <template #action>
          <KollioStatusMark class="space-status" :label="t(`decisionSpaces.status.${space.status}`)" />
        </template>
      </KollioPageHeader>

      <dl class="space-facts">
        <div><dt>{{ t('decisionSpaces.header.owner') }}</dt><dd>{{ memberName(space.owner_id) }}</dd></div>
        <div><dt>{{ t('decisionSpaces.header.deadline') }}</dt><dd>{{ deadlineLabel(space.deadline) }}</dd></div>
        <div>
          <dt>{{ t('decisionSpaces.header.participants') }}</dt>
          <dd>
            <ul class="space-participants">
              <li v-for="participant in space.participants" :key="participant.user_id">{{ memberName(participant.user_id) }}</li>
            </ul>
            <span v-if="!space.participants.length">{{ t('decisionSpaces.header.noParticipants') }}</span>
          </dd>
        </div>
      </dl>

      <section v-if="offeredTransitions.length" class="space-transition" :aria-label="t('decisionSpaces.transition.choose')">
        <div class="space-transition-target">
          <span>{{ t('decisionSpaces.transition.choose') }}</span>
          <KollioStatusMark :label="t(`decisionSpaces.status.${transitionTarget}`)" />
        </div>
        <label v-if="transitionTarget === 'REOPENED'">
          <span>{{ t('decisionSpaces.transition.reason') }}</span>
          <input v-model="transitionReason" type="text">
        </label>
        <p v-if="transitionError" class="space-transition-error" role="alert">{{ transitionError }}</p>
        <KollioPrimaryAction :label="t('decisionSpaces.transition.submit', { status: t(`decisionSpaces.status.${transitionTarget}`) })" :disabled="transitioning" @click="applyTransition" />
      </section>

      <nav class="space-sections" :aria-label="t('decisionSpaces.title')">
        <div v-for="moment in moments" :key="moment.key" class="space-moment" :class="{ 'is-current': momentIsActive(moment) }">
          <p class="space-moment-label">{{ t(`decisionSpaces.moments.${moment.key}.label`) }}</p>
          <div class="space-moment-links">
            <NuxtLink v-for="section in moment.sections" :key="section" :to="sectionLink(section)" :class="{ 'is-active': sectionIsActive(section) }">
              {{ sectionLabel(section) }}
            </NuxtLink>
          </div>
        </div>
      </nav>

      <div class="space-body">
        <NuxtPage />
      </div>
    </template>
  </div>
</template>

<style scoped>
.space { width: 100%; padding: var(--kollio-space-md) var(--kollio-space-md) var(--kollio-space-xl); }
.space-feedback { display: flex; min-height: 60vh; flex-direction: column; justify-content: center; }
.space-back { display: inline-flex; min-height: var(--kollio-control-height); align-items: center; gap: var(--kollio-space-sm); color: var(--ui-text-muted); font-size: var(--kollio-text-caption); font-weight: var(--kollio-weight-strong); }
.space-back__icon { width: var(--kollio-space-md); transform: rotate(180deg); }
.space-back:hover { color: var(--kollio-active-ink); }
.space-header { margin-top: var(--kollio-space-sm); }
.space-facts { display: flex; flex-wrap: wrap; gap: var(--kollio-space-md) var(--kollio-space-2xl); margin-top: var(--kollio-space-lg); border-top: 1px solid var(--ui-border); border-bottom: 1px solid var(--ui-border); padding: var(--kollio-space-md) 0; }
.space-facts dt { color: var(--ui-text-muted); font-size: var(--kollio-text-micro); font-weight: var(--kollio-weight-strong); text-transform: uppercase; letter-spacing: var(--kollio-tracking-label); }
.space-facts dd { margin-top: var(--kollio-space-sm); color: var(--kollio-heading); font-size: var(--kollio-text-small); font-weight: var(--kollio-weight-strong); }
.space-participants { display: flex; flex-wrap: wrap; gap: var(--kollio-space-sm) var(--kollio-space-md); font-weight: var(--kollio-weight-regular); }
.space-transition { display: flex; flex-wrap: wrap; align-items: flex-end; gap: var(--kollio-space-md); margin-top: var(--kollio-space-lg); }
.space-transition-target, .space-transition label { display: grid; gap: var(--kollio-space-sm); }
.space-transition-target > span, .space-transition label > span { color: var(--ui-text-muted); font-size: var(--kollio-text-micro); font-weight: var(--kollio-weight-strong); text-transform: uppercase; letter-spacing: var(--kollio-tracking-label); }
.space-transition input { min-height: var(--kollio-control-height); border: 1px solid var(--ui-border); border-radius: var(--kollio-radius-md); background: var(--ui-bg-elevated); padding: var(--kollio-space-sm) var(--kollio-space-md); color: var(--kollio-heading); font-size: var(--kollio-text-small); }
.space-transition input:focus-visible { outline: 2px solid var(--kollio-active-ink); outline-offset: var(--kollio-space-xs); }
.space-transition button[disabled] { opacity: .6; }
.space-transition-error { flex-basis: 100%; color: var(--ui-error); font-size: var(--kollio-text-caption); font-weight: var(--kollio-weight-strong); }
.space-sections { display: flex; flex-wrap: wrap; gap: var(--kollio-space-md) var(--kollio-space-xl); margin-top: var(--kollio-space-xl); border-bottom: 1px solid var(--ui-border); padding-bottom: var(--kollio-space-md); }
.space-moment { display: grid; gap: var(--kollio-space-sm); }
.space-moment-label { color: var(--ui-text-muted); font-size: var(--kollio-text-micro); font-weight: var(--kollio-weight-strong); text-transform: uppercase; letter-spacing: var(--kollio-tracking-label); }
.space-moment.is-current .space-moment-label { color: var(--kollio-active-ink); }
.space-moment-links { display: flex; flex-wrap: wrap; gap: var(--kollio-space-xs) var(--kollio-space-sm); }
.space-sections a { display: inline-flex; min-height: var(--kollio-control-height); align-items: center; border-radius: var(--kollio-radius-pill); padding: 0 var(--kollio-space-md); color: var(--ui-text-muted); font-size: var(--kollio-text-small); font-weight: var(--kollio-weight-strong); }
.space-sections a:hover { color: var(--kollio-heading); }
.space-sections a.is-active { background: var(--ui-bg-accented); color: var(--kollio-active-ink); }
.space-body { margin-top: var(--kollio-space-lg); }
@media (max-width: 760px) {
  .space { padding: var(--kollio-space-md) var(--kollio-space-md) var(--kollio-space-2xl); }
  .space-sections { display: grid; grid-template-columns: 1fr; gap: var(--kollio-space-md); }
  .space-moment-links { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .space-sections a { justify-content: center; }
}
</style>
