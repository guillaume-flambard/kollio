<script setup lang="ts">
const { t } = useI18n()
const route = useRoute()
const localePath = useLocalePath()

defineEmits<{ navigate: [] }>()

const inboxRoot = computed(() => localePath('/workspace'))
const decisionSpacesRoot = computed(() => localePath('/workspace/decision-spaces'))
const settingsRoot = computed(() => localePath('/workspace/settings'))
const inboxActive = computed(() => route.path === inboxRoot.value)
const decisionSpacesActive = computed(() =>
  route.path === decisionSpacesRoot.value || route.path.startsWith(`${decisionSpacesRoot.value}/`),
)
const settingsActive = computed(() => route.path.startsWith(settingsRoot.value))
</script>

<template>
  <nav class="workspace-nav" :aria-label="t('navigation.label')">
    <NuxtLink
      :to="inboxRoot"
      class="group flex min-h-11 w-full items-center rounded-xl text-sm font-medium text-muted transition-colors hover:text-default"
      :class="inboxActive ? 'text-default' : ''"
      :data-active="inboxActive ? 'true' : 'false'"
      @click="$emit('navigate')"
    >
      <KollioSketchAnnotation :active="inboxActive" kind="loop" class="workspace-nav-sketch">
        <span class="flex items-center gap-3">
          <KollioIcon name="inbox" class="size-5 shrink-0" />
          {{ t('navigation.inbox') }}
        </span>
      </KollioSketchAnnotation>
    </NuxtLink>

    <NuxtLink
      :to="decisionSpacesRoot"
      class="group mt-2 flex min-h-11 w-full items-center gap-3 rounded-xl px-3 text-sm font-medium text-muted transition-colors hover:text-default"
      :class="decisionSpacesActive ? 'text-default' : ''"
      :data-active="decisionSpacesActive ? 'true' : 'false'"
      @click="$emit('navigate')"
    >
      <KollioIcon name="spaces" class="size-5 shrink-0" />
      {{ t('navigation.decisionSpaces') }}
    </NuxtLink>

    <NuxtLink
      :to="settingsRoot"
      class="group mt-2 flex min-h-11 w-full items-center gap-3 rounded-xl px-3 text-sm font-medium text-muted transition-colors hover:text-default"
      :class="settingsActive ? 'text-default' : ''"
      :data-active="settingsActive ? 'true' : 'false'"
      @click="$emit('navigate')"
    >
      <KollioIcon name="settings" class="size-5 shrink-0" />
      {{ t('navigation.settings') }}
    </NuxtLink>
  </nav>
</template>
