<script setup lang="ts">
const props = withDefaults(defineProps<{
  items: Array<{ id: string, label: string }>
  label: string
  modelValue: string
  idPrefix?: string
}>(), {
  idPrefix: 'context',
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const tabRefs = ref<Array<HTMLButtonElement | null>>([])

function tabId(id: string) {
  return `${props.idPrefix}-tab-${id}`
}

function select(id: string, focus = false) {
  emit('update:modelValue', id)
  if (!focus) return
  nextTick(() => tabRefs.value.find(tab => tab?.id === tabId(id))?.focus())
}

function handleKeydown(event: KeyboardEvent, index: number) {
  let nextIndex: number | undefined
  if (event.key === 'ArrowRight') nextIndex = (index + 1) % props.items.length
  if (event.key === 'ArrowLeft') nextIndex = (index - 1 + props.items.length) % props.items.length
  if (event.key === 'Home') nextIndex = 0
  if (event.key === 'End') nextIndex = props.items.length - 1
  if (nextIndex === undefined) return
  event.preventDefault()
  const item = props.items[nextIndex]
  if (item) select(item.id, true)
}
</script>

<template>
  <div class="context-tabs" role="tablist" :aria-label="label">
    <button
      v-for="(item, index) in items"
      :id="tabId(item.id)"
      :key="item.id"
      :ref="element => tabRefs[index] = element as HTMLButtonElement"
      type="button"
      role="tab"
      :aria-selected="modelValue === item.id"
      :tabindex="modelValue === item.id ? 0 : -1"
      :aria-controls="`${idPrefix}-panel`"
      @click="select(item.id)"
      @keydown="handleKeydown($event, index)"
    >
      <KollioSketchAnnotation :active="modelValue === item.id" kind="loop">{{ item.label }}</KollioSketchAnnotation>
    </button>
  </div>
</template>
