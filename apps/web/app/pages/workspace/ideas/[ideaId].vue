<script setup lang="ts">
import type { IdeaResponse } from '@kollio/api-client'

definePageMeta({ layout: 'workspace', middleware: 'authenticated' })

const { t, locale } = useI18n()
const route = useRoute()
const requestFetch = useRequestFetch()
const ideaId = String(route.params.ideaId)
const activePanel = ref<'team' | 'questions' | 'evidence'>('team')
const descriptionExpanded = ref(false)
const canvasRef = ref<HTMLElement>()
const documentRef = ref<HTMLElement>()
const annotationRef = ref<HTMLElement>()
const relationshipTargetRef = ref<HTMLElement>()
const connection = reactive({ path: '', width: 1, height: 1, startX: 0, startY: 0 })
let canvasObserver: ResizeObserver | undefined

const { data: idea, error, status, refresh } = useLazyAsyncData(`idea-${ideaId}`, () =>
  requestFetch<IdeaResponse>(`/api/ideas/${encodeURIComponent(ideaId)}`),
)

const dateFormatter = computed(() =>
  new Intl.DateTimeFormat(locale.value, { day: 'numeric', month: 'long', year: 'numeric' }),
)
const panels = ['team', 'questions', 'evidence'] as const
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
  const start = Math.min(words.length - 4, Math.floor(words.length * 0.38))
  const end = Math.min(words.length, start + 4)
  return {
    before: `${words.slice(0, start).join(' ')} `,
    highlight: words.slice(start, end).join(' '),
    after: ` ${words.slice(end).join(' ')}`,
  }
})
const legacySourceLabel = computed(() => idea.value?.legacy_context?.source === 'prospecteur' ? 'Prospecteur' : idea.value?.legacy_context?.source)
const errorTitle = computed(() => error.value?.statusCode === 404 ? t('ideas.detail.notFound') : t('ideas.detail.loadError.title'))
const errorDescription = computed(() => error.value?.statusCode === 404 ? t('ideas.detail.notFoundDescription') : t('ideas.detail.loadError.description'))

function updateConnection() {
  const canvas = canvasRef.value
  const documentSurface = documentRef.value
  const annotation = annotationRef.value
  const target = relationshipTargetRef.value
  if (activePanel.value !== 'team' || !canvas || !documentSurface || !annotation || !target) {
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
  const startX = annotationRect.right - canvasRect.left + 8
  const startY = annotationRect.top + annotationRect.height / 2 - canvasRect.top
  const endX = targetRect.left - canvasRect.left
  const endY = targetRect.top + Math.min(42, targetRect.height / 2) - canvasRect.top
  const horizontalSpan = Math.max(1, endX - startX)
  const curveSpan = Math.min(220, horizontalSpan)
  const curveStartX = endX - curveSpan
  const controlOffset = Math.max(34, curveSpan * 0.45)
  connection.width = canvasRect.width
  connection.height = canvas.scrollHeight
  connection.startX = startX
  connection.startY = startY
  connection.path = `M ${startX} ${startY} L ${curveStartX} ${startY} C ${curveStartX + controlOffset} ${startY}, ${endX - controlOffset} ${endY}, ${endX} ${endY}`
}

function selectPanel(panel: string) {
  if (!panels.includes(panel as typeof panels[number])) return
  const nextPanel = panel as typeof panels[number]
  activePanel.value = nextPanel
  nextTick(() => requestAnimationFrame(updateConnection))
}

function handleRelationshipTarget(target?: HTMLElement) {
  relationshipTargetRef.value = target
  nextTick(() => requestAnimationFrame(updateConnection))
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
  <KollioIdeaDetailSkeleton v-if="status === 'pending' || status === 'idle'" :label="t('ideas.detail.loading')" />
  <KollioIdeaDetailError
    v-else-if="error"
    :title="errorTitle"
    :description="errorDescription"
    :reassurance="t('ideas.detail.loadError.reassurance')"
    :retry-label="t('ideas.detail.retry')"
    :back-label="t('ideas.detail.explore')"
    :back-to="$localePath('/workspace')"
    @retry="refresh"
  />
  <article
    v-else-if="idea"
    class="idea-enter w-full"
  >
    <div ref="canvasRef" class="idea-layout relative grid min-w-0">
      <svg v-if="connection.path" aria-hidden="true" class="pointer-events-none absolute inset-0 z-40 hidden overflow-visible lg:block" :viewBox="`0 0 ${connection.width} ${connection.height}`" preserveAspectRatio="none">
        <path class="relationship-path" :d="connection.path" pathLength="1" fill="none" stroke="var(--kollio-connector)" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" />
        <circle :cx="connection.startX" :cy="connection.startY" r="4.5" fill="var(--kollio-connector)" />
      </svg>

      <div ref="documentRef" class="kollio-surface idea-document relative z-10 min-w-0 p-5 sm:p-7 lg:p-7 xl:p-9">
        <header class="idea-header">
          <NuxtLink :to="$localePath('/workspace')" class="idea-breadcrumb inline-flex items-center gap-2 text-sm font-medium text-muted hover:text-default">
            {{ t('navigation.ideas') }}
            <svg aria-hidden="true" viewBox="0 0 24 24" class="size-4" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m9 18 6-6-6-6" /></svg>
            {{ t(`ideas.stage.${idea.stage}`) }}
          </NuxtLink>
          <div class="idea-header-actions flex items-center gap-3">
            <KollioPrimaryAction :label="t('ideas.detail.advance')" @click="selectPanel('questions')" />
            <button type="button" class="idea-more-action" :aria-label="t('ideas.detail.moreActions')">
              <svg aria-hidden="true" viewBox="0 0 24 24" class="size-5" fill="currentColor"><circle cx="5" cy="12" r="1.5" /><circle cx="12" cy="12" r="1.5" /><circle cx="19" cy="12" r="1.5" /></svg>
            </button>
          </div>
          <h1 class="idea-title max-w-[630px]">{{ idea.title }}</h1>
          <div class="idea-topics flex flex-wrap items-center gap-x-5 gap-y-3 text-sm text-muted">
            <KollioSketchAnnotation active kind="swash">{{ t(`ideas.stage.${idea.stage}`) }}</KollioSketchAnnotation>
            <template v-for="topic in legacyTopics" :key="topic">
              <span class="inline-flex items-center gap-5">
                <span aria-hidden="true" class="idea-dot" />
                <span class="first-letter:uppercase">{{ topic }}</span>
              </span>
            </template>
            <button type="button" class="idea-topic-add" :aria-label="t('ideas.detail.enrich')" @click="selectPanel('questions')">
              <svg aria-hidden="true" viewBox="0 0 24 24" class="size-5" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 5v14M5 12h14" /></svg>
            </button>
          </div>
          <p class="idea-summary line-clamp-2 max-w-[70ch] text-muted">{{ ideaSummary }}</p>
          <div class="idea-stats flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-muted">
            <span>{{ t('ideas.detail.stats.contributors', { count: 0 }) }}</span>
            <span aria-hidden="true" class="size-1 rounded-full bg-muted" />
            <button type="button" class="transition-colors hover:text-default" @click="selectPanel('questions')">{{ t('ideas.detail.stats.questions', { count: 0 }) }}</button>
            <span aria-hidden="true" class="size-1 rounded-full bg-muted" />
            <button type="button" class="transition-colors hover:text-default" @click="selectPanel('evidence')">{{ t('ideas.detail.stats.evidence', { count: 0 }) }}</button>
            <span aria-hidden="true" class="size-1 rounded-full bg-muted" />
            <time :datetime="idea.created_at">{{ dateFormatter.format(new Date(idea.created_at)) }}</time>
          </div>
        </header>

        <section id="description" class="idea-description mt-11 rounded-2xl border border-default p-5 sm:p-6" :aria-labelledby="'idea-pitch-title'">
          <h2 id="idea-pitch-title" class="text-[1.375rem] font-semibold tracking-[-0.025em]">{{ t('ideas.detail.pitchTitle') }}</h2>
          <KollioDisclosure
            v-model="descriptionExpanded"
            content-id="idea-description-content"
            :expand-label="t('ideas.detail.showFull')"
            :collapse-label="t('ideas.detail.showLess')"
            class="mt-4 max-w-[72ch]"
          >
            <div class="idea-prose space-y-5 text-muted">
              <p v-if="problemAnnotation">
                {{ problemAnnotation.before }}<button ref="annotationRef" type="button" class="linked-passage text-left" :aria-label="t('ideas.detail.annotation.provenance', { excerpt: problemAnnotation.highlight })" :aria-pressed="activePanel === 'team'" @click="selectPanel('team')"><KollioSketchAnnotation active kind="swash">{{ problemAnnotation.highlight }}</KollioSketchAnnotation></button><br class="linked-passage-break">{{ problemAnnotation.after }}
              </p>
              <p v-else-if="detailParagraphs[0]">{{ detailParagraphs[0] }}</p>
              <p v-for="(paragraph, index) in detailParagraphs.slice(1)" :key="index">{{ paragraph }}</p>
            </div>
          </KollioDisclosure>
          <button type="button" class="idea-writing-prompt mt-6 w-full text-left" @click="selectPanel('questions')">{{ t('ideas.detail.writeToEnrich') }}</button>
        </section>

        <KollioIterationTimeline
          :context="idea.legacy_context"
          :created-at="idea.created_at"
          :date-label="dateFormatter.format(new Date(idea.created_at))"
          :count-label="t('ideas.detail.iterations.count', { count: iterationCount })"
          :title="t('ideas.detail.iterations.title')"
          :imported-label="t('ideas.detail.iterations.imported')"
          :empty-label="t('ideas.detail.iterations.empty')"
          :source-label="legacySourceLabel"
        />

        <KollioCommentComposer :label="t('ideas.detail.comment')" @activate="selectPanel('team')" />
      </div>

      <KollioIdeaCompanion
        :idea="idea"
        :active-panel="activePanel"
        @update:active-panel="selectPanel"
        @target-ready="handleRelationshipTarget"
      />
    </div>
  </article>
</template>
