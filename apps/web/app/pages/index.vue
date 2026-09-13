<script setup lang="ts">
import { motion, useReducedMotion } from 'motion-v'
const { t, locale } = useI18n()
const switchLocalePath = useSwitchLocalePath()
const reducedMotion = useReducedMotion()
const config = useRuntimeConfig()
const { data: session } = await useFetch('/api/session')
const authEnabled = config.public.authEnabled === true || String(config.public.authEnabled) === 'true'
useSeoMeta({ title: () => t('meta.title'), description: () => t('meta.description') })
</script>

<template>
  <div class="mx-auto flex min-h-screen max-w-7xl flex-col px-6 sm:px-12">
    <header class="flex items-center justify-between border-b border-default py-6">
      <NuxtLink :to="$localePath('/')" :aria-label="t('brand')">
        <KollioBrand />
      </NuxtLink>
      <nav class="flex items-center gap-4" :aria-label="t('navigation')">
        <NuxtLink :to="switchLocalePath(locale === 'fr' ? 'en' : 'fr')" class="text-sm font-medium underline-offset-4 hover:underline" :hreflang="locale === 'fr' ? 'en' : 'fr'">
          {{ t('language.switch') }}
        </NuxtLink>
        <NuxtLink v-if="authEnabled && session?.signedIn" :to="$localePath('/workspace')" class="rounded-md px-3 py-2 text-sm font-medium hover:bg-elevated">
          {{ t('navigation.workspace') }}
        </NuxtLink>
        <a v-if="authEnabled" :href="session?.signedIn ? '/sign-out' : '/sign-in'" class="rounded-md border border-default px-4 py-2 text-sm font-medium hover:bg-elevated">
          {{ session?.signedIn ? t('auth.signOut') : t('auth.signIn') }}
        </a>
      </nav>
    </header>
    <main id="main" class="grid flex-1 items-center gap-12 py-20 lg:grid-cols-[1.4fr_1fr] lg:gap-24">
      <motion.div :initial="{ opacity: 0, y: reducedMotion ? 0 : 14 }" :animate="{ opacity: 1, y: 0 }" :transition="{ duration: reducedMotion ? 0 : 0.4 }">
        <p class="mb-6 text-sm font-semibold tracking-wide text-primary">{{ t('hero.eyebrow') }}</p>
        <h1 class="font-display max-w-3xl text-5xl leading-[1.04] font-bold tracking-tight sm:text-7xl">{{ t('hero.title') }}</h1>
        <p class="mt-7 max-w-xl text-lg leading-relaxed text-muted">{{ t('hero.description') }}</p>
        <NuxtLink v-if="authEnabled && session?.signedIn" class="mt-9 inline-flex rounded-md bg-primary px-5 py-3 font-semibold text-white hover:bg-primary/90" :to="$localePath('/workspace')">{{ t('hero.action') }}</NuxtLink>
        <a v-else-if="authEnabled" class="mt-9 inline-flex rounded-md bg-primary px-5 py-3 font-semibold text-white hover:bg-primary/90" href="/sign-in">{{ t('hero.action') }}</a>
        <p v-else class="mt-9 text-sm text-muted" role="status">{{ t('auth.pending') }}</p>
      </motion.div>
      <aside class="space-y-0 border-y border-default" :aria-label="t('principles.label')">
        <article v-for="step in ['idea', 'challenge', 'team']" :key="step" class="border-b border-default py-7 last:border-0">
          <h2 class="font-display text-2xl font-semibold">{{ t(`principles.${step}.title`) }}</h2>
          <p class="mt-2 text-sm leading-relaxed text-muted">{{ t(`principles.${step}.description`) }}</p>
        </article>
      </aside>
    </main>
    <footer class="flex flex-wrap justify-between gap-4 border-t border-default py-6 text-xs text-muted">
      <p>{{ t('footer.promise') }}</p><p>{{ t('footer.languages') }}</p>
    </footer>
  </div>
</template>
