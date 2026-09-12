<script setup lang="ts">
const { t, locale } = useI18n()
const switchLocalePath = useSwitchLocalePath()
</script>

<template>
  <div class="min-h-screen bg-default text-default lg:grid lg:grid-cols-[220px_minmax(0,1fr)]">
    <header class="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-default bg-default/95 px-5 backdrop-blur lg:hidden">
      <NuxtLink :to="$localePath('/workspace')" class="text-xl font-bold tracking-[-0.03em]" :aria-label="t('brand')">
        {{ t('brand') }}
      </NuxtLink>
      <div class="flex items-center gap-2">
        <NuxtLink :to="switchLocalePath(locale === 'fr' ? 'en' : 'fr')" class="min-h-11 rounded-xl px-3 text-sm font-medium leading-11 text-muted">
          {{ t('language.switch') }}
        </NuxtLink>
        <a href="/sign-out" class="min-h-11 rounded-xl border border-default bg-elevated px-3 text-sm font-medium leading-11">
          {{ t('auth.signOut') }}
        </a>
      </div>
    </header>

    <aside class="sticky top-0 hidden h-screen flex-col border-r border-default bg-elevated/70 px-5 py-7 lg:flex">
      <NuxtLink :to="$localePath('/workspace')" class="px-2 text-2xl font-bold tracking-[-0.04em]" :aria-label="t('brand')">
        {{ t('brand') }}
      </NuxtLink>
      <p class="mt-1 px-2 text-sm leading-snug text-muted">{{ t('navigation.promise') }}</p>

      <nav class="mt-12" :aria-label="t('navigation.label')">
        <NuxtLink
          :to="$localePath('/workspace')"
          class="group flex min-h-11 items-center gap-3 rounded-xl px-3 text-sm font-medium text-muted transition-colors hover:text-default"
          active-class="text-default"
        >
          <svg aria-hidden="true" viewBox="0 0 24 24" class="size-5 shrink-0" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M9 18h6m-5 3h4m4.5-10.5a6.5 6.5 0 1 0-10.7 5l.7.6c.9.8 1.5 1.9 1.5 3.1h4c0-1.2.6-2.3 1.5-3.1l.7-.6a6.5 6.5 0 0 0 2.3-5Z" /></svg>
          <span class="marker-active" aria-current="page">{{ t('navigation.ideas') }}</span>
        </NuxtLink>
      </nav>

      <div class="mt-auto space-y-1 border-t border-default pt-5">
        <NuxtLink
          :to="switchLocalePath(locale === 'fr' ? 'en' : 'fr')"
          class="flex min-h-11 items-center rounded-xl px-3 text-sm font-medium text-muted transition-colors hover:bg-muted hover:text-default"
          :hreflang="locale === 'fr' ? 'en' : 'fr'"
        >
          {{ t('language.switch') }}
        </NuxtLink>
        <a href="/sign-out" class="flex min-h-11 items-center rounded-xl px-3 text-sm font-medium text-muted transition-colors hover:bg-muted hover:text-default">
          {{ t('auth.signOut') }}
        </a>
      </div>
    </aside>

    <main id="main" class="min-w-0 px-5 py-8 sm:px-8 lg:px-10 lg:py-10 xl:px-12">
      <slot />
    </main>
  </div>
</template>
