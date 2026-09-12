<script setup lang="ts">
const { t, locale } = useI18n()
const switchLocalePath = useSwitchLocalePath()
</script>

<template>
  <div class="min-h-screen bg-default text-default">
    <header class="sticky top-0 z-20 border-b border-default bg-default/90 backdrop-blur-xl">
      <div class="mx-auto flex h-18 max-w-7xl items-center justify-between px-6 sm:px-10">
        <div class="flex items-center gap-8">
          <NuxtLink
            :to="$localePath('/workspace')"
            class="font-display text-2xl font-extrabold tracking-tight"
            :aria-label="t('brand')"
          >
            {{ t('brand') }}<span class="text-primary" aria-hidden="true">.</span>
          </NuxtLink>
          <nav class="hidden items-center gap-1 sm:flex" :aria-label="t('navigation')">
            <NuxtLink
              :to="$localePath('/workspace')"
              class="rounded-lg px-3 py-2 text-sm font-medium text-muted transition-colors hover:bg-elevated hover:text-default"
              active-class="bg-elevated text-default"
            >
              {{ t('navigation.ideas') }}
            </NuxtLink>
          </nav>
        </div>
        <div class="flex items-center gap-2">
          <NuxtLink
            :to="switchLocalePath(locale === 'fr' ? 'en' : 'fr')"
            class="rounded-lg px-3 py-2 text-sm font-medium text-muted transition-colors hover:bg-elevated hover:text-default"
            :hreflang="locale === 'fr' ? 'en' : 'fr'"
          >
            {{ t('language.switch') }}
          </NuxtLink>
          <a
            href="/sign-out"
            class="rounded-lg border border-default bg-elevated px-3 py-2 text-sm font-medium shadow-xs transition-colors hover:bg-accented"
          >
            {{ t('auth.signOut') }}
          </a>
        </div>
      </div>
    </header>
    <main id="main" class="mx-auto max-w-7xl px-6 py-10 sm:px-10 sm:py-14">
      <slot />
    </main>
  </div>
</template>
