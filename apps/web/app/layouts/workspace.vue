<script setup lang="ts">
const { t, locale } = useI18n()
const switchLocalePath = useSwitchLocalePath()
</script>

<template>
  <div class="workspace-canvas workspace-shell min-h-screen bg-default text-default">
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

    <aside class="workspace-rail sticky hidden flex-col border border-default bg-elevated/80 lg:flex">
      <NuxtLink :to="$localePath('/workspace')" class="px-2 text-[1.75rem] font-bold tracking-[-0.04em]" :aria-label="t('brand')">
        {{ t('brand') }}
      </NuxtLink>
      <p class="mt-1 px-2 text-sm leading-snug text-muted">{{ t('navigation.promise') }}</p>

      <nav class="mt-12" :aria-label="t('navigation.label')">
        <NuxtLink
          :to="$localePath('/workspace')"
          class="workspace-nav-active group flex min-h-11 items-center gap-3 rounded-xl px-3 text-sm font-medium text-muted transition-colors hover:text-default"
          active-class="workspace-nav-active text-default"
        >
          <svg aria-hidden="true" viewBox="0 0 24 24" class="size-5 shrink-0" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M9 18h6m-5 3h4m4.5-10.5a6.5 6.5 0 1 0-10.7 5l.7.6c.9.8 1.5 1.9 1.5 3.1h4c0-1.2.6-2.3 1.5-3.1l.7-.6a6.5 6.5 0 0 0 2.3-5Z" /></svg>
          <KollioFeltMark active>{{ t('navigation.ideas') }}</KollioFeltMark>
        </NuxtLink>

        <div class="mt-2 space-y-1" :aria-label="t('navigation.upcoming')">
          <span v-for="item in ['workshops', 'community', 'resources']" :key="item" class="flex min-h-11 cursor-default items-center gap-3 rounded-xl px-3 text-sm text-muted/55" aria-disabled="true">
            <svg v-if="item === 'workshops'" aria-hidden="true" viewBox="0 0 24 24" class="size-5" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M4 7h16M7 4v6m10-6v6M5 11h14v9H5z" /></svg>
            <svg v-else-if="item === 'community'" aria-hidden="true" viewBox="0 0 24 24" class="size-5" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M16 20a4 4 0 0 0-8 0M12 13a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm7 7a3 3 0 0 0-3-3m1-9a3 3 0 0 1 0 6M5 20a3 3 0 0 1 3-3M7 8a3 3 0 0 0 0 6" /></svg>
            <svg v-else aria-hidden="true" viewBox="0 0 24 24" class="size-5" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H11v17H6.5A2.5 2.5 0 0 0 4 22V5.5ZM20 5.5A2.5 2.5 0 0 0 17.5 3H13v17h4.5A2.5 2.5 0 0 1 20 22V5.5Z" /></svg>
            {{ t(`navigation.${item}`) }}
          </span>
        </div>

        <div class="mt-7 space-y-1 border-t border-default pt-5">
          <span v-for="item in ['search', 'notifications']" :key="item" class="flex min-h-11 cursor-default items-center gap-3 rounded-xl px-3 text-sm text-muted/55" aria-disabled="true">
            <svg v-if="item === 'search'" aria-hidden="true" viewBox="0 0 24 24" class="size-5" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="11" cy="11" r="7" /><path d="m16 16 5 5" /></svg>
            <svg v-else aria-hidden="true" viewBox="0 0 24 24" class="size-5" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9ZM10 21h4" /></svg>
            {{ t(`navigation.${item}`) }}
          </span>
        </div>
      </nav>

      <div class="mt-auto space-y-1 border-t border-default pt-5">
        <NuxtLink
          :to="switchLocalePath(locale === 'fr' ? 'en' : 'fr')"
          class="flex min-h-11 items-center rounded-xl px-3 text-sm font-medium text-muted transition-colors hover:bg-muted hover:text-default"
          :hreflang="locale === 'fr' ? 'en' : 'fr'"
        >
          {{ t('language.switch') }}
        </NuxtLink>
        <a href="/sign-out" class="flex min-h-11 items-center rounded-xl px-3 text-sm font-medium text-muted transition-colors hover:bg-muted hover:text-default" :aria-label="t('auth.signOut')">
          {{ t('auth.signOut') }}
        </a>
      </div>
    </aside>

    <main id="main" class="workspace-main min-w-0">
      <slot />
    </main>
  </div>
</template>
