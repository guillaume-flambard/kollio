<script setup lang="ts">
import type {
  BranchResponse,
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
const kinds = ['idea', 'claim', 'evidence', 'objection', 'constraint'] as const

const branchFormOpen = ref(false)
const branchTitle = ref('')
const branchSummary = ref('')
const branchVisibility = ref<'private' | 'shared'>('private')
const branchError = ref<string>()
const creatingBranch = ref(false)

const proposalBranchId = ref('')
const proposalKind = ref<string>('idea')
const proposalTitle = ref('')
const proposalBody = ref('')
const proposalSource = ref('')
const proposalToolModel = ref('')
const proposalError = ref<string>()
const proposing = ref(false)

const confirming = ref('')
const confirmError = ref<string>()

const { data: workspaces } = await useAsyncData('workspaces', () => requestFetch<WorkspaceResponse[]>('/api/workspaces'))

const workspaceId = computed(() => {
  const requested = typeof route.query.workspace === 'string' ? route.query.workspace : undefined
  return workspaces.value?.find(workspace => workspace.id === requested)?.id ?? workspaces.value?.[0]?.id
})

const branchesPath = computed(() => `/api/workspaces/${encodeURIComponent(workspaceId.value ?? '')}/decision-spaces/${encodeURIComponent(spaceId)}`)

const { data: branchPage, error: branchesError, refresh: refreshBranches } = await useAsyncData(
  `explore-branches-${spaceId}`,
  async () => {
    if (!workspaceId.value) return undefined
    return requestFetch<{ items: BranchResponse[] }>(`${branchesPath.value}/branches`)
  },
  { watch: [workspaceId] },
)

const { data: contributionPage, error: contributionsError, refresh: refreshContributions } = await useAsyncData(
  `explore-contributions-${spaceId}`,
  async () => {
    if (!workspaceId.value) return undefined
    return requestFetch<{ items: ContributionResponse[] }>(`${branchesPath.value}/contributions`)
  },
  { watch: [workspaceId] },
)

const { data: members } = await useAsyncData(
  `explore-members-${spaceId}`,
  async () => {
    if (!workspaceId.value) return undefined
    return requestFetch<WorkspaceMemberResponse[]>(`/api/workspaces/${encodeURIComponent(workspaceId.value)}/members`)
  },
  { watch: [workspaceId] },
)

const branches = computed(() => branchPage.value?.items ?? [])
const contributions = computed(() => contributionPage.value?.items ?? [])
const pendingContributions = computed(() => contributions.value.filter(item => item.status === 'suggested'))
const confirmedContributions = computed(() => contributions.value.filter(item => item.status === 'confirmed'))
const proposalOpen = computed(() => Boolean(proposalBranchId.value))
const proposalBranch = computed(() => branches.value.find(branch => branch.id === proposalBranchId.value))

const { formatDate: dateLabel } = useFormatters()

function memberName(userId: string) {
  return members.value?.find(member => member.id === userId)?.display_name ?? userId
}
function branchTitleOf(branchId: string) {
  return branches.value.find(branch => branch.id === branchId)?.title ?? branchId
}
function toggleBranchForm() {
  branchFormOpen.value = !branchFormOpen.value
  branchError.value = undefined
}
function cancelBranchForm() {
  branchFormOpen.value = false
  branchError.value = undefined
}
function openProposal(branch: BranchResponse) {
  proposalBranchId.value = branch.id
  proposalError.value = undefined
}
function closeProposal() {
  proposalBranchId.value = ''
  proposalError.value = undefined
}

async function createBranch() {
  const title = branchTitle.value.trim()
  if (!title) {
    branchError.value = t('decisionSpaces.explore.branch.form.nameRequired')
    return
  }
  creatingBranch.value = true
  branchError.value = undefined
  try {
    await $fetch(`${branchesPath.value}/branches`, {
      method: 'POST',
      body: { title, summary: branchSummary.value.trim() || null, visibility: branchVisibility.value },
    })
    branchTitle.value = ''
    branchSummary.value = ''
    branchVisibility.value = 'private'
    branchFormOpen.value = false
    await refreshBranches()
  } catch {
    branchError.value = t('decisionSpaces.explore.branch.form.failed')
  } finally {
    creatingBranch.value = false
  }
}

async function proposeContribution() {
  const title = proposalTitle.value.trim()
  if (!title) {
    proposalError.value = t('decisionSpaces.explore.contributions.titleRequired')
    return
  }
  proposing.value = true
  proposalError.value = undefined
  try {
    await $fetch(`${branchesPath.value}/contributions`, {
      method: 'POST',
      body: {
        branch_id: proposalBranchId.value,
        kind: proposalKind.value,
        title,
        body: proposalBody.value.trim() || null,
        source: proposalSource.value.trim() || null,
        tool_model: proposalToolModel.value.trim() || null,
      },
    })
    proposalTitle.value = ''
    proposalBody.value = ''
    proposalSource.value = ''
    proposalToolModel.value = ''
    proposalKind.value = 'idea'
    proposalBranchId.value = ''
    await refreshContributions()
  } catch {
    proposalError.value = t('decisionSpaces.explore.contributions.failed')
  } finally {
    proposing.value = false
  }
}

async function confirmContribution(contribution: ContributionResponse) {
  confirming.value = contribution.id
  confirmError.value = undefined
  try {
    await $fetch(`${branchesPath.value}/contributions/${encodeURIComponent(contribution.id)}/confirmation`, { method: 'POST' })
    await refreshContributions()
  } catch {
    confirmError.value = t('decisionSpaces.explore.contributions.confirmFailed')
  } finally {
    confirming.value = ''
  }
}

useSeoMeta({ title: () => t('decisionSpaces.section.explore.title') })
</script>

<template>
  <section class="explore">
    <h2>{{ t('decisionSpaces.section.explore.title') }}</h2>
    <p class="explore-intro">{{ t('decisionSpaces.section.explore.body') }}</p>

    <p v-if="branchesError || contributionsError" class="explore-error" role="alert">
      {{ t('decisionSpaces.explore.loadFailed') }}
    </p>

    <template v-else>
      <div class="explore-block">
        <div class="explore-block-head">
          <h3>{{ t('decisionSpaces.explore.branches.title') }}</h3>
          <button type="button" class="explore-toggle" :aria-expanded="branchFormOpen" @click="toggleBranchForm">
            <span aria-hidden="true" v-text="glyphs.plus" /> {{ t('decisionSpaces.explore.branches.create') }}
          </button>
        </div>

        <form v-if="branchFormOpen" class="explore-form" @submit.prevent="createBranch">
          <h4>{{ t('decisionSpaces.explore.branch.form.title') }}</h4>
          <label>
            <span>{{ t('decisionSpaces.explore.branch.form.name') }}</span>
            <input v-model="branchTitle" type="text" :placeholder="t('decisionSpaces.explore.branch.form.namePlaceholder')">
          </label>
          <label>
            <span>{{ t('decisionSpaces.explore.branch.form.summary') }}</span>
            <textarea v-model="branchSummary" rows="4" />
            <small>{{ t('decisionSpaces.explore.branch.form.summaryHint') }}</small>
          </label>
          <fieldset class="explore-choice">
            <legend>{{ t('decisionSpaces.explore.branch.form.visibility') }}</legend>
            <label>
              <input v-model="branchVisibility" type="radio" value="private">
              {{ t('decisionSpaces.explore.visibility.private') }}
            </label>
            <label>
              <input v-model="branchVisibility" type="radio" value="shared">
              {{ t('decisionSpaces.explore.visibility.shared') }}
            </label>
          </fieldset>
          <p v-if="branchError" class="explore-form-error" role="alert">{{ branchError }}</p>
          <div class="explore-form-actions">
            <button type="submit" :disabled="creatingBranch">
              {{ creatingBranch ? t('decisionSpaces.explore.branch.form.submitting') : t('decisionSpaces.explore.branch.form.submit') }}
            </button>
            <button type="button" class="explore-secondary" @click="cancelBranchForm">{{ t('decisionSpaces.cancel') }}</button>
          </div>
        </form>

        <ul v-if="branches.length" class="branch-list">
          <li v-for="branch in branches" :key="branch.id" class="branch">
            <div class="branch-head">
              <h4>{{ branch.title }}</h4>
              <span class="branch-visibility">{{ t(`decisionSpaces.explore.visibility.${branch.visibility}`) }}</span>
            </div>
            <template v-if="branch.summary">
              <p class="branch-raw-label">{{ t('decisionSpaces.explore.branch.form.summary') }}</p>
              <p class="branch-raw">{{ branch.summary }}</p>
            </template>
            <p class="branch-meta">{{ t('decisionSpaces.explore.branches.byline', { name: memberName(branch.created_by), date: dateLabel(branch.created_at) }) }}</p>
            <button type="button" class="explore-secondary" @click="openProposal(branch)">
              {{ t('decisionSpaces.explore.contributions.propose') }}
            </button>
          </li>
        </ul>
        <p v-else class="explore-empty">{{ t('decisionSpaces.explore.branches.empty') }}</p>
      </div>

      <form v-if="proposalOpen" class="explore-form" @submit.prevent="proposeContribution">
        <h4>{{ t('decisionSpaces.explore.contributions.propose') }}</h4>
        <p class="explore-hint">{{ t('decisionSpaces.explore.contributions.forBranch', { name: proposalBranch?.title ?? '' }) }}</p>
        <label>
          <span>{{ t('decisionSpaces.explore.contributions.kind') }}</span>
          <select v-model="proposalKind">
            <option v-for="kind in kinds" :key="kind" :value="kind">{{ t(`decisionSpaces.explore.contributions.kinds.${kind}`) }}</option>
          </select>
        </label>
        <label>
          <span>{{ t('decisionSpaces.explore.contributions.titleLabel') }}</span>
          <input v-model="proposalTitle" type="text" :placeholder="t('decisionSpaces.explore.contributions.titlePlaceholder')">
        </label>
        <label>
          <span>{{ t('decisionSpaces.explore.contributions.body') }}</span>
          <textarea v-model="proposalBody" rows="4" :placeholder="t('decisionSpaces.explore.contributions.bodyPlaceholder')" />
        </label>
        <label>
          <span>{{ t('decisionSpaces.explore.contributions.source') }}</span>
          <input v-model="proposalSource" type="text" :placeholder="t('decisionSpaces.explore.contributions.sourcePlaceholder')">
        </label>
        <label>
          <span>{{ t('decisionSpaces.explore.contributions.toolModel') }}</span>
          <input v-model="proposalToolModel" type="text" :placeholder="t('decisionSpaces.explore.contributions.toolModelPlaceholder')">
        </label>
        <p v-if="proposalError" class="explore-form-error" role="alert">{{ proposalError }}</p>
        <div class="explore-form-actions">
          <button type="submit" :disabled="proposing">
            {{ proposing ? t('decisionSpaces.explore.contributions.submitting') : t('decisionSpaces.explore.contributions.submit') }}
          </button>
          <button type="button" class="explore-secondary" @click="closeProposal">{{ t('decisionSpaces.cancel') }}</button>
        </div>
      </form>

      <div class="explore-block">
        <h3>{{ t('decisionSpaces.explore.contributions.title') }}</h3>
        <p class="explore-hint">{{ t('decisionSpaces.explore.contributions.intro') }}</p>

        <p v-if="confirmError" class="explore-form-error" role="alert">{{ confirmError }}</p>

        <h4 class="explore-group">{{ t('decisionSpaces.explore.contributions.pending') }}</h4>
        <ul v-if="pendingContributions.length" class="contribution-list">
          <li v-for="contribution in pendingContributions" :key="contribution.id" class="contribution">
            <div class="contribution-head">
              <h5>{{ contribution.title }}</h5>
              <span class="contribution-status">{{ t(`decisionSpaces.explore.contributions.status.${contribution.status}`) }}</span>
            </div>
            <p v-if="contribution.body" class="contribution-body">{{ contribution.body }}</p>
            <dl class="contribution-provenance">
              <div><dt>{{ t('decisionSpaces.explore.provenance.author') }}</dt><dd>{{ memberName(contribution.author_id) }}</dd></div>
              <div><dt>{{ t('decisionSpaces.explore.provenance.branch') }}</dt><dd>{{ branchTitleOf(contribution.branch_id) }}</dd></div>
              <div><dt>{{ t('decisionSpaces.explore.provenance.source') }}</dt><dd>{{ contribution.source || t('decisionSpaces.explore.provenance.none') }}</dd></div>
              <div><dt>{{ t('decisionSpaces.explore.provenance.tool') }}</dt><dd>{{ contribution.tool_model || t('decisionSpaces.explore.provenance.none') }}</dd></div>
              <div><dt>{{ t('decisionSpaces.explore.provenance.added') }}</dt><dd>{{ dateLabel(contribution.created_at) }}</dd></div>
            </dl>
            <button type="button" @click="confirmContribution(contribution)">
              {{ confirming === contribution.id ? t('decisionSpaces.explore.contributions.confirming') : t('decisionSpaces.explore.contributions.confirm') }}
            </button>
          </li>
        </ul>
        <p v-else class="explore-empty">{{ t('decisionSpaces.explore.contributions.pendingEmpty') }}</p>

        <h4 class="explore-group">{{ t('decisionSpaces.explore.contributions.confirmed') }}</h4>
        <ul v-if="confirmedContributions.length" class="contribution-list">
          <li v-for="contribution in confirmedContributions" :key="contribution.id" class="contribution">
            <div class="contribution-head">
              <h5>{{ contribution.title }}</h5>
              <span class="contribution-status">{{ t(`decisionSpaces.explore.contributions.status.${contribution.status}`) }}</span>
            </div>
            <p v-if="contribution.body" class="contribution-body">{{ contribution.body }}</p>
            <dl class="contribution-provenance">
              <div><dt>{{ t('decisionSpaces.explore.provenance.author') }}</dt><dd>{{ memberName(contribution.author_id) }}</dd></div>
              <div><dt>{{ t('decisionSpaces.explore.provenance.branch') }}</dt><dd>{{ branchTitleOf(contribution.branch_id) }}</dd></div>
              <div><dt>{{ t('decisionSpaces.explore.provenance.source') }}</dt><dd>{{ contribution.source || t('decisionSpaces.explore.provenance.none') }}</dd></div>
              <div><dt>{{ t('decisionSpaces.explore.provenance.tool') }}</dt><dd>{{ contribution.tool_model || t('decisionSpaces.explore.provenance.none') }}</dd></div>
              <div><dt>{{ t('decisionSpaces.explore.provenance.added') }}</dt><dd>{{ dateLabel(contribution.created_at) }}</dd></div>
            </dl>
          </li>
        </ul>
        <p v-else class="explore-empty">{{ t('decisionSpaces.explore.contributions.confirmedEmpty') }}</p>
      </div>
    </template>
  </section>
</template>

<style scoped>
.explore { display: grid; max-width: 76ch; gap: 8px; }
.explore h2 { color: var(--kollio-heading); font-size: var(--kollio-text-title); font-weight: var(--kollio-weight-display); }
.explore-intro { color: var(--ui-text-muted); font-size: var(--kollio-text-small); line-height: var(--kollio-leading-body); }
.explore-error { margin-top: 10px; color: var(--ui-error); font-size: var(--kollio-text-caption); font-weight: var(--kollio-weight-strong); }
.explore-block { margin-top: 26px; border-top: 1px solid var(--ui-border); padding-top: 18px; }
.explore-block-head { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px; }
.explore-block h3 { color: var(--kollio-heading); font-size: var(--kollio-text-lead); font-weight: var(--kollio-weight-strong); }
.explore-group { margin-top: 20px; color: var(--ui-text-muted); font-size: var(--kollio-text-micro); font-weight: var(--kollio-weight-strong); text-transform: uppercase; letter-spacing: .08em; }
.explore-hint, .explore-empty { margin-top: 8px; color: var(--ui-text-muted); font-size: var(--kollio-text-small); line-height: var(--kollio-leading-body); }
.explore-toggle, .explore-form button { display: inline-flex; min-height: 44px; align-items: center; gap: 8px; border-radius: var(--kollio-radius-md); background: var(--kollio-heading); padding: 0 20px; color: var(--ui-bg-elevated); font-size: var(--kollio-text-caption); font-weight: var(--kollio-weight-strong); }
.explore-toggle[aria-expanded='true'] { background: var(--ui-bg-accented); color: var(--kollio-active-ink); }
.explore-secondary { display: inline-flex; min-height: 44px; align-items: center; border: 1px solid var(--ui-border); border-radius: var(--kollio-radius-md); background: var(--ui-bg-elevated); padding: 0 18px; color: var(--kollio-heading); font-size: var(--kollio-text-caption); font-weight: var(--kollio-weight-strong); }
.explore-secondary:hover { border-color: var(--kollio-active-ink); color: var(--kollio-active-ink); }
.explore-form { display: grid; gap: 14px; margin-top: 16px; border: 1px solid var(--ui-border); border-radius: var(--kollio-radius-md); background: var(--ui-bg-elevated); padding: 18px; }
.explore-form h4 { color: var(--kollio-heading); font-size: var(--kollio-text-small); font-weight: var(--kollio-weight-strong); }
.explore-form label { display: grid; gap: 6px; }
.explore-form label > span { color: var(--ui-text-muted); font-size: var(--kollio-text-micro); font-weight: var(--kollio-weight-strong); text-transform: uppercase; letter-spacing: .08em; }
.explore-form small { color: var(--ui-text-muted); font-size: var(--kollio-text-micro); line-height: var(--kollio-leading-body); }
.explore-form input, .explore-form textarea, .explore-form select { min-height: 44px; border: 1px solid var(--ui-border); border-radius: var(--kollio-radius-md); background: var(--ui-bg); padding: 10px 12px; color: var(--kollio-heading); font-size: var(--kollio-text-small); }
.explore-form textarea { min-height: 96px; resize: vertical; }
.explore-form input:focus-visible, .explore-form textarea:focus-visible, .explore-form select:focus-visible { outline: 2px solid var(--kollio-active-ink); outline-offset: 1px; }
.explore-choice { display: flex; flex-wrap: wrap; gap: 10px 22px; border: 1px solid var(--ui-border); border-radius: var(--kollio-radius-md); padding: 12px 14px; }
.explore-choice legend { padding: 0 6px; color: var(--ui-text-muted); font-size: var(--kollio-text-micro); font-weight: var(--kollio-weight-strong); text-transform: uppercase; letter-spacing: .08em; }
.explore-choice label { display: inline-flex; min-height: 40px; align-items: center; gap: 8px; color: var(--kollio-heading); font-size: var(--kollio-text-small); }
.explore-form-actions { display: flex; flex-wrap: wrap; gap: 10px; }
.explore-form-error { color: var(--ui-error); font-size: var(--kollio-text-caption); font-weight: var(--kollio-weight-strong); }
.branch-list, .contribution-list { display: grid; gap: 14px; margin-top: 16px; }
.branch, .contribution { border: 1px solid var(--ui-border); border-radius: var(--kollio-radius-md); background: var(--ui-bg-elevated); padding: 16px; }
.branch-head, .contribution-head { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px; }
.branch-head h4, .contribution-head h5 { color: var(--kollio-heading); font-size: var(--kollio-text-small); font-weight: var(--kollio-weight-strong); }
.branch-visibility, .contribution-status { flex: none; border-radius: var(--kollio-radius-pill); background: var(--kollio-active-wash); padding: 5px 12px; color: var(--kollio-active-ink); font-size: var(--kollio-text-micro); font-weight: var(--kollio-weight-strong); }
.branch-raw-label { margin-top: 12px; color: var(--ui-text-muted); font-size: var(--kollio-text-micro); font-weight: var(--kollio-weight-strong); text-transform: uppercase; letter-spacing: .08em; }
.branch-raw, .contribution-body { margin-top: 6px; color: var(--ui-text-muted); font-size: var(--kollio-text-small); line-height: var(--kollio-leading-body); white-space: pre-wrap; }
.branch-meta { margin-top: 12px; color: var(--ui-text-muted); font-size: var(--kollio-text-micro); }
.branch button { margin-top: 14px; }
.contribution-provenance { display: flex; flex-wrap: wrap; gap: 10px 26px; margin-top: 14px; border-top: 1px solid var(--ui-border); padding-top: 12px; }
.contribution-provenance dt { color: var(--ui-text-muted); font-size: var(--kollio-text-micro); font-weight: var(--kollio-weight-strong); text-transform: uppercase; letter-spacing: .08em; }
.contribution-provenance dd { margin-top: 4px; color: var(--kollio-heading); font-size: var(--kollio-text-caption); }
.contribution button { margin-top: 14px; }
.explore-form button[disabled], .explore-toggle[disabled] { opacity: .6; }
@media (max-width: 760px) {
  .explore-block-head { align-items: flex-start; flex-direction: column; }
}
</style>
