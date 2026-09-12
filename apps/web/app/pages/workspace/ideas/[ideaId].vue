<script setup lang="ts">
import type { IdeaResponse } from '@kollio/api-client'
import { motion, useReducedMotion } from 'motion-v'

definePageMeta({ layout: 'workspace', middleware: 'authenticated' })

const { t, locale } = useI18n()
const route = useRoute()
const requestFetch = useRequestFetch()
const reducedMotion = useReducedMotion()
const ideaId = String(route.params.ideaId)
const activePanel = ref<'team' | 'questions' | 'evidence'>('team')
const canvasRef = ref<HTMLElement>()
const annotationRef = ref<HTMLElement>()
const relationshipTargetRef = ref<HTMLElement>()
const connection = reactive({ path: '', width: 1, height: 1, startX: 0, startY: 0 })
let canvasObserver: ResizeObserver | undefined

const { data: idea, error } = await useAsyncData(`idea-${ideaId}`, () =>
  requestFetch<IdeaResponse>(`/api/ideas/${encodeURIComponent(ideaId)}`),
)

if (error.value) {
  throw createError({ statusCode: error.value.statusCode ?? 404, statusMessage: t('ideas.detail.notFound') })
}

const dateFormatter = computed(() =>
  new Intl.DateTimeFormat(locale.value, { day: 'numeric', month: 'long', year: 'numeric' }),
)
const panels = ['team', 'questions', 'evidence'] as const
const panelCounts = { questions: 0, evidence: 0 } as const
const contextTabs = computed(() => panels.map(panel => ({
  id: panel,
  label: panel === 'team'
    ? t(`ideas.detail.companion.${panel}.tab`)
    : t('ideas.detail.companion.tabWithCount', { label: t(`ideas.detail.companion.${panel}.tab`), count: panelCounts[panel] }),
})))
const pitchParagraphs = computed(() => idea.value?.pitch.split(/\n\s*\n/).filter(Boolean) ?? [])
const pitchSentences = computed(() => idea.value?.pitch.split(/(?<=[.!?])\s+(?=[A-ZÀ-ÖØ-Þ])/).map(sentence => sentence.trim()).filter(Boolean) ?? [])
const ideaSummary = computed(() => pitchSentences.value[0] ?? pitchParagraphs.value[0] ?? '')
const detailParagraphs = computed(() => pitchSentences.value.length > 1 ? pitchSentences.value.slice(1) : pitchParagraphs.value)
const legacyTopics = computed(() => idea.value?.legacy_context?.domain?.split('·').map(topic => topic.trim()).filter(Boolean) ?? [])
const iterationCount = computed(() => idea.value?.legacy_context ? 1 : 0)
const problemAnnotation = computed(() => {
  const paragraph = detailParagraphs.value[0] ?? ''
  if (!idea.value?.legacy_context || !paragraph) return undefined
  const words = paragraph.split(/\s+/)
  if (words.length < 8) return { before: '', highlight: paragraph, after: '' }
  const start = Math.min(words.length - 5, Math.floor(words.length * 0.55))
  const end = Math.min(words.length, start + 6)
  return {
    before: `${words.slice(0, start).join(' ')} `,
    highlight: words.slice(start, end).join(' '),
    after: ` ${words.slice(end).join(' ')}`,
  }
})
const legacySourceLabel = computed(() => idea.value?.legacy_context?.source === 'prospecteur' ? 'Prospecteur' : idea.value?.legacy_context?.source)

function updateConnection() {
  const canvas = canvasRef.value
  const annotation = annotationRef.value
  const target = relationshipTargetRef.value
  if (activePanel.value !== 'team' || !canvas || !annotation || !target) {
    connection.path = ''
    return
  }
  const canvasRect = canvas.getBoundingClientRect()
  const annotationRect = annotation.getBoundingClientRect()
  const targetRect = target.getBoundingClientRect()
  const annotationVisible = annotationRect.bottom > 0 && annotationRect.top < window.innerHeight
  const targetVisible = targetRect.bottom > 0 && targetRect.top < window.innerHeight
  if (!annotationVisible || !targetVisible) {
    connection.path = ''
    return
  }
  const startX = annotationRect.right - canvasRect.left
  const startY = annotationRect.top + annotationRect.height / 2 - canvasRect.top
  const endX = targetRect.left - canvasRect.left
  const endY = targetRect.top + Math.min(42, targetRect.height / 2) - canvasRect.top
  const curve = Math.max(48, (endX - startX) * 0.48)
  connection.width = canvasRect.width
  connection.height = canvas.scrollHeight
  connection.startX = startX
  connection.startY = startY
  connection.path = `M ${startX} ${startY} C ${startX + curve} ${startY}, ${endX - curve} ${endY}, ${endX} ${endY}`
}

function selectPanel(panel: string) {
  if (!panels.includes(panel as typeof panels[number])) return
  const nextPanel = panel as typeof panels[number]
  activePanel.value = nextPanel
  nextTick(() => {
    document.getElementById(`idea-context-tab-${nextPanel}`)?.focus()
    requestAnimationFrame(updateConnection)
  })
}

watch(activePanel, () => nextTick(() => requestAnimationFrame(updateConnection)))
onMounted(() => {
  window.addEventListener('resize', updateConnection)
  window.addEventListener('scroll', updateConnection, { passive: true })
  canvasObserver = new ResizeObserver(updateConnection)
  if (canvasRef.value) canvasObserver.observe(canvasRef.value)
  requestAnimationFrame(updateConnection)
})
onBeforeUnmount(() => {
  window.removeEventListener('resize', updateConnection)
  window.removeEventListener('scroll', updateConnection)
  canvasObserver?.disconnect()
})

useSeoMeta({ title: () => idea.value ? `${idea.value.title} | Kollio` : t('ideas.detail.metaTitle') })
</script>

<template>
  <motion.article
    v-if="idea"
    :initial="{ opacity: 0, y: reducedMotion ? 0 : 8 }"
    :animate="{ opacity: 1, y: 0 }"
    :transition="{ duration: reducedMotion ? 0 : 0.28 }"
    class="mx-auto max-w-[1320px]"
  >
    <div ref="canvasRef" class="idea-layout relative grid min-w-0">
      <svg v-if="connection.path" aria-hidden="true" class="pointer-events-none absolute inset-0 z-40 hidden overflow-visible lg:block" :viewBox="`0 0 ${connection.width} ${connection.height}`" preserveAspectRatio="none">
        <path class="relationship-path" :d="connection.path" pathLength="1" fill="none" stroke="var(--ui-primary)" stroke-width="1.5" />
        <circle :cx="connection.startX" :cy="connection.startY" r="4" fill="var(--ui-primary)" />
      </svg>

      <div class="kollio-surface idea-document relative z-10 min-w-0 p-5 sm:p-7 lg:min-h-[calc(100vh-2.5rem)] lg:p-7 xl:p-9">
        <header>
          <div class="flex flex-col items-start gap-3 sm:flex-row sm:items-center sm:justify-between">
            <NuxtLink :to="$localePath('/workspace')" class="inline-flex min-h-11 items-center gap-2 text-sm font-medium text-muted hover:text-default">
              {{ t('navigation.ideas') }}
              <svg aria-hidden="true" viewBox="0 0 24 24" class="size-4" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m9 18 6-6-6-6" /></svg>
              {{ t(`ideas.stage.${idea.stage}`) }}
            </NuxtLink>
            <KollioPrimaryAction :label="t('ideas.detail.inspectSource')" @click="selectPanel('evidence')" />
          </div>
          <h1 class="idea-title mt-7 max-w-4xl">{{ idea.title }}</h1>
          <div class="mt-6 flex flex-wrap items-center gap-x-5 gap-y-3 text-sm text-muted">
            <KollioFeltMark active>{{ t(`ideas.stage.${idea.stage}`) }}</KollioFeltMark>
            <template v-for="topic in legacyTopics" :key="topic">
              <span aria-hidden="true" class="idea-dot" />
              <span class="first-letter:uppercase">{{ topic }}</span>
            </template>
            <button type="button" class="idea-topic-add" :aria-label="t('ideas.detail.enrich')" @click="selectPanel('questions')">
              <svg aria-hidden="true" viewBox="0 0 24 24" class="size-5" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 5v14M5 12h14" /></svg>
            </button>
          </div>
          <p class="idea-summary mt-6 max-w-[70ch] text-muted">{{ ideaSummary }}</p>
          <div class="mt-6 flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-muted">
            <span>{{ t('ideas.detail.stats.contributors', { count: 0 }) }}</span>
            <span aria-hidden="true" class="size-1 rounded-full bg-muted" />
            <button type="button" class="transition-colors hover:text-default" @click="selectPanel('questions')">{{ t('ideas.detail.stats.questions', { count: 0 }) }}</button>
            <span aria-hidden="true" class="size-1 rounded-full bg-muted" />
            <button type="button" class="transition-colors hover:text-default" @click="selectPanel('evidence')">{{ t('ideas.detail.stats.evidence', { count: 0 }) }}</button>
            <span aria-hidden="true" class="size-1 rounded-full bg-muted" />
            <time :datetime="idea.created_at">{{ dateFormatter.format(new Date(idea.created_at)) }}</time>
          </div>
        </header>

        <section id="description" class="idea-description mt-9 rounded-2xl border border-default p-5 sm:p-7" :aria-labelledby="'idea-pitch-title'">
          <h2 id="idea-pitch-title" class="text-xl font-semibold">{{ t('ideas.detail.pitchTitle') }}</h2>
          <div class="relative mt-5 max-w-[72ch]">
            <div class="idea-prose space-y-5 text-muted">
              <p v-if="problemAnnotation">
                {{ problemAnnotation.before }}<button ref="annotationRef" type="button" class="linked-passage text-left" :aria-label="t('ideas.detail.annotation.provenance', { excerpt: problemAnnotation.highlight })" :aria-pressed="activePanel === 'team'" @click="selectPanel('team')"><KollioFeltMark active variant="passage">{{ problemAnnotation.highlight }}</KollioFeltMark></button>{{ problemAnnotation.after }}
              </p>
              <p v-else-if="detailParagraphs[0]">{{ detailParagraphs[0] }}</p>
              <p v-for="(paragraph, index) in detailParagraphs.slice(1)" :key="index">{{ paragraph }}</p>
            </div>
          </div>
          <button type="button" class="idea-writing-prompt mt-6 w-full text-left" @click="selectPanel('questions')">{{ t('ideas.detail.writeToEnrich') }}</button>
        </section>

        <section class="mt-8" aria-labelledby="iterations-title">
          <div class="flex items-center justify-between gap-4">
            <h2 id="iterations-title" class="text-xl font-semibold">{{ t('ideas.detail.iterations.title') }}</h2>
            <span class="text-sm text-muted">{{ t('ideas.detail.iterations.count', { count: iterationCount }) }}</span>
          </div>
          <div v-if="idea.legacy_context" class="mt-4 grid gap-2 rounded-2xl bg-muted/55 px-5 py-5 text-sm sm:grid-cols-[auto_minmax(0,1fr)] sm:gap-5">
            <time :datetime="idea.created_at" class="text-muted">{{ dateFormatter.format(new Date(idea.created_at)) }}</time>
            <div>
              <p class="font-medium text-default">{{ t('ideas.detail.iterations.imported') }}</p>
              <p class="mt-1 flex flex-wrap items-center gap-2 text-muted">
                <span>{{ legacySourceLabel }}</span>
                <span aria-hidden="true" class="size-1 rounded-full bg-muted" />
                <span>{{ idea.legacy_context.source_id }}</span>
              </p>
            </div>
          </div>
          <div v-else class="mt-4 rounded-2xl bg-muted/55 px-5 py-6 text-sm leading-relaxed text-muted">
            {{ t('ideas.detail.iterations.empty') }}
          </div>
        </section>

        <button type="button" class="mt-8 flex min-h-14 w-full items-center gap-3 rounded-2xl border border-default px-4 text-left transition-colors hover:bg-muted/45" @click="selectPanel('team')">
          <svg aria-hidden="true" viewBox="0 0 24 24" class="size-5 shrink-0 text-primary" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M21 11.5a8.4 8.4 0 0 1-9 8.5 9.5 9.5 0 0 1-4-.9L3 21l1.7-4.4A8.2 8.2 0 0 1 3 11.5a8.4 8.4 0 0 1 9-8.5 8.4 8.4 0 0 1 9 8.5Z" /></svg>
          <span class="min-h-11 flex-1 text-sm leading-11 text-muted">{{ t('ideas.detail.comment') }}</span>
          <span class="grid size-9 place-items-center rounded-xl bg-primary/15 text-primary" aria-hidden="true">
            <svg viewBox="0 0 24 24" class="size-4" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M5 12h14m-5-5 5 5-5 5" /></svg>
          </span>
        </button>
      </div>

      <aside class="kollio-surface idea-companion relative z-30 self-start overflow-hidden lg:sticky">
        <KollioContextTabs id-prefix="idea-context" :items="contextTabs" :label="t('ideas.detail.companion.label')" :model-value="activePanel" @update:model-value="selectPanel" />
        <motion.div
          id="idea-context-panel"
          :key="activePanel"
          :initial="{ opacity: 0, x: reducedMotion ? 0 : 6 }"
          :animate="{ opacity: 1, x: 0 }"
          :transition="{ duration: reducedMotion ? 0 : 0.2 }"
          role="tabpanel"
          :aria-labelledby="`tab-${activePanel}`"
          class="p-6"
        >
          <template v-if="activePanel === 'team'">
            <section v-if="idea.legacy_context">
              <h2 class="text-lg font-semibold">{{ t('ideas.detail.companion.team.source') }}</h2>
              <div ref="relationshipTargetRef" class="source-person mt-5">
                <span class="source-person-avatar" aria-hidden="true">{{ legacySourceLabel?.charAt(0) }}</span>
                <span class="min-w-0">
                  <strong class="block truncate text-sm font-semibold text-default">{{ legacySourceLabel }}</strong>
                  <span class="mt-0.5 block text-sm text-muted">{{ t('ideas.detail.companion.team.importedBy') }}</span>
                </span>
              </div>
            </section>
            <section :class="idea.legacy_context ? 'mt-7 border-t border-default pt-7' : ''">
              <div class="flex items-center justify-between gap-3">
                <h2 class="text-lg font-semibold">{{ t('ideas.detail.companion.team.contributors') }}</h2>
                <span class="text-sm text-muted">{{ t('ideas.detail.stats.contributors', { count: 0 }) }}</span>
              </div>
              <div class="mt-5 rounded-2xl bg-muted/55 p-5 text-sm leading-relaxed text-muted">{{ t('ideas.detail.companion.team.empty') }}</div>
            </section>
            <section class="mt-7 border-t border-default pt-7">
              <div class="flex items-center justify-between gap-3">
                <h2 class="text-lg font-semibold">{{ t('ideas.detail.companion.questions.title') }}</h2>
                <button type="button" class="text-sm text-primary" @click="selectPanel('questions')">{{ t('ideas.detail.companion.seeAll') }}</button>
              </div>
              <div class="mt-5 rounded-2xl bg-muted/55 p-5 text-sm leading-relaxed text-muted">{{ t('ideas.detail.companion.questions.empty') }}</div>
            </section>
          </template>
          <template v-else-if="activePanel === 'evidence' && idea.legacy_context">
            <h2 class="text-lg font-semibold">{{ t('ideas.detail.companion.evidence.sourceTitle') }}</h2>
            <div class="mt-5 rounded-2xl bg-accented p-5">
              <p class="font-medium text-default">{{ legacySourceLabel }}</p>
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
            <h2 class="text-lg font-semibold">{{ t(`ideas.detail.companion.${activePanel}.title`) }}</h2>
            <div class="mt-5 rounded-2xl bg-muted/55 p-5 text-sm leading-relaxed text-muted">{{ t(`ideas.detail.companion.${activePanel}.empty`) }}</div>
          </template>
        </motion.div>
      </aside>
    </div>
  </motion.article>
</template>
