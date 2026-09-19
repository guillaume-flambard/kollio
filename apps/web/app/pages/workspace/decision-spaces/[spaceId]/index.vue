<script setup lang="ts">
definePageMeta({ layout: 'workspace', middleware: 'authenticated' })

const { t } = useI18n()
const route = useRoute()
const localePath = useLocalePath()

const moments = [
  { key: 'frame', first: 'explore' },
  { key: 'choose', first: 'options' },
  { key: 'happened', first: 'experiment' },
] as const

const spaceId = String(route.params.spaceId)

function momentLink(section: string) {
  return {
    path: localePath(`/workspace/decision-spaces/${spaceId}/${section}`),
    query: route.query.workspace ? { workspace: route.query.workspace } : undefined,
  }
}
</script>

<template>
  <section class="space-orientation" :aria-label="t('decisionSpaces.moments.title')">
    <h2 class="space-orientation-title">{{ t('decisionSpaces.moments.title') }}</h2>
    <ul class="space-orientation-moments">
      <li v-for="moment in moments" :key="moment.key" class="space-orientation-moment">
        <h3>{{ t(`decisionSpaces.moments.${moment.key}.label`) }}</h3>
        <p class="space-orientation-description">{{ t(`decisionSpaces.moments.${moment.key}.description`) }}</p>
        <p class="space-orientation-guidance">{{ t(`decisionSpaces.moments.${moment.key}.empty`) }}</p>
        <NuxtLink class="space-orientation-action" :to="momentLink(moment.first)">
          {{ t(`decisionSpaces.moments.${moment.key}.action`) }}
        </NuxtLink>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.space-orientation {
  display: grid;
  gap: var(--kollio-space-lg);
}

.space-orientation-title {
  color: var(--kollio-heading);
  font-size: var(--kollio-text-title);
  font-weight: var(--kollio-weight-display);
}

.space-orientation-moments {
  display: grid;
  gap: var(--kollio-space-md);
  margin: 0;
  padding: 0;
  list-style: none;
}

.space-orientation-moment {
  display: grid;
  gap: 6px;
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-lg);
  padding: var(--kollio-space-md);
}

.space-orientation-moment h3 {
  color: var(--kollio-heading);
  font-size: var(--kollio-text-lead);
  font-weight: var(--kollio-weight-strong);
}

.space-orientation-description {
  color: var(--ui-text);
  font-size: var(--kollio-text-small);
}

.space-orientation-guidance {
  color: var(--ui-text-muted);
  font-size: var(--kollio-text-small);
}

.space-orientation-action {
  justify-self: start;
  display: inline-flex;
  min-height: 42px;
  align-items: center;
  border-radius: var(--kollio-radius-pill);
  padding: 0 16px;
  background: var(--ui-bg-accented);
  color: var(--kollio-active-ink);
  font-size: var(--kollio-text-small);
  font-weight: var(--kollio-weight-strong);
}

.space-orientation-action:focus-visible {
  outline: 2px solid var(--kollio-active-ink);
  outline-offset: 1px;
}
</style>
