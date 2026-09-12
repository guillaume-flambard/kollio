<script setup lang="ts">
if (!import.meta.dev) {
  throw createError({ statusCode: 404 })
}

definePageMeta({ layout: false })

const enabled = ref(true)
const intensity = ref(68)
const stroke = ref(1.45)
const glyphs = Object.freeze({ dot: '·', percent: '%', pixels: 'px', arrow: '→' })

const copy = {
  eyebrow: 'Kollio interaction study',
  title: 'Annotation language',
  description: 'Deterministic SVG paths tested across real interface sizes before product integration.',
  replay: 'Replay motion',
  intensity: 'Opacity',
  stroke: 'Stroke',
  loopTitle: 'Sketch loop',
  loopDescription: 'Active navigation and tabs with a complete, controlled gesture.',
  swashTitle: 'Marker swash',
  swashDescription: 'Status and meaningful fragments inside content.',
  arrowTitle: 'Sketch arrow',
  arrowDescription: 'Secondary attention without competing with the primary action.',
  bracketTitle: 'Selection bracket',
  bracketDescription: 'Connects a selected list row to its contextual preview.',
  short: 'Ideas',
  medium: 'For you',
  long: 'Team formed',
  status: 'In validation',
  sentenceBefore: 'Human review helps us',
  sentenceMarked: 'reduce inappropriate model outputs',
  sentenceAfter: 'before they reach users.',
  action: 'Open the idea',
  selectedTitle: 'Human validation registry for LLM outputs',
  selectedCopy: 'Document, review and improve human validation with a shared source of truth.',
  accepted: 'Recommended intensity',
}

const annotationStyle = computed(() => ({
  '--sketch-opacity': String(intensity.value / 100),
  '--sketch-stroke': `${stroke.value}px`,
}))

async function replay() {
  enabled.value = false
  await nextTick()
  requestAnimationFrame(() => {
    enabled.value = true
  })
}
</script>

<template>
  <main class="annotation-lab" :style="annotationStyle">
    <header class="lab-header">
      <div>
        <p v-text="copy.eyebrow" />
        <h1 v-text="copy.title" />
        <span v-text="copy.description" />
      </div>
      <button type="button" @click="replay" v-text="copy.replay" />
    </header>

    <section class="lab-controls" aria-label="Annotation controls">
      <label>
        <span>{{ copy.intensity }} {{ glyphs.dot }} {{ intensity }}{{ glyphs.percent }}</span>
        <input v-model="intensity" type="range" min="35" max="90" step="1">
      </label>
      <label>
        <span>{{ copy.stroke }} {{ glyphs.dot }} {{ stroke }}{{ glyphs.pixels }}</span>
        <input v-model="stroke" type="range" min="0.8" max="2.4" step="0.05">
      </label>
      <span class="recommended" v-text="copy.accepted" />
    </section>

    <div class="lab-grid">
      <section class="lab-card">
        <header><h2 v-text="copy.loopTitle" /><p v-text="copy.loopDescription" /></header>
        <div class="loop-samples">
          <KollioSketchAnnotation :active="enabled" kind="loop"><span v-text="copy.short" /></KollioSketchAnnotation>
          <KollioSketchAnnotation :active="enabled" kind="loop"><span v-text="copy.medium" /></KollioSketchAnnotation>
          <KollioSketchAnnotation :active="enabled" kind="loop"><span v-text="copy.long" /></KollioSketchAnnotation>
        </div>
      </section>

      <section class="lab-card">
        <header><h2 v-text="copy.swashTitle" /><p v-text="copy.swashDescription" /></header>
        <div class="swash-samples">
          <KollioSketchAnnotation :active="enabled" kind="swash"><strong v-text="copy.status" /></KollioSketchAnnotation>
          <p>
            {{ copy.sentenceBefore }}
            <KollioSketchAnnotation :active="enabled" kind="swash"><span v-text="copy.sentenceMarked" /></KollioSketchAnnotation>
            {{ copy.sentenceAfter }}
          </p>
        </div>
      </section>

      <section class="lab-card lab-card-compact">
        <header><h2 v-text="copy.arrowTitle" /><p v-text="copy.arrowDescription" /></header>
        <KollioSketchAnnotation :active="enabled" kind="arrow"><a href="#" @click.prevent v-text="copy.action" /></KollioSketchAnnotation>
      </section>

      <section class="lab-card lab-card-wide">
        <header><h2 v-text="copy.bracketTitle" /><p v-text="copy.bracketDescription" /></header>
        <KollioSketchAnnotation :active="enabled" kind="bracket">
          <article class="selected-sample">
            <div>
              <small v-text="copy.status" />
              <h3 v-text="copy.selectedTitle" />
              <p v-text="copy.selectedCopy" />
            </div>
            <span aria-hidden="true" v-text="glyphs.arrow" />
          </article>
        </KollioSketchAnnotation>
      </section>
    </div>
  </main>
</template>

<style scoped>
.annotation-lab { min-height: 100vh; background: #f7f5f7; padding: clamp(24px, 5vw, 72px); color: #252229; font-family: Geist, system-ui, sans-serif; }
.lab-header { display: flex; max-width: 1280px; align-items: end; justify-content: space-between; gap: 28px; margin: 0 auto 30px; }
.lab-header p { color: #493b57; font-size: .72rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; }
.lab-header h1 { margin-top: 10px; font-size: clamp(2.5rem, 6vw, 5.8rem); font-weight: 620; letter-spacing: -.075em; line-height: .92; }
.lab-header div > span { display: block; max-width: 640px; margin-top: 20px; color: #726d79; font-size: 1rem; line-height: 1.6; }
.lab-header button { min-height: 46px; flex: none; border-radius: 12px; background: #252229; padding: 0 18px; color: #fff; font-size: .82rem; font-weight: 600; }
.lab-controls { display: flex; max-width: 1280px; flex-wrap: wrap; align-items: end; gap: 26px; margin: 0 auto 20px; border: 1px solid #e5e0e7; border-radius: 16px; background: #fff; padding: 18px 22px; }
.lab-controls label { display: grid; min-width: 220px; gap: 9px; color: #726d79; font-size: .72rem; }
.lab-controls input { width: 100%; accent-color: #493b57; }
.recommended { margin-left: auto; color: #493b57; font-size: .72rem; font-weight: 600; }
.lab-grid { display: grid; max-width: 1280px; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 20px; margin: 0 auto; }
.lab-card { min-height: 300px; border: 1px solid #e5e0e7; border-radius: 22px; background: #fff; padding: clamp(24px, 3vw, 42px); }
.lab-card > header { margin-bottom: 42px; }
.lab-card h2 { font-size: 1.25rem; font-weight: 620; letter-spacing: -.03em; }
.lab-card header p { max-width: 470px; margin-top: 8px; color: #817b87; font-size: .83rem; line-height: 1.55; }
.loop-samples { display: flex; flex-wrap: wrap; align-items: center; gap: 18px; font-size: .9rem; font-weight: 600; }
.swash-samples { display: grid; gap: 36px; }
.swash-samples strong { font-size: .82rem; font-weight: 620; }
.swash-samples > p { max-width: 540px; color: #57515f; font-size: 1.05rem; line-height: 1.7; }
.lab-card-compact { min-height: 240px; }
.lab-card-compact a { color: #493b57; font-size: .95rem; font-weight: 620; }
.lab-card-wide { min-height: 240px; }
.selected-sample { display: flex; width: 100%; align-items: center; justify-content: space-between; gap: 24px; }
.selected-sample small { color: #726d79; font-size: .68rem; text-transform: uppercase; }
.selected-sample h3 { margin-top: 7px; font-size: 1.04rem; font-weight: 620; letter-spacing: -.02em; }
.selected-sample p { margin-top: 7px; color: #817b87; font-size: .8rem; line-height: 1.5; }
.selected-sample > span { color: #493b57; font-size: 1.2rem; }
@media (max-width: 760px) {
  .annotation-lab { padding: 30px 14px 60px; }
  .lab-header { align-items: start; flex-direction: column; }
  .lab-grid { grid-template-columns: 1fr; }
  .lab-controls { align-items: stretch; flex-direction: column; }
  .lab-controls label { width: 100%; }
  .recommended { margin-left: 0; }
  .lab-card { min-height: 0; }
}
</style>
