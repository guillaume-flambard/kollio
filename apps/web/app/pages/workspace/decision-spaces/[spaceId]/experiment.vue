<script setup lang="ts">
definePageMeta({ layout: 'workspace', middleware: 'authenticated' })

const { t } = useI18n()
</script>

<template>
  <KollioSpaceSection :title="t('decisionSpaces.section.experiment.title')" :body="t('decisionSpaces.section.experiment.body')" />
</template>
