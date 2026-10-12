<script setup lang="ts">
import type { SpatialV3Edge, SpatialV3Fixture, SpatialV3Node } from '~/utils/spatialV3.generated'
import { fitSpatialV3, spatialV3Bounds, zoomSpatialV3, panSpatialV3, type SpatialV3Camera } from '~/utils/spatialV3Camera'

const props = defineProps<{ fixture: SpatialV3Fixture, initialDepth?: 1 | 2 }>()
const { t } = useI18n()
const depth = ref<1 | 2>(props.initialDepth ?? 1)
const selectedId = ref<string | null>(null)
const spotlightId = ref<string | null>(null)
const spotlightIDs = computed(() => {
  if (!spotlightId.value) return null
  const ids = new Set([spotlightId.value])
  for (const edge of props.fixture.edges) {
    if (edge.source === spotlightId.value) ids.add(edge.target)
    if (edge.target === spotlightId.value) ids.add(edge.source)
  }
  return ids
})
function returnToContext() { spotlightId.value = null; showEverything() }
const searchQuery = ref('')
const focusedGroup = ref<number | null>(null)
const GROUP_SIZE = 12
const groups = computed(() => Array.from({ length: Math.ceil(props.fixture.nodes.length / GROUP_SIZE) }, (_, index) => ({
  index,
  ids: props.fixture.nodes.slice(index * GROUP_SIZE, (index + 1) * GROUP_SIZE).map(node => node.id),
})))
const matchingNodes = computed(() => props.fixture.nodes.filter(node => node.label.toLocaleLowerCase().includes(searchQuery.value.trim().toLocaleLowerCase()) || node.id.toLocaleLowerCase().includes(searchQuery.value.trim().toLocaleLowerCase())))
const shownIds = computed(() => focusedGroup.value === null ? null : new Set(groups.value[focusedGroup.value]?.ids ?? []))
function focusNode(node: SpatialV3Node) {
  depth.value = 2
  focusedGroup.value = null
  selectedId.value = node.id
  spotlightId.value = node.id
  nextTick(() => {
    const element = stageRef.value
    if (!element) return
    const zoom = Math.min(1.2, Math.max(0.8, camera.value.zoom))
    camera.value = { zoom, x: element.clientWidth / 2 - (node.x * 1000 - sceneOrigin.value.x) * zoom,
      y: element.clientHeight / 2 - (node.y * 640 - sceneOrigin.value.y) * zoom }
    hasMovedCamera = true
  })
}
function focusGroup(index: number) {
  focusedGroup.value = index
  spotlightId.value = null
  depth.value = 2
  const members = props.fixture.nodes.filter(node => groups.value[index]?.ids.includes(node.id))
  nextTick(() => {
    const viewport = stageRef.value
    if (!viewport || !members.length) return
    const bounds = spatialV3Bounds(members)
    camera.value = fitSpatialV3(viewport.clientWidth, viewport.clientHeight, {
      x: bounds.x - sceneOrigin.value.x, y: bounds.y - sceneOrigin.value.y, width: bounds.width, height: bounds.height,
    })
    hasMovedCamera = true
  })
}
function showEverything() {
  focusedGroup.value = null
  spotlightId.value = null
  depth.value = 2
  nextTick(() => fitView())
}

const stageRef = ref<HTMLElement | null>(null)
const camera = ref<SpatialV3Camera>({ zoom: 1, x: 0, y: 0 })
const isPanning = ref(false)
let panPointer: number | null = null
let pointerPosition = { x: 0, y: 0 }
let resizeObserver: ResizeObserver | undefined
let hasMovedCamera = false

function fitView() {
  const stage = stageRef.value
  if (!stage) return
  camera.value = fitSpatialV3(stage.clientWidth, stage.clientHeight, {
    x: sceneBounds.value.x - sceneOrigin.value.x,
    y: sceneBounds.value.y - sceneOrigin.value.y,
    width: sceneBounds.value.width,
    height: sceneBounds.value.height,
  })
  hasMovedCamera = false
}
function zoomView(factor: number, clientX?: number, clientY?: number) {
  const rect = stageRef.value?.getBoundingClientRect()
  if (!rect) return
  const cx = clientX === undefined ? rect.width / 2 : clientX - rect.left
  const cy = clientY === undefined ? rect.height / 2 : clientY - rect.top
  camera.value = zoomSpatialV3(camera.value, factor, cx, cy)
  hasMovedCamera = true
}
function onWheel(event: WheelEvent) {
  if (event.ctrlKey || event.metaKey) zoomView(Math.exp(-event.deltaY * 0.003), event.clientX, event.clientY)
  else {
    camera.value = panSpatialV3(camera.value, -event.deltaX, -event.deltaY)
    hasMovedCamera = true
  }
}
function onPointerDown(event: PointerEvent) {
  if (event.button !== 0 || (event.target as HTMLElement).closest('[data-spatial-node], button')) return
  panPointer = event.pointerId
  pointerPosition = { x: event.clientX, y: event.clientY }
  isPanning.value = true
  stageRef.value?.setPointerCapture(event.pointerId)
}
function onPointerMove(event: PointerEvent) {
  if (panPointer !== event.pointerId) return
  camera.value = panSpatialV3(camera.value, event.clientX - pointerPosition.x, event.clientY - pointerPosition.y)
  pointerPosition = { x: event.clientX, y: event.clientY }
  hasMovedCamera = true
}
function onPointerEnd(event: PointerEvent) {
  if (panPointer !== event.pointerId) return
  panPointer = null
  isPanning.value = false
  if (stageRef.value?.hasPointerCapture(event.pointerId))
    stageRef.value.releasePointerCapture(event.pointerId)
}
function onStageKeydown(event: KeyboardEvent) {
  if (event.target !== stageRef.value) return
  if (event.key === '0') fitView()
  else if (event.key === '+' || event.key === '=') zoomView(1.2)
  else if (event.key === '-') zoomView(1 / 1.2)
  else if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(event.key)) {
    const movement: Record<string, [number, number]> = { ArrowUp: [0, 42], ArrowDown: [0, -42], ArrowLeft: [42, 0], ArrowRight: [-42, 0] }
    const [dx, dy] = movement[event.key]!
    camera.value = panSpatialV3(camera.value, dx, dy)
  } else return
  event.preventDefault()
}
onMounted(() => {
  resizeObserver = new ResizeObserver(() => { if (!hasMovedCamera) fitView() })
  if (stageRef.value) resizeObserver.observe(stageRef.value)
  fitView()
})
onBeforeUnmount(() => { resizeObserver?.disconnect() })


const visibleNodes = computed(() => props.fixture.nodes.filter(node => node.depth <= depth.value && (!shownIds.value || shownIds.value.has(node.id))))
const visibleEdges = computed(() => props.fixture.edges.filter(edge => edge.depth <= depth.value && (!shownIds.value || (shownIds.value.has(edge.source) && shownIds.value.has(edge.target)))))
const selectedNode = computed(() => visibleNodes.value.find(node => node.id === selectedId.value))
const hiddenCount = computed(() => props.fixture.nodes.filter(node => node.depth > depth.value).length)
// Stable origin: expansion cannot shift existing objects as hidden nodes appear.
const sceneBounds = computed(() => spatialV3Bounds(visibleNodes.value))
const fullBounds = computed(() => spatialV3Bounds(props.fixture.nodes))
const sceneOrigin = computed(() => ({
  x: Math.min(0, fullBounds.value.x),
  y: Math.min(0, fullBounds.value.y),
}))
const sceneSize = computed(() => ({
  width: Math.max(1000, fullBounds.value.x + fullBounds.value.width - sceneOrigin.value.x),
  height: Math.max(640, fullBounds.value.y + fullBounds.value.height - sceneOrigin.value.y),
}))
const svgViewBox = computed(() => [
  sceneOrigin.value.x, sceneOrigin.value.y, sceneSize.value.width, sceneSize.value.height,
].join(' '))


function edgePath(edge: SpatialV3Edge): string {
  const points = edge.points
  if (!points || points.length < 2)
    return ''
  return points.map((p, index) => `${index ? 'L' : 'M'} ${p.x} ${p.y}`).join(' ')
}
function changeDepth(next: 1 | 2) {
  const mayRefit = !hasMovedCamera
  depth.value = next
  if (selectedId.value && !visibleNodes.value.some(node => node.id === selectedId.value))
    selectedId.value = null
  if (mayRefit)
    nextTick(() => fitView())
}
function selectNode(node: SpatialV3Node) {
  selectedId.value = selectedId.value === node.id ? null : node.id
  spotlightId.value = selectedId.value
}
</script>

<template>
  <section class="spatial-v3" :aria-label="t('spatialV3.accessibleStage')">
    <div class="spatial-v3__heading">
      <div>
        <p class="spatial-v3__eyebrow">{{ t('spatialV3.eyebrow') }}</p>
        <h1>{{ fixture.title }}</h1>
        <p>{{ fixture.subtitle }}</p>
      </div>
      <button type="button" class="spatial-v3__expand" :aria-expanded="depth === 2" @click="changeDepth(depth === 1 ? 2 : 1)">
        {{ depth === 1 ? t('spatialV3.expand', { count: hiddenCount }) : t('spatialV3.collapse') }}
      </button>
    </div>

    <div v-if="spotlightId" class="spatial-v3__focusbar" role="status">
      {{ t('spatialV3.focusContext', { count: spotlightIDs?.size ?? 0 }) }}
      <button type="button" @click="returnToContext">{{ t('spatialV3.returnToContext') }}</button>
    </div>
    <div v-if="fixture.nodes.length > 20" class="spatial-v3__discovery">
      <label class="spatial-v3__search-label">
        {{ t('spatialV3.findObject') }}
        <input v-model="searchQuery" type="search" :placeholder="t('spatialV3.searchPlaceholder')">
      </label>
      <div v-if="searchQuery.trim()" class="spatial-v3__matches" role="list">
        <button v-for="node in matchingNodes.slice(0, 8)" :key="node.id" type="button" @click="focusNode(node)">{{ node.label }}</button>
        <p v-if="!matchingNodes.length">{{ t('spatialV3.noMatch') }}</p>
      </div>
      <div class="spatial-v3__group-list" role="group" :aria-label="t('spatialV3.groups')">
        <button type="button" :aria-pressed="focusedGroup === null" @click="showEverything">{{ t('spatialV3.overview') }}</button>
        <button v-for="group in groups" :key="group.index" type="button" :aria-pressed="focusedGroup === group.index" @click="focusGroup(group.index)">
          {{ t('spatialV3.groupNumber', { number: group.index + 1, count: group.ids.length }) }}
        </button>
      </div>
    </div>
    <div
      ref="stageRef"
      class="spatial-v3__scroll"
      :class="{ 'spatial-v3__scroll--panning': isPanning }"
      role="region"
      :aria-label="t('spatialV3.accessibleCanvas')"
      tabindex="0"
      @pointerdown="onPointerDown"
      @pointermove="onPointerMove"
      @pointerup="onPointerEnd"
      @pointercancel="onPointerEnd"
      @lostpointercapture="onPointerEnd"
      @wheel.prevent="onWheel"
      @keydown="onStageKeydown"
    >
      <div class="spatial-v3__canvas" :style="{ width: sceneSize.width + 'px', height: sceneSize.height + 'px', transform: 'translate(' + camera.x + 'px, ' + camera.y + 'px) scale(' + camera.zoom + ')' }">
        <p class="spatial-v3__folio">{{ t('spatialV3.folio') }}</p>
        <svg aria-hidden="true" class="spatial-v3__edges" :viewBox="svgViewBox" preserveAspectRatio="none">
          <path v-for="edge in visibleEdges" :key="edge.id" :class="[`spatial-v3__edge--${edge.type}`, { 'spatial-v3__edge--dimmed': spotlightId && edge.source !== spotlightId && edge.target !== spotlightId }]" :d="edgePath(edge)" />
        </svg>
        <button
          v-for="node in visibleNodes"
          :key="node.id"
          data-spatial-node
          type="button"
          class="spatial-v3__node"
          :class="[`spatial-v3__node--${node.kind}`, `spatial-v3__node--${node.status}`, { 'spatial-v3__node--dimmed': spotlightIDs && !spotlightIDs.has(node.id) }]"
          :style="{ left: (node.x * 1000 - sceneOrigin.x) + 'px', top: (node.y * 640 - sceneOrigin.y) + 'px' }"
          :aria-pressed="selectedId === node.id"
          :aria-label="t('spatialV3.nodeAria', { role: node.eyebrow, label: node.label, status: node.status })"
          @click="selectNode(node)"
        >
          <span class="spatial-v3__type">{{ node.eyebrow }}</span>
          <strong>{{ node.label }}</strong>
          <small>{{ node.kind === 'mission' ? t('spatialV3.missionCaption') : node.kind === 'source' ? t('spatialV3.sourceCaption') : node.kind === 'proposal' ? t('spatialV3.proposalCaption') : '' }}</small>
        </button>
        <div class="spatial-v3__legend" aria-label="Types de relations">
          <span>{{ t('spatialV3.relationConfirmed') }}</span><span>{{ t('spatialV3.relationProposed') }}</span><span>{{ t('spatialV3.countShown', { count: visibleNodes.length }) }}</span>
        </div>
      </div>
      <div class="spatial-v3__controls" role="group" :aria-label="t('spatialV3.cameraControls')">
        <button type="button" :aria-label="t('spatialV3.zoomOut')" @click="zoomView(1 / 1.2)">{{ t('spatialV3.zoomOutSymbol') }}</button>
        <span aria-live="polite">{{ t('spatialV3.zoomPercent', { count: Math.round(camera.zoom * 100) }) }}</span>
        <button type="button" :aria-label="t('spatialV3.zoomIn')" @click="zoomView(1.2)">{{ t('spatialV3.zoomInSymbol') }}</button>
        <button type="button" :aria-label="t('spatialV3.fitView')" @click="fitView()">{{ t('spatialV3.fitView') }}</button>
      </div>
    </div>

    <div class="spatial-v3__below">
      <p v-if="!selectedNode">{{ t('spatialV3.selectHint') }}</p>
      <aside v-else class="spatial-v3__inspector" aria-live="polite" :aria-label="t('spatialV3.details')">
        <div>
          <span class="spatial-v3__type">{{ t('spatialV3.nodeStatus', { role: selectedNode.eyebrow, status: selectedNode.status }) }}</span>
          <h2>{{ selectedNode.label }}</h2>
          <p>{{ selectedNode.detail }}</p>
        </div>
        <button type="button" :aria-label="t('spatialV3.closeAria')" class="spatial-v3__close" @click="selectedId = null">{{ t('spatialV3.close') }}</button>
      </aside>
    </div>
    <p class="spatial-v3__disclaimer">{{ t('spatialV3.disclaimer') }}</p>
  </section>
</template>

<style scoped>
.spatial-v3__focusbar{display:flex;align-items:center;justify-content:space-between;gap:12px;background:var(--k-color-accent-soft);color:var(--k-color-ink);border-radius:11px;padding:10px 14px;margin-bottom:12px;font-size:12px}
.spatial-v3__focusbar button{min-height:36px;padding:6px 11px;border-radius:8px;border:1px solid var(--k-color-border);background:var(--k-color-surface);color:var(--k-color-ink)}
.spatial-v3__node--dimmed{opacity:.17}
.spatial-v3__edges .spatial-v3__edge--dimmed{opacity:.09}

.spatial-v3__discovery{display:grid;gap:10px;margin:0 0 14px}
.spatial-v3__search-label{display:flex;align-items:center;gap:12px;font-size:12px;color:var(--k-color-muted)}
.spatial-v3__search-label input{min-height:40px;min-width:240px;border:1px solid var(--k-color-border);border-radius:9px;padding:7px 12px;background:var(--k-color-surface);color:var(--k-color-ink)}
.spatial-v3__matches,.spatial-v3__group-list{display:flex;flex-wrap:wrap;gap:7px}
.spatial-v3__matches button,.spatial-v3__group-list button{padding:7px 10px;border:1px solid var(--k-color-border);border-radius:9px;background:var(--k-color-surface);color:var(--k-color-ink);font-size:12px;cursor:pointer}
.spatial-v3__group-list button[aria-pressed="true"]{background:var(--k-color-accent);color:var(--k-color-on-accent)}
.spatial-v3__matches p{font-size:12px;color:var(--k-color-muted)}

.spatial-v3{color:var(--k-color-ink);font:15px/1.55 -apple-system,BlinkMacSystemFont,system-ui,sans-serif;max-width:1300px;margin:0 auto;padding:28px 20px 70px}
.spatial-v3 *{box-sizing:border-box}
.spatial-v3__heading{display:flex;align-items:flex-end;justify-content:space-between;gap:18px;margin-bottom:22px}
.spatial-v3__heading h1{font-size:clamp(29px,3vw,38px);letter-spacing:-.05em;margin:0 0 4px;font-weight:640}
.spatial-v3__heading p{color:var(--k-color-muted);margin:0}
.spatial-v3__eyebrow{font-size:11px;letter-spacing:.14em;text-transform:uppercase;font-weight:650;margin-bottom:10px!important}
.spatial-v3__expand{background:var(--k-color-accent);color:var(--k-color-on-accent);border:1px solid var(--k-color-accent);border-radius:11px;padding:10px 16px;white-space:nowrap;font-size:13px;min-height:44px}
.spatial-v3__expand:hover{filter:brightness(1.13)}
.spatial-v3__scroll{position:relative;overflow:hidden;border:1px solid var(--k-color-border);border-radius:19px;height:640px;touch-action:none;cursor:grab;user-select:none}
.spatial-v3__scroll--panning{cursor:grabbing}
.spatial-v3__scroll:focus-visible{outline:3px solid var(--k-color-accent);outline-offset:3px}
.spatial-v3__controls{position:absolute;right:17px;bottom:16px;display:flex;gap:7px;align-items:center;z-index:5;background:var(--k-color-surface);padding:6px;border:1px solid var(--k-color-border);border-radius:12px;box-shadow:0 5px 15px color-mix(in srgb,var(--k-color-accent) 7%,transparent)}
.spatial-v3__controls button{min-width:35px;min-height:35px;border:1px solid var(--k-color-border);border-radius:8px;background:var(--k-color-paper);color:var(--k-color-ink);cursor:pointer}
.spatial-v3__controls span{font-size:11px;min-width:34px;text-align:center;color:var(--k-color-muted)}
.spatial-v3__canvas{position:relative;width:1000px;min-width:1000px;height:640px;transform-origin:top left;background-color:var(--k-color-paper);background-image:radial-gradient(var(--k-color-grid-dot) .75px,transparent 1px);background-size:26px 26px}
.spatial-v3__folio{position:absolute;left:22px;top:17px;color:var(--k-color-muted);font-size:10px;letter-spacing:.17em;font-weight:700;z-index:1}
.spatial-v3__edges{position:absolute;inset:0;height:100%;width:100%;pointer-events:none}
.spatial-v3__edges path{fill:none;stroke:var(--k-color-relation);stroke-width:1.9}
.spatial-v3__edges .spatial-v3__edge--evidence{stroke:var(--k-color-evidence-link)}
.spatial-v3__edges .spatial-v3__edge--proposes{stroke:var(--k-color-accent);stroke-dasharray:7 7;stroke-width:2.3}
.spatial-v3__edges .spatial-v3__edge--questions{stroke:var(--k-color-question-link);stroke-dasharray:3 9}
.spatial-v3__node{position:absolute;transform:translate(-50%,-50%);z-index:2;width:210px;min-height:96px;display:flex;flex-direction:column;align-items:flex-start;justify-content:center;gap:5px;padding:15px 16px;background:var(--k-color-paper);color:var(--k-color-ink);border:1px solid transparent;border-radius:13px;text-align:left;cursor:pointer;transition:border-color .15s,background .15s}
.spatial-v3__node:hover,.spatial-v3__node[aria-pressed="true"]{background:var(--k-color-surface);border-color:var(--k-color-accent)}
.spatial-v3__node:focus-visible,.spatial-v3__expand:focus-visible,.spatial-v3__close:focus-visible{outline:3px solid var(--k-color-accent);outline-offset:3px}
.spatial-v3__type{font-size:10px;letter-spacing:.11em;text-transform:uppercase;font-weight:700;color:var(--k-color-eyebrow)}
.spatial-v3__node strong{font-weight:650;font-size:15px;line-height:1.34}
.spatial-v3__node small{font-size:11px;color:var(--k-color-muted)}
.spatial-v3__node--mission{width:247px;min-height:115px;text-align:center;align-items:center;background:var(--k-color-accent);color:white;border-color:var(--k-color-accent);box-shadow:0 10px 28px color-mix(in srgb, var(--k-color-accent) 14%, transparent)}
.spatial-v3__node--mission .spatial-v3__type,.spatial-v3__node--mission small{color:var(--k-color-on-accent-muted)}
.spatial-v3__node--mission strong{font-size:19px}
.spatial-v3__node--mission:hover,.spatial-v3__node--mission[aria-pressed="true"]{background:var(--k-color-accent);border-color:var(--k-color-ink)}
.spatial-v3__node--source{background:var(--k-color-surface);border-color:var(--k-color-source-border)}
.spatial-v3__node--source .spatial-v3__type{color:var(--k-color-source-ink)}
.spatial-v3__node--proposal{background:var(--k-color-accent-soft);border:2px dashed var(--k-color-accent)}
.spatial-v3__node--question{width:170px;min-height:60px;border-bottom:1px dotted var(--k-color-question);border-radius:0}
.spatial-v3__node--question .spatial-v3__type{color:var(--k-color-question)}
.spatial-v3__legend{position:absolute;bottom:12px;left:17px;display:flex;flex-wrap:wrap;gap:16px;padding:8px 12px;background:var(--k-color-surface);color:var(--k-color-muted);font-size:11px;border-radius:10px}
.spatial-v3__below{min-height:84px;margin-top:13px}
.spatial-v3__below>p{font-size:12px;color:var(--k-color-muted)}
.spatial-v3__inspector{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;border:1px solid var(--k-color-border);background:var(--k-color-surface);border-radius:14px;padding:18px 21px}
.spatial-v3__inspector h2{font-size:18px;margin:5px 0 6px}
.spatial-v3__inspector p{font-size:13px;margin:0;color:var(--k-color-muted)}
.spatial-v3__close{background:transparent;border:1px solid var(--k-color-border);border-radius:8px;padding:8px 11px;min-height:40px}
.spatial-v3__disclaimer{font-size:11px;color:var(--k-color-muted);margin-top:23px}
@media(max-width:680px){.spatial-v3__heading{align-items:flex-start;flex-direction:column}.spatial-v3__canvas{min-width:1000px}.spatial-v3__inspector{flex-direction:column}}
@media(prefers-reduced-motion:reduce){.spatial-v3__node{transition:none}}
</style>
