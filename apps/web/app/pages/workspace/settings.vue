<script setup lang="ts">
import type {
  CompanyContextResponse,
  CompanyProfileResponse,
  CompanyConstraintResponse,
  CompanyConstraintUpdate,
  ObjectiveResponse,
  ObjectiveUpdate,
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

watch(context, (value) => {
  if (!value) return
  profileForm.name = value.profile.name ?? ''
  profileForm.description = value.profile.description ?? ''
  profileForm.business_model = value.profile.business_model ?? ''
  profileForm.products_services = value.profile.products_services ?? ''
  profileForm.customer_segments = value.profile.customer_segments ?? ''
  profileForm.markets = value.profile.markets ?? ''
  profileForm.structure = value.profile.structure ?? ''
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

function editedTitle(event: Event) {
  return (event.target as HTMLInputElement).value.trim()
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
</style>
