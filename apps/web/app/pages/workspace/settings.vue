<script setup lang="ts">
import type {
  CompanyContextResponse,
  CompanyProfileResponse,
  CompanyConstraintResponse,
  CompanyConstraintUpdate,
  MetricResponse,
  MetricUpdate,
  ObjectiveResponse,
  ObjectiveUpdate,
  PrincipleResponse,
  PrincipleUpdate,
  WorkspaceResponse,
} from '@kollio/api-client'

definePageMeta({ layout: 'workspace', middleware: 'authenticated' })

const { t } = useI18n()
const route = useRoute()
const requestFetch = useRequestFetch()

const { data: workspaces } = await useAsyncData('settings-workspaces', () =>
  requestFetch<WorkspaceResponse[]>('/api/workspaces'),
)
const activeWorkspace = computed(() => {
  const requested = typeof route.query.workspace === 'string' ? route.query.workspace : undefined
  return workspaces.value?.find(workspace => workspace.id === requested) ?? workspaces.value?.[0]
})

const { data: context, error: loadFailure } = await useAsyncData(
  'settings-company-context',
  async () => {
    if (!activeWorkspace.value) return undefined
    return requestFetch<CompanyContextResponse>(
      `/api/workspaces/${encodeURIComponent(activeWorkspace.value.id)}/company-context`,
    )
  },
  { watch: [activeWorkspace] },
)

const profileForm = reactive({
  name: '',
  description: '',
  business_model: '',
  products_services: '',
  customer_segments: '',
  markets: '',
  structure: '',
})
const savingProfile = ref(false)
const profileSaved = ref(false)
const actionError = ref(false)
const objectiveTitle = ref('')
const constraintTitle = ref('')
const constraintDetail = ref('')
const principleTitle = ref('')
const principleDetail = ref('')
const metricName = ref('')
const metricValue = ref('')
const metricUnit = ref('')
const metricSource = ref('')

const wizard = reactive({
  name: '',
  description: '',
  business_model: '',
  products_services: '',
  markets: '',
  customer_segments: '',
  objectives: ['', '', ''] as string[],
  constraints: ['', '', ''] as string[],
  principles: ['', '', ''] as string[],
  metrics: ['', '', ''] as string[],
})
const wizardSaving = ref(false)
const wizardSaved = ref(false)

function fillThree(target: string[], values: string[]) {
  for (let index = 0; index < 3; index += 1) {
    target[index] = values[index] ?? ''
  }
}

watch(context, (value) => {
  if (!value || wizardSaving.value) return
  profileForm.name = value.profile.name ?? ''
  profileForm.description = value.profile.description ?? ''
  profileForm.business_model = value.profile.business_model ?? ''
  profileForm.products_services = value.profile.products_services ?? ''
  profileForm.customer_segments = value.profile.customer_segments ?? ''
  profileForm.markets = value.profile.markets ?? ''
  profileForm.structure = value.profile.structure ?? ''
  wizard.name = value.profile.name ?? ''
  wizard.description = value.profile.description ?? ''
  wizard.business_model = value.profile.business_model ?? ''
  wizard.products_services = value.profile.products_services ?? ''
  wizard.customer_segments = value.profile.customer_segments ?? ''
  wizard.markets = value.profile.markets ?? ''
  fillThree(wizard.objectives, value.objectives.map(item => item.title))
  fillThree(wizard.constraints, value.constraints.map(item => item.title))
  fillThree(wizard.principles, value.principles.map(item => item.title))
  fillThree(wizard.metrics, value.metrics.map(item => item.name))
}, { immediate: true })

function contextUrl(suffix: string) {
  const workspaceId = activeWorkspace.value?.id
  if (!workspaceId) return undefined
  return `/api/workspaces/${encodeURIComponent(workspaceId)}/company-context${suffix}`
}

async function run(action: () => Promise<void>) {
  actionError.value = false
  try {
    await action()
  }
  catch {
    actionError.value = true
  }
}

function applyProfile(profile: CompanyProfileResponse) {
  const current = context.value
  if (!current) return
  context.value = { ...current, profile }
}

function applyObjective(updated: ObjectiveResponse) {
  const current = context.value
  if (!current) return
  context.value = {
    ...current,
    objectives: current.objectives.map(item => (item.id === updated.id ? updated : item)),
  }
}

function applyConstraint(updated: CompanyConstraintResponse) {
  const current = context.value
  if (!current) return
  context.value = {
    ...current,
    constraints: current.constraints.map(item => (item.id === updated.id ? updated : item)),
  }
}

function replaceObjective(created: ObjectiveResponse) {
  const current = context.value
  if (!current) return
  context.value = { ...current, objectives: [...current.objectives, created] }
}

function replaceConstraint(created: CompanyConstraintResponse) {
  const current = context.value
  if (!current) return
  context.value = { ...current, constraints: [...current.constraints, created] }
}

async function saveProfile() {
  const url = contextUrl('/profile')
  if (!url || savingProfile.value) return
  savingProfile.value = true
  profileSaved.value = false
  await run(async () => {
    const saved = await requestFetch<CompanyProfileResponse>(url, {
      method: 'PUT',
      body: { ...profileForm },
    })
    applyProfile(saved)
    profileSaved.value = true
  })
  savingProfile.value = false
}

async function createObjective() {
  const url = contextUrl('/objectives')
  if (!url || objectiveTitle.value.trim() === '') return
  await run(async () => {
    const created = await requestFetch<ObjectiveResponse>(url, {
      method: 'POST',
      body: { title: objectiveTitle.value.trim() },
    })
    replaceObjective(created)
    objectiveTitle.value = ''
  })
}

async function patchObjective(objective: ObjectiveResponse, patch: ObjectiveUpdate) {
  const workspaceId = activeWorkspace.value?.id
  if (!workspaceId || !context.value) return
  await run(async () => {
    const updated = await requestFetch<ObjectiveResponse>(
      `/api/workspaces/${encodeURIComponent(workspaceId)}/company-context/objectives/${encodeURIComponent(objective.id)}`,
      { method: 'PATCH', body: patch },
    )
    applyObjective(updated)
  })
}

async function createConstraint() {
  const url = contextUrl('/constraints')
  if (!url || constraintTitle.value.trim() === '') return
  await run(async () => {
    const created = await requestFetch<CompanyConstraintResponse>(url, {
      method: 'POST',
      body: { title: constraintTitle.value.trim(), detail: constraintDetail.value.trim() || undefined },
    })
    replaceConstraint(created)
    constraintTitle.value = ''
    constraintDetail.value = ''
  })
}

async function patchConstraint(constraint: CompanyConstraintResponse, patch: CompanyConstraintUpdate) {
  const workspaceId = activeWorkspace.value?.id
  if (!workspaceId || !context.value) return
  await run(async () => {
    const updated = await requestFetch<CompanyConstraintResponse>(
      `/api/workspaces/${encodeURIComponent(workspaceId)}/company-context/constraints/${encodeURIComponent(constraint.id)}`,
      { method: 'PATCH', body: patch },
    )
    applyConstraint(updated)
  })
}

function nextState(state: 'active' | 'archived') {
  return state === 'archived' ? 'active' : 'archived'
}

function nonEmpty(value: string) {
  return value.trim() === '' ? null : value.trim()
}

function editedTitle(event: Event) {
  return (event.target as HTMLInputElement).value.trim()
}

const wizardSteps = ['facts', 'model', 'markets', 'objectives', 'constraints', 'principles', 'metrics'] as const

const wizardAnswered = computed<Record<(typeof wizardSteps)[number], boolean>>(() => {
  const value = context.value
  const profile = value?.profile
  return {
    facts: Boolean(profile?.name || profile?.description),
    model: Boolean(profile?.business_model || profile?.products_services),
    markets: Boolean(profile?.markets || profile?.customer_segments),
    objectives: Boolean(value?.objectives.length),
    constraints: Boolean(value?.constraints.length),
    principles: Boolean(value?.principles.length),
    metrics: Boolean(value?.metrics.length),
  }
})

const wizardAnsweredCount = computed(() => wizardSteps.filter(step => wizardAnswered.value[step]).length)

function stepLabels(step: 'objectives' | 'constraints' | 'principles' | 'metrics') {
  return (['first', 'second', 'third'] as const).map(rank => t(`workspace.settings.onboarding.${step}.${rank}`))
}

function replacePrinciple(created: PrincipleResponse) {
  const current = context.value
  if (!current) return
  context.value = { ...current, principles: [...current.principles, created] }
}

function applyPrinciple(updated: PrincipleResponse) {
  const current = context.value
  if (!current) return
  context.value = {
    ...current,
    principles: current.principles.map(item => (item.id === updated.id ? updated : item)),
  }
}

function replaceMetric(created: MetricResponse) {
  const current = context.value
  if (!current) return
  context.value = { ...current, metrics: [...current.metrics, created] }
}

function applyMetric(updated: MetricResponse) {
  const current = context.value
  if (!current) return
  context.value = {
    ...current,
    metrics: current.metrics.map(item => (item.id === updated.id ? updated : item)),
  }
}

async function createPrinciple() {
  const url = contextUrl('/principles')
  if (!url || principleTitle.value.trim() === '') return
  await run(async () => {
    const created = await requestFetch<PrincipleResponse>(url, {
      method: 'POST',
      body: { title: principleTitle.value.trim(), detail: principleDetail.value.trim() || undefined },
    })
    replacePrinciple(created)
    principleTitle.value = ''
    principleDetail.value = ''
  })
}

async function patchPrinciple(principle: PrincipleResponse, patch: PrincipleUpdate) {
  const workspaceId = activeWorkspace.value?.id
  if (!workspaceId || !context.value) return
  await run(async () => {
    const updated = await requestFetch<PrincipleResponse>(
      `/api/workspaces/${encodeURIComponent(workspaceId)}/company-context/principles/${encodeURIComponent(principle.id)}`,
      { method: 'PATCH', body: patch },
    )
    applyPrinciple(updated)
  })
}

async function createMetric() {
  const url = contextUrl('/metrics')
  if (!url || metricName.value.trim() === '') return
  await run(async () => {
    const created = await requestFetch<MetricResponse>(url, {
      method: 'POST',
      body: {
        name: metricName.value.trim(),
        value: nonEmpty(metricValue.value),
        unit: nonEmpty(metricUnit.value),
        source: nonEmpty(metricSource.value),
      },
    })
    replaceMetric(created)
    metricName.value = ''
    metricValue.value = ''
    metricUnit.value = ''
    metricSource.value = ''
  })
}

async function patchMetric(metric: MetricResponse, patch: MetricUpdate) {
  const workspaceId = activeWorkspace.value?.id
  if (!workspaceId || !context.value) return
  await run(async () => {
    const updated = await requestFetch<MetricResponse>(
      `/api/workspaces/${encodeURIComponent(workspaceId)}/company-context/metrics/${encodeURIComponent(metric.id)}`,
      { method: 'PATCH', body: patch },
    )
    applyMetric(updated)
  })
}

function seedValues(fields: string[]) {
  return [...new Set(fields.map(field => field.trim()).filter(Boolean))]
}

async function seedList(base: string, path: string, key: 'title' | 'name', stored: string[], fields: string[]) {
  const existing = new Set(stored.map(value => value.trim().toLowerCase()))
  for (const value of seedValues(fields)) {
    if (existing.has(value.toLowerCase())) continue
    const created = await requestFetch<ObjectiveResponse & PrincipleResponse & MetricResponse>(
      `${base}${path}`,
      { method: 'POST', body: { [key]: value } },
    )
    if (path === '/objectives') replaceObjective(created)
    else if (path === '/constraints') replaceConstraint(created)
    else if (path === '/principles') replacePrinciple(created)
    else replaceMetric(created)
    existing.add(value.toLowerCase())
  }
}

async function saveWizard() {
  const base = contextUrl('')
  if (!base || wizardSaving.value) return
  // Snapshot the inputs before any await: the context watch refills the wizard arrays
  // from persisted data, which would otherwise clobber the not-yet-saved rows mid-run.
  const profileInput = {
    name: nonEmpty(wizard.name),
    description: nonEmpty(wizard.description),
    business_model: nonEmpty(wizard.business_model),
    products_services: nonEmpty(wizard.products_services),
    customer_segments: nonEmpty(wizard.customer_segments),
    markets: nonEmpty(wizard.markets),
    structure: context.value?.profile.structure ?? null,
  }
  const seed = {
    objectives: wizard.objectives.slice(),
    constraints: wizard.constraints.slice(),
    principles: wizard.principles.slice(),
    metrics: wizard.metrics.slice(),
  }
  const stored = {
    objectives: (context.value?.objectives ?? []).map(item => item.title),
    constraints: (context.value?.constraints ?? []).map(item => item.title),
    principles: (context.value?.principles ?? []).map(item => item.title),
    metrics: (context.value?.metrics ?? []).map(item => item.name),
  }
  wizardSaving.value = true
  wizardSaved.value = false
  await run(async () => {
    const saved = await requestFetch<CompanyProfileResponse>(`${base}/profile`, { method: 'PUT', body: profileInput })
    applyProfile(saved)
    await seedList(base, '/objectives', 'title', stored.objectives, seed.objectives)
    await seedList(base, '/constraints', 'title', stored.constraints, seed.constraints)
    await seedList(base, '/principles', 'title', stored.principles, seed.principles)
    await seedList(base, '/metrics', 'name', stored.metrics, seed.metrics)
    wizardSaved.value = true
  })
  wizardSaving.value = false
}

</script>

<template>
  <div class="settings-shell">
    <header class="settings-header">
      <h1>{{ t('workspace.settings.title') }}</h1>
      <p>{{ t('workspace.settings.description') }}</p>
    </header>

    <p v-if="loadFailure || (workspaces && !activeWorkspace)" role="alert" class="settings-error">
      {{ t('workspace.settings.loadError') }}
    </p>
    <p v-if="actionError" role="alert" class="settings-error">
      {{ t('workspace.settings.error') }}
    </p>

    <template v-if="context">
      <form class="settings-section settings-wizard" @submit.prevent="saveWizard">
        <div class="settings-wizard-head">
          <h2>{{ t('workspace.settings.onboarding.title') }}</h2>
          <span class="settings-note">{{ t('workspace.settings.onboarding.progress', { answered: wizardAnsweredCount, total: 7 }) }}</span>
        </div>
        <p class="settings-note">{{ t('workspace.settings.onboarding.intro') }}</p>

        <fieldset class="settings-step" data-step="facts" :data-answered="String(wizardAnswered.facts)">
          <legend>
            <span>{{ t('workspace.settings.onboarding.steps.facts') }}</span>
            <span v-if="!wizardAnswered.facts" class="settings-pending">{{ t('workspace.settings.onboarding.pending') }}</span>
          </legend>
          <label class="settings-field">
            <span>{{ t('workspace.settings.onboarding.facts.name') }}</span>
            <input v-model="wizard.name" type="text" maxlength="200">
          </label>
          <label class="settings-field">
            <span>{{ t('workspace.settings.onboarding.facts.description') }}</span>
            <textarea v-model="wizard.description" rows="2" />
          </label>
        </fieldset>

        <fieldset class="settings-step" data-step="model" :data-answered="String(wizardAnswered.model)">
          <legend>
            <span>{{ t('workspace.settings.onboarding.steps.model') }}</span>
            <span v-if="!wizardAnswered.model" class="settings-pending">{{ t('workspace.settings.onboarding.pending') }}</span>
          </legend>
          <label class="settings-field">
            <span>{{ t('workspace.settings.onboarding.model.businessModel') }}</span>
            <input v-model="wizard.business_model" type="text">
          </label>
          <label class="settings-field">
            <span>{{ t('workspace.settings.onboarding.model.productsServices') }}</span>
            <input v-model="wizard.products_services" type="text">
          </label>
        </fieldset>

        <fieldset class="settings-step" data-step="markets" :data-answered="String(wizardAnswered.markets)">
          <legend>
            <span>{{ t('workspace.settings.onboarding.steps.markets') }}</span>
            <span v-if="!wizardAnswered.markets" class="settings-pending">{{ t('workspace.settings.onboarding.pending') }}</span>
          </legend>
          <label class="settings-field">
            <span>{{ t('workspace.settings.onboarding.markets.markets') }}</span>
            <input v-model="wizard.markets" type="text">
          </label>
          <label class="settings-field">
            <span>{{ t('workspace.settings.onboarding.markets.customerSegments') }}</span>
            <input v-model="wizard.customer_segments" type="text">
          </label>
        </fieldset>

        <fieldset
          v-for="step in (['objectives', 'constraints', 'principles', 'metrics'] as const)"
          :key="step"
          class="settings-step"
          :data-step="step"
          :data-answered="String(wizardAnswered[step])"
        >
          <legend>
            <span>{{ t(`workspace.settings.onboarding.steps.${step}`) }}</span>
            <span v-if="!wizardAnswered[step]" class="settings-pending">{{ t('workspace.settings.onboarding.pending') }}</span>
          </legend>
          <label v-for="(label, index) in stepLabels(step)" :key="label" class="settings-field">
            <span>{{ label }}</span>
            <input v-model="wizard[step][index]" type="text" maxlength="300">
          </label>
        </fieldset>

        <div class="settings-actions">
          <button type="submit" class="settings-primary" :disabled="wizardSaving">
            {{ wizardSaving ? t('workspace.settings.onboarding.saving') : t('workspace.settings.onboarding.submit') }}
          </button>
          <span v-if="wizardSaved" class="settings-note">{{ t('workspace.settings.onboarding.saved') }}</span>
        </div>
      </form>

      <form class="settings-section" @submit.prevent="saveProfile">
        <h2>{{ t('workspace.settings.profile.title') }}</h2>
        <label class="settings-field">
          <span>{{ t('workspace.settings.profile.name') }}</span>
          <input v-model="profileForm.name" type="text" maxlength="200">
        </label>
        <label class="settings-field">
          <span>{{ t('workspace.settings.profile.description') }}</span>
          <textarea v-model="profileForm.description" rows="3" />
        </label>
        <label class="settings-field">
          <span>{{ t('workspace.settings.profile.businessModel') }}</span>
          <input v-model="profileForm.business_model" type="text">
        </label>
        <label class="settings-field">
          <span>{{ t('workspace.settings.profile.productsServices') }}</span>
          <input v-model="profileForm.products_services" type="text">
        </label>
        <label class="settings-field">
          <span>{{ t('workspace.settings.profile.customerSegments') }}</span>
          <input v-model="profileForm.customer_segments" type="text">
        </label>
        <label class="settings-field">
          <span>{{ t('workspace.settings.profile.markets') }}</span>
          <input v-model="profileForm.markets" type="text">
        </label>
        <label class="settings-field">
          <span>{{ t('workspace.settings.profile.structure') }}</span>
          <input v-model="profileForm.structure" type="text">
        </label>
        <div class="settings-actions">
          <button type="submit" class="settings-primary" :disabled="savingProfile">
            {{ savingProfile ? t('workspace.settings.profile.saving') : t('workspace.settings.profile.save') }}
          </button>
          <span v-if="profileSaved" class="settings-note">{{ t('workspace.settings.profile.saved') }}</span>
        </div>
      </form>

      <section class="settings-section">
        <h2>{{ t('workspace.settings.objectives.title') }}</h2>
        <form class="settings-inline" @submit.prevent="createObjective">
          <label class="settings-field">
            <span class="sr-only">{{ t('workspace.settings.objectives.placeholder') }}</span>
            <input v-model="objectiveTitle" type="text" :placeholder="t('workspace.settings.objectives.placeholder')" maxlength="300">
          </label>
          <button type="submit" class="settings-primary">{{ t('workspace.settings.objectives.create') }}</button>
        </form>
        <p v-if="!context.objectives.length" class="settings-note">{{ t('workspace.settings.objectives.empty') }}</p>
        <ul v-else class="settings-list" role="list">
          <li v-for="objective in context.objectives" :key="objective.id">
            <label class="settings-toggle">
              <input
                type="checkbox"
                :checked="objective.priority"
                @change="patchObjective(objective, { priority: !objective.priority })"
              >
              {{ t('workspace.settings.objectives.priority') }}
            </label>
            <input
              class="settings-title-input"
              type="text"
              maxlength="300"
              :value="objective.title"
              :aria-label="objective.title"
              @change="patchObjective(objective, { title: editedTitle($event) })"
            >
            <span class="settings-state">{{ t(`workspace.settings.state.${objective.state}`) }}</span>
            <button
              type="button"
              class="settings-link"
              @click="patchObjective(objective, { state: nextState(objective.state) })"
            >
              {{ objective.state === 'archived' ? t('workspace.settings.objectives.restore') : t('workspace.settings.objectives.archive') }}
            </button>
          </li>
        </ul>
      </section>

      <section class="settings-section">
        <h2>{{ t('workspace.settings.constraints.title') }}</h2>
        <form class="settings-inline" @submit.prevent="createConstraint">
          <label class="settings-field">
            <span class="sr-only">{{ t('workspace.settings.constraints.placeholder') }}</span>
            <input v-model="constraintTitle" type="text" :placeholder="t('workspace.settings.constraints.placeholder')" maxlength="300">
          </label>
          <label class="settings-field">
            <span class="sr-only">{{ t('workspace.settings.constraints.detailPlaceholder') }}</span>
            <input v-model="constraintDetail" type="text" :placeholder="t('workspace.settings.constraints.detailPlaceholder')">
          </label>
          <button type="submit" class="settings-primary">{{ t('workspace.settings.constraints.create') }}</button>
        </form>
        <p v-if="!context.constraints.length" class="settings-note">{{ t('workspace.settings.constraints.empty') }}</p>
        <ul v-else class="settings-list" role="list">
          <li v-for="constraint in context.constraints" :key="constraint.id">
            <input
              class="settings-title-input"
              type="text"
              maxlength="300"
              :value="constraint.title"
              :aria-label="constraint.title"
              @change="patchConstraint(constraint, { title: editedTitle($event) })"
            >
            <input
              class="settings-title-input"
              type="text"
              :value="constraint.detail ?? ''"
              :aria-label="`${t('workspace.settings.constraints.detailPlaceholder')} — ${constraint.title}`"
              @change="patchConstraint(constraint, { detail: editedTitle($event) })"
            >
            <span class="settings-state">{{ t(`workspace.settings.state.${constraint.state}`) }}</span>
            <button
              type="button"
              class="settings-link"
              @click="patchConstraint(constraint, { state: nextState(constraint.state) })"
            >
              {{ constraint.state === 'archived' ? t('workspace.settings.constraints.restore') : t('workspace.settings.constraints.archive') }}
            </button>
          </li>
        </ul>
      </section>

      <section class="settings-section">
        <h2>{{ t('workspace.settings.principles.title') }}</h2>
        <form class="settings-inline" @submit.prevent="createPrinciple">
          <label class="settings-field">
            <span class="sr-only">{{ t('workspace.settings.principles.placeholder') }}</span>
            <input v-model="principleTitle" type="text" :placeholder="t('workspace.settings.principles.placeholder')" maxlength="300">
          </label>
          <label class="settings-field">
            <span class="sr-only">{{ t('workspace.settings.principles.detailPlaceholder') }}</span>
            <input v-model="principleDetail" type="text" :placeholder="t('workspace.settings.principles.detailPlaceholder')">
          </label>
          <button type="submit" class="settings-primary">{{ t('workspace.settings.principles.create') }}</button>
        </form>
        <p v-if="!context.principles.length" class="settings-note">{{ t('workspace.settings.principles.empty') }}</p>
        <ul v-else class="settings-list" role="list">
          <li v-for="principle in context.principles" :key="principle.id">
            <input
              class="settings-title-input"
              type="text"
              maxlength="300"
              :value="principle.title"
              :aria-label="principle.title"
              @change="patchPrinciple(principle, { title: editedTitle($event) })"
            >
            <input
              class="settings-title-input"
              type="text"
              :value="principle.detail ?? ''"
              :aria-label="`${t('workspace.settings.principles.detailPlaceholder')} ${principle.title}`"
              @change="patchPrinciple(principle, { detail: editedTitle($event) })"
            >
            <span class="settings-state">{{ t(`workspace.settings.state.${principle.state}`) }}</span>
            <button
              type="button"
              class="settings-link"
              @click="patchPrinciple(principle, { state: nextState(principle.state) })"
            >
              {{ principle.state === 'archived' ? t('workspace.settings.principles.restore') : t('workspace.settings.principles.archive') }}
            </button>
          </li>
        </ul>
      </section>

      <section class="settings-section">
        <h2>{{ t('workspace.settings.metrics.title') }}</h2>
        <form class="settings-metric-form" @submit.prevent="createMetric">
          <label class="settings-field">
            <span class="sr-only">{{ t('workspace.settings.metrics.namePlaceholder') }}</span>
            <input v-model="metricName" type="text" :placeholder="t('workspace.settings.metrics.namePlaceholder')" maxlength="200">
          </label>
          <label class="settings-field">
            <span class="sr-only">{{ t('workspace.settings.metrics.valuePlaceholder') }}</span>
            <input v-model="metricValue" type="text" :placeholder="t('workspace.settings.metrics.valuePlaceholder')" maxlength="200">
          </label>
          <label class="settings-field">
            <span class="sr-only">{{ t('workspace.settings.metrics.unitPlaceholder') }}</span>
            <input v-model="metricUnit" type="text" :placeholder="t('workspace.settings.metrics.unitPlaceholder')" maxlength="50">
          </label>
          <label class="settings-field">
            <span class="sr-only">{{ t('workspace.settings.metrics.sourcePlaceholder') }}</span>
            <input v-model="metricSource" type="text" :placeholder="t('workspace.settings.metrics.sourcePlaceholder')" maxlength="300">
          </label>
          <button type="submit" class="settings-primary">{{ t('workspace.settings.metrics.create') }}</button>
        </form>
        <p v-if="!context.metrics.length" class="settings-note">{{ t('workspace.settings.metrics.empty') }}</p>
        <ul v-else class="settings-list" role="list">
          <li v-for="metric in context.metrics" :key="metric.id">
            <input
              class="settings-title-input"
              type="text"
              maxlength="200"
              :value="metric.name"
              :aria-label="metric.name"
              @change="patchMetric(metric, { name: editedTitle($event) })"
            >
            <input
              class="settings-metric-value"
              type="text"
              maxlength="200"
              :value="metric.value ?? ''"
              :aria-label="`${t('workspace.settings.metrics.valuePlaceholder')} ${metric.name}`"
              @change="patchMetric(metric, { value: editedTitle($event) })"
            >
            <span v-if="metric.unit" class="settings-note">{{ metric.unit }}</span>
            <span class="settings-state">{{ t(`workspace.settings.state.${metric.state}`) }}</span>
            <button
              type="button"
              class="settings-link"
              @click="patchMetric(metric, { state: nextState(metric.state) })"
            >
              {{ metric.state === 'archived' ? t('workspace.settings.metrics.restore') : t('workspace.settings.metrics.archive') }}
            </button>
          </li>
        </ul>
      </section>
    </template>
  </div>
</template>

<style scoped>
.settings-shell { display: grid; gap: 26px; max-width: 720px; margin: 0 auto; padding: 22px 4px 64px; }
.settings-header h1 { margin: 0; font-size: 1.5rem; }
.settings-header p { margin: 6px 0 0; color: var(--ui-text-muted); font-size: .92rem; }
.settings-section { display: grid; gap: 12px; border: 1px solid var(--ui-border); border-radius: 16px; padding: 18px 20px; }
.settings-section h2 { margin: 0; font-size: 1.05rem; font-weight: 620; }
.settings-field { display: grid; gap: 6px; font-size: .82rem; font-weight: 560; color: var(--ui-text-muted); }
.settings-field input, .settings-field textarea { border: 1px solid var(--ui-border); border-radius: 12px; padding: 8px 12px; background: var(--ui-bg); color: var(--ui-text); font: inherit; }
.settings-field textarea { resize: vertical; }
.settings-inline { display: grid; grid-template-columns: 1fr 1fr auto; gap: 10px; align-items: end; }
.settings-actions { display: flex; align-items: center; gap: 12px; }
.settings-primary { border: 0; border-radius: 12px; padding: 9px 16px; background: var(--kollio-heading); color: white; font: inherit; font-size: .85rem; font-weight: 570; cursor: pointer; }
.settings-primary:disabled { opacity: .6; cursor: progress; }
.settings-link { border: 0; background: transparent; color: var(--kollio-active-ink); font: inherit; font-size: .82rem; font-weight: 620; cursor: pointer; text-decoration: underline; text-underline-offset: 3px; }
.settings-note { color: var(--ui-text-muted); font-size: .82rem; }
.settings-error { border: 1px solid var(--ui-border); border-radius: 12px; padding: 10px 14px; background: var(--ui-bg-elevated); font-size: .85rem; }
.settings-list { display: grid; gap: 8px; margin: 0; padding: 0; list-style: none; }
.settings-list li { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; border-top: 1px solid var(--ui-border); padding-top: 8px; }
.settings-list li:first-child { border-top: 0; padding-top: 0; }
.settings-title-input { flex: 1 1 220px; border: 1px solid transparent; border-radius: 10px; padding: 6px 8px; background: transparent; color: var(--ui-text); font: inherit; font-weight: 560; }
.settings-title-input:hover, .settings-title-input:focus { border-color: var(--ui-border); background: var(--ui-bg); }
.settings-state { border-radius: 999px; padding: 2px 10px; background: var(--ui-bg-muted); color: var(--ui-text-muted); font-size: .72rem; font-weight: 600; }
.settings-toggle { display: flex; align-items: center; gap: 6px; font-size: .8rem; color: var(--ui-text-muted); }
.settings-wizard { gap: 16px; }
.settings-wizard-head { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; }
.settings-step { display: grid; gap: 10px; margin: 0; min-width: 0; border: 1px solid var(--ui-border); border-radius: 12px; padding: 4px 14px 14px; }
.settings-step legend { display: flex; align-items: center; gap: 8px; padding-inline: 4px; color: var(--ui-text); font-size: .9rem; font-weight: 620; }
.settings-pending { border-radius: 999px; padding: 1px 9px; background: color-mix(in srgb, var(--ui-warning) 22%, transparent); color: var(--ui-warning); font-size: .68rem; font-weight: 600; }
.settings-metric-form { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; align-items: end; }
.settings-metric-form .settings-primary { grid-column: 1 / -1; justify-self: start; }
.settings-metric-value { flex: 0 1 140px; border: 1px solid transparent; border-radius: 10px; padding: 6px 8px; background: transparent; color: var(--ui-text); font: inherit; }
.settings-metric-value:hover, .settings-metric-value:focus { border-color: var(--ui-border); background: var(--ui-bg); }
</style>
