<script setup lang="ts">
withDefaults(defineProps<{ title: string, tone?: 'settled' | 'question' }>(), { tone: 'settled' })
</script>

<template>
  <section class="reasoning-block" :class="`reasoning-block--${tone}`">
    <h3><KollioFeltMark>{{ title }}</KollioFeltMark></h3>
    <div class="reasoning-block__body"><slot /></div>
  </section>
</template>

<style scoped>
.reasoning-block { display: grid; gap: var(--kollio-space-sm); border-left: 1px solid var(--ui-border); padding: var(--kollio-space-md) 0 var(--kollio-space-md) var(--kollio-space-md); }
.reasoning-block h3 { color: var(--kollio-heading); font-size: var(--kollio-text-small); font-weight: var(--kollio-weight-strong); }
.reasoning-block__body { color: var(--ui-text-muted); font-size: var(--kollio-text-small); line-height: var(--kollio-leading-body); }
.reasoning-block--question { border-left-color: var(--kollio-question); }
</style>
