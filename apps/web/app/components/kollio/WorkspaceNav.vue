<script setup lang="ts">
const { t } = useI18n()

defineEmits<{ navigate: [] }>()

const upcoming = ['workshops', 'community', 'resources'] as const
const utilities = ['search', 'notifications'] as const
</script>

<template>
  <nav class="workspace-nav" :aria-label="t('navigation.label')">
    <NuxtLink
      :to="$localePath('/workspace')"
      class="workspace-nav-active group flex min-h-11 w-full items-center rounded-xl text-sm font-medium text-muted transition-colors hover:text-default"
      active-class="workspace-nav-active text-default"
      @click="$emit('navigate')"
    >
      <KollioSketchAnnotation active kind="loop" class="workspace-nav-sketch">
        <span class="flex items-center gap-3">
          <svg aria-hidden="true" viewBox="0 0 24 24" class="size-5 shrink-0" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M9 18h6m-5 3h4m4.5-10.5a6.5 6.5 0 1 0-10.7 5l.7.6c.9.8 1.5 1.9 1.5 3.1h4c0-1.2.6-2.3 1.5-3.1l.7-.6a6.5 6.5 0 0 0 2.3-5Z" /></svg>
          {{ t('navigation.ideas') }}
        </span>
      </KollioSketchAnnotation>
    </NuxtLink>

    <NuxtLink
      :to="$localePath('/workspace/settings')"
      class="group mt-2 flex min-h-11 w-full items-center gap-3 rounded-xl px-3 text-sm font-medium text-muted transition-colors hover:text-default"
      active-class="text-default"
      @click="$emit('navigate')"
    >
      <svg aria-hidden="true" viewBox="0 0 24 24" class="size-5 shrink-0" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z" /><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.9.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.9 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.9l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.9.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.9-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.9V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1Z" /></svg>
      {{ t('navigation.settings') }}
    </NuxtLink>

    <div class="mt-2 space-y-1" role="group" :aria-label="t('navigation.upcoming')">
      <button v-for="item in upcoming" :key="item" type="button" disabled aria-disabled="true" class="flex min-h-11 w-full cursor-default items-center gap-3 rounded-xl border-0 bg-transparent px-3 text-left text-sm text-muted">
        <svg v-if="item === 'workshops'" aria-hidden="true" viewBox="0 0 24 24" class="size-5" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M4 7h16M7 4v6m10-6v6M5 11h14v9H5z" /></svg>
        <svg v-else-if="item === 'community'" aria-hidden="true" viewBox="0 0 24 24" class="size-5" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M16 20a4 4 0 0 0-8 0M12 13a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm7 7a3 3 0 0 0-3-3m1-9a3 3 0 0 1 0 6M5 20a3 3 0 0 1 3-3M7 8a3 3 0 0 0 0 6" /></svg>
        <svg v-else aria-hidden="true" viewBox="0 0 24 24" class="size-5" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H11v17H6.5A2.5 2.5 0 0 0 4 22V5.5ZM20 5.5A2.5 2.5 0 0 0 17.5 3H13v17h4.5A2.5 2.5 0 0 1 20 22V5.5Z" /></svg>
        {{ t(`navigation.${item}`) }}
      </button>
    </div>

    <div class="mt-7 space-y-1 border-t border-default pt-5">
      <button v-for="item in utilities" :key="item" type="button" disabled aria-disabled="true" class="flex min-h-11 w-full cursor-default items-center gap-3 rounded-xl border-0 bg-transparent px-3 text-left text-sm text-muted">
        <svg v-if="item === 'search'" aria-hidden="true" viewBox="0 0 24 24" class="size-5" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="11" cy="11" r="7" /><path d="m16 16 5 5" /></svg>
        <svg v-else aria-hidden="true" viewBox="0 0 24 24" class="size-5" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9ZM10 21h4" /></svg>
        {{ t(`navigation.${item}`) }}
      </button>
    </div>
  </nav>
</template>
