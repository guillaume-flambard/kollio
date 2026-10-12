<script setup lang="ts">
import { spatialV3Fixture } from '~/utils/spatialV3.generated'

definePageMeta({ layout: false })
const { t } = useI18n()
useSeoMeta({
  title: () => t('spatialV3.previewTitle'),
  description: () => t('spatialV3.previewDescription'),
})
</script>

<template>
  <div class="spatial-v3-page" data-kollio-theme="light">
    <header class="spatial-v3-page__bar">
      <div class="spatial-v3-page__brand"><span class="spatial-v3-page__mark" aria-hidden="true" /> {{ t('brand') }} <span class="spatial-v3-page__version">{{ t('spatialV3.previewLabel') }}</span></div>
      <NuxtLink to="/" :aria-label="t('spatialV3.back')" class="spatial-v3-page__back">
        {{ t('spatialV3.back') }}
      </NuxtLink>
    </header>
    <KollioV3SpatialStage :fixture="spatialV3Fixture" />
  </div>
</template>

<style>
@import '../assets/css/spatial-v3.tokens.css';
.spatial-v3-page{min-height:100vh;background:var(--k-color-paper);color:var(--k-color-ink)}
.spatial-v3-page__bar{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:16px 30px;border-bottom:1px solid var(--k-color-border)}
.spatial-v3-page__brand{font-size:18px;font-weight:730;letter-spacing:-.045em;display:flex;align-items:center;gap:10px}
.spatial-v3-page__mark::before{content:'◇'}
.spatial-v3-page__mark{font-size:27px;line-height:1;color:var(--k-color-accent)}
.spatial-v3-page__version{font-size:11px;font-weight:550;letter-spacing:0;border:1px solid var(--k-color-border);padding:4px 8px;border-radius:7px;color:var(--k-color-muted)}
.spatial-v3-page__back{font-size:12px;color:var(--k-color-accent);min-height:40px;display:flex;align-items:center}
.spatial-v3-page__back:focus-visible{outline:2px solid var(--k-color-accent);outline-offset:3px}
@media(max-width:600px){.spatial-v3-page__bar{padding:12px 16px}.spatial-v3-page__brand{font-size:15px}.spatial-v3-page__version{display:none}}
</style>
