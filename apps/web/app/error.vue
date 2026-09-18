<script setup lang="ts">
import type { NuxtError } from '#app'

const props = defineProps<{ error: NuxtError }>()

const { t, locale } = useI18n()
const localePath = useLocalePath()
const switchLocalePath = useSwitchLocalePath()

const statusCode = computed(() => Number(props.error?.statusCode ?? 500))
const isNotFound = computed(() => statusCode.value === 404)
const homePath = computed(() => localePath('/'))

const i18nHead = useLocaleHead({ seo: true })

useHead(() => ({
  htmlAttrs: { ...i18nHead.value.htmlAttrs },
  title: `${isNotFound.value ? t('errors.notFound.title') : t('errors.generic.title')} · Kollio`,
  meta: [{ name: 'robots', content: 'noindex' }],
}))
</script>

<template>
  <div class="error-shell">
    <NuxtLink class="error-brand" :to="homePath" :aria-label="t('brand')">
      <KollioBrand />
    </NuxtLink>

    <main class="error-panel">
      <p class="error-code">{{ statusCode }}</p>
      <h1 class="error-title">{{ isNotFound ? t('errors.notFound.title') : t('errors.generic.title') }}</h1>
      <p class="error-description">
        {{ isNotFound ? t('errors.notFound.description') : t('errors.generic.description') }}
      </p>

      <KollioPrimaryAction
        :to="homePath"
        :label="isNotFound ? t('errors.notFound.action') : t('errors.generic.action')"
      />

      <NuxtLink
        class="error-language"
        :to="switchLocalePath(locale === 'fr' ? 'en' : 'fr')"
        :hreflang="locale === 'fr' ? 'en' : 'fr'"
      >
        {{ t('language.switch') }}
      </NuxtLink>
    </main>
  </div>
</template>

<style scoped>
.error-shell {
  display: grid;
  grid-template-rows: auto 1fr;
  gap: var(--kollio-space-2xl);
  min-height: 100vh;
  padding: var(--kollio-space-lg);
  background: var(--ui-bg);
  color: var(--ui-text);
}

.error-brand {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  min-height: 44px;
  border-radius: var(--kollio-radius-sm);
}

.error-panel {
  display: grid;
  gap: var(--kollio-space-md);
  justify-items: start;
  align-content: center;
  width: 100%;
  max-width: 620px;
  margin: 0 auto;
  padding-bottom: var(--kollio-space-4xl);
}

.error-code {
  margin: 0;
  font-family: var(--font-display);
  font-size: var(--kollio-display-section);
  font-weight: var(--kollio-weight-display);
  line-height: var(--kollio-leading-display);
  color: var(--kollio-action);
}

.error-title {
  margin: 0;
  font-family: var(--font-display);
  font-size: var(--kollio-text-title);
  font-weight: var(--kollio-weight-display);
  line-height: var(--kollio-leading-heading);
  color: var(--kollio-heading);
}

.error-description {
  margin: 0;
  max-width: 52ch;
  font-size: var(--kollio-text-body);
  line-height: var(--kollio-leading-relaxed);
  color: var(--ui-text-muted);
}

.error-language {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  font-size: var(--kollio-text-small);
  color: var(--ui-text-muted);
  border-radius: var(--kollio-radius-sm);
}

.error-brand:focus-visible,
.error-language:focus-visible {
  outline: 2px solid var(--kollio-connector);
  outline-offset: 2px;
}

@media (prefers-reduced-motion: no-preference) {
  .error-brand,
  .error-language {
    transition: color 160ms ease;
  }
}
</style>
