<script setup lang="ts">
withDefaults(defineProps<{
  title: string
  description: string
  reassurance?: string
  retryLabel: string
  backLabel: string
  backTo: string
  imageSrc?: string
}>(), {
  reassurance: undefined,
  imageSrc: '/images/states/idea-load-error.png',
})

defineEmits<{
  retry: []
}>()
</script>

<template>
  <section class="kollio-surface idea-detail-error" role="alert">
    <div class="idea-detail-error-copy">
      <div class="idea-detail-error-signal" aria-hidden="true">
        <span />
        <i />
        <span />
      </div>

      <div class="idea-detail-error-message">
        <h1>{{ title }}</h1>
        <p>{{ description }}</p>
        <p v-if="reassurance" class="idea-detail-error-reassurance">{{ reassurance }}</p>

        <div class="idea-detail-error-actions">
          <KollioPrimaryAction :label="retryLabel" @click="$emit('retry')" />
          <NuxtLink :to="backTo" class="idea-detail-error-back">
            {{ backLabel }}
            <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path d="M5 12h14m-5-5 5 5-5 5" />
            </svg>
          </NuxtLink>
        </div>
      </div>
    </div>

    <div class="idea-detail-error-visual" aria-hidden="true">
      <img :src="imageSrc" alt="">
      <div class="idea-detail-error-caption-line">
        <span />
        <i />
      </div>
    </div>
  </section>
</template>
