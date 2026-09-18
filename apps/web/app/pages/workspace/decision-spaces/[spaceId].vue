<script setup lang="ts">
import type { DecisionSpaceDetailResponse, WorkspaceMemberResponse, WorkspaceResponse } from '@kollio/api-client'

definePageMeta({ layout: 'workspace', middleware: 'authenticated' })

const { t } = useI18n()
const route = useRoute()
const requestFetch = useRequestFetch()
const localePath = useLocalePath()
const spaceId = String(route.params.spaceId)
const glyphs = Object.freeze({ back: '←' })
const sections = ['explore', 'converge', 'options', 'decision', 'experiment', 'learning'] as const
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
const { formatDate } = useFormatters()

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
    <p v-if="error" class="space-feedback">
      <strong>{{ t('decisionSpaces.notFound.title') }}</strong>
      <span>{{ t('decisionSpaces.notFound.description') }}</span>
    </p>

    <template v-else-if="space">
      <NuxtLink class="space-back" :to="localePath('/workspace')"><span aria-hidden="true" v-text="glyphs.back" /> {{ t('decisionSpaces.back') }}</NuxtLink>

      <header class="space-header">
        <div class="space-header-main">
          <h1>{{ space.question }}</h1>
          <p v-if="space.description">{{ space.description }}</p>
        </div>
        <span class="space-status">{{ t(`decisionSpaces.status.${space.status}`) }}</span>
      </header>

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

      <form v-if="offeredTransitions.length" class="space-transition" @submit.prevent="applyTransition">
        <label>
          <span>{{ t('decisionSpaces.transition.choose') }}</span>
          <select v-model="transitionTarget">
            <option v-for="target in offeredTransitions" :key="target" :value="target">{{ t(`decisionSpaces.status.${target}`) }}</option>
          </select>
        </label>
        <label v-if="transitionTarget === 'REOPENED'">
          <span>{{ t('decisionSpaces.transition.reason') }}</span>
          <input v-model="transitionReason" type="text">
        </label>
        <p v-if="transitionError" class="space-transition-error" role="alert">{{ transitionError }}</p>
        <button type="submit" :disabled="transitioning">{{ t('decisionSpaces.transition.submit') }}</button>
      </form>

      <nav class="space-sections" :aria-label="t('decisionSpaces.title')">
        <NuxtLink v-for="section in sections" :key="section" :to="sectionLink(section)" :class="{ 'is-active': sectionIsActive(section) }">
          {{ sectionLabel(section) }}
        </NuxtLink>
      </nav>

      <div class="space-body">
        <NuxtPage />
      </div>
    </template>
  </div>
</template>

<style scoped>
.space { width: 100%; padding: 16px 16px 34px; }
.space-feedback { display: flex; min-height: 60vh; flex-direction: column; gap: 8px; justify-content: center; max-width: 560px; color: var(--ui-text-muted); }
.space-feedback strong { color: var(--kollio-heading); font-size: var(--kollio-text-title); font-weight: var(--kollio-weight-display); }
.space-back { display: inline-flex; min-height: 40px; align-items: center; gap: 8px; color: var(--ui-text-muted); font-size: var(--kollio-text-caption); font-weight: var(--kollio-weight-strong); }
.space-back:hover { color: var(--kollio-active-ink); }
.space-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 22px; margin-top: 10px; }
.space-header h1 { max-width: 46ch; color: var(--kollio-heading); font-size: var(--kollio-text-headline); font-weight: var(--kollio-weight-display); letter-spacing: -.03em; line-height: var(--kollio-leading-heading); }
.space-header-main p { margin-top: 10px; max-width: 62ch; color: var(--ui-text-muted); font-size: var(--kollio-text-small); line-height: var(--kollio-leading-body); }
.space-status { flex: none; border-radius: var(--kollio-radius-pill); background: var(--kollio-active-wash); padding: 7px 15px; color: var(--kollio-active-ink); font-size: var(--kollio-text-caption); font-weight: var(--kollio-weight-strong); }
.space-facts { display: flex; flex-wrap: wrap; gap: 12px 40px; margin-top: 22px; border-top: 1px solid var(--ui-border); border-bottom: 1px solid var(--ui-border); padding: 16px 0; }
.space-facts dt { color: var(--ui-text-muted); font-size: var(--kollio-text-micro); font-weight: var(--kollio-weight-strong); text-transform: uppercase; letter-spacing: .08em; }
.space-facts dd { margin-top: 6px; color: var(--kollio-heading); font-size: var(--kollio-text-small); font-weight: var(--kollio-weight-strong); }
.space-participants { display: flex; flex-wrap: wrap; gap: 6px 14px; font-weight: var(--kollio-weight-regular); }
.space-transition { display: flex; flex-wrap: wrap; align-items: flex-end; gap: 14px; margin-top: 18px; }
.space-transition label { display: grid; gap: 6px; }
.space-transition label > span { color: var(--ui-text-muted); font-size: var(--kollio-text-micro); font-weight: var(--kollio-weight-strong); text-transform: uppercase; letter-spacing: .08em; }
.space-transition select, .space-transition input { min-height: 44px; border: 1px solid var(--ui-border); border-radius: var(--kollio-radius-md); background: var(--ui-bg-elevated); padding: 10px 12px; color: var(--kollio-heading); font-size: var(--kollio-text-small); }
.space-transition select:focus-visible, .space-transition input:focus-visible { outline: 2px solid var(--kollio-active-ink); outline-offset: 1px; }
.space-transition button { min-height: 44px; border-radius: var(--kollio-radius-md); background: var(--kollio-heading); padding: 0 20px; color: var(--ui-bg-elevated); font-size: var(--kollio-text-caption); font-weight: var(--kollio-weight-strong); }
.space-transition button[disabled] { opacity: .6; }
.space-transition-error { flex-basis: 100%; color: var(--ui-error); font-size: var(--kollio-text-caption); font-weight: var(--kollio-weight-strong); }
.space-sections { display: flex; flex-wrap: wrap; gap: 4px 6px; margin-top: 26px; border-bottom: 1px solid var(--ui-border); padding-bottom: 12px; }
.space-sections a { display: inline-flex; min-height: 42px; align-items: center; border-radius: var(--kollio-radius-pill); padding: 0 16px; color: var(--ui-text-muted); font-size: var(--kollio-text-small); font-weight: var(--kollio-weight-strong); }
.space-sections a:hover { color: var(--kollio-heading); }
.space-sections a.is-active { background: var(--ui-bg-accented); color: var(--kollio-active-ink); }
.space-body { margin-top: 22px; }
@media (max-width: 760px) {
  .space { padding: 20px 14px 50px; }
  .space-header { flex-direction: column; }
  .space-sections { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .space-sections a { justify-content: center; }
}
</style>
