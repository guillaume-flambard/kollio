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
    <div class="grid min-w-0 gap-4 lg:grid-cols-[minmax(0,1fr)_280px] xl:grid-cols-[minmax(0,1fr)_340px]">
      <div class="kollio-surface min-w-0 p-5 sm:p-7 lg:min-h-[calc(100vh-2.5rem)] lg:p-7 xl:p-9">
        <header>
          <div class="flex flex-wrap items-center justify-between gap-3">
            <NuxtLink :to="$localePath('/workspace')" class="inline-flex min-h-11 items-center gap-2 text-sm font-medium text-muted hover:text-default">
              <svg aria-hidden="true" viewBox="0 0 24 24" class="size-4" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m15 18-6-6 6-6" /></svg>
              {{ t('ideas.detail.back') }}
            </NuxtLink>
            <NuxtLink :to="$localePath('/workspace')" class="split-action">
              {{ t('ideas.detail.explore') }}
              <svg aria-hidden="true" viewBox="0 0 24 24" class="split-action-arrow size-4" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M5 12h14m-5-5 5 5-5 5" /></svg>
            </NuxtLink>
          </div>
          <h1 class="mt-7 max-w-4xl text-3xl leading-[1.08] font-semibold tracking-[-0.04em] sm:text-4xl xl:text-5xl">{{ idea.title }}</h1>
          <div class="mt-6 flex flex-wrap items-center gap-3 text-sm text-muted">
            <span class="marker-active is-active font-semibold text-default">{{ t(`ideas.stage.${idea.stage}`) }}</span>
            <span aria-hidden="true" class="size-1 rounded-full bg-muted" />
            <span class="uppercase">{{ idea.lang }}</span>
            <span aria-hidden="true" class="size-1 rounded-full bg-muted" />
            <time :datetime="idea.created_at">{{ dateFormatter.format(new Date(idea.created_at)) }}</time>
          </div>
        </header>

        <section class="mt-10" :aria-labelledby="'idea-pitch-title'">
          <h2 id="idea-pitch-title" class="text-xl font-semibold">{{ t('ideas.detail.pitchTitle') }}</h2>
          <div class="mt-5 rounded-2xl border border-default bg-default/45 p-5 sm:p-7">
            <p class="max-w-3xl whitespace-pre-wrap text-base leading-7 text-default xl:text-lg xl:leading-8">{{ idea.pitch }}</p>
          </div>
        </section>

        <footer class="mt-10 border-t border-default pt-6">
          <p class="text-sm leading-relaxed text-muted">{{ t('ideas.detail.foundationNote') }}</p>
        </footer>
      </div>

      <aside class="kollio-surface self-start overflow-hidden lg:sticky lg:top-5 lg:min-h-[calc(100vh-2.5rem)]">
        <div class="grid grid-cols-3 border-b border-default" role="tablist" :aria-label="t('ideas.detail.companion.label')">
          <button
            v-for="panel in panels"
            :id="`tab-${panel}`"
            :key="panel"
            type="button"
            role="tab"
            class="min-h-14 px-2 text-sm font-medium text-muted transition-colors hover:text-default"
            :class="{ 'text-default': activePanel === panel }"
            :aria-selected="activePanel === panel"
            :aria-controls="`panel-${panel}`"
            @click="activePanel = panel"
          >
            <span class="marker-active" :class="{ 'is-active': activePanel === panel }">{{ t(`ideas.detail.companion.${panel}.tab`) }}</span>
          </button>
        </div>
        <motion.div
          :id="`panel-${activePanel}`"
          :key="activePanel"
          :initial="{ opacity: 0, x: reducedMotion ? 0 : 6 }"
          :animate="{ opacity: 1, x: 0 }"
          :transition="{ duration: reducedMotion ? 0 : 0.2 }"
          role="tabpanel"
          :aria-labelledby="`tab-${activePanel}`"
          class="p-6"
        >
          <h2 class="text-lg font-semibold">{{ t(`ideas.detail.companion.${activePanel}.title`) }}</h2>
          <p class="mt-3 text-sm leading-relaxed text-muted">{{ t(`ideas.detail.companion.${activePanel}.empty`) }}</p>
        </motion.div>
      </aside>
    </div>
  </motion.article>
</template>
