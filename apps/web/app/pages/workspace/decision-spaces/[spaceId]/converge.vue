<script setup lang="ts">
definePageMeta({ layout: 'workspace', middleware: 'authenticated' })

const { t } = useI18n()
</script>

<template>
  <KollioSpaceSection :title="t('decisionSpaces.section.converge.title')" :body="t('decisionSpaces.section.converge.body')" />
</template>
