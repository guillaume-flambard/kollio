<script setup lang="ts">
import type { IdeaResponse } from '@kollio/api-client'
import { motion, useReducedMotion } from 'motion-v'

definePageMeta({ layout: 'workspace', middleware: 'authenticated' })

const { t, locale } = useI18n()
const route = useRoute()
const requestFetch = useRequestFetch()
const reducedMotion = useReducedMotion()
const ideaId = String(route.params.ideaId)

const { data: idea, error } = await useAsyncData(`idea-${ideaId}`, () =>
  requestFetch<IdeaResponse>(`/api/ideas/${encodeURIComponent(ideaId)}`),
)

if (error.value) {
  throw createError({ statusCode: error.value.statusCode ?? 404, statusMessage: t('ideas.detail.notFound') })
}

const dateFormatter = computed(() =>
  new Intl.DateTimeFormat(locale.value, { day: 'numeric', month: 'long', year: 'numeric' }),
)

useSeoMeta({ title: () => idea.value ? `${idea.value.title} | Kollio` : t('ideas.detail.metaTitle') })
</script>

<template>
  <motion.article
    v-if="idea"
    :initial="{ opacity: 0, y: reducedMotion ? 0 : 10 }"
    :animate="{ opacity: 1, y: 0 }"
    :transition="{ duration: reducedMotion ? 0 : 0.35 }"
    class="mx-auto max-w-4xl"
  >
    <NuxtLink
      :to="$localePath('/workspace')"
      class="inline-flex items-center gap-2 text-sm font-medium text-muted hover:text-default"
    >
      <svg aria-hidden="true" viewBox="0 0 24 24" class="size-4" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m15 18-6-6 6-6" /></svg>
      {{ t('ideas.detail.back') }}
    </NuxtLink>

    <header class="mt-9 border-b border-default pb-9">
      <div class="flex flex-wrap items-center gap-2">
        <span class="rounded-full bg-muted px-3 py-1 text-xs font-semibold text-muted">{{ t(`ideas.stage.${idea.stage}`) }}</span>
        <span class="rounded-full border border-default px-3 py-1 font-mono text-xs text-muted uppercase">{{ idea.lang }}</span>
      </div>
      <h1 class="font-display mt-6 max-w-3xl text-4xl leading-tight font-bold tracking-tight sm:text-6xl">{{ idea.title }}</h1>
      <div class="mt-6 flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-muted">
        <time :datetime="idea.created_at">{{ dateFormatter.format(new Date(idea.created_at)) }}</time>
        <span class="font-mono">{{ idea.slug }}</span>
      </div>
    </header>

    <section class="py-10" :aria-labelledby="'idea-pitch-title'">
      <p class="text-xs font-semibold tracking-[0.14em] text-primary uppercase">{{ t('ideas.detail.eyebrow') }}</p>
      <h2 id="idea-pitch-title" class="font-display mt-2 text-2xl font-semibold">{{ t('ideas.detail.pitchTitle') }}</h2>
      <p class="mt-6 whitespace-pre-wrap text-lg leading-8 text-default">{{ idea.pitch }}</p>
    </section>

    <aside class="rounded-2xl border border-default bg-elevated p-6 shadow-xs">
      <p class="text-sm leading-relaxed text-muted">{{ t('ideas.detail.foundationNote') }}</p>
    </aside>
  </motion.article>
</template>
