<script setup lang="ts">
const { t } = useI18n()
const route = useRoute()
const localePath = useLocalePath()

defineEmits<{ navigate: [] }>()

const inboxRoot = computed(() => localePath('/workspace'))
const decisionSpacesRoot = computed(() => localePath('/workspace/decision-spaces'))
const ideasRoot = computed(() => localePath('/workspace/ideas'))
const settingsRoot = computed(() => localePath('/workspace/settings'))
const inboxActive = computed(() => route.path === inboxRoot.value)
const decisionSpacesActive = computed(() =>
  route.path === decisionSpacesRoot.value || route.path.startsWith(`${decisionSpacesRoot.value}/`),
)
const ideasActive = computed(() => route.path.startsWith(ideasRoot.value))
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
          <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" class="size-5 shrink-0">
            <path
              d="M4 11h5l2 3h2l2-3h5"
              stroke="currentColor"
              stroke-width="1.6"
              stroke-linejoin="round"
            />
            <path
              d="M4 11 6.5 5h11L20 11v7H4z"
              stroke="currentColor"
              stroke-width="1.6"
              stroke-linejoin="round"
            />
          </svg>
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
      <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" class="size-5 shrink-0">
        <path
          d="M12 3 3 8l9 5 9-5-9-5Z"
          stroke="currentColor"
          stroke-width="1.6"
          stroke-linejoin="round"
        />
        <path
          d="m3 14 9 5 9-5"
          stroke="currentColor"
          stroke-width="1.6"
          stroke-linejoin="round"
        />
      </svg>
      {{ t('navigation.decisionSpaces') }}
    </NuxtLink>

    <NuxtLink
      :to="ideasRoot"
      class="group mt-2 flex min-h-11 w-full items-center gap-3 rounded-xl px-3 text-sm font-medium text-muted transition-colors hover:text-default"
      :class="ideasActive ? 'text-default' : ''"
      :data-active="ideasActive ? 'true' : 'false'"
      @click="$emit('navigate')"
    >
      <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" class="size-5 shrink-0">
        <path
          d="M9 18h6m-5 3h4M12 3a6 6 0 0 0-3 11v1h6v-1a6 6 0 0 0-3-11Z"
          stroke="currentColor"
          stroke-width="1.6"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
      {{ t('navigation.ideas') }}
    </NuxtLink>

    <NuxtLink
      :to="settingsRoot"
      class="group mt-2 flex min-h-11 w-full items-center gap-3 rounded-xl px-3 text-sm font-medium text-muted transition-colors hover:text-default"
      :class="settingsActive ? 'text-default' : ''"
      :data-active="settingsActive ? 'true' : 'false'"
      @click="$emit('navigate')"
    >
      <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" class="size-5 shrink-0">
        <path
          d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"
          stroke="currentColor"
          stroke-width="1.6"
          stroke-linejoin="round"
        />
        <path
          d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-2.9 1.2 2 2 0 1 1-4 0 1.7 1.7 0 0 0-2.9-1.2l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1A1.7 1.7 0 0 0 3 15a2 2 0 1 1 0-4 1.7 1.7 0 0 0 1.3-2.9l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1A1.7 1.7 0 0 0 10 4a2 2 0 1 1 4 0 1.7 1.7 0 0 0 2.9 1.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1A1.7 1.7 0 0 0 21 11a2 2 0 1 1 0 4Z"
          stroke="currentColor"
          stroke-width="1.6"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
      {{ t('navigation.settings') }}
    </NuxtLink>
  </nav>
</template>
