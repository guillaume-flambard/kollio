<script setup lang="ts">
import type { DecisionInboxResponse, InboxEntryResponse, InboxSectionResponse } from '@kollio/api-client'

definePageMeta({ layout: 'workspace', middleware: 'authenticated' })

const { t } = useI18n()
const requestFetch = useRequestFetch()
const localePath = useLocalePath()

const { data: inbox, error } = await useAsyncData('inbox', () =>
  requestFetch<DecisionInboxResponse>('/api/inbox'),
)

const sections = computed(() => [
  { key: 'needsConvergence', value: inbox.value?.needs_convergence },
  { key: 'needsMyInput', value: inbox.value?.needs_my_input },
  { key: 'readyToDecide', value: inbox.value?.ready_to_decide },
  { key: 'needsLearning', value: inbox.value?.needs_learning },
])

const hasAnything = computed(() =>
  sections.value.some(section => (section.value?.entries.length ?? 0) > 0),
)

const nextEntry = computed(() => {
  const candidates = sections.value.flatMap(section => entriesOf(section.value))
  return candidates.reduce<InboxEntryResponse | undefined>((oldest, entry) => {
    if (!oldest || new Date(entry.created_at).getTime() < new Date(oldest.created_at).getTime()) return entry
    return oldest
  }, undefined)
})

const { formatDate: dateLabel } = useFormatters()

function entriesOf(section?: InboxSectionResponse) {
  return section?.entries ?? []
}

function remaining(section?: InboxSectionResponse) {
  const total = section?.total ?? 0
  const shown = section?.entries.length ?? 0
  return Math.max(total - shown, 0)
}

function kindLabel(kind: InboxEntryResponse['kind']) {
  return t(`inbox.kinds.${kind}`)
}

function sectionOf(kind: InboxEntryResponse['kind']) {
  switch (kind) {
    case 'contribution_awaits_confirmation':
      return 'explore'
    case 'finding_awaits_resolution':
    case 'decision_awaits_commitment':
      return 'decision'
    case 'experiment_awaits_outcome':
      return 'experiment'
    case 'learning_awaits_confirmation':
      return 'learning'
    default:
      return 'converge'
  }
}

function entryLink(entry: InboxEntryResponse) {
  return {
    path: localePath(`/workspace/decision-spaces/${entry.space_id}/${sectionOf(entry.kind)}`),
    query: { workspace: entry.workspace_id },
  }
}

function entryKey(entry: InboxEntryResponse) {
  return `${entry.kind}:${entry.space_id}:${entry.subject_id ?? 'space'}`
}

const spacesPath = computed(() => localePath('/workspace/decision-spaces'))

useSeoMeta({ title: () => t('inbox.metaTitle') })
</script>

<template>
  <div class="inbox">
    <KollioPageHeader class="inbox-header" :title="t('inbox.title')" :summary="t('inbox.description')" />

    <KollioFeedbackState v-if="error" :title="t('inbox.loadFailed')" tone="error" role="alert" />

    <template v-else>
      <KollioFeedbackState v-if="!hasAnything" class="inbox-empty-state" :title="t('inbox.empty.title')" :body="t('inbox.empty.body')" />

      <section v-if="nextEntry" class="inbox-next-action" aria-labelledby="inbox-next-title">
        <KollioReasoningBlock :title="t('inbox.next.title')">
          <p class="inbox-next-action__kind">{{ kindLabel(nextEntry.kind) }}</p>
          <h2 id="inbox-next-title">{{ nextEntry.space_question }}</h2>
          <p v-if="nextEntry.detail">{{ nextEntry.detail }}</p>
          <KollioPrimaryAction :label="t('inbox.next.action')" :to="entryLink(nextEntry)" />
        </KollioReasoningBlock>
      </section>

      <section v-for="section in sections" :key="section.key" class="inbox-section">
        <h2>{{ t(`inbox.sections.${section.key}.title`) }}</h2>
        <p class="inbox-intro">{{ t(`inbox.sections.${section.key}.intro`) }}</p>

        <ul v-if="entriesOf(section.value).length" class="inbox-list">
          <li v-for="entry in entriesOf(section.value)" :key="entryKey(entry)" class="inbox-entry">
            <NuxtLink class="inbox-entry-link" :to="entryLink(entry)">
              <span class="inbox-entry-kind">{{ kindLabel(entry.kind) }}</span>
              <span class="inbox-entry-question">{{ entry.space_question }}</span>
              <span v-if="entry.detail" class="inbox-entry-detail">{{ entry.detail }}</span>
              <span class="inbox-entry-date">{{ dateLabel(entry.created_at) }}</span>
            </NuxtLink>
          </li>
        </ul>
        <p v-else class="inbox-empty">{{ t(`inbox.sections.${section.key}.empty`) }}</p>

        <p v-if="remaining(section.value)" class="inbox-more">
          {{ t('inbox.more', { count: remaining(section.value) }) }}
        </p>
      </section>

      <section class="inbox-section inbox-memory">
        <h2>{{ t('inbox.memory.title') }}</h2>
        <p class="inbox-intro">{{ t('inbox.memory.body') }}</p>
      </section>

      <p class="inbox-spaces">
        <NuxtLink class="inbox-spaces-link" :to="spacesPath">{{ t('inbox.spacesLink') }}</NuxtLink>
      </p>
    </template>
  </div>
</template>

<style scoped>
.inbox {
  display: grid;
  gap: var(--kollio-space-lg);
  width: 100%;
  padding: var(--kollio-space-md) var(--kollio-space-md) var(--kollio-space-xl);
}

.inbox-empty-state {
  min-height: var(--kollio-space-4xl);
}

.inbox-next-action { border: 1px solid var(--ui-border); border-radius: var(--kollio-radius-lg); background: var(--ui-bg-elevated); padding: var(--kollio-space-md); }
.inbox-next-action :deep(.reasoning-block) { border-left-color: var(--kollio-connector); }
.inbox-next-action h2 { color: var(--kollio-heading); font-size: var(--kollio-text-lead); font-weight: var(--kollio-weight-display); }
.inbox-next-action__kind { color: var(--kollio-active-ink); font-size: var(--kollio-text-micro); font-weight: var(--kollio-weight-strong); letter-spacing: var(--kollio-tracking-label); text-transform: uppercase; }

.inbox-section {
  display: grid;
  gap: var(--kollio-space-sm);
}

.inbox-section h2 {
  color: var(--kollio-heading);
  font-size: var(--kollio-text-title);
  font-weight: var(--kollio-weight-display);
}

.inbox-intro {
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-small);
  line-height: var(--kollio-leading-body);
}

.inbox-list {
  display: grid;
  gap: var(--kollio-space-sm);
  margin-top: var(--kollio-space-sm);
}

.inbox-entry-link {
  display: grid;
  gap: 6px;
  min-height: var(--kollio-control-height);
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-lg);
  background: var(--ui-bg-elevated);
  padding: var(--kollio-space-md);
}

.inbox-entry-link:hover {
  border-color: var(--kollio-active-ink);
}

.inbox-entry-kind {
  color: var(--kollio-active-ink);
  font-size: var(--kollio-text-micro);
  font-weight: var(--kollio-weight-strong);
  letter-spacing: var(--kollio-tracking-label);
  text-transform: uppercase;
}

.inbox-entry-question {
  color: var(--kollio-heading);
  font-size: var(--kollio-text-body);
  font-weight: var(--kollio-weight-strong);
}

.inbox-entry-detail {
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-small);
  line-height: var(--kollio-leading-body);
}

.inbox-entry-date {
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-micro);
}

.inbox-empty {
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-small);
}

.inbox-more {
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-caption);
}

.inbox-memory {
  margin-top: var(--kollio-space-sm);
  border-top: 1px solid var(--ui-border);
  padding-top: var(--kollio-space-lg);
}

.inbox-spaces-link {
  display: inline-flex;
  min-height: var(--kollio-control-height);
  align-items: center;
  color: var(--kollio-active-ink);
  font-size: var(--kollio-text-caption);
  font-weight: var(--kollio-weight-strong);
}

.inbox-entry-link:focus-visible,
.inbox-spaces-link:focus-visible {
  outline: 2px solid var(--kollio-active-ink);
  outline-offset: var(--kollio-space-xs);
}

@media (max-width: 760px) {
  .inbox {
    padding: var(--kollio-space-md);
  }
}
</style>
