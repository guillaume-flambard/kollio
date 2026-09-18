<script setup lang="ts">
import type {
  ChallengeFindingResponse,
  ChallengeListResponse,
  DecisionResponse,
  DecisionSpaceDetailResponse,
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

type ArgumentDraft = { contributionId: string, side: string }
type TriggerDraft = { metric: string, direction: string, threshold: string, note: string }

function emptyTrigger(): TriggerDraft {
  return { metric: '', direction: '', threshold: '', note: '' }
}

const { data: workspaces } = await useAsyncData('workspaces', () =>
  requestFetch<WorkspaceResponse[]>('/api/workspaces'),
)

const workspaceId = computed(() => {
  const requested = typeof route.query.workspace === 'string' ? route.query.workspace : undefined
  return workspaces.value?.find(entry => entry.id === requested)?.id ?? workspaces.value?.[0]?.id
})

const basePath = computed(
  () =>
    '/api/workspaces/' +
    encodeURIComponent(workspaceId.value ?? '') +
    '/decision-spaces/' +
    encodeURIComponent(spaceId),
)

const { data: space } = await useAsyncData(
  'decision-space-' + spaceId,
  async () => {
    if (!workspaceId.value) {
      return undefined
    }
    return await requestFetch<DecisionSpaceDetailResponse>(basePath.value)
  },
  { watch: [workspaceId] },
)

const {
  data: options,
  error: optionsError,
} = await useAsyncData(
  'decision-options-' + spaceId,
  async () => {
    if (!workspaceId.value) {
      return [] as OptionResponse[]
    }
    const list = await requestFetch<{ items: OptionResponse[] }>(basePath.value + '/options')
    return list.items
  },
  { watch: [workspaceId] },
)

const { data: contributions } = await useAsyncData(
  'decision-contributions-' + spaceId,
  async () => {
    if (!workspaceId.value) {
      return [] as ContributionResponse[]
    }
    const list = await requestFetch<{ items: ContributionResponse[] }>(
      basePath.value + '/contributions',
    )
    return list.items
  },
  { watch: [workspaceId] },
)

const { data: members } = await useAsyncData('decision-members-' + spaceId, async () => {
  if (!workspaceId.value) {
    return [] as WorkspaceMemberResponse[]
  }
  return await requestFetch<WorkspaceMemberResponse[]>(
    '/api/workspaces/' + encodeURIComponent(workspaceId.value) + '/members',
  )
})

const {
  data: record,
  error: recordError,
  refresh: refreshRecord,
} = await useAsyncData(
  'decision-record-' + spaceId,
  async () => {
    if (!workspaceId.value) {
      return null
    }
    return await requestFetch<DecisionResponse | null>(basePath.value + '/decision')
  },
  { watch: [workspaceId] },
)

const {
  data: versions,
  error: versionsError,
  refresh: refreshVersions,
} = await useAsyncData(
  'decision-versions-' + spaceId,
  async () => {
    if (!workspaceId.value) {
      return [] as DecisionResponse[]
    }
    const list = await requestFetch<{ items: DecisionResponse[] }>(
      basePath.value + '/decision/versions',
    )
    return list.items
  },
  { watch: [workspaceId] },
)

const challengedOptionId = ref('')
const {
  data: challenges,
  error: challengeReadError,
  refresh: refreshChallenges,
} = await useAsyncData(
  'decision-challenges-' + spaceId,
  async () => {
    if (!workspaceId.value || !challengedOptionId.value) {
      return undefined
    }
    return await requestFetch<ChallengeListResponse>(
      basePath.value + '/options/' + encodeURIComponent(challengedOptionId.value) + '/challenges',
    )
  },
  { watch: [workspaceId, challengedOptionId] },
)

const opening = ref(false)
const openError = ref<string>()
const settling = ref('')
const settleError = ref<string>()

const commitOption = ref('')
const commitRationale = ref('')
const commitRejected = ref<string[]>([])
const commitAssumptions = ref('')
const commitUncertainty = ref('')
const commitCriteria = ref('')
const commitArguments = ref<ArgumentDraft[]>([])
const argumentContribution = ref('')
const argumentSide = ref<string>('for')
const triggers = ref<TriggerDraft[]>([emptyTrigger()])
const committing = ref(false)
const commitError = ref<string>()

const optionList = computed(() => options.value ?? [])
const hasOptions = computed(() => optionList.value.length > 0)
const confirmedContributions = computed(() =>
  (contributions.value ?? []).filter(contribution => contribution.status === 'confirmed'),
)

watch(options, (list) => {
  const first = list?.[0]?.id ?? ''
  if (!challengedOptionId.value) {
    challengedOptionId.value = first
  }
  if (!commitOption.value) {
    commitOption.value = first
  }
}, { immediate: true })

const currentRun = computed(() => {
  const runs = [...(challenges.value?.runs ?? [])]
  runs.sort((left, right) => left.created_at.localeCompare(right.created_at))
  return runs[runs.length - 1]
})

const currentFindings = computed(() =>
  (challenges.value?.findings ?? []).filter(finding => finding.run_id === currentRun.value?.id),
)

const coverage = computed(() => challenges.value?.coverage)

const spaceStatus = computed(() => space.value?.status)
const canCommit = computed(() => spaceStatus.value === 'READY_TO_DECIDE')

const otherOptions = computed(() =>
  optionList.value.filter(option => option.id !== commitOption.value),
)

const argumentCandidates = computed(() => {
  const used = new Set(commitArguments.value.map(row => row.contributionId))
  return confirmedContributions.value.filter(contribution => !used.has(contribution.id))
})

const { formatDate: dateLabel } = useFormatters()

function memberName(userId: string) {
  return members.value?.find(entry => entry.id === userId)?.display_name ?? userId
}

function optionTitle(optionId: string) {
  return optionList.value.find(entry => entry.id === optionId)?.title ?? optionId
}

function contributionTitle(contributionId: string) {
  return (
    confirmedContributions.value.find(entry => entry.id === contributionId)?.title ?? contributionId
  )
}


function runStatusLabel(status: string) {
  return t('decisionSpaces.decision.challenge.status.' + status)
}

function modelLabel(run: { model?: string | null }) {
  return run.model
    ? t('decisionSpaces.decision.challenge.model', { name: run.model })
    : t('decisionSpaces.decision.challenge.noModel')
}

function kindLabel(kind: string) {
  return t('decisionSpaces.decision.challenge.kind.' + kind)
}

function severityLabel(severity: string) {
  return t('decisionSpaces.decision.challenge.severity.' + severity)
}

function findingStatusLabel(status: string) {
  return t('decisionSpaces.decision.challenge.findingStatus.' + status)
}

function originLabel(origin: string) {
  return t('decisionSpaces.decision.challenge.origin.' + origin)
}

function sideLabel(side: string) {
  return side === 'against'
    ? t('decisionSpaces.decision.record.against')
    : t('decisionSpaces.decision.record.for')
}

function kindList(values: readonly string[] | undefined) {
  const list = (values ?? []).map(kindLabel)
  return list.length ? list.join(' · ') : t('decisionSpaces.decision.challenge.coverage.none')
}

function argumentLabel(contributionId: string, side: string) {
  return contributionTitle(contributionId) + ' · ' + sideLabel(side)
}

function coverageLabel() {
  const read = coverage.value
  if (!read) {
    return ''
  }
  return [
    t('decisionSpaces.decision.challenge.coverage.title'),
    t('decisionSpaces.decision.challenge.coverage.covered', { list: kindList(read.covered) }),
    t('decisionSpaces.decision.challenge.coverage.uncovered', { list: kindList(read.uncovered) }),
  ].join(' · ')
}

function triggerLabel(trigger: { metric: string, direction?: string | null, threshold?: string | null, note?: string | null }) {
  const parts = [trigger.metric]
  if (trigger.direction) {
    parts.push(
      trigger.direction === 'above'
        ? t('decisionSpaces.decision.record.form.above')
        : t('decisionSpaces.decision.record.form.below'),
    )
  }
  if (trigger.threshold) {
    parts.push(trigger.threshold)
  }
  if (trigger.note) {
    parts.push(trigger.note)
  }
  return parts.join(' · ')
}

let pollTimer: ReturnType<typeof setInterval> | undefined

watch(currentRun, (run) => {
  if (run?.status === 'RUNNING') {
    if (!pollTimer) {
      pollTimer = setInterval(() => {
        void refreshChallenges()
      }, 5000)
    }
    return
  }
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = undefined
  }
}, { immediate: true })

onBeforeUnmount(() => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = undefined
  }
})

async function openChallenge() {
  if (!challengedOptionId.value) {
    return
  }
  opening.value = true
  openError.value = undefined
  try {
    await $fetch(
      basePath.value + '/options/' + encodeURIComponent(challengedOptionId.value) + '/challenges',
      { method: 'POST' },
    )
    await refreshChallenges()
  } catch {
    openError.value = t('decisionSpaces.decision.challenge.openFailed')
  } finally {
    opening.value = false
  }
}

async function settle(finding: ChallengeFindingResponse, resolution: 'confirmed' | 'dismissed') {
  const run = currentRun.value
  if (!run) {
    return
  }
  settling.value = finding.id
  settleError.value = undefined
  try {
    await $fetch(
      basePath.value +
        '/options/' +
        encodeURIComponent(challengedOptionId.value) +
        '/challenges/' +
        encodeURIComponent(run.id) +
        '/findings/' +
        encodeURIComponent(finding.id) +
        '/resolution',
      { method: 'POST', body: { resolution } },
    )
    await refreshChallenges()
  } catch {
    settleError.value =
      resolution === 'confirmed'
        ? t('decisionSpaces.decision.challenge.confirmFailed')
        : t('decisionSpaces.decision.challenge.dismissFailed')
  } finally {
    settling.value = ''
  }
}

function addArgument() {
  if (!argumentContribution.value) {
    return
  }
  commitArguments.value.push({
    contributionId: argumentContribution.value,
    side: argumentSide.value,
  })
  argumentContribution.value = ''
  argumentSide.value = 'for'
}

function removeArgument(index: number) {
  commitArguments.value.splice(index, 1)
}

function addTrigger() {
  triggers.value.push(emptyTrigger())
}

function removeTrigger(index: number) {
  triggers.value.splice(index, 1)
}

function resetCommitForm() {
  commitRationale.value = ''
  commitRejected.value = []
  commitAssumptions.value = ''
  commitUncertainty.value = ''
  commitCriteria.value = ''
  commitArguments.value = []
  argumentContribution.value = ''
  argumentSide.value = 'for'
  triggers.value = [emptyTrigger()]
  commitError.value = undefined
}

async function commitRecord() {
  const rationale = commitRationale.value.trim()
  if (!rationale) {
    commitError.value = t('decisionSpaces.decision.record.form.rationaleRequired')
    return
  }
  if (!commitOption.value) {
    return
  }
  committing.value = true
  commitError.value = undefined
  try {
    await $fetch(basePath.value + '/decision', {
      method: 'POST',
      body: {
        selected_option_id: commitOption.value,
        rationale,
        critical_assumptions: commitAssumptions.value.trim() || null,
        uncertainty: commitUncertainty.value.trim() || null,
        success_criteria: commitCriteria.value.trim() || null,
        rejected_option_ids: commitRejected.value.filter(id => id !== commitOption.value),
        arguments: commitArguments.value.map(row => ({
          contribution_id: row.contributionId,
          side: row.side,
        })),
        revisit_triggers: triggers.value
          .filter(row => row.metric.trim())
          .map(row => ({
            metric: row.metric.trim(),
            direction: row.direction || null,
            threshold: row.threshold.trim() || null,
            note: row.note.trim() || null,
          })),
      },
    })
    resetCommitForm()
    await refreshRecord()
    await refreshVersions()
    await refreshNuxtData('decision-space-' + spaceId)
  } catch (error) {
    const status = (error as { statusCode?: number, status?: number })?.statusCode
      ?? (error as { status?: number })?.status
    commitError.value = status === 403
      ? t('decisionSpaces.decision.record.form.forbidden')
      : t('decisionSpaces.decision.record.form.failed')
  } finally {
    committing.value = false
  }
}

useSeoMeta({ title: () => t('decisionSpaces.section.decision.title') })
</script>

<template>
  <section class="decision">
    <h2>{{ t('decisionSpaces.section.decision.title') }}</h2>
    <p class="decision-intro">{{ t('decisionSpaces.section.decision.body') }}</p>

    <p v-if="optionsError || recordError || versionsError" class="decision-error" role="alert">
      {{ t('decisionSpaces.decision.loadFailed') }}
    </p>

    <template v-else>
      <div v-if="!hasOptions" class="decision-empty-state">
        <h3>{{ t('decisionSpaces.decision.empty.title') }}</h3>
        <p>{{ t('decisionSpaces.decision.empty.body') }}</p>
      </div>

      <template v-else>
        <div class="decision-block">
          <h3>{{ t('decisionSpaces.decision.challenge.title') }}</h3>
          <p class="decision-hint">{{ t('decisionSpaces.decision.challenge.intro') }}</p>

          <label>
            <span>{{ t('decisionSpaces.decision.challenge.option') }}</span>
            <select v-model="challengedOptionId">
              <option v-for="option in optionList" :key="option.id" :value="option.id">
                {{ option.title }}
              </option>
            </select>
          </label>

          <div class="decision-form-actions">
            <button type="button" :disabled="opening" @click="openChallenge">
              {{
                opening
                  ? t('decisionSpaces.decision.challenge.opening')
                  : t('decisionSpaces.decision.challenge.open')
              }}
            </button>
          </div>

          <p v-if="openError" class="decision-form-error" role="alert">{{ openError }}</p>
          <p v-if="challengeReadError" class="decision-form-error" role="alert">
            {{ t('decisionSpaces.decision.loadFailed') }}
          </p>
          <p v-if="settleError" class="decision-form-error" role="alert">{{ settleError }}</p>

          <div v-if="currentRun" class="run">
            <p class="run-head">
              <span class="run-status">{{ runStatusLabel(currentRun.status) }}</span>
              <span class="run-model">{{ modelLabel(currentRun) }}</span>
            </p>
            <p v-if="currentRun.failure_reason" class="run-failure">
              {{
                t('decisionSpaces.decision.challenge.failure', { reason: currentRun.failure_reason })
              }}
            </p>

            <h4 class="decision-group">{{ t('decisionSpaces.decision.challenge.findings') }}</h4>
            <p v-if="!currentFindings.length" class="decision-empty">
              {{ t('decisionSpaces.decision.challenge.findingsEmpty') }}
            </p>
            <ul v-else class="finding-list">
              <li v-for="finding in currentFindings" :key="finding.id" class="finding">
                <p class="finding-head">
                  <span class="finding-kind">{{ kindLabel(finding.kind) }}</span>
                  <span class="finding-severity">{{ severityLabel(finding.severity) }}</span>
                  <span class="finding-status">{{ findingStatusLabel(finding.status) }}</span>
                </p>
                <p class="finding-detail">{{ finding.detail }}</p>
                <p class="finding-origin">{{ originLabel(finding.origin) }}</p>
                <div v-if="finding.status === 'proposed'" class="decision-form-actions">
                  <button
                    type="button"
                    class="decision-secondary"
                    :disabled="settling === finding.id"
                    @click="settle(finding, 'confirmed')"
                  >
                    {{
                      settling === finding.id
                        ? t('decisionSpaces.decision.challenge.confirming')
                        : t('decisionSpaces.decision.challenge.confirm')
                    }}
                  </button>
                  <button
                    type="button"
                    class="decision-secondary"
                    :disabled="settling === finding.id"
                    @click="settle(finding, 'dismissed')"
                  >
                    {{
                      settling === finding.id
                        ? t('decisionSpaces.decision.challenge.dismissing')
                        : t('decisionSpaces.decision.challenge.dismiss')
                    }}
                  </button>
                </div>
              </li>
            </ul>

            <div v-if="currentRun.status === 'FAILED'" class="decision-form-actions">
              <button type="button" :disabled="opening" @click="openChallenge">
                {{ t('decisionSpaces.decision.challenge.retry') }}
              </button>
            </div>
          </div>
          <p v-else class="decision-empty">{{ t('decisionSpaces.decision.challenge.empty') }}</p>

          <p v-if="coverage" class="decision-hint">{{ coverageLabel() }}</p>
          <p class="decision-note">{{ t('decisionSpaces.decision.challenge.criticNote') }}</p>
        </div>

        <div class="decision-block">
          <h3>{{ t('decisionSpaces.decision.record.title') }}</h3>
          <p class="decision-hint">{{ t('decisionSpaces.decision.record.intro') }}</p>

          <div v-if="record" class="record">
            <p class="record-head">
              <span class="record-version">
                {{ t('decisionSpaces.decision.record.version', { number: record.version }) }}
              </span>
              <span class="record-meta">
                {{
                  t('decisionSpaces.decision.record.committed', {
                    name: memberName(record.decided_by),
                    date: dateLabel(record.created_at),
                  })
                }}
              </span>
            </p>
            <dl class="record-fields">
              <div>
                <dt>{{ t('decisionSpaces.decision.record.selected') }}</dt>
                <dd>{{ optionTitle(record.selected_option_id) }}</dd>
              </div>
              <div>
                <dt>{{ t('decisionSpaces.decision.record.rationale') }}</dt>
                <dd>{{ record.rationale }}</dd>
              </div>
              <div>
                <dt>{{ t('decisionSpaces.decision.record.rejected') }}</dt>
                <dd v-if="record.rejected_option_ids.length">
                  {{ record.rejected_option_ids.map(optionTitle).join(' · ') }}
                </dd>
                <dd v-else>{{ t('decisionSpaces.decision.record.absent') }}</dd>
              </div>
              <div>
                <dt>{{ t('decisionSpaces.decision.record.arguments') }}</dt>
                <dd v-if="record.arguments.length">
                  {{
                    record.arguments
                      .map(argument => argumentLabel(argument.contribution_id, argument.side))
                      .join(' · ')
                  }}
                </dd>
                <dd v-else>{{ t('decisionSpaces.decision.record.absent') }}</dd>
              </div>
              <div>
                <dt>{{ t('decisionSpaces.decision.record.assumptions') }}</dt>
                <dd>{{ record.critical_assumptions || t('decisionSpaces.decision.record.absent') }}</dd>
              </div>
              <div>
                <dt>{{ t('decisionSpaces.decision.record.uncertainty') }}</dt>
                <dd>{{ record.uncertainty || t('decisionSpaces.decision.record.absent') }}</dd>
              </div>
              <div>
                <dt>{{ t('decisionSpaces.decision.record.criteria') }}</dt>
                <dd>{{ record.success_criteria || t('decisionSpaces.decision.record.absent') }}</dd>
              </div>
              <div>
                <dt>{{ t('decisionSpaces.decision.record.triggers') }}</dt>
                <dd v-if="record.revisit_triggers && record.revisit_triggers.length">
                  {{ record.revisit_triggers.map(triggerLabel).join(' · ') }}
                </dd>
                <dd v-else>{{ t('decisionSpaces.decision.record.absent') }}</dd>
              </div>
            </dl>
          </div>
          <p v-else class="decision-empty">{{ t('decisionSpaces.decision.record.empty') }}</p>

          <h4 class="decision-group">{{ t('decisionSpaces.decision.record.versions') }}</h4>
          <ul v-if="versions && versions.length" class="version-list">
            <li v-for="version in versions" :key="version.id" class="version">
              <p class="version-head">
                <span class="version-number">
                  {{ t('decisionSpaces.decision.record.version', { number: version.version }) }}
                </span>
                <span class="version-meta">{{ dateLabel(version.created_at) }}</span>
              </p>
              <p class="version-proposal">{{ version.rationale }}</p>
            </li>
          </ul>
          <p v-else class="decision-empty">{{ t('decisionSpaces.decision.record.versionsEmpty') }}</p>

          <template v-if="canCommit">
            <h4 class="decision-group">{{ t('decisionSpaces.decision.record.form.title') }}</h4>
            <form class="decision-form" @submit.prevent="commitRecord">
              <label>
                <span>{{ t('decisionSpaces.decision.record.form.selectedOption') }}</span>
                <select v-model="commitOption">
                  <option v-for="option in optionList" :key="option.id" :value="option.id">
                    {{ option.title }}
                  </option>
                </select>
              </label>
              <label>
                <span>{{ t('decisionSpaces.decision.record.form.rationale') }}</span>
                <textarea v-model="commitRationale" rows="3" />
              </label>

              <fieldset class="decision-choice">
                <legend>{{ t('decisionSpaces.decision.record.rejected') }}</legend>
                <p class="decision-hint">
                  {{ t('decisionSpaces.decision.record.form.rejectedHint') }}
                </p>
                <label v-for="option in otherOptions" :key="option.id" class="decision-check">
                  <input v-model="commitRejected" type="checkbox" :value="option.id">
                  <span>{{ option.title }}</span>
                </label>
              </fieldset>

              <fieldset class="decision-choice">
                <legend>{{ t('decisionSpaces.decision.record.arguments') }}</legend>
                <p class="decision-hint">
                  {{ t('decisionSpaces.decision.record.form.argumentsHint') }}
                </p>
                <ul v-if="commitArguments.length" class="argument-list">
                  <li v-for="(row, index) in commitArguments" :key="row.contributionId + row.side">
                    <span class="argument-label">
                      {{ argumentLabel(row.contributionId, row.side) }}
                    </span>
                    <button type="button" class="decision-secondary" @click="removeArgument(index)">
                      {{ t('decisionSpaces.decision.record.form.removeArgument') }}
                    </button>
                  </li>
                </ul>
                <div class="argument-add">
                  <label>
                    <span>{{ t('decisionSpaces.decision.record.form.contribution') }}</span>
                    <select v-model="argumentContribution">
                      <option value="">{{ t('decisionSpaces.decision.record.form.choose') }}</option>
                      <option v-for="candidate in argumentCandidates" :key="candidate.id" :value="candidate.id">
                        {{ candidate.title }}
                      </option>
                    </select>
                  </label>
                  <label>
                    <span>{{ t('decisionSpaces.decision.record.form.side') }}</span>
                    <select v-model="argumentSide">
                      <option value="for">{{ t('decisionSpaces.decision.record.for') }}</option>
                      <option value="against">{{ t('decisionSpaces.decision.record.against') }}</option>
                    </select>
                  </label>
                  <button type="button" class="decision-secondary" @click="addArgument">
                    {{ t('decisionSpaces.decision.record.form.addArgument') }}
                  </button>
                </div>
              </fieldset>

              <label>
                <span>{{ t('decisionSpaces.decision.record.assumptions') }}</span>
                <textarea v-model="commitAssumptions" rows="2" />
              </label>
              <label>
                <span>{{ t('decisionSpaces.decision.record.uncertainty') }}</span>
                <textarea v-model="commitUncertainty" rows="2" />
              </label>
              <label>
                <span>{{ t('decisionSpaces.decision.record.criteria') }}</span>
                <textarea v-model="commitCriteria" rows="2" />
              </label>

              <fieldset class="decision-choice">
                <legend>{{ t('decisionSpaces.decision.record.triggers') }}</legend>
                <p class="decision-hint">
                  {{ t('decisionSpaces.decision.record.form.triggersHint') }}
                </p>
                <div v-for="(row, index) in triggers" :key="index" class="trigger-row">
                  <label>
                    <span>{{ t('decisionSpaces.decision.record.form.triggerMetric') }}</span>
                    <input v-model="row.metric" type="text">
                  </label>
                  <label>
                    <span>{{ t('decisionSpaces.decision.record.form.triggerDirection') }}</span>
                    <select v-model="row.direction">
                      <option value="">{{ t('decisionSpaces.decision.record.form.directionNone') }}</option>
                      <option value="above">{{ t('decisionSpaces.decision.record.form.above') }}</option>
                      <option value="below">{{ t('decisionSpaces.decision.record.form.below') }}</option>
                    </select>
                  </label>
                  <label>
                    <span>{{ t('decisionSpaces.decision.record.form.triggerThreshold') }}</span>
                    <input v-model="row.threshold" type="text">
                  </label>
                  <label>
                    <span>{{ t('decisionSpaces.decision.record.form.triggerNote') }}</span>
                    <input v-model="row.note" type="text">
                  </label>
                  <button type="button" class="decision-secondary" @click="removeTrigger(index)">
                    {{ t('decisionSpaces.decision.record.form.removeTrigger') }}
                  </button>
                </div>
                <button type="button" class="decision-secondary" @click="addTrigger">
                  {{ t('decisionSpaces.decision.record.form.addTrigger') }}
                </button>
              </fieldset>

              <p v-if="commitError" class="decision-form-error" role="alert">{{ commitError }}</p>
              <div class="decision-form-actions">
                <button type="submit" :disabled="committing">
                  {{
                    committing
                      ? t('decisionSpaces.decision.record.form.submitting')
                      : t('decisionSpaces.decision.record.form.submit')
                  }}
                </button>
              </div>
            </form>
          </template>
          <p v-else class="decision-hint">
            {{
              t('decisionSpaces.decision.record.notReady', {
                status: spaceStatus
                  ? t('decisionSpaces.status.' + spaceStatus)
                  : t('decisionSpaces.decision.record.absent'),
              })
            }}
          </p>
        </div>
      </template>
    </template>
  </section>
</template>

<style scoped>
.decision {
  display: grid;
  gap: 8px;
  max-width: 76ch;
}

.decision h2 {
  margin: 0;
  color: var(--kollio-heading);
  font-size: var(--kollio-text-title);
  font-weight: var(--kollio-weight-display);
}

.decision-intro,
.decision-hint,
.decision-empty,
.decision-note {
  margin: 0;
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-small);
  line-height: var(--kollio-leading-body);
}

.decision-note {
  font-style: italic;
}

.decision-error,
.decision-form-error {
  margin: 0;
  color: var(--ui-error);
  font-size: var(--kollio-text-caption);
  font-weight: var(--kollio-weight-strong);
}

.decision-empty-state {
  display: grid;
  gap: 6px;
  margin-top: 12px;
}

.decision-empty-state h3 {
  margin: 0;
  color: var(--kollio-heading);
  font-size: var(--kollio-text-lead);
  font-weight: var(--kollio-weight-strong);
}

.decision-block {
  display: grid;
  gap: 10px;
  margin-top: 26px;
  border-top: 1px solid var(--ui-border);
  padding-top: 18px;
}

.decision-block h3 {
  margin: 0;
  color: var(--kollio-heading);
  font-size: var(--kollio-text-lead);
  font-weight: var(--kollio-weight-strong);
}

.decision-group {
  margin: 14px 0 0;
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-micro);
  font-weight: var(--kollio-weight-strong);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.run,
.record {
  display: grid;
  gap: 10px;
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-md);
  background: var(--ui-bg-elevated);
  padding: 16px;
}

.run-head,
.record-head,
.version-head {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin: 0;
}

.run-status,
.finding-status,
.record-version,
.version-number {
  border-radius: var(--kollio-radius-pill);
  background: var(--kollio-active-wash);
  color: var(--kollio-active-ink);
  font-size: var(--kollio-text-micro);
  font-weight: var(--kollio-weight-strong);
  letter-spacing: 0.04em;
  padding: 2px 10px;
}

.run-model,
.record-meta,
.version-meta,
.finding-origin {
  margin: 0;
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-caption);
}

.run-failure {
  margin: 0;
  border-radius: var(--kollio-radius-sm);
  background: var(--kollio-active-wash);
  color: var(--ui-error);
  font-size: var(--kollio-text-caption);
  font-weight: var(--kollio-weight-strong);
  padding: 8px 12px;
}

.finding-list,
.version-list,
.argument-list,
.cluster-list {
  display: grid;
  gap: 12px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.finding,
.version,
.argument-list li {
  display: grid;
  gap: 6px;
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-md);
  background: var(--ui-bg-elevated);
  padding: 14px;
}

.finding-head {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin: 0;
}

.finding-kind {
  color: var(--kollio-heading);
  font-size: var(--kollio-text-small);
  font-weight: var(--kollio-weight-strong);
}

.finding-severity {
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-micro);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.finding-detail {
  margin: 0;
  color: var(--kollio-heading);
  font-size: var(--kollio-text-small);
  line-height: var(--kollio-leading-body);
}

.record-fields {
  display: grid;
  gap: 10px;
  margin: 0;
}

.record-fields dt {
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-micro);
  font-weight: var(--kollio-weight-strong);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.record-fields dd {
  margin: 2px 0 0;
  color: var(--kollio-heading);
  font-size: var(--kollio-text-small);
  line-height: var(--kollio-leading-body);
  white-space: pre-wrap;
}

.version-proposal {
  margin: 0;
  color: var(--kollio-heading);
  font-size: var(--kollio-text-small);
}

.decision-form {
  display: grid;
  gap: 12px;
}

.decision-form label,
.argument-add label {
  display: grid;
  gap: 4px;
}

.decision-form label > span,
.argument-add label > span,
.decision-choice legend {
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-micro);
  font-weight: var(--kollio-weight-strong);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.decision-form input[type='text'],
.decision-form textarea,
.decision-form select,
.argument-add select {
  min-height: 44px;
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-sm);
  background: var(--ui-bg-elevated);
  color: var(--kollio-heading);
  font: inherit;
  padding: 8px 10px;
}

.decision-form textarea {
  resize: vertical;
}

.decision-form input:focus-visible,
.decision-form textarea:focus-visible,
.decision-form select:focus-visible,
.argument-add select:focus-visible,
.decision-form button:focus-visible {
  outline: 2px solid var(--kollio-active-ink);
  outline-offset: 1px;
}

.decision-choice {
  display: grid;
  gap: 8px;
  margin: 0;
  border: 1px dashed var(--ui-border);
  border-radius: var(--kollio-radius-md);
  padding: 12px;
}

.decision-check {
  display: flex;
  gap: 8px;
  align-items: center;
}

.decision-check span {
  color: var(--kollio-heading);
  font-size: var(--kollio-text-small);
}

.argument-add {
  display: grid;
  gap: 8px;
  grid-template-columns: 1fr auto auto;
  align-items: end;
}

.argument-label {
  color: var(--kollio-heading);
  font-size: var(--kollio-text-small);
}

.trigger-row {
  display: grid;
  gap: 8px;
  grid-template-columns: repeat(4, minmax(0, 1fr)) auto;
  align-items: end;
}

.decision-form-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.decision-form-actions button {
  min-height: 44px;
  border: 0;
  border-radius: var(--kollio-radius-md);
  background: var(--kollio-heading);
  color: var(--ui-bg-elevated);
  cursor: pointer;
  font: inherit;
  font-weight: var(--kollio-weight-strong);
  padding: 0 20px;
}

.decision-secondary {
  min-height: 44px;
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-md);
  background: var(--ui-bg-elevated);
  color: var(--kollio-heading);
  cursor: pointer;
  font: inherit;
  padding: 0 16px;
}

.decision-form-actions button:disabled,
.decision-secondary:disabled {
  opacity: 0.6;
}

@media (max-width: 760px) {
  .argument-add,
  .trigger-row {
    grid-template-columns: 1fr;
  }
}
</style>
