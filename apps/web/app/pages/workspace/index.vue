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
    <header class="inbox-header">
      <h1>{{ t('inbox.title') }}</h1>
      <p>{{ t('inbox.description') }}</p>
    </header>

    <p v-if="error" role="alert" class="inbox-error">{{ t('inbox.loadFailed') }}</p>

    <template v-else>
      <div v-if="!hasAnything" class="inbox-empty-state">
        <h2>{{ t('inbox.empty.title') }}</h2>
        <p>{{ t('inbox.empty.body') }}</p>
      </div>

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
  padding: 16px 16px 34px;
}

.inbox-header h1 {
  color: var(--kollio-heading);
  font-size: var(--kollio-display-section);
  font-weight: var(--kollio-weight-display);
  letter-spacing: -0.06em;
}

.inbox-header p {
  margin-top: 8px;
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-body);
  line-height: var(--kollio-leading-body);
}

.inbox-error {
  border: 1px solid var(--ui-error);
  border-radius: var(--kollio-radius-md);
  background: var(--ui-bg-elevated);
  padding: 14px 16px;
  color: var(--ui-error);
  font-size: var(--kollio-text-caption);
  font-weight: var(--kollio-weight-strong);
}

.inbox-empty-state {
  display: grid;
  gap: 8px;
  min-height: 220px;
  align-content: center;
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-lg);
  background: var(--ui-bg-elevated);
  padding: 24px;
}

.inbox-empty-state h2 {
  color: var(--kollio-heading);
  font-size: var(--kollio-text-title);
  font-weight: var(--kollio-weight-display);
}

.inbox-empty-state p {
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-small);
  line-height: var(--kollio-leading-body);
}

.inbox-section {
  display: grid;
  gap: 8px;
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
  gap: 10px;
  margin-top: 6px;
}

.inbox-entry-link {
  display: grid;
  gap: 6px;
  min-height: 64px;
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-lg);
  background: var(--ui-bg-elevated);
  padding: 14px 16px;
}

.inbox-entry-link:hover {
  border-color: var(--kollio-active-ink);
}

.inbox-entry-kind {
  color: var(--kollio-active-ink);
  font-size: var(--kollio-text-micro);
  font-weight: var(--kollio-weight-strong);
  letter-spacing: 0.08em;
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
  margin-top: 8px;
  border-top: 1px solid var(--ui-border);
  padding-top: 18px;
}

.inbox-spaces-link {
  display: inline-flex;
  min-height: 44px;
  align-items: center;
  color: var(--kollio-active-ink);
  font-size: var(--kollio-text-caption);
  font-weight: var(--kollio-weight-strong);
}

.inbox-entry-link:focus-visible,
.inbox-spaces-link:focus-visible {
  outline: 2px solid var(--kollio-active-ink);
  outline-offset: 1px;
}

@media (max-width: 760px) {
  .inbox {
    padding: 12px 12px 28px;
  }
}
</style>
