<script setup lang="ts">
definePageMeta({ layout: 'workspace', middleware: 'authenticated' })

const { t } = useI18n()
</script>

<template>
  <KollioSpaceSection :title="t('decisionSpaces.section.options.title')" :body="t('decisionSpaces.section.options.body')" />
</template>
