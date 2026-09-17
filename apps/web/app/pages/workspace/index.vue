<script setup lang="ts">
import type {
  DecisionSpaceDetailResponse,
  DecisionSpaceListResponse,
  DecisionSpaceResponse,
  WorkspaceMemberResponse,
  WorkspaceResponse,
} from '@kollio/api-client'
import { motion, useReducedMotion } from 'motion-v'

definePageMeta({ layout: 'workspace', middleware: 'authenticated' })

const { t, locale } = useI18n()
const router = useRouter()
const requestFetch = useRequestFetch()
const localePath = useLocalePath()
const reducedMotion = useReducedMotion()
const glyphs = Object.freeze({ plus: '＋' })

const formOpen = ref(false)
const formQuestion = ref('')
const formDescription = ref('')
const formDeadline = ref('')
const formError = ref<string>()
const submitting = ref(false)

const { data: workspaces } = await useAsyncData('workspaces', () => requestFetch<WorkspaceResponse[]>('/api/workspaces'))

const activeWorkspace = computed(() => workspaces.value?.[0])

const { data: spacePage, status, error, refresh } = await useAsyncData(
  'decision-spaces',
  async () => {
    const workspace = activeWorkspace.value
    if (!workspace) return undefined
    const base = `/api/workspaces/${encodeURIComponent(workspace.id)}/decision-spaces`
    const list = await requestFetch<DecisionSpaceListResponse>(base)
    const details = await Promise.all(
      list.items.map(space => requestFetch<DecisionSpaceDetailResponse>(`${base}/${encodeURIComponent(space.id)}`)),
    )
    const participantCounts: Record<string, number> = {}
    for (const detail of details) participantCounts[detail.id] = detail.participants.length
    return { items: list.items, participantCounts }
  },
  { watch: [activeWorkspace] },
)

const { data: members } = await useAsyncData(
  'workspace-members',
  async () => {
    if (!activeWorkspace.value) return undefined
    return requestFetch<WorkspaceMemberResponse[]>(
      `/api/workspaces/${encodeURIComponent(activeWorkspace.value.id)}/members`,
    )
  },
  { watch: [activeWorkspace] },
)

const dateFormatter = computed(() =>
  new Intl.DateTimeFormat(locale.value, { day: 'numeric', month: 'long', year: 'numeric' }),
)

function ownerName(ownerId: string) {
  return members.value?.find(member => member.id === ownerId)?.display_name ?? t('decisionSpaces.list.owner')
}
function deadlineLabel(deadline: string | null | undefined) {
  return deadline ? dateFormatter.value.format(new Date(deadline)) : t('decisionSpaces.list.noDeadline')
}
function spaceLink(space: DecisionSpaceResponse) {
  return {
    path: localePath(`/workspace/decision-spaces/${space.id}`),
    query: activeWorkspace.value ? { workspace: activeWorkspace.value.id } : undefined,
  }
}
function toggleForm() {
  formOpen.value = !formOpen.value
  formError.value = undefined
}
async function openSpace() {
  const workspace = activeWorkspace.value
  if (!workspace) return
  const question = formQuestion.value.trim()
  if (!question) {
    formError.value = t('decisionSpaces.form.questionRequired')
    return
  }
  submitting.value = true
  formError.value = undefined
  try {
    const created = await $fetch<DecisionSpaceResponse>(
      `/api/workspaces/${encodeURIComponent(workspace.id)}/decision-spaces`,
      {
        method: 'POST',
        body: {
          question,
          description: formDescription.value.trim() || null,
          deadline: formDeadline.value || null,
        },
      },
    )
    await router.push(spaceLink(created))
  } catch {
    formError.value = t('decisionSpaces.form.failed')
  } finally {
    submitting.value = false
  }
}

useSeoMeta({ title: () => t('decisionSpaces.metaTitle') })
</script>

<template>
  <div class="spaces">
    <section v-if="!activeWorkspace" class="py-24 text-center">
      <h1 class="text-3xl font-semibold tracking-[-0.03em]">{{ t('workspace.empty.title') }}</h1>
      <p class="mx-auto mt-3 max-w-lg leading-relaxed text-muted">{{ t('workspace.empty.description') }}</p>
    </section>

    <template v-else>
      <motion.header :initial="{ opacity: 0, y: reducedMotion ? 0 : 7 }" :animate="{ opacity: 1, y: 0 }" :transition="{ duration: reducedMotion ? 0 : 0.26 }" class="spaces-header">
        <div>
          <h1>{{ t('decisionSpaces.title') }}</h1>
          <p>{{ t('decisionSpaces.description') }}</p>
        </div>
        <button type="button" class="spaces-open-action" :aria-expanded="formOpen" @click="toggleForm">
          {{ t('decisionSpaces.open') }}<span aria-hidden="true" v-text="glyphs.plus" />
        </button>
      </motion.header>

      <form v-if="formOpen" class="spaces-form" @submit.prevent="openSpace">
        <h2>{{ t('decisionSpaces.form.title') }}</h2>
        <label class="spaces-field">
          <span>{{ t('decisionSpaces.form.question') }}</span>
          <input v-model="formQuestion" type="text" maxlength="500" :placeholder="t('decisionSpaces.form.questionPlaceholder')" required>
        </label>
        <label class="spaces-field">
          <span>{{ t('decisionSpaces.form.description') }}</span>
          <textarea v-model="formDescription" rows="3" :placeholder="t('decisionSpaces.form.descriptionPlaceholder')" />
        </label>
        <label class="spaces-field">
          <span>{{ t('decisionSpaces.form.deadline') }}</span>
          <input v-model="formDeadline" type="date">
        </label>
        <p v-if="formError" class="spaces-form-error" role="alert">{{ formError }}</p>
        <div class="spaces-form-actions">
          <button type="submit" :disabled="submitting">{{ submitting ? t('decisionSpaces.form.submitting') : t('decisionSpaces.form.submit') }}</button>
          <button type="button" class="spaces-form-cancel" @click="toggleForm">{{ t('decisionSpaces.cancel') }}</button>
        </div>
      </form>

      <div v-if="status === 'pending'" aria-live="polite" class="spaces-list">
        <div v-for="index in 3" :key="index" class="spaces-row spaces-row-skeleton"><i class="skeleton-line w-2/3" /><i class="skeleton-line mt-3 w-1/3" /></div>
      </div>

      <div v-else-if="error" class="spaces-feedback">
        <h2>{{ t('decisionSpaces.error.title') }}</h2>
        <p>{{ t('decisionSpaces.error.description') }}</p>
        <KollioPrimaryAction :label="t('decisionSpaces.retry')" @click="() => refresh()" />
      </div>

      <div v-else-if="spacePage?.items.length" class="spaces-list">
        <NuxtLink v-for="space in spacePage.items" :key="space.id" class="spaces-row" :to="spaceLink(space)">
          <span class="spaces-row-main">
            <strong>{{ space.question }}</strong>
            <span class="spaces-row-meta">
              <span>{{ t('decisionSpaces.list.ownerLine', { name: ownerName(space.owner_id) }) }}</span>
              <span>{{ t('decisionSpaces.list.deadlineLine', { label: deadlineLabel(space.deadline) }) }}</span>
              <span>{{ t('decisionSpaces.list.participants', { count: spacePage.participantCounts[space.id] ?? 0 }) }}</span>
            </span>
          </span>
          <span class="spaces-row-status">{{ t(`decisionSpaces.status.${space.status}`) }}</span>
        </NuxtLink>
      </div>

      <div v-else class="spaces-feedback">
        <h2>{{ t('decisionSpaces.empty.title') }}</h2>
        <p>{{ t('decisionSpaces.empty.description') }}</p>
        <KollioPrimaryAction :label="t('decisionSpaces.open')" @click="toggleForm" />
      </div>
    </template>
  </div>
</template>

<style scoped>
.spaces { width: 100%; padding: 16px 16px 34px; }
.spaces-header { display: grid; grid-template-columns: minmax(0, 1fr) auto; align-items: center; gap: 22px; margin-bottom: 20px; }
.spaces-header h1 { color: var(--kollio-heading); font-size: var(--kollio-display-section); font-weight: var(--kollio-weight-display); letter-spacing: -.06em; line-height: .96; }
.spaces-header p { margin-top: 8px; color: var(--ui-text-muted); font-size: var(--kollio-text-body); }
.spaces-open-action { display: flex; min-height: 48px; align-items: center; gap: 24px; border-radius: var(--kollio-radius-md); background: var(--kollio-heading); padding: 0 20px; color: var(--ui-bg-elevated); font-size: var(--kollio-text-caption); font-weight: var(--kollio-weight-strong); box-shadow: 0 8px 22px color-mix(in srgb, var(--kollio-heading) 17%, transparent); transition: transform 180ms ease, box-shadow 180ms ease; }
.spaces-open-action:hover { transform: translateY(-1px); box-shadow: 0 11px 28px color-mix(in srgb, var(--kollio-heading) 22%, transparent); }
.spaces-open-action span { font-size: var(--kollio-text-lead); font-weight: var(--kollio-weight-regular); }
.spaces-form { display: grid; max-width: 620px; gap: 16px; margin-bottom: 26px; border: 1px solid var(--ui-border); border-radius: var(--kollio-radius-lg); background: var(--ui-bg-elevated); padding: 22px; box-shadow: var(--kollio-shadow); }
.spaces-form h2 { color: var(--kollio-heading); font-size: var(--kollio-text-title); font-weight: var(--kollio-weight-display); }
.spaces-field { display: grid; gap: 7px; }
.spaces-field > span { color: var(--ui-text-muted); font-size: var(--kollio-text-caption); font-weight: var(--kollio-weight-strong); }
.spaces-field input, .spaces-field textarea { min-height: 48px; border: 1px solid var(--ui-border); border-radius: var(--kollio-radius-md); background: var(--ui-bg); padding: 12px 14px; color: var(--kollio-heading); font-size: var(--kollio-text-small); }
.spaces-field input:focus-visible, .spaces-field textarea:focus-visible { outline: 2px solid var(--kollio-active-ink); outline-offset: 1px; }
.spaces-form-error { color: var(--ui-error); font-size: var(--kollio-text-caption); font-weight: var(--kollio-weight-strong); }
.spaces-form-actions { display: flex; align-items: center; gap: 12px; }
.spaces-form-actions button[type='submit'] { min-height: 46px; border-radius: var(--kollio-radius-md); background: var(--kollio-heading); padding: 0 20px; color: var(--ui-bg-elevated); font-size: var(--kollio-text-caption); font-weight: var(--kollio-weight-strong); }
.spaces-form-actions button[disabled] { opacity: .6; }
.spaces-form-cancel { min-height: 46px; padding: 0 12px; color: var(--ui-text-muted); font-size: var(--kollio-text-caption); font-weight: var(--kollio-weight-strong); }
.spaces-list { display: grid; gap: 10px; }
.spaces-row { display: flex; min-height: 104px; align-items: center; justify-content: space-between; gap: 18px; border: 1px solid var(--ui-border); border-radius: var(--kollio-radius-lg); background: var(--ui-bg-elevated); padding: 20px 22px; transition: border-color 180ms ease, transform 180ms ease; }
.spaces-row:hover { transform: translateY(-1px); border-color: color-mix(in srgb, var(--kollio-active-ink) 32%, var(--ui-border)); }
.spaces-row-main { display: grid; min-width: 0; gap: 9px; }
.spaces-row-main strong { color: var(--kollio-heading); font-size: var(--kollio-text-lead); font-weight: var(--kollio-weight-strong); }
.spaces-row-meta { display: flex; flex-wrap: wrap; gap: 6px 18px; color: var(--ui-text-muted); font-size: var(--kollio-text-caption); }
.spaces-row-status { flex: none; border-radius: var(--kollio-radius-pill); background: var(--kollio-active-wash); padding: 6px 13px; color: var(--kollio-active-ink); font-size: var(--kollio-text-caption); font-weight: var(--kollio-weight-strong); }
.spaces-row-skeleton { display: grid; gap: 0; }
.spaces-feedback { display: flex; min-height: 340px; max-width: 560px; align-items: flex-start; flex-direction: column; justify-content: center; }
.spaces-feedback h2 { color: var(--kollio-heading); font-size: var(--kollio-text-title); font-weight: var(--kollio-weight-strong); }
.spaces-feedback p { margin: 9px 0 22px; color: var(--ui-text-muted); font-size: var(--kollio-text-small); }
@media (max-width: 760px) {
  .spaces { padding: 24px 14px 50px; }
  .spaces-header { grid-template-columns: 1fr; }
  .spaces-header h1 { font-size: var(--kollio-display-hero); }
  .spaces-open-action { justify-content: space-between; }
  .spaces-row { flex-direction: column; align-items: flex-start; }
}
</style>
