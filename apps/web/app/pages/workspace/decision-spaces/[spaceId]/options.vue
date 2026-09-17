<script setup lang="ts">
import type {
  OptionDetailResponse,
  OptionResponse,
  SrcModulesBranchesApiSchemasContributionResponse as ContributionResponse,
  WorkspaceMemberResponse,
  WorkspaceResponse,
} from '@kollio/api-client'

definePageMeta({ layout: 'workspace', middleware: 'authenticated' })

const { t } = useI18n()
const route = useRoute()
const requestFetch = useRequestFetch()
const spaceId = String(route.params.spaceId)
const glyphs = Object.freeze({ plus: '＋' })
const sides = ['for', 'against'] as const
const optionalFields = [
  'mechanism',
  'upside',
  'cost',
  'risks',
  'critical_assumptions',
  'success_metrics',
] as const

const formOpen = ref(false)
const formTitle = ref('')
const formProposal = ref('')
const formMechanism = ref('')
const formUpside = ref('')
const formCost = ref('')
const formRisks = ref('')
const formAssumptions = ref('')
const formMetrics = ref('')
const formError = ref<string>()
const submitting = ref(false)

const editingId = ref('')
const editTitle = ref('')
const editProposal = ref('')
const editMechanism = ref('')
const editUpside = ref('')
const editCost = ref('')
const editRisks = ref('')
const editAssumptions = ref('')
const editMetrics = ref('')
const editError = ref<string>()
const saving = ref(false)

const linkingId = ref('')
const linkChoice = ref('')
const linkSide = ref<string>('for')
const linkError = ref<string>()
const linkingBusy = ref(false)
const unlinking = ref('')
const unlinkError = ref<string>()

const deletingId = ref('')
const deleteError = ref<string>()

const { data: workspaces } = await useAsyncData('workspaces', () =>
  requestFetch<WorkspaceResponse[]>('/api/workspaces'),
)

const workspaceId = computed(() => {
  const requested = typeof route.query.workspace === 'string' ? route.query.workspace : undefined
  return workspaces.value?.find(entry => entry.id === requested)?.id ?? workspaces.value?.[0]?.id
})

const optionsPath = computed(
  () =>
    '/api/workspaces/' +
    encodeURIComponent(workspaceId.value ?? '') +
    '/decision-spaces/' +
    encodeURIComponent(spaceId) +
    '/options',
)

const {
  data: options,
  error: optionsError,
  refresh: refreshOptions,
} = await useAsyncData(
  'options-list-' + spaceId,
  async () => {
    if (!workspaceId.value) {
      return [] as OptionDetailResponse[]
    }
    const list = await requestFetch<{ items: OptionResponse[] }>(optionsPath.value)
    return await Promise.all(
      list.items.map(entry =>
        requestFetch<OptionDetailResponse>(optionsPath.value + '/' + entry.id),
      ),
    )
  },
  { watch: [workspaceId] },
)

const { data: contributions } = await useAsyncData(
  'options-contributions-' + spaceId,
  async () => {
    if (!workspaceId.value) {
      return [] as ContributionResponse[]
    }
    const path =
      '/api/workspaces/' +
      encodeURIComponent(workspaceId.value) +
      '/decision-spaces/' +
      encodeURIComponent(spaceId)
    const list = await requestFetch<{ items: ContributionResponse[] }>(path + '/contributions')
    return list.items
  },
  { watch: [workspaceId] },
)

const { data: members } = await useAsyncData('options-members-' + spaceId, async () => {
  if (!workspaceId.value) {
    return [] as WorkspaceMemberResponse[]
  }
  return await requestFetch<WorkspaceMemberResponse[]>(
    '/api/workspaces/' + encodeURIComponent(workspaceId.value) + '/members',
  )
})

const confirmedContributions = computed(() =>
  (contributions.value ?? []).filter(contribution => contribution.status === 'confirmed'),
)

const hasOptions = computed(() => (options.value ?? []).length > 0)

function memberName(userId: string) {
  return members.value?.find(entry => entry.id === userId)?.display_name ?? userId
}

function contributionTitle(contributionId: string) {
  return (
    confirmedContributions.value.find(entry => entry.id === contributionId)?.title ?? contributionId
  )
}

function evidenceLabel(option: OptionDetailResponse) {
  const support = option.evidence.filter(link => link.side === 'for').length
  const against = option.evidence.filter(link => link.side === 'against').length
  if (!support && !against) {
    return t('decisionSpaces.options.list.noEvidence')
  }
  return t('decisionSpaces.options.list.evidence', { for: support, against })
}

function candidatesFor(option: OptionDetailResponse) {
  const linked = new Set(option.evidence.map(link => link.contribution_id))
  return confirmedContributions.value.filter(entry => !linked.has(entry.id))
}

function resetForm() {
  formTitle.value = ''
  formProposal.value = ''
  formMechanism.value = ''
  formUpside.value = ''
  formCost.value = ''
  formRisks.value = ''
  formAssumptions.value = ''
  formMetrics.value = ''
  formError.value = undefined
}

function toggleForm() {
  formOpen.value = !formOpen.value
  formError.value = undefined
}

function cancelForm() {
  formOpen.value = false
  resetForm()
}

async function createOption() {
  const title = formTitle.value.trim()
  const proposal = formProposal.value.trim()
  if (!title) {
    formError.value = t('decisionSpaces.options.form.nameRequired')
    return
  }
  if (!proposal) {
    formError.value = t('decisionSpaces.options.form.proposalRequired')
    return
  }
  submitting.value = true
  formError.value = undefined
  try {
    await $fetch(optionsPath.value, {
      method: 'POST',
      body: {
        title,
        proposal,
        mechanism: formMechanism.value.trim() || null,
        upside: formUpside.value.trim() || null,
        cost: formCost.value.trim() || null,
        risks: formRisks.value.trim() || null,
        critical_assumptions: formAssumptions.value.trim() || null,
        success_metrics: formMetrics.value.trim() || null,
      },
    })
    cancelForm()
    await refreshOptions()
  } catch {
    formError.value = t('decisionSpaces.options.form.failed')
  } finally {
    submitting.value = false
  }
}

function startEdit(option: OptionDetailResponse) {
  editingId.value = option.id
  editTitle.value = option.title
  editProposal.value = option.proposal
  editMechanism.value = option.mechanism ?? ''
  editUpside.value = option.upside ?? ''
  editCost.value = option.cost ?? ''
  editRisks.value = option.risks ?? ''
  editAssumptions.value = option.critical_assumptions ?? ''
  editMetrics.value = option.success_metrics ?? ''
  editError.value = undefined
}

function stopEdit() {
  editingId.value = ''
  editError.value = undefined
}

async function saveOption(option: OptionDetailResponse) {
  const title = editTitle.value.trim()
  const proposal = editProposal.value.trim()
  if (!title) {
    editError.value = t('decisionSpaces.options.form.nameRequired')
    return
  }
  if (!proposal) {
    editError.value = t('decisionSpaces.options.form.proposalRequired')
    return
  }
  saving.value = true
  editError.value = undefined
  try {
    await $fetch(optionsPath.value + '/' + option.id, {
      method: 'PATCH',
      body: {
        title,
        proposal,
        mechanism: editMechanism.value.trim() || null,
        upside: editUpside.value.trim() || null,
        cost: editCost.value.trim() || null,
        risks: editRisks.value.trim() || null,
        critical_assumptions: editAssumptions.value.trim() || null,
        success_metrics: editMetrics.value.trim() || null,
      },
    })
    stopEdit()
    await refreshOptions()
  } catch {
    editError.value = t('decisionSpaces.options.form.failed')
  } finally {
    saving.value = false
  }
}

function toggleLink(option: OptionDetailResponse) {
  linkingId.value = linkingId.value === option.id ? '' : option.id
  linkChoice.value = ''
  linkSide.value = 'for'
  linkError.value = undefined
}

async function linkEvidence(option: OptionDetailResponse) {
  if (!linkChoice.value) {
    linkError.value = t('decisionSpaces.options.evidence.choose')
    return
  }
  linkingBusy.value = true
  linkError.value = undefined
  try {
    await $fetch(optionsPath.value + '/' + option.id + '/evidence', {
      method: 'POST',
      body: { contribution_id: linkChoice.value, side: linkSide.value },
    })
    linkingId.value = ''
    linkChoice.value = ''
    await refreshOptions()
  } catch {
    linkError.value = t('decisionSpaces.options.evidence.addFailed')
  } finally {
    linkingBusy.value = false
  }
}

async function unlinkEvidence(option: OptionDetailResponse, contributionId: string) {
  unlinking.value = option.id + ':' + contributionId
  unlinkError.value = undefined
  try {
    await $fetch(optionsPath.value + '/' + option.id + '/evidence/' + contributionId, {
      method: 'DELETE',
    })
    await refreshOptions()
  } catch {
    unlinkError.value = t('decisionSpaces.options.evidence.unlinkFailed')
  } finally {
    unlinking.value = ''
  }
}

async function removeOption(option: OptionDetailResponse) {
  deletingId.value = option.id
  deleteError.value = undefined
  try {
    await $fetch(optionsPath.value + '/' + option.id, { method: 'DELETE' })
    await refreshOptions()
  } catch {
    deleteError.value = t('decisionSpaces.options.actions.deleteFailed')
  } finally {
    deletingId.value = ''
  }
}

useSeoMeta({ title: () => t('decisionSpaces.section.options.title') })
</script>

<template>
  <section class="options">
    <h2>{{ t('decisionSpaces.section.options.title') }}</h2>
    <p class="options-intro">{{ t('decisionSpaces.section.options.body') }}</p>

    <p v-if="optionsError" class="options-error" role="alert">
      {{ t('decisionSpaces.options.loadFailed') }}
    </p>

    <template v-else>
      <div v-if="!hasOptions" class="options-empty-state">
        <h3>{{ t('decisionSpaces.options.empty.title') }}</h3>
        <p>{{ t('decisionSpaces.options.empty.body') }}</p>
      </div>

      <div class="options-block">
        <div class="options-block-head">
          <h3>{{ t('decisionSpaces.options.list.title') }}</h3>
          <button
            type="button"
            class="options-toggle"
            :aria-expanded="formOpen"
            @click="toggleForm"
          >
            <span aria-hidden="true" v-text="glyphs.plus" />
            {{ t('decisionSpaces.options.form.create') }}
          </button>
        </div>
        <p class="options-hint">{{ t('decisionSpaces.options.list.intro') }}</p>

        <form v-if="formOpen" class="options-form" @submit.prevent="createOption">
          <h4>{{ t('decisionSpaces.options.form.newTitle') }}</h4>
          <label>
            <span>{{ t('decisionSpaces.options.form.name') }}</span>
            <input
              v-model="formTitle"
              type="text"
              :placeholder="t('decisionSpaces.options.form.namePlaceholder')"
            >
          </label>
          <label>
            <span>{{ t('decisionSpaces.options.form.proposal') }}</span>
            <textarea
              v-model="formProposal"
              rows="3"
              :placeholder="t('decisionSpaces.options.form.proposalPlaceholder')"
            />
          </label>
          <p class="options-hint">{{ t('decisionSpaces.options.form.optional') }}</p>
          <p class="options-hint">{{ t('decisionSpaces.options.form.optionalHint') }}</p>
          <label>
            <span>{{ t('decisionSpaces.options.fields.mechanism') }}</span>
            <textarea v-model="formMechanism" rows="2" />
          </label>
          <label>
            <span>{{ t('decisionSpaces.options.fields.upside') }}</span>
            <textarea v-model="formUpside" rows="2" />
          </label>
          <label>
            <span>{{ t('decisionSpaces.options.fields.cost') }}</span>
            <textarea v-model="formCost" rows="2" />
          </label>
          <label>
            <span>{{ t('decisionSpaces.options.fields.risks') }}</span>
            <textarea v-model="formRisks" rows="2" />
          </label>
          <label>
            <span>{{ t('decisionSpaces.options.fields.criticalAssumptions') }}</span>
            <textarea v-model="formAssumptions" rows="2" />
          </label>
          <label>
            <span>{{ t('decisionSpaces.options.fields.successMetrics') }}</span>
            <textarea v-model="formMetrics" rows="2" />
          </label>
          <p v-if="formError" class="options-form-error" role="alert">{{ formError }}</p>
          <div class="options-form-actions">
            <button type="submit" :disabled="submitting">
              {{
                submitting
                  ? t('decisionSpaces.options.form.saving')
                  : t('decisionSpaces.options.form.submit')
              }}
            </button>
            <button type="button" class="options-secondary" @click="cancelForm">
              {{ t('decisionSpaces.cancel') }}
            </button>
          </div>
        </form>

        <p v-if="deleteError" class="options-form-error" role="alert">{{ deleteError }}</p>
        <p v-if="unlinkError" class="options-form-error" role="alert">{{ unlinkError }}</p>

        <ul v-if="hasOptions" class="option-list">
          <li v-for="option in options" :key="option.id" class="option">
            <div class="option-head">
              <h4>{{ option.title }}</h4>
              <span class="option-evidence-count">{{ evidenceLabel(option) }}</span>
            </div>
            <p class="option-proposal">{{ option.proposal }}</p>
            <dl v-if="optionalFields.some(field => option[field])" class="option-fields">
              <div v-if="option.mechanism">
                <dt>{{ t('decisionSpaces.options.fields.mechanism') }}</dt>
                <dd>{{ option.mechanism }}</dd>
              </div>
              <div v-if="option.upside">
                <dt>{{ t('decisionSpaces.options.fields.upside') }}</dt>
                <dd>{{ option.upside }}</dd>
              </div>
              <div v-if="option.cost">
                <dt>{{ t('decisionSpaces.options.fields.cost') }}</dt>
                <dd>{{ option.cost }}</dd>
              </div>
              <div v-if="option.risks">
                <dt>{{ t('decisionSpaces.options.fields.risks') }}</dt>
                <dd>{{ option.risks }}</dd>
              </div>
              <div v-if="option.critical_assumptions">
                <dt>{{ t('decisionSpaces.options.fields.criticalAssumptions') }}</dt>
                <dd>{{ option.critical_assumptions }}</dd>
              </div>
              <div v-if="option.success_metrics">
                <dt>{{ t('decisionSpaces.options.fields.successMetrics') }}</dt>
                <dd>{{ option.success_metrics }}</dd>
              </div>
            </dl>
            <p class="option-meta">
              {{
                t('decisionSpaces.options.list.createdBy', { name: memberName(option.created_by) })
              }}
            </p>

            <div class="option-actions">
              <button
                type="button"
                class="options-secondary"
                @click="editingId === option.id ? stopEdit() : startEdit(option)"
              >
                {{
                  editingId === option.id
                    ? t('decisionSpaces.options.actions.done')
                    : t('decisionSpaces.options.actions.edit')
                }}
              </button>
              <button type="button" class="options-secondary" @click="toggleLink(option)">
                {{ t('decisionSpaces.options.actions.link') }}
              </button>
              <button
                type="button"
                class="options-secondary"
                :disabled="deletingId === option.id"
                @click="removeOption(option)"
              >
                {{
                  deletingId === option.id
                    ? t('decisionSpaces.options.actions.deleting')
                    : t('decisionSpaces.options.actions.delete')
                }}
              </button>
            </div>

            <form
              v-if="editingId === option.id"
              class="options-form"
              @submit.prevent="saveOption(option)"
            >
              <h4>{{ t('decisionSpaces.options.form.editTitle') }}</h4>
              <label>
                <span>{{ t('decisionSpaces.options.form.name') }}</span>
                <input v-model="editTitle" type="text">
              </label>
              <label>
                <span>{{ t('decisionSpaces.options.form.proposal') }}</span>
                <textarea v-model="editProposal" rows="3" />
              </label>
              <label>
                <span>{{ t('decisionSpaces.options.fields.mechanism') }}</span>
                <textarea v-model="editMechanism" rows="2" />
              </label>
              <label>
                <span>{{ t('decisionSpaces.options.fields.upside') }}</span>
                <textarea v-model="editUpside" rows="2" />
              </label>
              <label>
                <span>{{ t('decisionSpaces.options.fields.cost') }}</span>
                <textarea v-model="editCost" rows="2" />
              </label>
              <label>
                <span>{{ t('decisionSpaces.options.fields.risks') }}</span>
                <textarea v-model="editRisks" rows="2" />
              </label>
              <label>
                <span>{{ t('decisionSpaces.options.fields.criticalAssumptions') }}</span>
                <textarea v-model="editAssumptions" rows="2" />
              </label>
              <label>
                <span>{{ t('decisionSpaces.options.fields.successMetrics') }}</span>
                <textarea v-model="editMetrics" rows="2" />
              </label>
              <p v-if="editError" class="options-form-error" role="alert">{{ editError }}</p>
              <div class="options-form-actions">
                <button type="submit" :disabled="saving">
                  {{
                    saving
                      ? t('decisionSpaces.options.form.saving')
                      : t('decisionSpaces.options.form.save')
                  }}
                </button>
                <button type="button" class="options-secondary" @click="stopEdit">
                  {{ t('decisionSpaces.cancel') }}
                </button>
              </div>
            </form>

            <div class="option-evidence">
              <h5>{{ t('decisionSpaces.options.evidence.title') }}</h5>
              <p class="options-hint">{{ t('decisionSpaces.options.evidence.intro') }}</p>
              <dl class="option-evidence-list">
                <div v-for="side in sides" :key="side">
                  <dt>
                    {{
                      side === 'for'
                        ? t('decisionSpaces.options.evidence.for')
                        : t('decisionSpaces.options.evidence.against')
                    }}
                  </dt>
                  <dd>
                    <ul
                      v-if="option.evidence.filter(link => link.side === side).length"
                      class="option-evidence-links"
                    >
                      <li
                        v-for="link in option.evidence.filter(entry => entry.side === side)"
                        :key="link.contribution_id"
                      >
                        <span class="option-evidence-title">
                          {{ contributionTitle(link.contribution_id) }}
                        </span>
                        <button
                          type="button"
                          class="options-secondary"
                          :disabled="unlinking === option.id + ':' + link.contribution_id"
                          @click="unlinkEvidence(option, link.contribution_id)"
                        >
                          {{
                            unlinking === option.id + ':' + link.contribution_id
                              ? t('decisionSpaces.options.evidence.unlinking')
                              : t('decisionSpaces.options.evidence.unlink')
                          }}
                        </button>
                      </li>
                    </ul>
                    <p v-else class="options-empty">
                      {{ t('decisionSpaces.options.evidence.empty') }}
                    </p>
                  </dd>
                </div>
              </dl>

              <form
                v-if="linkingId === option.id"
                class="options-form"
                @submit.prevent="linkEvidence(option)"
              >
                <h4>{{ t('decisionSpaces.options.actions.link') }}</h4>
                <template v-if="candidatesFor(option).length">
                  <label>
                    <span>{{ t('decisionSpaces.options.evidence.label') }}</span>
                    <select v-model="linkChoice">
                      <option value="">{{ t('decisionSpaces.options.evidence.choose') }}</option>
                      <option
                        v-for="candidate in candidatesFor(option)"
                        :key="candidate.id"
                        :value="candidate.id"
                      >
                        {{ candidate.title }}
                      </option>
                    </select>
                  </label>
                  <label>
                    <span>{{ t('decisionSpaces.options.evidence.side') }}</span>
                    <select v-model="linkSide">
                      <option value="for">{{ t('decisionSpaces.options.evidence.for') }}</option>
                      <option value="against">
                        {{ t('decisionSpaces.options.evidence.against') }}
                      </option>
                    </select>
                  </label>
                  <p v-if="linkError" class="options-form-error" role="alert">{{ linkError }}</p>
                  <div class="options-form-actions">
                    <button type="submit" :disabled="linkingBusy">
                      {{
                        linkingBusy
                          ? t('decisionSpaces.options.evidence.adding')
                          : t('decisionSpaces.options.evidence.add')
                      }}
                    </button>
                    <button type="button" class="options-secondary" @click="toggleLink(option)">
                      {{ t('decisionSpaces.cancel') }}
                    </button>
                  </div>
                </template>
                <p v-else class="options-empty">
                  {{ t('decisionSpaces.options.evidence.noCandidates') }}
                </p>
              </form>
            </div>
          </li>
        </ul>
      </div>
    </template>
  </section>
</template>

<style scoped>
.options {
  display: grid;
  gap: 8px;
  max-width: 76ch;
}

.options h2 {
  margin: 0;
  color: var(--kollio-heading);
  font-size: var(--kollio-text-title);
  font-weight: var(--kollio-weight-display);
}

.options-intro,
.options-hint,
.options-empty,
.options-empty-state p {
  margin: 0;
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-small);
  line-height: var(--kollio-leading-body);
}

.options-error,
.options-form-error {
  margin: 0;
  color: var(--ui-error);
  font-size: var(--kollio-text-caption);
  font-weight: var(--kollio-weight-strong);
}

.options-empty-state {
  display: grid;
  gap: 10px;
  margin-top: 26px;
  padding: 20px;
  border: 1px dashed var(--ui-border);
  border-radius: var(--kollio-radius-md);
  background: var(--ui-bg-elevated);
}

.options-empty-state h3 {
  margin: 0;
  color: var(--kollio-heading);
  font-size: var(--kollio-text-lead);
  font-weight: var(--kollio-weight-strong);
}

.options-block {
  margin-top: 26px;
  padding-top: 18px;
  border-top: 1px solid var(--ui-border);
}

.options-block h3 {
  margin: 0;
  color: var(--kollio-heading);
  font-size: var(--kollio-text-lead);
  font-weight: var(--kollio-weight-strong);
}

.options-block-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.options-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 44px;
  padding: 0 16px;
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-md);
  background: var(--ui-bg-elevated);
  color: var(--kollio-heading);
  font-size: var(--kollio-text-small);
  font-weight: var(--kollio-weight-medium);
  cursor: pointer;
}

.options-form {
  display: grid;
  gap: 12px;
  margin-top: 16px;
  padding: 16px;
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-md);
  background: var(--ui-bg-elevated);
}

.options-form h4 {
  margin: 0;
  color: var(--kollio-heading);
  font-size: var(--kollio-text-body);
  font-weight: var(--kollio-weight-strong);
}

.options-form label {
  display: grid;
  gap: 6px;
}

.options-form label > span {
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-micro);
  font-weight: var(--kollio-weight-strong);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.options-form input,
.options-form textarea,
.options-form select {
  min-height: 44px;
  padding: 10px 12px;
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-sm);
  background: var(--ui-bg);
  color: var(--kollio-heading);
  font-family: inherit;
  font-size: var(--kollio-text-small);
}

.options-form textarea {
  resize: vertical;
}

.options-form input:focus-visible,
.options-form textarea:focus-visible,
.options-form select:focus-visible {
  outline: 2px solid var(--kollio-active-ink);
  outline-offset: 1px;
}

.options-form-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.options-form-actions button {
  min-height: 44px;
  padding: 0 20px;
  border: 0;
  border-radius: var(--kollio-radius-md);
  background: var(--kollio-heading);
  color: var(--ui-bg-elevated);
  font-size: var(--kollio-text-small);
  font-weight: var(--kollio-weight-strong);
  cursor: pointer;
}

.options-secondary {
  min-height: 44px;
  padding: 0 16px;
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-md);
  background: var(--ui-bg-elevated);
  color: var(--kollio-heading);
  font-size: var(--kollio-text-small);
  font-weight: var(--kollio-weight-medium);
  cursor: pointer;
}

.options-form-actions button[disabled],
.options-secondary[disabled] {
  opacity: 0.6;
  cursor: default;
}

.option-list {
  display: grid;
  gap: 14px;
  margin: 18px 0 0;
  padding: 0;
  list-style: none;
}

.option {
  display: grid;
  gap: 10px;
  padding: 16px;
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-md);
  background: var(--ui-bg-elevated);
}

.option-head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: 10px;
}

.option-head h4 {
  margin: 0;
  color: var(--kollio-heading);
  font-size: var(--kollio-text-body);
  font-weight: var(--kollio-weight-strong);
}

.option-evidence-count {
  padding: 2px 10px;
  border-radius: var(--kollio-radius-pill);
  background: var(--kollio-active-wash);
  color: var(--kollio-active-ink);
  font-size: var(--kollio-text-micro);
  font-weight: var(--kollio-weight-strong);
}

.option-proposal,
.option-meta {
  margin: 0;
  color: var(--kollio-heading);
  font-size: var(--kollio-text-small);
  line-height: var(--kollio-leading-body);
  white-space: pre-wrap;
}

.option-meta {
  color: var(--ui-text-muted);
}

.option-fields {
  display: grid;
  gap: 8px;
  margin: 0;
}

.option-fields dt,
.option-evidence-list dt {
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-micro);
  font-weight: var(--kollio-weight-strong);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.option-fields dd,
.option-evidence-list dd {
  margin: 2px 0 0;
  color: var(--kollio-heading);
  font-size: var(--kollio-text-small);
  line-height: var(--kollio-leading-body);
  white-space: pre-wrap;
}

.option-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.option-evidence {
  display: grid;
  gap: 8px;
  margin-top: 6px;
  padding-top: 12px;
  border-top: 1px solid var(--ui-border);
}

.option-evidence h5 {
  margin: 0;
  color: var(--kollio-heading);
  font-size: var(--kollio-text-small);
  font-weight: var(--kollio-weight-strong);
}

.option-evidence-list {
  display: grid;
  gap: 10px;
  margin: 0;
}

.option-evidence-links {
  display: grid;
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.option-evidence-links li {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.option-evidence-title {
  color: var(--kollio-heading);
  font-size: var(--kollio-text-small);
}

@media (max-width: 760px) {
  .options-block-head {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
