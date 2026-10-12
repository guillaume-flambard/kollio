<script setup lang="ts">
import type { SpatialV3Edge, SpatialV3Fixture, SpatialV3Node } from '~/utils/spatialV3.generated'

const props = defineProps<{ fixture: SpatialV3Fixture }>()
const { t } = useI18n()
const depth = ref<1 | 2>(1)
const selectedId = ref<string | null>(null)

const visibleNodes = computed(() => props.fixture.nodes.filter(node => node.depth <= depth.value))
const visibleEdges = computed(() => props.fixture.edges.filter(edge => edge.depth <= depth.value))
const selectedNode = computed(() => visibleNodes.value.find(node => node.id === selectedId.value))
const nodeById = computed(() => new Map(props.fixture.nodes.map(node => [node.id, node])))
const hiddenCount = computed(() => props.fixture.nodes.filter(node => node.depth > depth.value).length)

function edgePath(edge: SpatialV3Edge): string {
  const from = nodeById.value.get(edge.source)
  const to = nodeById.value.get(edge.target)
  if (!from || !to)
    return ''
  const x1 = from.x * 1000
  const y1 = from.y * 640
  const x2 = to.x * 1000
  const y2 = to.y * 640
  const bend = Math.max(45, Math.min(120, Math.abs(y2 - y1) * 0.35))
  const direction = y2 < y1 ? -1 : 1
  return `M ${x1} ${y1} C ${x1} ${y1 + direction * bend}, ${x2} ${y2 - direction * bend}, ${x2} ${y2}`
}
function changeDepth(next: 1 | 2) {
  depth.value = next
  if (selectedId.value && !visibleNodes.value.some(node => node.id === selectedId.value))
    selectedId.value = null
}
function selectNode(node: SpatialV3Node) {
  selectedId.value = selectedId.value === node.id ? null : node.id
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

    <div class="spatial-v3__scroll" role="region" :aria-label="t('spatialV3.accessibleCanvas')" tabindex="0">
      <div class="spatial-v3__canvas">
        <p class="spatial-v3__folio">{{ t('spatialV3.folio') }}</p>
        <svg aria-hidden="true" class="spatial-v3__edges" viewBox="0 0 1000 640" preserveAspectRatio="none">
          <path v-for="edge in visibleEdges" :key="edge.id" :class="`spatial-v3__edge--${edge.type}`" :d="edgePath(edge)" />
        </svg>
        <button
          v-for="node in visibleNodes"
          :key="node.id"
          type="button"
          class="spatial-v3__node"
          :class="[`spatial-v3__node--${node.kind}`, `spatial-v3__node--${node.status}`]"
          :style="{ left: `${node.x * 100}%`, top: `${node.y * 100}%` }"
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
.spatial-v3{color:var(--k-color-ink);font:15px/1.55 -apple-system,BlinkMacSystemFont,system-ui,sans-serif;max-width:1300px;margin:0 auto;padding:28px 20px 70px}
.spatial-v3 *{box-sizing:border-box}
.spatial-v3__heading{display:flex;align-items:flex-end;justify-content:space-between;gap:18px;margin-bottom:22px}
.spatial-v3__heading h1{font-size:clamp(29px,3vw,38px);letter-spacing:-.05em;margin:0 0 4px;font-weight:640}
.spatial-v3__heading p{color:var(--k-color-muted);margin:0}
.spatial-v3__eyebrow{font-size:11px;letter-spacing:.14em;text-transform:uppercase;font-weight:650;margin-bottom:10px!important}
.spatial-v3__expand{background:var(--k-color-accent);color:var(--k-color-on-accent);border:1px solid var(--k-color-accent);border-radius:11px;padding:10px 16px;white-space:nowrap;font-size:13px;min-height:44px}
.spatial-v3__expand:hover{filter:brightness(1.13)}
.spatial-v3__scroll{overflow-x:auto;border:1px solid var(--k-color-border);border-radius:19px}
.spatial-v3__canvas{position:relative;min-width:780px;height:640px;background-color:var(--k-color-paper);background-image:radial-gradient(var(--k-color-grid-dot) .75px,transparent 1px);background-size:26px 26px}
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
@media(max-width:680px){.spatial-v3__heading{align-items:flex-start;flex-direction:column}.spatial-v3__canvas{min-width:780px}.spatial-v3__inspector{flex-direction:column}}
@media(prefers-reduced-motion:reduce){.spatial-v3__node{transition:none}}
</style>
