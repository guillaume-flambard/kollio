<script setup lang="ts">
const { t, locale } = useI18n()
const switchLocalePath = useSwitchLocalePath()

const config = useRuntimeConfig()
const authEnabled = config.public.authEnabled === true || String(config.public.authEnabled) === 'true'
const { data: session } = await useFetch('/api/session')

const sections = [
  { key: 'platform', href: '#product' },
  { key: 'teams', href: '#teams' },
  { key: 'method', href: '#method' },
  { key: 'security', href: '#trust' },
] as const
</script>

<template>
  <footer class="site-footer">
    <div class="site-footer__inner">
      <div class="site-footer__brand">
        <NuxtLink :to="$localePath('/')" :aria-label="t('brand')"><KollioBrand /></NuxtLink>
        <p class="site-footer__promise">{{ t('footer.promise') }}</p>
      </div>

      <nav class="site-footer__nav" :aria-label="t('navigation.label')">
        <a v-for="section in sections" :key="section.key" :href="section.href">{{ t(`landing.navigation.${section.key}`) }}</a>
      </nav>

      <div class="site-footer__actions">
        <NuxtLink :to="switchLocalePath(locale === 'fr' ? 'en' : 'fr')" :hreflang="locale === 'fr' ? 'en' : 'fr'">{{ t('language.switch') }}</NuxtLink>
        <NuxtLink :to="$localePath('/workspace')">{{ t('landing.navigation.workspace') }}</NuxtLink>
        <a v-if="authEnabled" :href="session?.signedIn ? '/sign-out' : '/sign-in'">{{ session?.signedIn ? t('auth.signOut') : t('auth.signIn') }}</a>
      </div>
    </div>

    <p class="site-footer__languages">{{ t('footer.languages') }}</p>
  </footer>
</template>

<style scoped>
.site-footer { border-top: 1px solid var(--ui-border); padding: var(--kollio-space-4xl) 0 var(--kollio-space-2xl); }
.site-footer__inner { display: grid; width: min(1240px, calc(100% - 48px)); grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr) minmax(0, 1fr); gap: var(--kollio-space-3xl); margin-inline: auto; }
.site-footer__brand a { display: inline-flex; min-height: 44px; align-items: center; }
.site-footer__brand a:focus-visible { outline: 2px solid var(--kollio-connector); outline-offset: 2px; border-radius: var(--kollio-radius-sm); }
.site-footer__brand p { margin-top: var(--kollio-space-lg); max-width: 34ch; color: var(--ui-text-muted); font-size: var(--kollio-text-small); line-height: var(--kollio-leading-body); }
.site-footer__nav, .site-footer__actions { display: flex; flex-direction: column; gap: var(--kollio-space-sm); }
.site-footer__nav a, .site-footer__actions a { display: inline-flex; min-height: 44px; align-items: center; color: var(--ui-text-muted); font-size: var(--kollio-text-small); font-weight: var(--kollio-weight-medium); text-decoration: none; transition: color 160ms ease; }
.site-footer__nav a:hover, .site-footer__actions a:hover { color: var(--kollio-heading); }
.site-footer__nav a:focus-visible, .site-footer__actions a:focus-visible { outline: 2px solid var(--kollio-connector); outline-offset: 2px; border-radius: var(--kollio-radius-sm); }
.site-footer__languages { width: min(1240px, calc(100% - 48px)); margin: var(--kollio-space-3xl) auto 0; padding-top: var(--kollio-space-lg); border-top: 1px solid var(--ui-border); color: var(--ui-text-muted); font-size: var(--kollio-text-caption); }
@media (max-width: 960px) { .site-footer__inner { grid-template-columns: 1fr; gap: var(--kollio-space-2xl); } }
</style>
