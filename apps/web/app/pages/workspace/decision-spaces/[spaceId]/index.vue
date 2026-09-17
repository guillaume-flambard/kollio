<script setup lang="ts">
definePageMeta({ layout: 'workspace', middleware: 'authenticated' })

await navigateTo(`${useRoute().path}/explore`, { redirectCode: 302 })
</script>

<template>
  <div />
</template>
