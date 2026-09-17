<script setup lang="ts">
import type {
  ClusterResponse,
  MapContributionResponse,
  MapResponse,
  RelationResponse,
  WorkspaceResponse,
} from '@kollio/api-client'

definePageMeta({ layout: 'workspace', middleware: 'authenticated' })

const { t } = useI18n()
const route = useRoute()
const requestFetch = useRequestFetch()
const localePath = useLocalePath()
const spaceId = String(route.params.spaceId)
const glyphs = Object.freeze({ plus: '＋' })
const kinds = ['idea', 'claim', 'evidence', 'objection', 'constraint'] as const
const relationTypes = [
  'SUPPORTS',
  'CONTRADICTS',
  'DUPLICATES',
  'ALTERNATIVE_TO',
  'DERIVED_FROM',
  'SUPERSEDES',
  'EVIDENCE_FOR',
  'EVIDENCE_AGAINST',
] as const

const relationFormOpen = ref(false)
const relationFrom = ref('')
const relationTo = ref('')
const relationType = ref<string>('SUPPORTS')
const relationError = ref<string>()
const creatingRelation = ref(false)
const removingRelation = ref('')
const relationRemoveError = ref<string>()

const clusterFormOpen = ref(false)
const clusterTitle = ref('')
const clusterFormError = ref<string>()
const creatingCluster = ref(false)
const clusterError = ref<string>()
const removingCluster = ref('')
const memberChoice = ref<Record<string, string>>({})
const addingMember = ref('')
const removingMember = ref('')
const memberError = ref<string>()

const { data: workspaces } = await useAsyncData('workspaces', () =>
  requestFetch<WorkspaceResponse[]>('/api/workspaces'),
)

const workspaceId = computed(() => {
  const requested = typeof route.query.workspace === 'string' ? route.query.workspace : undefined
  return workspaces.value?.find(entry => entry.id === requested)?.id ?? workspaces.value?.[0]?.id
})

const mapPath = computed(
  () =>
    '/api/workspaces/' +
    encodeURIComponent(workspaceId.value ?? '') +
    '/decision-spaces/' +
    encodeURIComponent(spaceId),
)

const {
  data: map,
  error: mapError,
  refresh: refreshMap,
} = await useAsyncData(
  'converge-map-' + spaceId,
  async () => {
    if (!workspaceId.value) return undefined
    return requestFetch<MapResponse>(mapPath.value + '/converge/map')
  },
  { watch: [workspaceId] },
)

const contributions = computed(() => map.value?.contributions ?? [])
const relations = computed(() => map.value?.relations ?? [])
const clusters = computed(() => map.value?.clusters ?? [])
const hasReasoning = computed(() => contributions.value.length > 0)

watch(
  contributions,
  (list) => {
    const first = list[0]?.id ?? ''
    const second = list[1]?.id ?? ''
    if (!list.some(entry => entry.id === relationFrom.value)) relationFrom.value = first
    if (!list.some(entry => entry.id === relationTo.value)) relationTo.value = second
  },
  { immediate: true },
)

function kindLabel(kind: string): string {
  return kinds.includes(kind as (typeof kinds)[number])
    ? t('decisionSpaces.converge.kinds.' + kind)
    : kind
}

function relationTypeLabel(value: string): string {
  return t('decisionSpaces.converge.relations.types.' + value)
}

function contributionTitle(contributionId: string): string {
  return contributions.value.find(entry => entry.id === contributionId)?.title ?? contributionId
}

function clusterTitleOf(contribution: MapContributionResponse): string {
  const cluster = clusters.value.find(entry => entry.id === contribution.cluster_id)
  return cluster?.title ?? t('decisionSpaces.converge.map.ungrouped')
}

function membersOf(cluster: ClusterResponse): MapContributionResponse[] {
  const ids = cluster.member_ids ?? []
  return contributions.value.filter(entry => ids.includes(entry.id))
}

function candidatesFor(cluster: ClusterResponse): MapContributionResponse[] {
  const ids = cluster.member_ids ?? []
  return contributions.value.filter(entry => !ids.includes(entry.id))
}

function openRelationForm(): void {
  relationFormOpen.value = true
  relationError.value = undefined
}

function cancelRelationForm(): void {
  relationFormOpen.value = false
  relationError.value = undefined
}

function openClusterForm(): void {
  clusterFormOpen.value = true
  clusterFormError.value = undefined
}

function cancelClusterForm(): void {
  clusterFormOpen.value = false
  clusterTitle.value = ''
  clusterFormError.value = undefined
}

async function createRelation(): Promise<void> {
  if (relationFrom.value === relationTo.value) {
    relationError.value = t('decisionSpaces.converge.relations.form.sameEnds')
    return
  }
  creatingRelation.value = true
  relationError.value = undefined
  try {
    await $fetch(mapPath.value + '/relations', {
      method: 'POST',
      body: {
        from_contribution_id: relationFrom.value,
        to_contribution_id: relationTo.value,
        relation_type: relationType.value,
      },
    })
    relationFormOpen.value = false
    await refreshMap()
  } catch {
    relationError.value = t('decisionSpaces.converge.relations.form.failed')
  } finally {
    creatingRelation.value = false
  }
}

async function removeRelation(relation: RelationResponse): Promise<void> {
  removingRelation.value = relation.id
  relationRemoveError.value = undefined
  try {
    await $fetch(mapPath.value + '/relations/' + encodeURIComponent(relation.id), {
      method: 'DELETE',
    })
    await refreshMap()
  } catch {
    relationRemoveError.value = t('decisionSpaces.converge.relations.removeFailed')
  } finally {
    removingRelation.value = ''
  }
}

async function createCluster(): Promise<void> {
  const title = clusterTitle.value.trim()
  if (!title) {
    clusterFormError.value = t('decisionSpaces.converge.clusters.form.nameRequired')
    return
  }
  creatingCluster.value = true
  clusterFormError.value = undefined
  try {
    await $fetch(mapPath.value + '/clusters', { method: 'POST', body: { title } })
    clusterTitle.value = ''
    clusterFormOpen.value = false
    await refreshMap()
  } catch {
    clusterFormError.value = t('decisionSpaces.converge.clusters.form.failed')
  } finally {
    creatingCluster.value = false
  }
}

async function removeCluster(cluster: ClusterResponse): Promise<void> {
  removingCluster.value = cluster.id
  clusterError.value = undefined
  try {
    await $fetch(mapPath.value + '/clusters/' + encodeURIComponent(cluster.id), {
      method: 'DELETE',
    })
    await refreshMap()
  } catch {
    clusterError.value = t('decisionSpaces.converge.clusters.removeFailed')
  } finally {
    removingCluster.value = ''
  }
}

async function addMember(cluster: ClusterResponse): Promise<void> {
  const chosen = memberChoice.value[cluster.id] ?? candidatesFor(cluster)[0]?.id
  if (!chosen) return
  addingMember.value = cluster.id
  memberError.value = undefined
  try {
    await $fetch(mapPath.value + '/clusters/' + encodeURIComponent(cluster.id) + '/members', {
      method: 'POST',
      body: { contribution_id: chosen },
    })
    memberChoice.value = { ...memberChoice.value, [cluster.id]: '' }
    await refreshMap()
  } catch {
    memberError.value = t('decisionSpaces.converge.clusters.addFailed')
  } finally {
    addingMember.value = ''
  }
}

async function removeMember(cluster: ClusterResponse, contributionId: string): Promise<void> {
  removingMember.value = contributionId
  memberError.value = undefined
  try {
    await $fetch(
      mapPath.value +
        '/clusters/' +
        encodeURIComponent(cluster.id) +
        '/members/' +
        encodeURIComponent(contributionId),
      { method: 'DELETE' },
    )
    await refreshMap()
  } catch {
    memberError.value = t('decisionSpaces.converge.clusters.removeMemberFailed')
  } finally {
    removingMember.value = ''
  }
}

useSeoMeta({ title: () => t('decisionSpaces.section.converge.title') })
</script>

<template>
  <section class="converge">
    <h2>{{ t('decisionSpaces.section.converge.title') }}</h2>
    <p class="converge-intro">{{ t('decisionSpaces.section.converge.body') }}</p>

    <p v-if="mapError" class="converge-error" role="alert">
      {{ t('decisionSpaces.converge.loadFailed') }}
    </p>

    <template v-else>
      <div v-if="!hasReasoning" class="converge-empty-state">
        <h3>{{ t('decisionSpaces.converge.empty.title') }}</h3>
        <p>{{ t('decisionSpaces.converge.empty.body') }}</p>
        <NuxtLink
          class="converge-link"
          :to="localePath('/workspace/decision-spaces/' + spaceId + '/explore')"
        >
          {{ t('decisionSpaces.converge.empty.action') }}
        </NuxtLink>
      </div>

      <template v-else>
        <div class="converge-block">
          <h3>{{ t('decisionSpaces.converge.map.title') }}</h3>
          <p class="converge-hint">{{ t('decisionSpaces.converge.map.intro') }}</p>
          <ul class="contribution-list">
            <li v-for="contribution in contributions" :key="contribution.id" class="contribution">
              <div class="contribution-head">
                <h4>{{ contribution.title }}</h4>
                <span class="contribution-kind">{{ kindLabel(contribution.kind) }}</span>
              </div>
              <p class="contribution-meta">
                {{ t('decisionSpaces.converge.map.belongs', { name: clusterTitleOf(contribution) }) }}
              </p>
            </li>
          </ul>
        </div>

        <div class="converge-block">
          <div class="converge-block-head">
            <h3>{{ t('decisionSpaces.converge.relations.title') }}</h3>
            <button
              type="button"
              class="converge-toggle"
              :aria-expanded="relationFormOpen"
              @click="openRelationForm"
            >
              <span aria-hidden="true" v-text="glyphs.plus" />
              {{ t('decisionSpaces.converge.relations.create') }}
            </button>
          </div>
          <p class="converge-hint">{{ t('decisionSpaces.converge.relations.intro') }}</p>

          <form v-if="relationFormOpen" class="converge-form" @submit.prevent="createRelation">
            <h4>{{ t('decisionSpaces.converge.relations.form.title') }}</h4>
            <label>
              <span>{{ t('decisionSpaces.converge.relations.form.from') }}</span>
              <select v-model="relationFrom">
                <option v-for="entry in contributions" :key="entry.id" :value="entry.id">
                  {{ entry.title }}
                </option>
              </select>
            </label>
            <label>
              <span>{{ t('decisionSpaces.converge.relations.form.to') }}</span>
              <select v-model="relationTo">
                <option v-for="entry in contributions" :key="entry.id" :value="entry.id">
                  {{ entry.title }}
                </option>
              </select>
            </label>
            <label>
              <span>{{ t('decisionSpaces.converge.relations.form.type') }}</span>
              <select v-model="relationType">
                <option v-for="value in relationTypes" :key="value" :value="value">
                  {{ relationTypeLabel(value) }}
                </option>
              </select>
            </label>
            <p v-if="relationError" class="converge-form-error" role="alert">{{ relationError }}</p>
            <div class="converge-form-actions">
              <button type="submit" :disabled="creatingRelation">
                {{
                  creatingRelation
                    ? t('decisionSpaces.converge.relations.form.submitting')
                    : t('decisionSpaces.converge.relations.form.submit')
                }}
              </button>
              <button type="button" class="converge-secondary" @click="cancelRelationForm">
                {{ t('decisionSpaces.cancel') }}
              </button>
            </div>
          </form>

          <p v-if="relationRemoveError" class="converge-form-error" role="alert">
            {{ relationRemoveError }}
          </p>
          <ul v-if="relations.length" class="relation-list">
            <li v-for="relation in relations" :key="relation.id" class="relation">
              <p class="relation-line">
                <span class="relation-end">{{ contributionTitle(relation.from_contribution_id) }}</span>
                <span class="relation-type">{{ relationTypeLabel(relation.relation_type) }}</span>
                <span class="relation-end">{{ contributionTitle(relation.to_contribution_id) }}</span>
              </p>
              <button
                type="button"
                class="converge-secondary"
                :disabled="removingRelation === relation.id"
                @click="removeRelation(relation)"
              >
                {{
                  removingRelation === relation.id
                    ? t('decisionSpaces.converge.relations.removing')
                    : t('decisionSpaces.converge.relations.remove')
                }}
              </button>
            </li>
          </ul>
          <p v-else class="converge-empty">{{ t('decisionSpaces.converge.relations.empty') }}</p>
        </div>

        <div class="converge-block">
          <div class="converge-block-head">
            <h3>{{ t('decisionSpaces.converge.clusters.title') }}</h3>
            <button
              type="button"
              class="converge-toggle"
              :aria-expanded="clusterFormOpen"
              @click="openClusterForm"
            >
              <span aria-hidden="true" v-text="glyphs.plus" />
              {{ t('decisionSpaces.converge.clusters.create') }}
            </button>
          </div>
          <p class="converge-hint">{{ t('decisionSpaces.converge.clusters.intro') }}</p>

          <form v-if="clusterFormOpen" class="converge-form" @submit.prevent="createCluster">
            <h4>{{ t('decisionSpaces.converge.clusters.form.title') }}</h4>
            <label>
              <span>{{ t('decisionSpaces.converge.clusters.form.name') }}</span>
              <input
                v-model="clusterTitle"
                type="text"
                :placeholder="t('decisionSpaces.converge.clusters.form.namePlaceholder')"
              >
            </label>
            <p v-if="clusterFormError" class="converge-form-error" role="alert">
              {{ clusterFormError }}
            </p>
            <div class="converge-form-actions">
              <button type="submit" :disabled="creatingCluster">
                {{
                  creatingCluster
                    ? t('decisionSpaces.converge.clusters.form.submitting')
                    : t('decisionSpaces.converge.clusters.form.submit')
                }}
              </button>
              <button type="button" class="converge-secondary" @click="cancelClusterForm">
                {{ t('decisionSpaces.cancel') }}
              </button>
            </div>
          </form>

          <p v-if="memberError" class="converge-form-error" role="alert">{{ memberError }}</p>
          <p v-if="clusterError" class="converge-form-error" role="alert">{{ clusterError }}</p>
          <ul v-if="clusters.length" class="cluster-list">
            <li v-for="cluster in clusters" :key="cluster.id" class="cluster">
              <div class="cluster-head">
                <h4>{{ cluster.title }}</h4>
              </div>
              <p class="cluster-members-label">
                {{ t('decisionSpaces.converge.clusters.members') }}
              </p>
              <ul v-if="membersOf(cluster).length" class="cluster-members">
                <li v-for="member in membersOf(cluster)" :key="member.id">
                  <span class="cluster-member-title">{{ member.title }}</span>
                  <button
                    type="button"
                    class="converge-secondary"
                    :disabled="removingMember === member.id"
                    @click="removeMember(cluster, member.id)"
                  >
                    {{
                      removingMember === member.id
                        ? t('decisionSpaces.converge.clusters.removingMember')
                        : t('decisionSpaces.converge.clusters.removeMember')
                    }}
                  </button>
                </li>
              </ul>
              <p v-else class="converge-empty">
                {{ t('decisionSpaces.converge.clusters.noMembers') }}
              </p>

              <div class="cluster-add">
                <label>
                  <span>{{ t('decisionSpaces.converge.clusters.addLabel') }}</span>
                  <select v-model="memberChoice[cluster.id]">
                    <option value="">{{ t('decisionSpaces.converge.clusters.choose') }}</option>
                    <option
                      v-for="candidate in candidatesFor(cluster)"
                      :key="candidate.id"
                      :value="candidate.id"
                    >
                      {{ candidate.title }}
                    </option>
                  </select>
                </label>
                <button
                  type="button"
                  :disabled="addingMember === cluster.id || !candidatesFor(cluster).length"
                  @click="addMember(cluster)"
                >
                  {{
                    addingMember === cluster.id
                      ? t('decisionSpaces.converge.clusters.adding')
                      : t('decisionSpaces.converge.clusters.add')
                  }}
                </button>
              </div>

              <button
                type="button"
                class="converge-secondary"
                :disabled="removingCluster === cluster.id"
                @click="removeCluster(cluster)"
              >
                {{
                  removingCluster === cluster.id
                    ? t('decisionSpaces.converge.clusters.removing')
                    : t('decisionSpaces.converge.clusters.remove')
                }}
              </button>
            </li>
          </ul>
          <p v-else class="converge-empty">{{ t('decisionSpaces.converge.clusters.empty') }}</p>
        </div>
      </template>
    </template>
  </section>
</template>

<style scoped>
.converge {
  display: grid;
  gap: 8px;
  max-width: 76ch;
}

.converge h2 {
  margin: 0;
  color: var(--kollio-heading);
  font-size: var(--kollio-text-title);
  font-weight: var(--kollio-weight-display);
}

.converge-intro,
.converge-hint,
.converge-empty,
.converge-empty-state p {
  margin: 0;
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-small);
  line-height: var(--kollio-leading-body);
}

.converge-error,
.converge-form-error {
  margin: 0;
  color: var(--ui-error);
  font-size: var(--kollio-text-caption);
  font-weight: var(--kollio-weight-strong);
}

.converge-empty-state {
  display: grid;
  gap: 10px;
  margin-top: 26px;
  padding: 20px;
  border: 1px dashed var(--ui-border);
  border-radius: var(--kollio-radius-md);
  background: var(--ui-bg-elevated);
}

.converge-empty-state h3 {
  margin: 0;
  color: var(--kollio-heading);
  font-size: var(--kollio-text-lead);
  font-weight: var(--kollio-weight-strong);
}

.converge-link {
  justify-self: start;
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  padding: 0 20px;
  border-radius: var(--kollio-radius-md);
  background: var(--kollio-heading);
  color: var(--ui-bg-elevated);
  font-size: var(--kollio-text-small);
  font-weight: var(--kollio-weight-strong);
  text-decoration: none;
}

.converge-block {
  margin-top: 26px;
  padding-top: 18px;
  border-top: 1px solid var(--ui-border);
}

.converge-block h3 {
  margin: 0;
  color: var(--kollio-heading);
  font-size: var(--kollio-text-lead);
  font-weight: var(--kollio-weight-strong);
}

.converge-block-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.converge-toggle {
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

.converge-hint {
  margin-top: 6px;
}

.converge-form {
  display: grid;
  gap: 12px;
  margin-top: 16px;
  padding: 16px;
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-md);
  background: var(--ui-bg-elevated);
}

.converge-form h4 {
  margin: 0;
  color: var(--kollio-heading);
  font-size: var(--kollio-text-body);
  font-weight: var(--kollio-weight-strong);
}

.converge-form label,
.cluster-add label {
  display: grid;
  gap: 6px;
}

.converge-form label > span,
.cluster-add label > span,
.cluster-members-label {
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-micro);
  font-weight: var(--kollio-weight-medium);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.converge-form input,
.converge-form select,
.cluster-add select {
  min-height: 44px;
  padding: 0 12px;
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-sm);
  background: var(--ui-bg);
  color: var(--kollio-heading);
  font-size: var(--kollio-text-small);
}

.converge-form input:focus-visible,
.converge-form select:focus-visible,
.cluster-add select:focus-visible {
  outline: 2px solid var(--kollio-active-ink);
  outline-offset: 1px;
}

.converge-form-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.converge-form-actions button,
.cluster-add button {
  min-height: 44px;
  padding: 0 20px;
  border: 1px solid var(--kollio-heading);
  border-radius: var(--kollio-radius-md);
  background: var(--kollio-heading);
  color: var(--ui-bg-elevated);
  font-size: var(--kollio-text-small);
  font-weight: var(--kollio-weight-strong);
  cursor: pointer;
}

.converge-secondary {
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

.converge button[disabled] {
  opacity: 0.6;
}

.contribution-list,
.relation-list,
.cluster-list,
.cluster-members {
  display: grid;
  gap: 12px;
  margin: 16px 0 0;
  padding: 0;
  list-style: none;
}

.contribution,
.relation,
.cluster {
  display: grid;
  gap: 10px;
  padding: 16px;
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-md);
  background: var(--ui-bg-elevated);
}

.contribution-head,
.cluster-head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: 10px;
}

.contribution-head h4,
.cluster-head h4 {
  margin: 0;
  color: var(--kollio-heading);
  font-size: var(--kollio-text-body);
  font-weight: var(--kollio-weight-strong);
}

.contribution-kind,
.relation-type {
  padding: 2px 10px;
  border-radius: var(--kollio-radius-pill);
  background: var(--kollio-active-wash);
  color: var(--kollio-active-ink);
  font-size: var(--kollio-text-micro);
  font-weight: var(--kollio-weight-medium);
}

.contribution-meta {
  margin: 0;
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-caption);
}

.relation-line {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin: 0;
  color: var(--kollio-heading);
  font-size: var(--kollio-text-small);
}

.relation-end {
  font-weight: var(--kollio-weight-medium);
}

.cluster-members-label {
  margin: 0;
}

.cluster-members li {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 8px 12px;
  border-radius: var(--kollio-radius-sm);
  background: var(--ui-bg-accented);
}

.cluster-member-title {
  color: var(--kollio-heading);
  font-size: var(--kollio-text-small);
}

.cluster-add {
  display: grid;
  gap: 12px;
  padding-top: 10px;
  border-top: 1px solid var(--ui-border);
}

@media (max-width: 760px) {
  .converge-block-head {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
