<script setup lang="ts">
defineProps<{
  label: string
}>()
</script>

<template>
  <div class="idea-layout idea-detail-skeleton relative grid min-w-0" role="status" aria-live="polite">
    <span class="sr-only">{{ label }}</span>
    <div class="kollio-surface idea-document min-w-0 p-5 sm:p-7">
      <div class="skeleton-line w-28" />
      <div class="mt-8 space-y-3">
        <div class="skeleton-line h-10 w-4/5" />
        <div class="skeleton-line h-10 w-3/5" />
      </div>
      <div class="mt-7 flex gap-3">
        <div class="skeleton-line h-5 w-24" />
        <div class="skeleton-line h-5 w-40" />
      </div>
      <div class="mt-8 space-y-3">
        <div class="skeleton-line w-full" />
        <div class="skeleton-line w-5/6" />
      </div>
      <div class="skeleton-card mt-11 h-[340px]" />
      <div class="skeleton-card mt-7 h-28" />
    </div>
    <aside class="kollio-surface idea-companion self-start overflow-hidden">
      <div class="grid h-16 grid-cols-3 gap-5 border-b border-default px-7 py-5">
        <div class="skeleton-line" />
        <div class="skeleton-line" />
        <div class="skeleton-line" />
      </div>
      <div class="space-y-6 p-5">
        <div class="skeleton-line h-6 w-2/5" />
        <div class="flex items-center gap-3">
          <div class="skeleton-circle" />
          <div class="flex-1 space-y-2">
            <div class="skeleton-line w-1/2" />
            <div class="skeleton-line w-1/3" />
          </div>
        </div>
        <div class="skeleton-card h-24" />
      </div>
    </aside>
  </div>
</template>
