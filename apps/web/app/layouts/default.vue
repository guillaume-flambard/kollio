<script setup lang="ts">
const { t, locale } = useI18n()
const switchLocalePath = useSwitchLocalePath()
const localePath = useLocalePath()
const config = useRuntimeConfig()
const { data: session } = await useFetch('/api/session')

const authEnabled = config.public.authEnabled === true || String(config.public.authEnabled) === 'true'
const workspaceTarget = computed(() => session.value?.signedIn ? localePath('/workspace') : authEnabled ? '/sign-in' : localePath('/workspace'))

const sections = [
  { key: 'platform', href: '#product' },
  { key: 'teams', href: '#teams' },
  { key: 'method', href: '#method' },
  { key: 'security', href: '#trust' },
] as const

const { menuOpen, menuToggle, drawer, openMenu, closeMenu } = useDrawer()
</script>

<template>
  <div class="site-shell">
    <a class="site-skip" href="#main">{{ t('navigation.skipToContent') }}</a>

    <header class="site-header">
      <div class="site-header__inner">
        <NuxtLink :to="$localePath('/')" class="site-header__brand" :aria-label="t('brand')"><KollioBrand /></NuxtLink>

        <nav class="site-header__nav" :aria-label="t('navigation.label')">
          <a v-for="section in sections" :key="section.key" :href="section.href">{{ t(`landing.navigation.${section.key}`) }}</a>
        </nav>

        <div class="site-header__actions">
          <NuxtLink :to="switchLocalePath(locale === 'fr' ? 'en' : 'fr')" class="site-header__language" :hreflang="locale === 'fr' ? 'en' : 'fr'">{{ t('language.switch') }}</NuxtLink>
          <a v-if="authEnabled" :href="session?.signedIn ? '/sign-out' : '/sign-in'" class="site-header__signin">{{ session?.signedIn ? t('auth.signOut') : t('auth.signIn') }}</a>
          <KollioPrimaryAction
            :to="authEnabled && !session?.signedIn ? undefined : workspaceTarget"
            :href="authEnabled && !session?.signedIn ? '/sign-in' : undefined"
            :label="session?.signedIn ? t('landing.navigation.workspace') : t('auth.getStarted')"
          />
          <button
            ref="menuToggle"
            type="button"
            class="site-header__toggle"
            :aria-expanded="menuOpen"
            aria-controls="site-mobile-nav"
            :aria-label="menuOpen ? t('navigation.menuClose') : t('navigation.menuOpen')"
            @click="menuOpen ? closeMenu() : openMenu()"
          >
            <KollioIcon :name="menuOpen ? 'close' : 'menu'" class="site-header__toggle-icon" />
          </button>
        </div>
      </div>
    </header>

    <Transition name="site-drawer">
      <div v-if="menuOpen" class="site-drawer-layer">
        <button
          type="button"
          tabindex="-1"
          class="site-drawer-backdrop"
          :aria-label="t('navigation.menuClose')"
          @click="closeMenu(true)"
        />
        <aside
          id="site-mobile-nav"
          ref="drawer"
          class="site-drawer"
          role="dialog"
          aria-modal="true"
          :aria-label="t('navigation.label')"
          tabindex="-1"
        >
          <nav class="site-drawer__nav" :aria-label="t('navigation.label')">
            <a v-for="section in sections" :key="section.key" :href="section.href" @click="closeMenu()">{{ t(`landing.navigation.${section.key}`) }}</a>
          </nav>
          <div class="site-drawer__actions">
            <NuxtLink :to="switchLocalePath(locale === 'fr' ? 'en' : 'fr')" :hreflang="locale === 'fr' ? 'en' : 'fr'">{{ t('language.switch') }}</NuxtLink>
            <a v-if="authEnabled" :href="session?.signedIn ? '/sign-out' : '/sign-in'">{{ session?.signedIn ? t('auth.signOut') : t('auth.signIn') }}</a>
            <NuxtLink :to="workspaceTarget">{{ t('landing.navigation.workspace') }}</NuxtLink>
          </div>
        </aside>
      </div>
    </Transition>

    <main id="main">
      <slot />
    </main>

    <KollioSiteFooter />
  </div>
</template>

<style scoped>
.site-shell { min-height: 100vh; background: var(--ui-bg); color: var(--ui-text); }
.site-skip { position: absolute; left: var(--kollio-space-sm); top: -100px; z-index: 60; border-radius: var(--kollio-radius-md); background: var(--kollio-action); padding: var(--kollio-space-md) var(--kollio-space-lg); color: var(--kollio-on-action); font-size: var(--kollio-text-small); font-weight: var(--kollio-weight-strong); text-decoration: none; }
.site-skip:focus-visible { top: var(--kollio-space-sm); outline: 2px solid var(--kollio-connector); outline-offset: 2px; }
.site-header { position: sticky; top: 0; z-index: 40; border-bottom: 1px solid var(--ui-border); background: color-mix(in srgb, var(--ui-bg) 88%, transparent); backdrop-filter: blur(10px); }
.site-header__inner { display: grid; width: min(1440px, calc(100% - 48px)); min-height: 68px; grid-template-columns: auto 1fr auto; align-items: center; gap: var(--kollio-space-4xl); margin-inline: auto; }
.site-header__brand { display: inline-flex; min-height: 44px; align-items: center; }
.site-header__nav { display: flex; align-items: center; gap: var(--kollio-space-xl); }
.site-header__nav a, .site-header__language, .site-header__signin { display: inline-flex; min-height: 44px; align-items: center; color: var(--ui-text); font-size: var(--kollio-text-small); font-weight: var(--kollio-weight-medium); text-decoration: none; transition: color 160ms ease; }
.site-header__language, .site-header__signin { color: var(--ui-text-muted); }
.site-header__nav a:hover, .site-header__language:hover, .site-header__signin:hover { color: var(--kollio-heading); }
.site-header__nav a:focus-visible, .site-header__language:focus-visible, .site-header__signin:focus-visible, .site-header__brand:focus-visible, .site-drawer__nav a:focus-visible, .site-drawer__actions a:focus-visible, .site-drawer__actions :deep(a):focus-visible { outline: 2px solid var(--kollio-connector); outline-offset: 2px; border-radius: var(--kollio-radius-sm); }
.site-header__actions { display: flex; align-items: center; justify-content: flex-end; gap: var(--kollio-space-md); }
.site-header__toggle { display: none; width: 44px; height: 44px; place-items: center; border: 1px solid var(--ui-border); border-radius: var(--kollio-radius-md); background: var(--ui-bg-elevated); color: var(--ui-text); cursor: pointer; }
.site-header__toggle-icon { width: 20px; height: 20px; }
.site-drawer-layer { position: fixed; inset: 0; z-index: 50; }
.site-drawer-backdrop { position: absolute; inset: 0; border: 0; background: color-mix(in srgb, var(--kollio-heading) 22%, transparent); backdrop-filter: blur(2px); cursor: pointer; }
.site-drawer { position: absolute; inset-block: 0; right: 0; display: flex; width: 22rem; max-width: 86vw; flex-direction: column; gap: var(--kollio-space-2xl); overflow-y: auto; border-left: 1px solid var(--ui-border); background: var(--ui-bg-elevated); padding: var(--kollio-space-2xl) var(--kollio-space-lg); box-shadow: 0 24px 60px color-mix(in srgb, var(--kollio-active-ink) 22%, transparent); }
.site-drawer__nav, .site-drawer__actions { display: flex; flex-direction: column; gap: var(--kollio-space-xs); }
.site-drawer__actions { border-top: 1px solid var(--ui-border); padding-top: var(--kollio-space-lg); }
.site-drawer__nav a, .site-drawer__actions a { display: inline-flex; min-height: 44px; align-items: center; color: var(--ui-text); font-size: var(--kollio-text-body); font-weight: var(--kollio-weight-medium); text-decoration: none; }
.site-drawer__actions a { color: var(--ui-text-muted); }
.site-drawer-enter-active, .site-drawer-leave-active { transition: opacity 180ms ease; }
.site-drawer-enter-active .site-drawer { transition: transform 220ms cubic-bezier(.16, 1, .3, 1); }
.site-drawer-leave-active .site-drawer { transition: transform 160ms cubic-bezier(.3, 0, .7, 1); }
.site-drawer-enter-from, .site-drawer-leave-to { opacity: 0; }
.site-drawer-enter-from .site-drawer, .site-drawer-leave-to .site-drawer { transform: translateX(100%); }
@media (max-width: 1024px) {
  .site-header__inner { grid-template-columns: auto 1fr; min-height: 64px; gap: var(--kollio-space-lg); }
  .site-header__nav, .site-header__language, .site-header__signin { display: none; }
  .site-header__toggle { display: grid; }
}
@media (min-width: 1025px) { .site-drawer-layer { display: none; } }
@media (prefers-reduced-motion: reduce) {
  .site-drawer-enter-active, .site-drawer-leave-active, .site-drawer-enter-active .site-drawer, .site-drawer-leave-active .site-drawer { transition: none; }
}
</style>
