<script setup lang="ts">
const { t, locale } = useI18n()
const switchLocalePath = useSwitchLocalePath()

const { menuOpen, menuToggle, drawer, openMenu, closeMenu } = useDrawer()
</script>

<template>
  <div class="workspace-canvas workspace-shell min-h-screen bg-default text-default">
    <header class="sticky top-0 z-40 flex h-16 items-center justify-between gap-2 border-b border-default bg-default px-2 lg:hidden">
      <NuxtLink :to="$localePath('/workspace')" :aria-label="t('brand')">
        <KollioBrand />
      </NuxtLink>
      <div class="flex items-center gap-1">
        <button
          ref="menuToggle"
          type="button"
          class="grid size-11 place-items-center rounded-xl text-muted transition-colors hover:bg-muted hover:text-default"
          :aria-expanded="menuOpen"
          aria-controls="workspace-mobile-nav"
          :aria-label="menuOpen ? t('navigation.menuClose') : t('navigation.menuOpen')"
          @click="menuOpen ? closeMenu() : openMenu()"
        >
          <KollioIcon :name="menuOpen ? 'close' : 'menu'" class="size-5" />
        </button>
        <NuxtLink :to="switchLocalePath(locale === 'fr' ? 'en' : 'fr')" class="min-h-11 rounded-xl px-2 text-sm font-medium leading-11 text-muted">
          {{ t('language.switch') }}
        </NuxtLink>
        <a href="/sign-out" class="min-h-11 rounded-xl border border-default bg-elevated px-2 text-sm font-medium leading-11">
          {{ t('auth.signOut') }}
        </a>
      </div>
    </header>

    <Transition name="workspace-drawer">
      <div v-if="menuOpen" class="workspace-drawer-layer fixed inset-x-0 bottom-0 top-16 z-30 lg:hidden">
        <button
          type="button"
          tabindex="-1"
          class="workspace-drawer-backdrop absolute inset-0"
          :aria-label="t('navigation.menuClose')"
          @click="closeMenu(true)"
        />
        <aside
          id="workspace-mobile-nav"
          ref="drawer"
          class="workspace-drawer absolute inset-y-0 left-0 w-80 max-w-[86vw] overflow-y-auto border-r border-default bg-elevated px-2 pt-4"
          role="dialog"
          aria-modal="true"
          :aria-label="t('navigation.label')"
          tabindex="-1"
        >
          <KollioWorkspaceNav @navigate="closeMenu()" />
        </aside>
      </div>
    </Transition>

    <aside class="workspace-rail sticky hidden flex-col border border-default bg-elevated/80 lg:flex">
      <NuxtLink :to="$localePath('/workspace')" class="inline-flex min-h-11 items-center px-2" :aria-label="t('brand')">
        <KollioBrand />
      </NuxtLink>
      <p class="mt-1 px-2 text-sm leading-snug text-muted">{{ t('navigation.promise') }}</p>

      <KollioWorkspaceNav class="mt-12" />

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

<style scoped>
.workspace-drawer {
  box-shadow: 0 24px 60px color-mix(in srgb, var(--kollio-active-ink) 22%, transparent);
}

.workspace-drawer-backdrop {
  background: color-mix(in srgb, var(--kollio-heading) 22%, transparent);
  backdrop-filter: blur(2px);
}

.workspace-drawer-enter-active,
.workspace-drawer-leave-active {
  transition: opacity 180ms ease;
}

.workspace-drawer-enter-active .workspace-drawer {
  transition: transform 220ms cubic-bezier(.16, 1, .3, 1);
}

.workspace-drawer-leave-active .workspace-drawer {
  transition: transform 160ms cubic-bezier(.3, 0, .7, 1);
}

.workspace-drawer-enter-from,
.workspace-drawer-leave-to {
  opacity: 0;
}

.workspace-drawer-enter-from .workspace-drawer,
.workspace-drawer-leave-to .workspace-drawer {
  transform: translateX(-100%);
}

@media (prefers-reduced-motion: reduce) {
  .workspace-drawer-enter-active,
  .workspace-drawer-leave-active,
  .workspace-drawer-enter-active .workspace-drawer,
  .workspace-drawer-leave-active .workspace-drawer {
    transition: none;
  }
}
</style>
