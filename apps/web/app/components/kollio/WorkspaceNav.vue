<script setup lang="ts">
const { t } = useI18n()
const route = useRoute()
const localePath = useLocalePath()

defineEmits<{ navigate: [] }>()

const spacesRoot = computed(() => localePath('/workspace'))
const ideasRoot = computed(() => localePath('/workspace/ideas'))
const settingsRoot = computed(() => localePath('/workspace/settings'))
const spacesActive = computed(() => route.path === spacesRoot.value || route.path.startsWith(`${spacesRoot.value}/decision-spaces`))
const ideasActive = computed(() => route.path.startsWith(ideasRoot.value))
const settingsActive = computed(() => route.path.startsWith(settingsRoot.value))
</script>

<template>
  <nav class="workspace-nav" :aria-label="t('navigation.label')">
    <NuxtLink
      :to="spacesRoot"
      class="group flex min-h-11 w-full items-center rounded-xl text-sm font-medium text-muted transition-colors hover:text-default"
      :class="spacesActive ? 'text-default' : ''"
      :data-active="spacesActive ? 'true' : 'false'"
      @click="$emit('navigate')"
    >
      <KollioSketchAnnotation :active="spacesActive" kind="loop" class="workspace-nav-sketch">
        <span class="flex items-center gap-3">
          <svg aria-hidden="true" viewBox="0 0 24 24" class="size-5 shrink-0" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M12 3 3 8l9 5 9-5-9-5Z" /><path d="m3 14 9 5 9-5" /></svg>
          {{ t('navigation.decisionSpaces') }}
        </span>
      </KollioSketchAnnotation>
    </NuxtLink>

    <NuxtLink
      :to="ideasRoot"
      class="group mt-2 flex min-h-11 w-full items-center gap-3 rounded-xl px-3 text-sm font-medium text-muted transition-colors hover:text-default"
      :class="ideasActive ? 'text-default' : ''"
      :data-active="ideasActive ? 'true' : 'false'"
      @click="$emit('navigate')"
    >
      <svg aria-hidden="true" viewBox="0 0 24 24" class="size-5 shrink-0" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M9 18h6m-5 3h4m4.5-10.5a6.5 6.5 0 1 0-10.7 5l.7.6c.9.8 1.5 1.9 1.5 3.1h4c0-1.2.6-2.3 1.5-3.1l.7-.6a6.5 6.5 0 0 0 2.3-5Z" /></svg>
      {{ t('navigation.ideas') }}
    </NuxtLink>

    <NuxtLink
      :to="settingsRoot"
      class="group mt-2 flex min-h-11 w-full items-center gap-3 rounded-xl px-3 text-sm font-medium text-muted transition-colors hover:text-default"
      :class="settingsActive ? 'text-default' : ''"
      :data-active="settingsActive ? 'true' : 'false'"
      @click="$emit('navigate')"
    >
      <svg aria-hidden="true" viewBox="0 0 24 24" class="size-5 shrink-0" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z" /><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.9.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.9 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.9l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.9.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.9-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.9V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1Z" /></svg>
      {{ t('navigation.settings') }}
    </NuxtLink>
  </nav>
</template>
