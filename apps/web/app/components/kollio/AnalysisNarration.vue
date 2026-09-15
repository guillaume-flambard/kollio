<script setup lang="ts">
interface ProgressItem {
  id?: string
  url?: string
  text?: string
  snippet?: string
}
interface AnalysisProgress {
  profile?: string | null
  objectives?: string[]
  constraints?: string[]
  learnings?: ProgressItem[]
  sources?: ProgressItem[]
  areas?: number
}

const props = defineProps<{ progress?: AnalysisProgress | null }>()

const { t } = useI18n()

const GROUP_CAP = 3

function firstItems(items: unknown[]): string[] {
  return items.slice(0, GROUP_CAP).map(String)
}

function itemsWithMore(items: unknown[], extraKey: string): string[] {
  const shown = firstItems(items)
  const rest = items.length - shown.length
  return rest > 0 ? [...shown, t(extraKey, { count: rest })] : shown
}

const groups = computed<{ key: string, title: string, items: string[] }[]>(() => {
  const progress = props.progress
  if (!progress) {
    return [
      { key: 'context', title: t('ideas.deposit.narration.context'), items: [] },
      { key: 'areas', title: t('ideas.deposit.narration.areas'), items: [] },
      { key: 'deciding', title: t('ideas.deposit.narration.deciding'), items: [] },
    ]
  }
  const list: { key: string, title: string, items: string[] }[] = [
    {
      key: 'context',
      title: progress.profile
        ? t('ideas.deposit.narration.contextNamed', { name: progress.profile })
        : t('ideas.deposit.narration.context'),
      items: [],
    },
  ]
  const objectives = progress.objectives ?? []
  if (objectives.length) {
    list.push({
      key: 'objectives',
      title: t('ideas.deposit.narration.objectives', { count: objectives.length }),
      items: itemsWithMore(objectives, 'ideas.deposit.narration.more'),
    })
  }
  const constraints = progress.constraints ?? []
  if (constraints.length) {
    list.push({
      key: 'constraints',
      title: t('ideas.deposit.narration.constraints', { count: constraints.length }),
      items: itemsWithMore(constraints, 'ideas.deposit.narration.more'),
    })
  }
  const learnings = (progress.learnings ?? []).map(item => item.text ?? item.id ?? '').filter(Boolean)
  if (learnings.length) {
    list.push({
      key: 'learnings',
      title: t('ideas.deposit.narration.learnings', { count: learnings.length }),
      items: itemsWithMore(learnings, 'ideas.deposit.narration.more'),
    })
  }
  const sources = (progress.sources ?? [])
    .map(item => item.snippet || item.url || item.id || '')
    .filter(Boolean)
  if (sources.length) {
    list.push({
      key: 'sources',
      title: t('ideas.deposit.narration.sources', { count: sources.length }),
      items: itemsWithMore(sources, 'ideas.deposit.narration.more'),
    })
  }
  list.push({ key: 'areas', title: t('ideas.deposit.narration.areas'), items: [] })
  list.push({ key: 'deciding', title: t('ideas.deposit.narration.deciding'), items: [] })
  return list
})

const active = ref(0)
let timer: ReturnType<typeof setInterval> | undefined

function settle() {
  active.value = groups.value.length - 1
}

onMounted(() => {
  if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false) {
    settle()
    return
  }
  timer = setInterval(() => {
    if (active.value >= groups.value.length - 1) {
      clearInterval(timer)
      return
    }
    active.value += 1
  }, 700)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <div class="narration" role="status">
    <p class="narration-title">{{ t('ideas.deposit.running') }}</p>
    <ol class="narration-groups">
      <li
        v-for="(group, index) in groups"
        :key="group.key"
        class="narration-group"
        :data-done="index <= active"
        :data-current="index === active"
        :data-group="group.key"
      >
        <span class="narration-dot" aria-hidden="true" />
        <div class="narration-body">
          <p class="narration-label">{{ group.title }}</p>
          <ul v-if="group.items.length" class="narration-items">
            <li v-for="(item, itemIndex) in group.items" :key="`${group.key}-${itemIndex}`">
              {{ item }}
            </li>
          </ul>
        </div>
      </li>
    </ol>
  </div>
</template>

<style scoped>
.narration {
  display: grid;
  gap: 14px;
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-lg);
  background: color-mix(in srgb, var(--ui-bg-muted) 72%, transparent);
  padding: 18px 20px;
}

.narration-title {
  margin: 0;
  color: var(--kollio-active-ink);
  font-size: var(--kollio-text-body);
  font-weight: 600;
}

.narration-groups {
  display: grid;
  gap: 12px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.narration-group {
  display: grid;
  grid-template-columns: 12px 1fr;
  gap: 10px;
  color: var(--ui-text-muted);
  transition: color 200ms ease;
}

.narration-dot {
  width: 10px;
  height: 10px;
  margin-top: 4px;
  border: 1.5px solid var(--ui-text-muted);
  border-radius: 50%;
  transition: background 200ms ease, border-color 200ms ease, transform 200ms ease;
}

.narration-group[data-done='true'] {
  color: var(--ui-text);
}

.narration-group[data-done='true'] .narration-dot {
  border-color: var(--ui-success);
  background: var(--ui-success);
}

.narration-group[data-current='true'] .narration-dot {
  transform: scale(1.18);
}

.narration-label {
  margin: 0;
  font-size: var(--kollio-text-small);
  font-weight: 500;
}

.narration-items {
  display: grid;
  gap: 2px;
  margin: 4px 0 0;
  padding: 0 0 0 14px;
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-small);
  line-height: 1.5;
}

.narration-items li {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (prefers-reduced-motion: reduce) {
  .narration-group,
  .narration-dot {
    transition: none;
  }
}
</style>
