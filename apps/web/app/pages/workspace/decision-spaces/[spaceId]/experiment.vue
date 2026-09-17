<script setup lang="ts">
import type {
  ExperimentDetailResponse,
  ExperimentResponse,
  IdeaPageResponse,
  OptionResponse,
  ScenarioRunResponse,
  ScenarioVariableResponse,
  SensitivityResponse,
  WorkspaceResponse,
} from '@kollio/api-client'

definePageMeta({ layout: 'workspace', middleware: 'authenticated' })

const { t } = useI18n()
const route = useRoute()
const requestFetch = useRequestFetch()
const spaceId = String(route.params.spaceId)
const glyphs = Object.freeze({ plus: '＋' })
const levels = ['optimistic', 'base', 'pessimistic', 'failure'] as const
const directions = ['above', 'below'] as const

const { data: workspaces } = await useAsyncData('workspaces', () =>
  requestFetch<WorkspaceResponse[]>('/api/workspaces'),
)

const workspaceId = computed(() => {
  const requested = typeof route.query.workspace === 'string' ? route.query.workspace : undefined
  return (
    workspaces.value?.find((workspace) => workspace.id === requested)?.id ??
    workspaces.value?.[0]?.id
  )
})

const basePath = computed(
  () =>
    `/api/workspaces/${encodeURIComponent(workspaceId.value ?? '')}/decision-spaces/${encodeURIComponent(spaceId)}`,
)

const { data: optionList, error: optionsError } = await useAsyncData(
  `experiment-options-${spaceId}`,
  async () => {
    if (!workspaceId.value) return undefined
    return requestFetch<{ items: OptionResponse[] }>(`${basePath.value}/options`)
  },
  { watch: [workspaceId] },
)

const options = computed(() => optionList.value?.items ?? [])
const hasOptions = computed(() => options.value.length > 0)

const {
  data: variableList,
  error: variablesError,
  refresh: refreshVariables,
} = await useAsyncData(
  `experiment-variables-${spaceId}`,
  async () => {
    if (!workspaceId.value) return undefined
    return requestFetch<{ items: ScenarioVariableResponse[] }>(
      `${basePath.value}/scenario-variables`,
    )
  },
  { watch: [workspaceId] },
)

const variables = computed(() => variableList.value?.items ?? [])

const runsOptionId = ref('')

watch(
  options,
  (list) => {
    if (!runsOptionId.value && list.length > 0) runsOptionId.value = list[0]?.id ?? ''
  },
  { immediate: true },
)

const {
  data: runList,
  error: runsError,
  refresh: refreshRuns,
} = await useAsyncData(
  `experiment-runs-${spaceId}`,
  async () => {
    if (!workspaceId.value || !runsOptionId.value) return undefined
    return requestFetch<{ items: ScenarioRunResponse[] }>(
      `${basePath.value}/options/${encodeURIComponent(runsOptionId.value)}/scenario-runs`,
    )
  },
  { watch: [workspaceId, runsOptionId] },
)

const runs = computed(() => runList.value?.items ?? [])

const metricVariableId = ref('')
const criterionDirection = ref<'above' | 'below'>('above')
const threshold = ref('')

const variableBounds = computed(() =>
  variables.value
    .map((variable) => `${variable.id}:${variable.low}:${variable.base}:${variable.high}`)
    .join('|'),
)

watch(
  variables,
  (list) => {
    if (!metricVariableId.value && list.length > 0) metricVariableId.value = list[0]?.id ?? ''
    if (threshold.value === '' && list.length > 0) threshold.value = list[0]?.base ?? ''
  },
  { immediate: true },
)

const {
  data: sensitivity,
  error: sensitivityError,
  status: sensitivityStatus,
  refresh: refreshSensitivity,
} = await useAsyncData(
  `experiment-sensitivity-${spaceId}`,
  async () => {
    if (!workspaceId.value || !runsOptionId.value) return undefined
    if (!metricVariableId.value || threshold.value.trim() === '') return undefined
    return requestFetch<SensitivityResponse>(
      `${basePath.value}/options/${encodeURIComponent(runsOptionId.value)}/sensitivity`,
      {
        query: {
          metric_variable_id: metricVariableId.value,
          direction: criterionDirection.value,
          threshold: threshold.value.trim(),
        },
      },
    )
  },
  {
    watch: [
      workspaceId,
      runsOptionId,
      metricVariableId,
      criterionDirection,
      threshold,
      variableBounds,
      runList,
    ],
  },
)

const readingSensitivity = computed(() => sensitivityStatus.value === 'pending')

const { data: ideaPage } = await useAsyncData(
  `experiment-ideas-${spaceId}`,
  async () => {
    if (!workspaceId.value) return undefined
    return requestFetch<IdeaPageResponse>(
      `/api/workspaces/${encodeURIComponent(workspaceId.value)}/ideas`,
      { query: { limit: 100, offset: 0 } },
    )
  },
  { watch: [workspaceId] },
)

const ideas = computed(() => ideaPage.value?.items ?? [])

const {
  data: experimentDetailList,
  error: experimentsError,
  refresh: refreshExperiments,
} = await useAsyncData(
  `experiment-list-${spaceId}`,
  async () => {
    if (!workspaceId.value) return undefined
    const experiments = await requestFetch<ExperimentResponse[]>(`${basePath.value}/experiments`)
    return await Promise.all(
      experiments.map((experiment) =>
        requestFetch<ExperimentDetailResponse>(
          `/api/experiments/${encodeURIComponent(experiment.id)}`,
        ),
      ),
    )
  },
  { watch: [workspaceId] },
)

const experiments = computed(() => experimentDetailList.value ?? [])

const variablesFormOpen = ref(false)
const editingVariableId = ref('')
const variableFormName = ref('')
const variableFormUnit = ref('')
const variableFormLow = ref('')
const variableFormBase = ref('')
const variableFormHigh = ref('')
const variableFormError = ref<string>()
const variableSaving = ref(false)
const deletingVariableId = ref('')
const variableDeleteError = ref<string>()

const runFormOpen = ref(false)
const runFormLevel = ref<string>('base')
const runFormAssumptions = ref('')
const runFormError = ref<string>()
const runSubmitting = ref(false)
const runValues = ref<Record<string, string>>({})
const deletingRunId = ref('')
const runDeleteError = ref<string>()

const experimentFormOpen = ref(false)
const experimentFormIdeaId = ref('')
const experimentFormOptionId = ref('')
const experimentFormTitle = ref('')
const experimentFormHypothesis = ref('')
const experimentFormSuccessMetric = ref('')
const experimentFormBaseline = ref('')
const experimentFormTarget = ref('')
const experimentFormError = ref<string>()
const experimentSubmitting = ref(false)
const experimentStatusError = ref<string>()
const changingStatusId = ref('')
const outcomeFormId = ref('')
const outcomeMetric = ref('')
const outcomeValue = ref('')
const outcomeUnit = ref('')
const outcomeObservedAt = ref('')
const outcomeComment = ref('')
const outcomeError = ref<string>()
const outcomeSubmitting = ref(false)

const transitions: Record<string, readonly string[]> = {
  proposed: ['running', 'cancelled'],
  running: ['completed', 'cancelled'],
}

function allowedStatuses(status: string): readonly string[] {
  return transitions[status] ?? []
}

function levelLabel(level: string): string {
  return t(`decisionSpaces.experiment.runs.form.levels.${level}`)
}

function statusLabel(status: string): string {
  return t(`decisionSpaces.experiment.experiments.status.${status}`)
}

function actionLabel(status: string): string {
  if (status === 'running') return t('decisionSpaces.experiment.experiments.start')
  if (status === 'completed') return t('decisionSpaces.experiment.experiments.complete')
  return t('decisionSpaces.experiment.experiments.abandon')
}

function actionBusyLabel(status: string): string {
  if (status === 'running') return t('decisionSpaces.experiment.experiments.starting')
  if (status === 'completed') return t('decisionSpaces.experiment.experiments.completing')
  return t('decisionSpaces.experiment.experiments.abandoning')
}

function sensitivityLabel(status: string): string {
  return t(`decisionSpaces.experiment.sensitivity.status.${status}`)
}

function travelLabel(travel: string): string {
  return t(`decisionSpaces.experiment.sensitivity.travel.${travel}`)
}

function variableLabel(variableId: string): string {
  const variable = variables.value.find((entry) => entry.id === variableId)
  return variable === undefined ? variableId : `${variable.name}${variableUnitSuffix(variable)}`
}

function variableUnitSuffix(variable: ScenarioVariableResponse): string {
  return variable.unit === null || variable.unit === undefined ? '' : ` (${variable.unit})`
}

function rangeLabel(variable: ScenarioVariableResponse): string {
  return t('decisionSpaces.experiment.variables.range', { low: variable.low, high: variable.high })
}

function baseLabel(variable: ScenarioVariableResponse): string {
  return t('decisionSpaces.experiment.variables.base', { value: variable.base })
}

function variableEditLabel(): string {
  return t('decisionSpaces.experiment.variables.edit')
}

function parseBound(value: string): number | undefined {
  const trimmed = value.trim()
  if (trimmed === '') return undefined
  const parsed = Number(trimmed)
  return Number.isFinite(parsed) ? parsed : undefined
}

function resetVariableForm(): void {
  variableFormName.value = ''
  variableFormUnit.value = ''
  variableFormLow.value = ''
  variableFormBase.value = ''
  variableFormHigh.value = ''
  variableFormError.value = undefined
}

function toggleVariableForm(): void {
  if (variablesFormOpen.value) {
    variablesFormOpen.value = false
    editingVariableId.value = ''
    resetVariableForm()
    return
  }
  editingVariableId.value = ''
  resetVariableForm()
  variablesFormOpen.value = true
}

function startVariableEdit(variable: ScenarioVariableResponse): void {
  editingVariableId.value = variable.id
  variablesFormOpen.value = true
  variableFormName.value = variable.name
  variableFormUnit.value = variable.unit ?? ''
  variableFormLow.value = variable.low
  variableFormBase.value = variable.base
  variableFormHigh.value = variable.high
  variableFormError.value = undefined
}

async function saveVariable(): Promise<void> {
  const name = variableFormName.value.trim()
  if (name === '') {
    variableFormError.value = t('decisionSpaces.experiment.variables.form.nameRequired')
    return
  }
  const low = parseBound(variableFormLow.value)
  const base = parseBound(variableFormBase.value)
  const high = parseBound(variableFormHigh.value)
  if (low === undefined || base === undefined || high === undefined) {
    variableFormError.value = t('decisionSpaces.experiment.variables.form.rangeInvalid')
    return
  }
  if (!(low <= base && base <= high)) {
    variableFormError.value = t('decisionSpaces.experiment.variables.form.rangeInvalid')
    return
  }
  variableSaving.value = true
  variableFormError.value = undefined
  try {
    const body = { name, unit: variableFormUnit.value.trim() || null, low, base, high }
    if (editingVariableId.value === '') {
      await $fetch(`${basePath.value}/scenario-variables`, { method: 'POST', body })
    } else {
      await $fetch(
        `${basePath.value}/scenario-variables/${encodeURIComponent(editingVariableId.value)}`,
        { method: 'PATCH', body },
      )
    }
    variablesFormOpen.value = false
    editingVariableId.value = ''
    resetVariableForm()
    await refreshVariables()
  } catch {
    variableFormError.value = t('decisionSpaces.experiment.variables.form.failed')
  } finally {
    variableSaving.value = false
  }
}

async function removeVariable(variable: ScenarioVariableResponse): Promise<void> {
  deletingVariableId.value = variable.id
  variableDeleteError.value = undefined
  try {
    await $fetch(`${basePath.value}/scenario-variables/${encodeURIComponent(variable.id)}`, {
      method: 'DELETE',
    })
    await refreshVariables()
  } catch {
    variableDeleteError.value = t('decisionSpaces.experiment.variables.deleteFailed')
  } finally {
    deletingVariableId.value = ''
  }
}

function toggleRunForm(): void {
  runFormOpen.value = !runFormOpen.value
  runFormError.value = undefined
  runFormLevel.value = 'base'
  runFormAssumptions.value = ''
  runValues.value = {}
}

async function saveRun(): Promise<void> {
  const assumptions = runFormAssumptions.value.trim()
  if (assumptions === '') {
    runFormError.value = t('decisionSpaces.experiment.runs.form.assumptionsRequired')
    return
  }
  const values: { variable_id: string; value: number }[] = []
  for (const variable of variables.value) {
    const raw = runValues.value[variable.id]?.trim() ?? ''
    if (raw === '') continue
    const parsed = Number(raw)
    if (!Number.isFinite(parsed)) {
      runFormError.value = t('decisionSpaces.experiment.runs.form.failed')
      return
    }
    values.push({ variable_id: variable.id, value: parsed })
  }
  runSubmitting.value = true
  runFormError.value = undefined
  try {
    await $fetch(
      `${basePath.value}/options/${encodeURIComponent(runsOptionId.value)}/scenario-runs`,
      {
        method: 'POST',
        body: { level: runFormLevel.value, assumptions, values },
      },
    )
    runFormOpen.value = false
    runFormAssumptions.value = ''
    runValues.value = {}
    await refreshRuns()
  } catch {
    runFormError.value = t('decisionSpaces.experiment.runs.form.failed')
  } finally {
    runSubmitting.value = false
  }
}

async function removeRun(run: ScenarioRunResponse): Promise<void> {
  deletingRunId.value = run.id
  runDeleteError.value = undefined
  try {
    await $fetch(
      `${basePath.value}/options/${encodeURIComponent(runsOptionId.value)}/scenario-runs/${encodeURIComponent(run.id)}`,
      { method: 'DELETE' },
    )
    await refreshRuns()
  } catch {
    runDeleteError.value = t('decisionSpaces.experiment.runs.removeFailed')
  } finally {
    deletingRunId.value = ''
  }
}

function toggleExperimentForm(): void {
  experimentFormOpen.value = !experimentFormOpen.value
  experimentFormError.value = undefined
  experimentFormTitle.value = ''
  experimentFormHypothesis.value = ''
  experimentFormSuccessMetric.value = ''
  experimentFormBaseline.value = ''
  experimentFormTarget.value = ''
  experimentFormOptionId.value = ''
  experimentFormIdeaId.value = ideas.value[0]?.id ?? ''
}

async function createExperiment(): Promise<void> {
  if (experimentFormIdeaId.value === '') {
    experimentFormError.value = t('decisionSpaces.experiment.experiments.initiativeRequired')
    return
  }
  const title = experimentFormTitle.value.trim()
  if (title === '') {
    experimentFormError.value = t('decisionSpaces.experiment.experiments.form.titleRequired')
    return
  }
  const hypothesis = experimentFormHypothesis.value.trim()
  if (hypothesis === '') {
    experimentFormError.value = t('decisionSpaces.experiment.experiments.form.hypothesisRequired')
    return
  }
  const successMetric = experimentFormSuccessMetric.value.trim()
  if (successMetric === '') {
    experimentFormError.value = t(
      'decisionSpaces.experiment.experiments.form.successMetricRequired',
    )
    return
  }
  experimentSubmitting.value = true
  experimentFormError.value = undefined
  try {
    await $fetch(`${basePath.value}/experiments`, {
      method: 'POST',
      body: {
        idea_id: experimentFormIdeaId.value,
        option_id: experimentFormOptionId.value || null,
        title,
        hypothesis,
        success_metric: successMetric,
        baseline: experimentFormBaseline.value.trim() || null,
        target: experimentFormTarget.value.trim() || null,
      },
    })
    experimentFormOpen.value = false
    await refreshExperiments()
  } catch (error) {
    experimentFormError.value =
      (error as { statusCode?: number })?.statusCode === 403
        ? t('decisionSpaces.experiment.experiments.form.forbidden')
        : t('decisionSpaces.experiment.experiments.form.failed')
  } finally {
    experimentSubmitting.value = false
  }
}

async function changeStatus(experiment: ExperimentResponse, status: string): Promise<void> {
  changingStatusId.value = `${experiment.id}:${status}`
  experimentStatusError.value = undefined
  try {
    await $fetch(`/api/experiments/${encodeURIComponent(experiment.id)}/status`, {
      method: 'POST',
      body: { status },
    })
    await refreshExperiments()
  } catch (error) {
    experimentStatusError.value =
      (error as { statusCode?: number })?.statusCode === 403
        ? t('decisionSpaces.experiment.experiments.form.forbidden')
        : t('decisionSpaces.experiment.experiments.statusFailed')
  } finally {
    changingStatusId.value = ''
  }
}

function toggleOutcomeForm(experiment: ExperimentResponse): void {
  outcomeFormId.value = outcomeFormId.value === experiment.id ? '' : experiment.id
  outcomeMetric.value = experiment.success_metric
  outcomeValue.value = ''
  outcomeUnit.value = ''
  outcomeObservedAt.value = ''
  outcomeComment.value = ''
  outcomeError.value = undefined
}

async function saveOutcome(experiment: ExperimentResponse): Promise<void> {
  const metric = outcomeMetric.value.trim()
  if (metric === '') {
    outcomeError.value = t('decisionSpaces.experiment.experiments.outcome.metricRequired')
    return
  }
  const value = outcomeValue.value.trim()
  if (value === '') {
    outcomeError.value = t('decisionSpaces.experiment.experiments.outcome.valueRequired')
    return
  }
  outcomeSubmitting.value = true
  outcomeError.value = undefined
  try {
    await $fetch(`/api/experiments/${encodeURIComponent(experiment.id)}/outcomes`, {
      method: 'POST',
      body: {
        metric,
        value,
        unit: outcomeUnit.value.trim() || null,
        observed_at: outcomeObservedAt.value || null,
        comment: outcomeComment.value.trim() || null,
      },
    })
    outcomeFormId.value = ''
    await refreshExperiments()
  } catch (error) {
    outcomeError.value =
      (error as { statusCode?: number })?.statusCode === 403
        ? t('decisionSpaces.experiment.experiments.form.forbidden')
        : t('decisionSpaces.experiment.experiments.outcome.failed')
  } finally {
    outcomeSubmitting.value = false
  }
}

useSeoMeta({ title: () => t('decisionSpaces.section.experiment.title') })
</script>

<template>
  <section class="experiment">
    <h2>{{ t('decisionSpaces.section.experiment.title') }}</h2>
    <p class="experiment-intro">{{ t('decisionSpaces.section.experiment.body') }}</p>

    <p
      v-if="optionsError || variablesError || runsError || experimentsError"
      class="experiment-error"
      role="alert"
    >
      {{ t('decisionSpaces.experiment.loadFailed') }}
    </p>

    <div v-else-if="!hasOptions" class="experiment-empty-state">
      <h3>{{ t('decisionSpaces.experiment.empty.title') }}</h3>
      <p>{{ t('decisionSpaces.experiment.empty.body') }}</p>
    </div>

    <template v-else>
      <div class="experiment-block">
        <div class="experiment-block-head">
          <h3>{{ t('decisionSpaces.experiment.variables.title') }}</h3>
          <button
            type="button"
            class="experiment-toggle"
            :aria-expanded="variablesFormOpen"
            @click="toggleVariableForm"
          >
            <span aria-hidden="true" v-text="glyphs.plus" />
            {{ t('decisionSpaces.experiment.variables.create') }}
          </button>
        </div>
        <p class="experiment-hint">{{ t('decisionSpaces.experiment.variables.intro') }}</p>

        <form v-if="variablesFormOpen" class="experiment-form" @submit.prevent="saveVariable">
          <h4>
            {{
              editingVariableId === ''
                ? t('decisionSpaces.experiment.variables.form.createTitle')
                : t('decisionSpaces.experiment.variables.form.editTitle')
            }}
          </h4>
          <label>
            <span>{{ t('decisionSpaces.experiment.variables.form.name') }}</span>
            <input
              v-model="variableFormName"
              type="text"
              :placeholder="t('decisionSpaces.experiment.variables.form.namePlaceholder')"
            >
          </label>
          <label>
            <span>{{ t('decisionSpaces.experiment.variables.form.unit') }}</span>
            <input
              v-model="variableFormUnit"
              type="text"
              :placeholder="t('decisionSpaces.experiment.variables.form.unitPlaceholder')"
            >
          </label>
          <label>
            <span>{{ t('decisionSpaces.experiment.variables.form.low') }}</span>
            <input v-model="variableFormLow" type="text" inputmode="decimal">
          </label>
          <label>
            <span>{{ t('decisionSpaces.experiment.variables.form.base') }}</span>
            <input v-model="variableFormBase" type="text" inputmode="decimal">
          </label>
          <label>
            <span>{{ t('decisionSpaces.experiment.variables.form.high') }}</span>
            <input v-model="variableFormHigh" type="text" inputmode="decimal">
          </label>
          <small class="experiment-field-hint">
            {{ t('decisionSpaces.experiment.variables.form.rangeHint') }}
          </small>
          <p v-if="variableFormError" class="experiment-form-error" role="alert">
            {{ variableFormError }}
          </p>
          <div class="experiment-form-actions">
            <button type="submit" :disabled="variableSaving">
              {{
                variableSaving
                  ? t('decisionSpaces.experiment.variables.form.saving')
                  : editingVariableId === ''
                    ? t('decisionSpaces.experiment.variables.form.submit')
                    : t('decisionSpaces.experiment.variables.form.save')
              }}
            </button>
            <button type="button" class="experiment-secondary" @click="toggleVariableForm">
              {{ t('decisionSpaces.cancel') }}
            </button>
          </div>
        </form>

        <p v-if="variableDeleteError" class="experiment-form-error" role="alert">
          {{ variableDeleteError }}
        </p>

        <ul v-if="variables.length > 0" class="variable-list">
          <li v-for="variable in variables" :key="variable.id" class="variable">
            <div class="variable-head">
              <h4>{{ variableLabel(variable.id) }}</h4>
            </div>
            <p class="variable-range">{{ rangeLabel(variable) }}</p>
            <p class="variable-base">{{ baseLabel(variable) }}</p>
            <div class="variable-actions">
              <button type="button" class="experiment-secondary" @click="startVariableEdit(variable)">
                {{ variableEditLabel() }}
              </button>
              <button
                type="button"
                class="experiment-secondary"
                :disabled="deletingVariableId === variable.id"
                @click="removeVariable(variable)"
              >
                {{
                  deletingVariableId === variable.id
                    ? t('decisionSpaces.experiment.variables.deleting')
                    : t('decisionSpaces.experiment.variables.delete')
                }}
              </button>
            </div>
          </li>
        </ul>
        <p v-else class="experiment-empty">{{ t('decisionSpaces.experiment.variables.empty') }}</p>
      </div>

      <div class="experiment-block">
        <div class="experiment-block-head">
          <h3>{{ t('decisionSpaces.experiment.runs.title') }}</h3>
          <button
            type="button"
            class="experiment-toggle"
            :aria-expanded="runFormOpen"
            @click="toggleRunForm"
          >
            <span aria-hidden="true" v-text="glyphs.plus" />
            {{ t('decisionSpaces.experiment.runs.create') }}
          </button>
        </div>
        <p class="experiment-hint">{{ t('decisionSpaces.experiment.runs.intro') }}</p>

        <label class="experiment-choice-field">
          <span>{{ t('decisionSpaces.experiment.runs.option') }}</span>
          <select v-model="runsOptionId">
            <option v-for="option in options" :key="option.id" :value="option.id">
              {{ option.title }}
            </option>
          </select>
        </label>

        <form v-if="runFormOpen" class="experiment-form" @submit.prevent="saveRun">
          <h4>{{ t('decisionSpaces.experiment.runs.form.title') }}</h4>
          <label>
            <span>{{ t('decisionSpaces.experiment.runs.form.level') }}</span>
            <select v-model="runFormLevel">
              <option v-for="level in levels" :key="level" :value="level">
                {{ levelLabel(level) }}
              </option>
            </select>
          </label>
          <label>
            <span>{{ t('decisionSpaces.experiment.runs.form.assumptions') }}</span>
            <textarea
              v-model="runFormAssumptions"
              rows="3"
              :placeholder="t('decisionSpaces.experiment.runs.form.assumptionsPlaceholder')"
            />
          </label>
          <fieldset v-if="variables.length > 0" class="experiment-values">
            <legend>{{ t('decisionSpaces.experiment.runs.form.values') }}</legend>
            <label v-for="variable in variables" :key="variable.id">
              <span>{{ variableLabel(variable.id) }}</span>
              <input v-model="runValues[variable.id]" type="text" inputmode="decimal" >
            </label>
            <small class="experiment-field-hint">
              {{ t('decisionSpaces.experiment.runs.form.valuesHint') }}
            </small>
          </fieldset>
          <p v-if="runFormError" class="experiment-form-error" role="alert">{{ runFormError }}</p>
          <div class="experiment-form-actions">
            <button type="submit" :disabled="runSubmitting">
              {{
                runSubmitting
                  ? t('decisionSpaces.experiment.runs.form.submitting')
                  : t('decisionSpaces.experiment.runs.form.submit')
              }}
            </button>
            <button type="button" class="experiment-secondary" @click="toggleRunForm">
              {{ t('decisionSpaces.cancel') }}
            </button>
          </div>
        </form>

        <p v-if="runDeleteError" class="experiment-form-error" role="alert">{{ runDeleteError }}</p>

        <ul v-if="runs.length > 0" class="run-list">
          <li v-for="run in runs" :key="run.id" class="run">
            <div class="run-head">
              <h4>{{ levelLabel(run.level) }}</h4>
            </div>
            <p class="run-assumptions">{{ run.assumptions }}</p>
            <dl v-if="run.values.length > 0" class="run-values">
              <div v-for="entry in run.values" :key="entry.variable_id">
                <dt>{{ variableLabel(entry.variable_id) }}</dt>
                <dd>{{ entry.value }}</dd>
              </div>
            </dl>
            <div class="run-actions">
              <button
                type="button"
                class="experiment-secondary"
                :disabled="deletingRunId === run.id"
                @click="removeRun(run)"
              >
                {{
                  deletingRunId === run.id
                    ? t('decisionSpaces.experiment.runs.removing')
                    : t('decisionSpaces.experiment.runs.remove')
                }}
              </button>
            </div>
          </li>
        </ul>
        <p v-else class="experiment-empty">{{ t('decisionSpaces.experiment.runs.empty') }}</p>
      </div>

      <div class="experiment-block">
        <div class="experiment-block-head">
          <h3>{{ t('decisionSpaces.experiment.sensitivity.title') }}</h3>
        </div>
        <p class="experiment-hint">{{ t('decisionSpaces.experiment.sensitivity.intro') }}</p>

        <div class="experiment-sensitivity-criteria">
          <label>
            <span>{{ t('decisionSpaces.experiment.sensitivity.metric') }}</span>
            <select v-model="metricVariableId">
              <option v-for="variable in variables" :key="variable.id" :value="variable.id">
                {{ variableLabel(variable.id) }}
              </option>
            </select>
          </label>
          <label>
            <span>{{ t('decisionSpaces.experiment.sensitivity.direction') }}</span>
            <select v-model="criterionDirection">
              <option v-for="direction in directions" :key="direction" :value="direction">
                {{ t(`decisionSpaces.experiment.sensitivity.directions.${direction}`) }}
              </option>
            </select>
          </label>
          <label>
            <span>{{ t('decisionSpaces.experiment.sensitivity.threshold') }}</span>
            <input v-model="threshold" type="text" inputmode="decimal">
          </label>
          <div class="experiment-form-actions">
            <button type="button" :disabled="readingSensitivity" @click="refreshSensitivity()">
              {{
                readingSensitivity
                  ? t('decisionSpaces.experiment.sensitivity.reading')
                  : t('decisionSpaces.experiment.sensitivity.read')
              }}
            </button>
          </div>
        </div>

        <p v-if="runs.length === 0" class="experiment-empty">
          {{ t('decisionSpaces.experiment.sensitivity.empty') }}
        </p>
        <p v-else-if="sensitivityError" class="experiment-form-error" role="alert">
          {{ t('decisionSpaces.experiment.sensitivity.failed') }}
        </p>
        <template v-else-if="sensitivity">
          <ul class="sensitivity-list">
            <li
              v-for="entry in sensitivity.ranked"
              :key="entry.variable_id"
              class="sensitivity"
            >
              <div class="sensitivity-head">
                <h4>{{ variableLabel(entry.variable_id) }}</h4>
                <span class="sensitivity-status">{{ sensitivityLabel(entry.status) }}</span>
              </div>
              <p v-if="entry.crossing" class="sensitivity-crossing">
                {{
                  t('decisionSpaces.experiment.sensitivity.crossing', {
                    value: entry.crossing,
                  })
                }}
              </p>
              <p v-if="entry.interval" class="sensitivity-interval">
                {{
                  t('decisionSpaces.experiment.sensitivity.interval', {
                    low: entry.interval[0],
                    high: entry.interval[1],
                  })
                }}
              </p>
              <p v-if="entry.slope_min && entry.slope_max" class="sensitivity-slopes">
                {{
                  t('decisionSpaces.experiment.sensitivity.slopes', {
                    min: entry.slope_min,
                    max: entry.slope_max,
                  })
                }}
              </p>
              <p v-if="entry.travel" class="sensitivity-travel">
                {{ travelLabel(entry.travel) }}
              </p>
              <p v-if="entry.crossings > 0" class="sensitivity-crossings">
                {{
                  t('decisionSpaces.experiment.sensitivity.crossings', {
                    count: entry.crossings,
                  })
                }}
              </p>
            </li>
          </ul>
          <p class="sensitivity-evidence">
            {{
              t('decisionSpaces.experiment.sensitivity.evidence', {
                pour: sensitivity.evidence.for_count,
                contre: sensitivity.evidence.against_count,
              })
            }}
          </p>
          <p v-if="sensitivity.incomplete_run_ids.length > 0" class="sensitivity-incomplete">
            {{
              t('decisionSpaces.experiment.sensitivity.incomplete', {
                count: sensitivity.incomplete_run_ids.length,
              })
            }}
          </p>
          <p class="experiment-hint">{{ t('decisionSpaces.experiment.sensitivity.noVerdict') }}</p>
        </template>
      </div>

      <div class="experiment-block">
        <div class="experiment-block-head">
          <h3>{{ t('decisionSpaces.experiment.experiments.list') }}</h3>
          <button
            type="button"
            class="experiment-toggle"
            :aria-expanded="experimentFormOpen"
            @click="toggleExperimentForm"
          >
            <span aria-hidden="true" v-text="glyphs.plus" />
            {{ t('decisionSpaces.experiment.experiments.create') }}
          </button>
        </div>
        <p class="experiment-hint">{{ t('decisionSpaces.experiment.experiments.intro') }}</p>

        <form v-if="experimentFormOpen" class="experiment-form" @submit.prevent="createExperiment">
          <h4>{{ t('decisionSpaces.experiment.experiments.form.title') }}</h4>
          <label>
            <span>{{ t('decisionSpaces.experiment.experiments.initiative') }}</span>
            <select v-model="experimentFormIdeaId">
              <option v-for="idea in ideas" :key="idea.id" :value="idea.id">
                {{ idea.title }}
              </option>
            </select>
          </label>
          <small class="experiment-field-hint">
            {{ t('decisionSpaces.experiment.experiments.initiativeHint') }}
          </small>
          <label>
            <span>{{ t('decisionSpaces.experiment.experiments.option') }}</span>
            <select v-model="experimentFormOptionId">
              <option value="">{{ t('decisionSpaces.experiment.experiments.optionNone') }}</option>
              <option v-for="option in options" :key="option.id" :value="option.id">
                {{ option.title }}
              </option>
            </select>
          </label>
          <label>
            <span>{{ t('decisionSpaces.experiment.experiments.form.titleLabel') }}</span>
            <input
              v-model="experimentFormTitle"
              type="text"
              :placeholder="t('decisionSpaces.experiment.experiments.form.titlePlaceholder')"
            >
          </label>
          <label>
            <span>{{ t('decisionSpaces.experiment.experiments.form.hypothesis') }}</span>
            <textarea v-model="experimentFormHypothesis" rows="3" />
          </label>
          <label>
            <span>{{ t('decisionSpaces.experiment.experiments.form.successMetric') }}</span>
            <input v-model="experimentFormSuccessMetric" type="text" >
          </label>
          <label>
            <span>{{ t('decisionSpaces.experiment.experiments.form.baseline') }}</span>
            <input v-model="experimentFormBaseline" type="text" >
          </label>
          <label>
            <span>{{ t('decisionSpaces.experiment.experiments.form.target') }}</span>
            <input v-model="experimentFormTarget" type="text" >
          </label>
          <p v-if="experimentFormError" class="experiment-form-error" role="alert">
            {{ experimentFormError }}
          </p>
          <div class="experiment-form-actions">
            <button type="submit" :disabled="experimentSubmitting">
              {{
                experimentSubmitting
                  ? t('decisionSpaces.experiment.experiments.form.submitting')
                  : t('decisionSpaces.experiment.experiments.form.submit')
              }}
            </button>
            <button type="button" class="experiment-secondary" @click="toggleExperimentForm">
              {{ t('decisionSpaces.cancel') }}
            </button>
          </div>
        </form>

        <p v-if="experimentStatusError" class="experiment-form-error" role="alert">
          {{ experimentStatusError }}
        </p>

        <ul v-if="experiments.length > 0" class="experiment-list">
          <li v-for="detail in experiments" :key="detail.experiment.id" class="tracked">
            <div class="tracked-head">
              <h4>{{ detail.experiment.title }}</h4>
              <span class="tracked-status">{{ statusLabel(detail.experiment.status) }}</span>
            </div>
            <dl class="tracked-fields">
              <div>
                <dt>{{ t('decisionSpaces.experiment.experiments.fields.hypothesis') }}</dt>
                <dd>{{ detail.experiment.hypothesis }}</dd>
              </div>
              <div>
                <dt>{{ t('decisionSpaces.experiment.experiments.fields.metric') }}</dt>
                <dd>{{ detail.experiment.success_metric }}</dd>
              </div>
              <div>
                <dt>{{ t('decisionSpaces.experiment.experiments.fields.baseline') }}</dt>
                <dd>{{ detail.experiment.baseline || t('decisionSpaces.experiment.experiments.optionNone') }}</dd>
              </div>
              <div>
                <dt>{{ t('decisionSpaces.experiment.experiments.expected') }}</dt>
                <dd>{{ detail.experiment.target || t('decisionSpaces.experiment.experiments.optionNone') }}</dd>
              </div>
            </dl>

            <div class="tracked-observed">
              <h5>{{ t('decisionSpaces.experiment.experiments.observed') }}</h5>
              <ul v-if="detail.outcomes.length > 0" class="outcome-list">
                <li v-for="outcome in detail.outcomes" :key="outcome.id" class="outcome">
                  <span class="outcome-value">{{ outcome.value }}</span>
                  <span class="outcome-unit">{{ outcome.unit || '' }}</span>
                  <span class="outcome-metric">{{ outcome.metric }}</span>
                  <p v-if="outcome.comment" class="outcome-comment">{{ outcome.comment }}</p>
                </li>
              </ul>
              <p v-else class="experiment-empty">
                {{ t('decisionSpaces.experiment.experiments.noOutcome') }}
              </p>
            </div>

            <div v-if="detail.learning" class="tracked-learning">
              <h5>{{ t('decisionSpaces.experiment.experiments.learning') }}</h5>
              <p class="learning-text">{{ detail.learning.text }}</p>
              <small class="experiment-field-hint">
                {{ t('decisionSpaces.experiment.experiments.learningHint') }}
              </small>
            </div>

            <div class="tracked-actions">
              <button
                v-for="target in allowedStatuses(detail.experiment.status)"
                :key="target"
                type="button"
                class="experiment-secondary"
                :disabled="changingStatusId === `${detail.experiment.id}:${target}`"
                @click="changeStatus(detail.experiment, target)"
              >
                {{
                  changingStatusId === `${detail.experiment.id}:${target}`
                    ? actionBusyLabel(target)
                    : actionLabel(target)
                }}
              </button>
              <button
                type="button"
                class="experiment-secondary"
                @click="toggleOutcomeForm(detail.experiment)"
              >
                {{ t('decisionSpaces.experiment.experiments.recordOutcome') }}
              </button>
            </div>

            <form
              v-if="outcomeFormId === detail.experiment.id"
              class="experiment-form"
              @submit.prevent="saveOutcome(detail.experiment)"
            >
              <h4>{{ t('decisionSpaces.experiment.experiments.outcome.title') }}</h4>
              <label>
                <span>{{ t('decisionSpaces.experiment.experiments.outcome.metric') }}</span>
                <input v-model="outcomeMetric" type="text" >
              </label>
              <label>
                <span>{{ t('decisionSpaces.experiment.experiments.outcome.value') }}</span>
                <input v-model="outcomeValue" type="text" >
              </label>
              <label>
                <span>{{ t('decisionSpaces.experiment.experiments.outcome.unit') }}</span>
                <input v-model="outcomeUnit" type="text" >
              </label>
              <label>
                <span>{{ t('decisionSpaces.experiment.experiments.outcome.observedAt') }}</span>
                <input v-model="outcomeObservedAt" type="date" >
              </label>
              <label>
                <span>{{ t('decisionSpaces.experiment.experiments.outcome.comment') }}</span>
                <textarea v-model="outcomeComment" rows="2" />
              </label>
              <p v-if="outcomeError" class="experiment-form-error" role="alert">{{ outcomeError }}</p>
              <div class="experiment-form-actions">
                <button type="submit" :disabled="outcomeSubmitting">
                  {{
                    outcomeSubmitting
                      ? t('decisionSpaces.experiment.experiments.outcome.submitting')
                      : t('decisionSpaces.experiment.experiments.outcome.submit')
                  }}
                </button>
                <button
                  type="button"
                  class="experiment-secondary"
                  @click="toggleOutcomeForm(detail.experiment)"
                >
                  {{ t('decisionSpaces.cancel') }}
                </button>
              </div>
            </form>
          </li>
        </ul>
        <p v-else class="experiment-empty">
          {{ t('decisionSpaces.experiment.experiments.empty') }}
        </p>
      </div>
    </template>
  </section>
</template>

<style scoped>
.experiment {
  display: grid;
  max-width: 76ch;
  gap: 8px;
}

.experiment h2 {
  color: var(--kollio-heading);
  font-size: var(--kollio-text-title);
  font-weight: var(--kollio-weight-display);
}

.experiment-intro,
.experiment-hint,
.experiment-field-hint {
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-small);
  line-height: var(--kollio-leading-body);
}

.experiment-field-hint {
  font-size: var(--kollio-text-caption);
}

.experiment-error,
.experiment-form-error {
  margin-top: 10px;
  color: var(--ui-error);
  font-size: var(--kollio-text-caption);
  font-weight: var(--kollio-weight-strong);
}

.experiment-empty-state {
  margin-top: 24px;
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-md);
  background: var(--ui-bg-elevated);
  padding: 20px;
}

.experiment-empty-state h3 {
  color: var(--kollio-heading);
  font-size: var(--kollio-text-lead);
  font-weight: var(--kollio-weight-strong);
}

.experiment-block {
  margin-top: 26px;
  border-top: 1px solid var(--ui-border);
  padding-top: 18px;
}

.experiment-block-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.experiment-block h3 {
  color: var(--kollio-heading);
  font-size: var(--kollio-text-lead);
  font-weight: var(--kollio-weight-strong);
}

.experiment-toggle,
.experiment-form button {
  display: inline-flex;
  min-height: 44px;
  align-items: center;
  gap: 8px;
  border-radius: var(--kollio-radius-md);
  background: var(--kollio-heading);
  padding: 0 20px;
  color: var(--ui-bg-elevated);
  font-size: var(--kollio-text-caption);
  font-weight: var(--kollio-weight-strong);
}

.experiment-toggle[aria-expanded='true'] {
  background: var(--ui-bg-accented);
  color: var(--kollio-active-ink);
}

.experiment-secondary {
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

.experiment-secondary:hover {
  border-color: var(--kollio-active-ink);
  color: var(--kollio-active-ink);
}

.experiment-form {
  display: grid;
  gap: 14px;
  margin-top: 16px;
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-md);
  background: var(--ui-bg-elevated);
  padding: 18px;
}

.experiment-form h4 {
  color: var(--kollio-heading);
  font-size: var(--kollio-text-body);
  font-weight: var(--kollio-weight-strong);
}

.experiment-form label,
.experiment-choice-field,
.experiment-sensitivity-criteria label {
  display: grid;
  gap: 6px;
}

.experiment-choice-field {
  margin-top: 14px;
}

.experiment-form label > span,
.experiment-choice-field > span,
.experiment-sensitivity-criteria label > span {
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-micro);
  font-weight: var(--kollio-weight-strong);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.experiment-form input,
.experiment-form textarea,
.experiment-form select,
.experiment-choice-field select,
.experiment-sensitivity-criteria select,
.experiment-sensitivity-criteria input {
  min-height: 44px;
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-md);
  background: var(--ui-bg);
  padding: 10px 12px;
  color: var(--kollio-heading);
  font-size: var(--kollio-text-small);
}

.experiment-form textarea {
  min-height: 96px;
  resize: vertical;
}

.experiment-form input:focus-visible,
.experiment-form textarea:focus-visible,
.experiment-form select:focus-visible,
.experiment-choice-field select:focus-visible,
.experiment-sensitivity-criteria select:focus-visible,
.experiment-sensitivity-criteria input:focus-visible,
.experiment-secondary:focus-visible,
.experiment-toggle:focus-visible {
  outline: 2px solid var(--kollio-active-ink);
  outline-offset: 1px;
}

.experiment-values {
  display: grid;
  gap: 10px;
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-md);
  padding: 12px 14px;
}

.experiment-values legend {
  padding: 0 6px;
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-micro);
  font-weight: var(--kollio-weight-strong);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.experiment-form-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.variable-list,
.run-list,
.sensitivity-list,
.experiment-list,
.outcome-list {
  display: grid;
  gap: 12px;
  margin-top: 16px;
  list-style: none;
}

.variable,
.run,
.sensitivity,
.tracked,
.outcome {
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-md);
  background: var(--ui-bg-elevated);
  padding: 16px;
}

.variable-head,
.run-head,
.sensitivity-head,
.tracked-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.variable h4,
.run h4,
.sensitivity h4,
.tracked h4,
.tracked h5 {
  color: var(--kollio-heading);
  font-size: var(--kollio-text-body);
  font-weight: var(--kollio-weight-strong);
}

.variable-range,
.variable-base,
.run-assumptions,
.sensitivity-crossing,
.sensitivity-interval,
.sensitivity-slopes,
.sensitivity-travel,
.sensitivity-crossings,
.sensitivity-evidence,
.sensitivity-incomplete,
.learning-text {
  margin-top: 6px;
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-small);
}

.variable-actions,
.run-actions,
.tracked-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 12px;
}

.experiment-empty {
  margin-top: 16px;
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-small);
}

.sensitivity-status,
.tracked-status {
  flex: none;
  border-radius: var(--kollio-radius-pill);
  background: var(--kollio-active-wash);
  padding: 5px 12px;
  color: var(--kollio-active-ink);
  font-size: var(--kollio-text-micro);
  font-weight: var(--kollio-weight-strong);
}

.experiment-sensitivity-criteria {
  display: grid;
  gap: 14px;
  margin-top: 16px;
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-md);
  background: var(--ui-bg-elevated);
  padding: 18px;
}

.run-values,
.tracked-fields {
  display: grid;
  gap: 6px;
  margin-top: 10px;
}

.run-values div,
.tracked-fields div {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.run-values dt,
.tracked-fields dt {
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-caption);
  font-weight: var(--kollio-weight-strong);
}

.run-values dd,
.tracked-fields dd {
  color: var(--kollio-heading);
  font-size: var(--kollio-text-small);
}

.tracked-observed,
.tracked-learning {
  margin-top: 16px;
}

.tracked-observed h5,
.tracked-learning h5 {
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-micro);
  font-weight: var(--kollio-weight-strong);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.outcome-list {
  margin-top: 10px;
}

.outcome {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 8px;
  padding: 10px 12px;
}

.outcome-value {
  color: var(--kollio-heading);
  font-size: var(--kollio-text-lead);
  font-weight: var(--kollio-weight-display);
}

.outcome-unit,
.outcome-metric {
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-small);
}

.outcome-comment {
  flex-basis: 100%;
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-caption);
}

button[disabled] {
  opacity: 0.6;
}

@media (max-width: 760px) {
  .experiment-block-head {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
