<script setup lang="ts">
const { t } = useI18n()

const stages = computed(() => [
  t('ideas.deposit.narration.context'),
  t('ideas.deposit.narration.fit'),
  t('ideas.deposit.narration.reuse'),
  t('ideas.deposit.narration.weigh'),
  t('ideas.deposit.narration.decide'),
])

const stage = ref(0)
let timer: ReturnType<typeof setInterval> | undefined

onMounted(() => {
  const reduced = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false
  if (reduced) {
    stage.value = stages.value.length - 1
    return
  }
  timer = setInterval(() => {
    if (stage.value >= stages.value.length - 1) {
      clearInterval(timer)
      return
    }
    stage.value += 1
  }, 700)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <div class="narration">
    <p class="narration-title" role="status">
      {{ t('ideas.deposit.running') }}
    </p>
    <ol class="narration-steps" :aria-label="t('ideas.deposit.running')">
      <li
        v-for="(label, index) in stages"
        :key="label"
        class="narration-step"
        :data-done="index <= stage"
        :data-current="index === stage"
      >
        <span class="narration-dot" aria-hidden="true" />
        <span>{{ label }}</span>
      </li>
    </ol>
  </div>
</template>

<style scoped>
.narration {
  display: grid;
  gap: 14px;
  border: 1px solid var(--ui-border);
  border-radius: var(--kollio-radius-lg);
  background: color-mix(in srgb, var(--ui-bg-muted) 72%, transparent);
  padding: 18px 20px;
}

.narration-title {
  margin: 0;
  color: var(--kollio-active-ink);
  font-size: .95rem;
  font-weight: 600;
}

.narration-steps {
  display: grid;
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.narration-step {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--ui-text-muted);
  font-size: .9rem;
  transition: color 200ms ease;
}

.narration-dot {
  width: 10px;
  height: 10px;
  flex: 0 0 auto;
  border: 1.5px solid var(--ui-text-muted);
  border-radius: 50%;
  transition: background 200ms ease, border-color 200ms ease, transform 200ms ease;
}

.narration-step[data-done='true'] {
  color: var(--ui-text);
}

.narration-step[data-done='true'] .narration-dot {
  border-color: var(--ui-success);
  background: var(--ui-success);
}

.narration-step[data-current='true'] .narration-dot {
  transform: scale(1.18);
}

@media (prefers-reduced-motion: reduce) {
  .narration-step,
  .narration-dot {
    transition: none;
  }
}
</style>
