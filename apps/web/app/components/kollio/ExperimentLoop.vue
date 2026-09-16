<script setup lang="ts">
import type { ExperimentDetailResponse, ExperimentResponse, OutcomeResponse } from '@kollio/api-client'

const props = defineProps<{
  ideaId: string
  isMember: boolean
}>()

const { t } = useI18n()
const requestFetch = useRequestFetch()

const experiments = ref<ExperimentResponse[]>([])
const listStatus = ref<'loading' | 'ready' | 'error'>('loading')
const openId = ref<string | null>(null)
const detail = ref<ExperimentDetailResponse | null>(null)
const detailStatus = ref<'idle' | 'loading' | 'ready' | 'error'>('idle')
const busy = ref(false)
const actionError = ref<'rule' | 'other' | ''>('')

const createOpen = ref(false)
const createForm = reactive({ title: '', hypothesis: '', success_metric: '', baseline: '', target: '' })
const outcomeForm = reactive({ metric: '', value: '', unit: '', observed_at: '', comment: '', qualitative: '' })
const learningText = ref('')

const actionErrorMessage = computed(() =>
  actionError.value === 'rule' ? t('ideas.experiments.ruleError') : t('ideas.experiments.actionError'),
)

function classify(error: unknown): 'rule' | 'other' {
  return (error as { statusCode?: number })?.statusCode === 422 ? 'rule' : 'other'
}

function outcomeLabel(outcome: OutcomeResponse) {
  return [outcome.metric, outcome.value, outcome.unit].filter(Boolean).join(' ')
}

async function fetchExperiments() {
  experiments.value = await requestFetch<ExperimentResponse[]>(
    `/api/ideas/${encodeURIComponent(props.ideaId)}/experiments`,
  )
}

async function openExperiment(id: string | null) {
  if (!id) return
  openId.value = id
  detailStatus.value = 'loading'
  actionError.value = ''
  try {
    const data = await requestFetch<ExperimentDetailResponse>(`/api/experiments/${encodeURIComponent(id)}`)
    detail.value = data
    learningText.value = data.learning?.text ?? ''
    detailStatus.value = 'ready'
  }
  catch {
    detailStatus.value = 'error'
  }
}

async function loadExperiments() {
  listStatus.value = 'loading'
  try {
    await fetchExperiments()
    listStatus.value = 'ready'
    const first = experiments.value[0]
    if (first && !openId.value) await openExperiment(first.id)
  }
  catch {
    listStatus.value = 'error'
  }
}

async function refreshList() {
  try {
    await fetchExperiments()
    listStatus.value = 'ready'
  }
  catch {
    listStatus.value = 'error'
  }
}

function openCreate() {
  createOpen.value = true
  actionError.value = ''
}

function resetCreate() {
  createForm.title = ''
  createForm.hypothesis = ''
  createForm.success_metric = ''
  createForm.baseline = ''
  createForm.target = ''
}

async function createExperiment() {
  if (busy.value) return
  busy.value = true
  actionError.value = ''
  try {
    const created = await requestFetch<ExperimentResponse>(
      `/api/ideas/${encodeURIComponent(props.ideaId)}/experiments`,
      {
        method: 'POST',
        body: {
          title: createForm.title.trim(),
          hypothesis: createForm.hypothesis.trim(),
          success_metric: createForm.success_metric.trim(),
          baseline: createForm.baseline.trim() || null,
          target: createForm.target.trim() || null,
        },
      },
    )
    createOpen.value = false
    resetCreate()
    await refreshList()
    await openExperiment(created.id)
  }
  catch (error: unknown) {
    actionError.value = classify(error)
  }
  finally {
    busy.value = false
  }
}

async function setStatus(target: 'running' | 'completed' | 'cancelled') {
  const id = openId.value
  if (busy.value || !id) return
  busy.value = true
  actionError.value = ''
  try {
    await requestFetch(`/api/experiments/${encodeURIComponent(id)}/status`, {
      method: 'POST',
      body: { status: target },
    })
    await refreshList()
    await openExperiment(id)
  }
  catch (error: unknown) {
    actionError.value = classify(error)
  }
  finally {
    busy.value = false
  }
}

function resetOutcome() {
  outcomeForm.metric = ''
  outcomeForm.value = ''
  outcomeForm.unit = ''
  outcomeForm.observed_at = ''
  outcomeForm.comment = ''
  outcomeForm.qualitative = ''
}

async function recordOutcome() {
  const id = openId.value
  if (busy.value || !id) return
  busy.value = true
  actionError.value = ''
  try {
    await requestFetch(`/api/experiments/${encodeURIComponent(id)}/outcomes`, {
      method: 'POST',
      body: {
        metric: outcomeForm.metric.trim(),
        value: outcomeForm.value.trim(),
        unit: outcomeForm.unit.trim() || null,
        observed_at: outcomeForm.observed_at || null,
        comment: outcomeForm.comment.trim() || null,
        qualitative: outcomeForm.qualitative.trim() || null,
      },
    })
    resetOutcome()
    await openExperiment(id)
  }
  catch (error: unknown) {
    actionError.value = classify(error)
  }
  finally {
    busy.value = false
  }
}

async function confirmLearning() {
  const id = openId.value
  if (busy.value || !id) return
  busy.value = true
  actionError.value = ''
  try {
    await requestFetch(`/api/experiments/${encodeURIComponent(id)}/learnings`, {
      method: 'POST',
      body: { text: learningText.value, confirm: true },
    })
    await openExperiment(id)
  }
  catch (error: unknown) {
    actionError.value = classify(error)
  }
  finally {
    busy.value = false
  }
}

onMounted(loadExperiments)
</script>

<template>
  <section id="experiments" class="idea-experiments mt-11 rounded-2xl border border-default p-5 sm:p-6" :aria-labelledby="'idea-experiments-title'">
    <div class="experiment-heading">
      <h2 id="idea-experiments-title" class="text-[length:var(--kollio-text-title)] font-semibold tracking-[-0.025em]">{{ t('ideas.experiments.title') }}</h2>
      <span v-if="listStatus === 'ready' && experiments.length" class="text-sm text-muted">{{ t('ideas.experiments.count', { count: experiments.length }) }}</span>
    </div>

    <p v-if="listStatus === 'loading'" class="mt-4 text-sm text-muted">{{ t('ideas.experiments.loading') }}</p>

    <div v-else-if="listStatus === 'error'" class="mt-4">
      <p role="alert" class="text-sm text-[color:var(--ui-error)]">{{ t('ideas.experiments.loadError') }}</p>
      <button type="button" class="experiment-action mt-2" @click="loadExperiments()">{{ t('ideas.experiments.retry') }}</button>
    </div>

    <template v-else>
      <KollioEmptyState
        v-if="!experiments.length"
        class="mt-4"
        :description="t('ideas.experiments.empty')"
        :action-label="isMember ? t('ideas.experiments.newAction') : undefined"
        @action="openCreate()"
      />

      <ul v-else class="mt-4 grid gap-2" role="list">
        <li v-for="experiment in experiments" :key="experiment.id">
          <button
            type="button"
            class="experiment-row"
            :data-status="experiment.status"
            :aria-expanded="openId === experiment.id"
            @click="openExperiment(experiment.id)"
          >
            <span class="experiment-row-title">{{ experiment.title }}</span>
            <span class="experiment-status" :data-status="experiment.status">{{ t(`ideas.experiments.status.${experiment.status}`) }}</span>
          </button>
        </li>
      </ul>

      <form v-if="isMember && createOpen" class="mt-5 grid max-w-[560px] gap-3" @submit.prevent="createExperiment">
        <h3 class="text-sm font-medium">{{ t('ideas.experiments.create.title') }}</h3>
        <label class="grid gap-1 text-sm font-medium">{{ t('ideas.experiments.create.name') }}
          <input v-model="createForm.title" type="text" required maxlength="300" name="experiment-title" class="rounded-xl border border-default bg-elevated px-3 py-2 text-sm font-normal">
        </label>
        <label class="grid gap-1 text-sm font-medium">{{ t('ideas.experiments.create.hypothesis') }}
          <textarea v-model="createForm.hypothesis" rows="2" required name="experiment-hypothesis" class="rounded-xl border border-default bg-elevated px-3 py-2 text-sm font-normal" />
        </label>
        <label class="grid gap-1 text-sm font-medium">{{ t('ideas.experiments.create.metric') }}
          <input v-model="createForm.success_metric" type="text" required maxlength="300" name="experiment-metric" class="rounded-xl border border-default bg-elevated px-3 py-2 text-sm font-normal">
        </label>
        <div class="grid gap-3 sm:grid-cols-2">
          <label class="grid gap-1 text-sm font-medium">{{ t('ideas.experiments.create.baseline') }}
            <input v-model="createForm.baseline" type="text" maxlength="200" name="experiment-baseline" class="rounded-xl border border-default bg-elevated px-3 py-2 text-sm font-normal">
          </label>
          <label class="grid gap-1 text-sm font-medium">{{ t('ideas.experiments.create.target') }}
            <input v-model="createForm.target" type="text" maxlength="200" name="experiment-target" class="rounded-xl border border-default bg-elevated px-3 py-2 text-sm font-normal">
          </label>
        </div>
        <p v-if="actionError" role="alert" class="text-sm text-[color:var(--ui-error)]">{{ actionErrorMessage }}</p>
        <div class="flex items-center gap-3">
          <button type="button" class="experiment-action" @click="createOpen = false">{{ t('ideas.experiments.create.cancel') }}</button>
          <button type="submit" class="experiment-action experiment-action--primary" :disabled="busy">
            {{ busy ? t('ideas.experiments.create.submitting') : t('ideas.experiments.create.submit') }}
          </button>
        </div>
      </form>
      <button v-else-if="isMember && experiments.length" type="button" class="experiment-action mt-3" @click="openCreate()">{{ t('ideas.experiments.newAction') }}</button>

      <p v-if="detailStatus === 'loading'" class="mt-5 text-sm text-muted">{{ t('ideas.experiments.detailLoading') }}</p>
      <div v-else-if="detailStatus === 'error'" class="mt-5">
        <p role="alert" class="text-sm text-[color:var(--ui-error)]">{{ t('ideas.experiments.loadError') }}</p>
        <button type="button" class="experiment-action mt-2" @click="openExperiment(openId)">{{ t('ideas.experiments.retry') }}</button>
      </div>
      <div v-else-if="detail" class="experiment-detail mt-5" :data-status="detail.experiment.status">
        <dl class="grid gap-4 text-sm">
          <div>
            <dt class="text-muted">{{ t('ideas.experiments.detail.hypothesis') }}</dt>
            <dd class="mt-1 leading-relaxed text-default">{{ detail.experiment.hypothesis }}</dd>
          </div>
          <div>
            <dt class="text-muted">{{ t('ideas.experiments.detail.metric') }}</dt>
            <dd class="mt-1 text-default">{{ detail.experiment.success_metric }}</dd>
          </div>
          <div v-if="detail.experiment.baseline">
            <dt class="text-muted">{{ t('ideas.experiments.detail.baseline') }}</dt>
            <dd class="mt-1 text-default">{{ detail.experiment.baseline }}</dd>
          </div>
          <div v-if="detail.experiment.target">
            <dt class="text-muted">{{ t('ideas.experiments.detail.target') }}</dt>
            <dd class="mt-1 text-default">{{ detail.experiment.target }}</dd>
          </div>
        </dl>

        <div v-if="isMember && (detail.experiment.status === 'proposed' || detail.experiment.status === 'running')" class="mt-4 flex flex-wrap gap-2">
          <button v-if="detail.experiment.status === 'proposed'" type="button" class="experiment-action experiment-action--primary" :disabled="busy" @click="setStatus('running')">
            {{ t('ideas.experiments.actions.start') }}
          </button>
          <button v-else type="button" class="experiment-action experiment-action--primary" :disabled="busy" @click="setStatus('completed')">
            {{ t('ideas.experiments.actions.complete') }}
          </button>
          <button type="button" class="experiment-action" :disabled="busy" @click="setStatus('cancelled')">
            {{ t('ideas.experiments.actions.cancel') }}
          </button>
        </div>
        <p v-if="actionError" role="alert" class="mt-3 text-sm text-[color:var(--ui-error)]">{{ actionErrorMessage }}</p>

        <div class="experiment-outcomes mt-5">
          <h3 class="text-sm font-medium">{{ t('ideas.experiments.outcomes.title') }}</h3>
          <ul v-if="detail.outcomes.length" class="mt-2 grid gap-2" role="list">
            <li v-for="outcome in detail.outcomes" :key="outcome.id" class="experiment-outcome">
              <p class="text-sm font-medium text-default">{{ outcomeLabel(outcome) }}</p>
              <p v-if="outcome.observed_at" class="text-sm text-muted">{{ outcome.observed_at }}</p>
              <p v-if="outcome.comment" class="mt-1 text-sm text-muted">{{ outcome.comment }}</p>
              <p v-if="outcome.qualitative" class="mt-1 text-sm text-muted">{{ outcome.qualitative }}</p>
            </li>
          </ul>
          <p v-else class="mt-2 text-sm text-muted">{{ t('ideas.experiments.outcomes.empty') }}</p>

          <form v-if="isMember && (detail.experiment.status === 'running' || detail.experiment.status === 'completed')" class="mt-4 grid max-w-[560px] gap-3" @submit.prevent="recordOutcome">
            <div class="grid gap-3 sm:grid-cols-2">
              <label class="grid gap-1 text-sm font-medium">{{ t('ideas.experiments.outcomes.metric') }}
                <input v-model="outcomeForm.metric" type="text" required maxlength="200" name="outcome-metric" class="rounded-xl border border-default bg-elevated px-3 py-2 text-sm font-normal">
              </label>
              <label class="grid gap-1 text-sm font-medium">{{ t('ideas.experiments.outcomes.value') }}
                <input v-model="outcomeForm.value" type="text" required maxlength="200" name="outcome-value" class="rounded-xl border border-default bg-elevated px-3 py-2 text-sm font-normal">
              </label>
            </div>
            <div class="grid gap-3 sm:grid-cols-2">
              <label class="grid gap-1 text-sm font-medium">{{ t('ideas.experiments.outcomes.unit') }}
                <input v-model="outcomeForm.unit" type="text" maxlength="50" name="outcome-unit" class="rounded-xl border border-default bg-elevated px-3 py-2 text-sm font-normal">
              </label>
              <label class="grid gap-1 text-sm font-medium">{{ t('ideas.experiments.outcomes.observedAt') }}
                <input v-model="outcomeForm.observed_at" type="date" name="outcome-observed-at" class="rounded-xl border border-default bg-elevated px-3 py-2 text-sm font-normal">
              </label>
            </div>
            <label class="grid gap-1 text-sm font-medium">{{ t('ideas.experiments.outcomes.comment') }}
              <input v-model="outcomeForm.comment" type="text" name="outcome-comment" class="rounded-xl border border-default bg-elevated px-3 py-2 text-sm font-normal">
            </label>
            <label class="grid gap-1 text-sm font-medium">{{ t('ideas.experiments.outcomes.qualitative') }}
              <textarea v-model="outcomeForm.qualitative" rows="2" name="outcome-qualitative" class="rounded-xl border border-default bg-elevated px-3 py-2 text-sm font-normal" />
            </label>
            <button type="submit" class="experiment-action experiment-action--primary w-fit" :disabled="busy">
              {{ busy ? t('ideas.experiments.outcomes.submitting') : t('ideas.experiments.outcomes.add') }}
            </button>
          </form>
        </div>

        <div v-if="detail.learning" class="experiment-learning mt-5">
          <div class="flex items-center justify-between gap-3">
            <h3 class="text-sm font-medium">{{ t('ideas.experiments.learning.title') }}</h3>
            <span class="experiment-status" :data-status="detail.learning.status">{{ t(`ideas.experiments.learning.${detail.learning.status}`) }}</span>
          </div>
          <template v-if="isMember && detail.learning.status === 'draft'">
            <label class="mt-3 grid gap-1 text-sm font-medium">
              <span class="sr-only">{{ t('ideas.experiments.learning.title') }}</span>
              <textarea v-model="learningText" rows="5" name="learning-text" class="rounded-xl border border-default bg-elevated px-3 py-2 text-sm font-normal" />
            </label>
            <button type="button" class="experiment-action experiment-action--primary mt-3" :disabled="busy" @click="confirmLearning">
              {{ busy ? t('ideas.experiments.learning.confirming') : t('ideas.experiments.learning.confirm') }}
            </button>
          </template>
          <template v-else>
            <p class="mt-3 whitespace-pre-line text-sm leading-relaxed text-default">{{ detail.learning.text }}</p>
            <p
              v-if="detail.learning.status === 'confirmed'"
              class="experiment-confirmed-note"
            >
              {{ t('ideas.experiments.learning.confirmedNote') }}
            </p>
          </template>
        </div>
      </div>
    </template>
  </section>
</template>

<style scoped>
.experiment-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.experiment-row {
  display: flex;
  width: 100%;
  min-height: 48px;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-md);
  background: var(--ui-bg-elevated);
  padding: 10px 14px;
  text-align: left;
  transition: border-color 180ms ease, background 180ms ease;
}

.experiment-row:hover {
  border-color: color-mix(in srgb, var(--ui-primary) 28%, var(--ui-border));
  background: var(--ui-bg-muted);
}

.experiment-row[aria-expanded='true'] {
  border-color: color-mix(in srgb, var(--kollio-active-ink) 34%, var(--ui-border));
}

.experiment-row-title {
  color: var(--ui-text);
  font-weight: var(--kollio-weight-medium);
}

.experiment-status {
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-small);
  font-weight: var(--kollio-weight-medium);
}

.experiment-status[data-status='running'] {
  color: var(--kollio-active-ink);
}

.experiment-status[data-status='completed'] {
  color: var(--ui-success);
}

.experiment-action {
  display: inline-flex;
  min-height: 40px;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-md);
  background: var(--ui-bg-elevated);
  padding: 0 14px;
  color: var(--ui-text);
  font-size: var(--kollio-text-small);
  font-weight: var(--kollio-weight-medium);
  transition: background 180ms ease, border-color 180ms ease, transform 180ms cubic-bezier(.16, 1, .3, 1);
}

.experiment-action:hover:not(:disabled) {
  border-color: color-mix(in srgb, var(--kollio-active-ink) 28%, var(--ui-border));
  background: var(--ui-bg-muted);
}

.experiment-action:active:not(:disabled) {
  transform: scale(.98);
}

.experiment-action:disabled {
  cursor: not-allowed;
  opacity: .5;
}

.experiment-action--primary {
  border-color: var(--kollio-action);
  background: var(--kollio-action);
  color: var(--ui-bg-elevated);
}

.experiment-action--primary:hover:not(:disabled) {
  border-color: var(--kollio-action);
  background: color-mix(in srgb, var(--kollio-action) 88%, var(--kollio-heading));
}

.experiment-detail {
  border-top: 1px solid var(--ui-border);
  padding-top: 20px;
}

.experiment-outcome {
  border-radius: var(--kollio-radius-md);
  background: color-mix(in srgb, var(--ui-bg-muted) 72%, transparent);
  padding: 12px 14px;
}

.experiment-learning {
  border-radius: var(--kollio-radius-lg);
  background: var(--ui-bg-accented);
  padding: 16px;
}

.experiment-confirmed-note {
  display: inline-flex;
  margin-top: 12px;
  border-radius: var(--kollio-radius-sm);
  background: color-mix(in srgb, var(--kollio-wash) 60%, transparent);
  padding: 4px 10px;
  color: var(--kollio-active-ink);
  font-size: var(--kollio-text-small);
  font-weight: var(--kollio-weight-medium);
}

@media (prefers-reduced-motion: no-preference) {
  .experiment-confirmed-note {
    animation: note-settle 220ms cubic-bezier(.16, 1, .3, 1) both;
  }
}

@keyframes note-settle {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
