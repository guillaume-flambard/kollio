<script setup lang="ts">
import type {
  ExperimentDetailResponse,
  ExperimentResponse,
  IdeaPageResponse,
  LearningResponse,
  OutcomeResponse,
  WorkspaceMemberResponse,
  WorkspaceResponse
} from '@kollio/api-client'

definePageMeta({ layout: 'workspace', middleware: 'authenticated' })

const { t } = useI18n()
const route = useRoute()
const requestFetch = useRequestFetch()

const spaceId = String(route.params.spaceId)

const textDrafts = ref<Record<string, string>>({})
const busyId = ref('')
const formError = ref<string>()

const { data: workspaces } = await useAsyncData('workspaces', () =>
  requestFetch<WorkspaceResponse[]>('/api/workspaces')
)

const workspaceId = computed(() => {
  const requested = typeof route.query.workspace === 'string' ? route.query.workspace : undefined
  return workspaces.value?.find(workspace => workspace.id === requested)?.id ?? workspaces.value?.[0]?.id
})

const basePath = computed(
  () =>
    `/api/workspaces/${encodeURIComponent(workspaceId.value ?? '')}/decision-spaces/${encodeURIComponent(spaceId)}`
)

const {
  data: experimentDetails,
  error: experimentsError,
  refresh: refreshExperiments
} = await useAsyncData(
  `learning-experiments-${spaceId}`,
  async () => {
    if (!workspaceId.value) return undefined
    const list = await requestFetch<ExperimentResponse[]>(`${basePath.value}/experiments`)
    return await Promise.all(
      list.map(item => requestFetch<ExperimentDetailResponse>(`/api/experiments/${encodeURIComponent(item.id)}`))
    )
  },
  { watch: [workspaceId] }
)

const {
  data: lessonList,
  error: lessonsError,
  refresh: refreshLessons
} = await useAsyncData(
  `learning-lessons-${spaceId}`,
  async () => {
    if (!workspaceId.value) return undefined
    return await requestFetch<LearningResponse[]>(`${basePath.value}/learnings`)
  },
  { watch: [workspaceId] }
)

const { data: members } = await useAsyncData(
  `learning-members-${spaceId}`,
  async () => {
    if (!workspaceId.value) return undefined
    return await requestFetch<WorkspaceMemberResponse[]>(
      `/api/workspaces/${encodeURIComponent(workspaceId.value)}/members`
    )
  },
  { watch: [workspaceId] }
)

const { data: ideas } = await useAsyncData(
  `learning-ideas-${spaceId}`,
  async () => {
    if (!workspaceId.value) return undefined
    return await requestFetch<IdeaPageResponse>(
      `/api/workspaces/${encodeURIComponent(workspaceId.value)}/ideas`,
      { query: { limit: 100, offset: 0 } }
    )
  },
  { watch: [workspaceId] }
)

const lessons = computed<LearningResponse[]>(() => lessonList.value ?? [])
const proposed = computed(() => lessons.value.filter(lesson => lesson.status === 'draft'))
const confirmed = computed(() => lessons.value.filter(lesson => lesson.status === 'confirmed'))

const { formatDate: dateLabel } = useFormatters()

function detailFor(experimentId: string) {
  return experimentDetails.value?.find(detail => detail.experiment.id === experimentId)
}

function experimentTitle(experimentId: string) {
  return detailFor(experimentId)?.experiment.title ?? experimentId
}

function outcomesFor(lesson: LearningResponse): OutcomeResponse[] {
  const detail = detailFor(lesson.experiment_id)
  if (!detail) return []
  const wanted = new Set(lesson.outcome_ids)
  const matched = detail.outcomes.filter(outcome => wanted.has(outcome.id))
  return matched.length ? matched : detail.outcomes
}

function ideaTitle(ideaId: string) {
  return ideas.value?.items.find(idea => idea.id === ideaId)?.title ?? ideaId
}

function memberName(userId: string | null | undefined) {
  if (!userId) return ''
  return members.value?.find(member => member.id === userId)?.display_name ?? userId
}

function statusLabel(status: string) {
  return t(`decisionSpaces.learning.status.${status}`)
}

function textOf(lesson: LearningResponse) {
  return textDrafts.value[lesson.id] ?? lesson.text
}

function setText(lessonId: string, value: string) {
  textDrafts.value = { ...textDrafts.value, [lessonId]: value }
}

async function writeLesson(lesson: LearningResponse, confirm: boolean) {
  busyId.value = lesson.id
  formError.value = undefined
  try {
    await $fetch(`/api/experiments/${encodeURIComponent(lesson.experiment_id)}/learnings`, {
      method: 'POST',
      body: { text: textOf(lesson).trim() || null, confirm }
    })
    await refreshLessons()
    await refreshExperiments()
  } catch {
    formError.value = confirm
      ? t('decisionSpaces.learning.actions.confirmFailed')
      : t('decisionSpaces.learning.actions.saveFailed')
  } finally {
    busyId.value = ''
  }
}

function confirmLesson(lesson: LearningResponse) {
  return writeLesson(lesson, true)
}

function saveDraft(lesson: LearningResponse) {
  return writeLesson(lesson, false)
}

useSeoMeta({ title: () => t('decisionSpaces.section.learning.title') })
</script>

<template>
  <section class="learning">
    <h2>{{ t('decisionSpaces.section.learning.title') }}</h2>
    <p class="learning-intro">{{ t('decisionSpaces.section.learning.body') }}</p>

    <p v-if="experimentsError || lessonsError" class="learning-error" role="alert">
      {{ t('decisionSpaces.learning.loadFailed') }}
    </p>

    <template v-else>
      <div v-if="!lessons.length" class="learning-empty-state">
        <h3>{{ t('decisionSpaces.learning.empty.title') }}</h3>
        <p class="learning-empty">{{ t('decisionSpaces.learning.empty.body') }}</p>
      </div>

      <template v-else>
        <p v-if="formError" class="learning-form-error" role="alert">{{ formError }}</p>

        <div class="learning-block">
          <h3>{{ t('decisionSpaces.learning.proposed.title') }}</h3>
          <p class="learning-hint">{{ t('decisionSpaces.learning.proposed.intro') }}</p>

          <ul v-if="proposed.length" class="lesson-list">
            <li v-for="lesson in proposed" :key="lesson.id" class="lesson">
              <div class="lesson-head">
                <h4>{{ experimentTitle(lesson.experiment_id) }}</h4>
                <span class="lesson-status">{{ statusLabel(lesson.status) }}</span>
              </div>

              <form class="learning-form" @submit.prevent="confirmLesson(lesson)">
                <label>
                  <span>{{ t('decisionSpaces.learning.card.text') }}</span>
                  <textarea
                    rows="4"
                    :value="textOf(lesson)"
                    :placeholder="t('decisionSpaces.learning.card.textPlaceholder')"
                    @input="setText(lesson.id, ($event.target as HTMLTextAreaElement).value)"
                  />
                </label>

                <dl class="lesson-descent">
                  <div>
                    <dt>{{ t('decisionSpaces.learning.card.outcome') }}</dt>
                    <dd>
                      <ul v-if="outcomesFor(lesson).length" class="lesson-outcomes">
                        <li v-for="outcome in outcomesFor(lesson)" :key="outcome.id" class="lesson-outcome">
                          <span class="outcome-metric">{{ outcome.metric }}</span>
                          <span class="outcome-value">{{ outcome.value }}</span>
                          <span v-if="outcome.unit" class="outcome-unit">{{ outcome.unit }}</span>
                        </li>
                      </ul>
                      <span v-else class="learning-empty">{{ t('decisionSpaces.learning.card.noOutcome') }}</span>
                    </dd>
                  </div>
                  <div>
                    <dt>{{ t('decisionSpaces.learning.card.initiative') }}</dt>
                    <dd>{{ ideaTitle(lesson.idea_id) }}</dd>
                  </div>
                </dl>

                <div class="learning-form-actions">
                  <button type="submit" :disabled="busyId === lesson.id">
                    {{
                      busyId === lesson.id
                        ? t('decisionSpaces.learning.actions.confirming')
                        : t('decisionSpaces.learning.actions.confirm')
                    }}
                  </button>
                  <button
                    type="button"
                    class="learning-secondary"
                    :disabled="busyId === lesson.id"
                    @click="saveDraft(lesson)"
                  >
                    {{ t('decisionSpaces.learning.actions.save') }}
                  </button>
                </div>
              </form>
            </li>
          </ul>
          <p v-else class="learning-empty">{{ t('decisionSpaces.learning.proposed.empty') }}</p>
        </div>

        <div class="learning-block">
          <h3>{{ t('decisionSpaces.learning.confirmed.title') }}</h3>
          <p class="learning-hint">{{ t('decisionSpaces.learning.confirmed.intro') }}</p>

          <ul v-if="confirmed.length" class="lesson-list">
            <li v-for="lesson in confirmed" :key="lesson.id" class="lesson">
              <div class="lesson-head">
                <h4>{{ experimentTitle(lesson.experiment_id) }}</h4>
                <span class="lesson-status">{{ statusLabel(lesson.status) }}</span>
              </div>

              <p class="lesson-text">{{ lesson.text }}</p>

              <dl class="lesson-descent">
                <div>
                  <dt>{{ t('decisionSpaces.learning.card.outcome') }}</dt>
                  <dd>
                    <ul v-if="outcomesFor(lesson).length" class="lesson-outcomes">
                      <li v-for="outcome in outcomesFor(lesson)" :key="outcome.id" class="lesson-outcome">
                        <span class="outcome-metric">{{ outcome.metric }}</span>
                        <span class="outcome-value">{{ outcome.value }}</span>
                        <span v-if="outcome.unit" class="outcome-unit">{{ outcome.unit }}</span>
                      </li>
                    </ul>
                    <span v-else class="learning-empty">{{ t('decisionSpaces.learning.card.noOutcome') }}</span>
                  </dd>
                </div>
                <div>
                  <dt>{{ t('decisionSpaces.learning.card.experiment') }}</dt>
                  <dd>{{ experimentTitle(lesson.experiment_id) }}</dd>
                </div>
                <div>
                  <dt>{{ t('decisionSpaces.learning.card.initiative') }}</dt>
                  <dd>{{ ideaTitle(lesson.idea_id) }}</dd>
                </div>
                <div>
                  <dt>{{ t('decisionSpaces.learning.status.confirmed') }}</dt>
                  <dd>
                    {{
                      t('decisionSpaces.learning.card.confirmedBy', {
                        name: memberName(lesson.confirmed_by_id),
                        date: dateLabel(lesson.updated_at)
                      })
                    }}
                  </dd>
                </div>
              </dl>
            </li>
          </ul>
          <p v-else class="learning-empty">{{ t('decisionSpaces.learning.confirmed.empty') }}</p>
        </div>

        <p class="learning-note">{{ t('decisionSpaces.learning.notes.neverAuto') }}</p>
        <p class="learning-note">{{ t('decisionSpaces.learning.notes.draftKept') }}</p>
      </template>
    </template>
  </section>
</template>

<style scoped>
.learning {
  display: grid;
  max-width: 76ch;
  gap: 8px;
}

.learning h2 {
  color: var(--kollio-heading);
  font-size: var(--kollio-text-title);
  font-weight: var(--kollio-weight-display);
}

.learning h3 {
  color: var(--kollio-heading);
  font-size: var(--kollio-text-lead);
  font-weight: var(--kollio-weight-strong);
}

.learning h4 {
  color: var(--kollio-heading);
  font-size: var(--kollio-text-body);
  font-weight: var(--kollio-weight-strong);
}

.learning-intro,
.learning-hint,
.learning-note,
.learning-empty {
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-small);
  line-height: var(--kollio-leading-body);
}

.learning-error,
.learning-form-error {
  margin-top: 10px;
  color: var(--ui-error);
  font-size: var(--kollio-text-caption);
  font-weight: var(--kollio-weight-strong);
}

.learning-empty-state {
  display: grid;
  gap: 8px;
  margin-top: 22px;
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-md);
  background: var(--ui-bg-elevated);
  padding: 20px;
}

.learning-block {
  margin-top: 26px;
  border-top: 1px solid var(--ui-border);
  padding-top: 18px;
}

.lesson-list {
  display: grid;
  gap: 14px;
  margin-top: 16px;
  padding: 0;
  list-style: none;
}

.lesson {
  display: grid;
  gap: 12px;
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-md);
  background: var(--ui-bg-elevated);
  padding: 16px;
}

.lesson-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.lesson-status {
  flex: none;
  border-radius: var(--kollio-radius-pill);
  background: var(--kollio-active-wash);
  padding: 5px 12px;
  color: var(--kollio-active-ink);
  font-size: var(--kollio-text-micro);
  font-weight: var(--kollio-weight-strong);
}

.lesson-text {
  color: var(--kollio-heading);
  font-size: var(--kollio-text-small);
  line-height: var(--kollio-leading-relaxed);
}

.learning-form {
  display: grid;
  gap: 14px;
}

.learning-form label {
  display: grid;
  gap: 6px;
}

.learning-form label > span {
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-micro);
  font-weight: var(--kollio-weight-strong);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.learning-form textarea {
  min-height: 96px;
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-md);
  background: var(--ui-bg);
  padding: 10px 12px;
  color: var(--kollio-heading);
  font-size: var(--kollio-text-small);
  resize: vertical;
}

.learning-form-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.learning-form-actions button {
  display: inline-flex;
  min-height: 44px;
  align-items: center;
  border: none;
  border-radius: var(--kollio-radius-md);
  background: var(--kollio-heading);
  padding: 0 20px;
  color: var(--ui-bg-elevated);
  font-size: var(--kollio-text-caption);
  font-weight: var(--kollio-weight-strong);
}

.learning-secondary {
  display: inline-flex;
  min-height: 44px;
  align-items: center;
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-md);
  background: var(--ui-bg-elevated);
  padding: 0 18px;
  color: var(--kollio-heading);
  font-size: var(--kollio-text-caption);
  font-weight: var(--kollio-weight-strong);
}

.learning-secondary:hover {
  border-color: var(--kollio-active-ink);
  color: var(--kollio-active-ink);
}

.learning-form-actions button:focus-visible,
.learning-form textarea:focus-visible,
.learning-secondary:focus-visible {
  outline: 2px solid var(--kollio-active-ink);
  outline-offset: 1px;
}

.learning-form-actions button[disabled] {
  opacity: 0.6;
}

.lesson-descent {
  display: grid;
  gap: 10px;
  margin: 0;
}

.lesson-descent div {
  display: grid;
  gap: 4px;
}

.lesson-descent dt {
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-micro);
  font-weight: var(--kollio-weight-strong);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.lesson-descent dd {
  margin: 0;
  color: var(--kollio-heading);
  font-size: var(--kollio-text-small);
}

.lesson-outcomes {
  display: grid;
  gap: 4px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.lesson-outcome {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

@media (max-width: 760px) {
  .lesson-head {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
