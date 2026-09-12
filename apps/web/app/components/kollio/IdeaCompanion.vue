<script setup lang="ts">
import type { IdeaResponse } from '@kollio/api-client'

const props = defineProps<{
  idea: IdeaResponse
  activePanel: 'team' | 'questions' | 'evidence'
}>()

const emit = defineEmits<{
  'update:activePanel': [panel: 'team' | 'questions' | 'evidence']
  'targetReady': [target?: HTMLElement]
}>()

const { t } = useI18n()
const relationshipTarget = ref<HTMLElement>()
const panels = ['team', 'questions', 'evidence'] as const
const panelCounts = { questions: 0, evidence: 0 } as const
const tabs = computed(() => panels.map(panel => ({
  id: panel,
  label: panel === 'team'
    ? t(`ideas.detail.companion.${panel}.tab`)
    : t('ideas.detail.companion.tabWithCount', {
        label: t(`ideas.detail.companion.${panel}.tab`),
        count: panelCounts[panel],
      }),
})))
const sourceLabel = computed(() => props.idea.legacy_context?.source === 'prospecteur'
  ? 'Prospecteur'
  : props.idea.legacy_context?.source)

function selectPanel(panel: string) {
  if (panels.includes(panel as typeof panels[number])) {
    emit('update:activePanel', panel as typeof panels[number])
  }
}

function publishTarget() {
  emit('targetReady', props.activePanel === 'team' ? relationshipTarget.value : undefined)
}

watch(() => props.activePanel, () => nextTick(publishTarget))
onMounted(() => nextTick(publishTarget))
onBeforeUnmount(() => emit('targetReady', undefined))
</script>

<template>
  <aside class="kollio-surface idea-companion relative z-30 self-start overflow-hidden lg:sticky">
    <KollioContextTabs
      id-prefix="idea-context"
      :items="tabs"
      :label="t('ideas.detail.companion.label')"
      :model-value="activePanel"
      @update:model-value="selectPanel"
    />
    <div
      id="idea-context-panel"
      :key="activePanel"
      role="tabpanel"
      :aria-labelledby="`idea-context-tab-${activePanel}`"
      class="companion-enter idea-companion-panel"
    >
      <template v-if="activePanel === 'team'">
        <section class="team-panel-primary">
          <div class="idea-panel-heading">
            <h2>{{ t('ideas.detail.companion.team.contributors') }}</h2>
            <span>{{ t('ideas.detail.stats.contributors', { count: 0 }) }}</span>
          </div>
          <div v-if="idea.legacy_context" ref="relationshipTarget" class="mt-5">
            <KollioPersonRow
              :name="sourceLabel || t('ideas.detail.companion.team.importedBy')"
              :meta="t('ideas.detail.companion.team.source')"
              :initials="sourceLabel?.charAt(0)"
            />
          </div>
          <KollioEmptyState
            class="mt-6"
            image-src="/images/empty-states/team.png"
            :description="t('ideas.detail.companion.team.empty')"
          />
        </section>
        <section class="idea-panel-section">
          <div class="idea-panel-heading">
            <h2>{{ t('ideas.detail.companion.questions.title') }}</h2>
            <button type="button" @click="selectPanel('questions')">{{ t('ideas.detail.companion.seeAll') }}</button>
          </div>
          <KollioEmptyState
            class="mt-5"
            image-src="/images/empty-states/questions.png"
            :description="t('ideas.detail.companion.questions.empty')"
          />
        </section>
      </template>

      <template v-else-if="activePanel === 'evidence' && idea.legacy_context">
        <div class="idea-panel-heading">
          <h2>{{ t('ideas.detail.companion.evidence.sourceTitle') }}</h2>
        </div>
        <div class="provenance-card mt-5">
          <p class="font-medium text-default">{{ sourceLabel }}</p>
          <p class="mt-1 break-words text-xs text-muted">{{ idea.legacy_context.source_id }}</p>
          <p class="mt-4 text-sm leading-relaxed text-muted">{{ t('ideas.detail.companion.evidence.provenanceNote') }}</p>
        </div>
        <dl class="mt-7 space-y-5 text-sm">
          <div v-if="idea.legacy_context.fatal_constraint">
            <dt class="text-muted">{{ t('ideas.detail.legacy.constraint') }}</dt>
            <dd class="mt-1 font-medium text-default">{{ idea.legacy_context.fatal_constraint }}</dd>
          </div>
          <div v-if="idea.legacy_context.channel">
            <dt class="text-muted">{{ t('ideas.detail.legacy.channel') }}</dt>
            <dd class="mt-1 leading-relaxed text-default">{{ idea.legacy_context.channel }}</dd>
          </div>
        </dl>
      </template>

      <template v-else>
        <div class="idea-panel-heading">
          <h2>{{ t(`ideas.detail.companion.${activePanel}.title`) }}</h2>
        </div>
        <KollioEmptyState
          class="mt-5"
          :image-src="`/images/empty-states/${activePanel}.png`"
          :description="t(`ideas.detail.companion.${activePanel}.empty`)"
        />
      </template>
    </div>
  </aside>
</template>
