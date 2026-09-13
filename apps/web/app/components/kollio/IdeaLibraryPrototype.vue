<script setup lang="ts">
import type { IdeaSummaryResponse } from '@kollio/api-client'

const props = defineProps<{
  ideas: IdeaSummaryResponse[]
  total: number
}>()

const route = useRoute()
const router = useRouter()
const { locale, t } = useI18n()
const localePath = useLocalePath()
const glyphs = Object.freeze({ command: '⌘ K', dot: '·', slash: '/', left: '←', right: '→', down: '↓', external: '↗' })
const stageCounts = Object.freeze({ seed: 128, iteration: 84, formed: 23 })

const variants = ['A', 'B', 'C'] as const
type Variant = typeof variants[number]

const currentVariant = computed<Variant>(() => {
  const requested = typeof route.query.variant === 'string' ? route.query.variant.toUpperCase() : 'A'
  return variants.includes(requested as Variant) ? requested as Variant : 'A'
})

const copy = computed(() => locale.value === 'fr' ? {
  prototype: 'Prototype de la bibliothèque',
  title: 'Trouver une idée à faire avancer',
  description: 'Explorez les idées ouvertes, comprenez où elles en sont et repérez celles qui ont besoin de vous.',
  search: 'Rechercher une idée, un domaine ou un besoin',
  filters: 'Affiner',
  stage: 'Stade',
  domain: 'Domaine',
  profile: 'Profil recherché',
  realism: 'Réalisme',
  all: 'Tout voir',
  seed: 'Graine',
  iteration: 'En itération',
  formed: 'Équipe formée',
  product: 'Produit',
  ai: 'IA responsable',
  infrastructure: 'Infrastructure',
  design: 'Design',
  engineering: 'Ingénierie',
  data: 'Data',
  growth: 'Growth',
  discover: 'Découvrir',
  active: 'Actives cette semaine',
  available: 'idées à explorer',
  openIdea: 'Ouvrir l’idée',
  needs: 'Recherche',
  signal: 'Signal du moment',
  signalCopy: 'Les idées liées à la fiabilité des produits IA gagnent en activité.',
  saved: 'Suivies',
  recent: 'Récentes',
  forYou: 'Pour vous',
  result: 'résultats',
  selected: 'Aperçu',
  next: 'Idée suivante',
  join: 'Voir comment contribuer',
  queue: 'À découvrir ensuite',
  variantNames: {
    A: 'Flux vivant',
    B: 'Index calme',
    C: 'Découverte guidée',
  },
} : {
  prototype: 'Library prototype',
  title: 'Find an idea to move forward',
  description: 'Explore open ideas, understand their progress and spot the ones that need you.',
  search: 'Search ideas, domains or needs',
  filters: 'Refine',
  stage: 'Stage',
  domain: 'Domain',
  profile: 'Profile sought',
  realism: 'Realism',
  all: 'View all',
  seed: 'Seed',
  iteration: 'In iteration',
  formed: 'Team formed',
  product: 'Product',
  ai: 'Responsible AI',
  infrastructure: 'Infrastructure',
  design: 'Design',
  engineering: 'Engineering',
  data: 'Data',
  growth: 'Growth',
  discover: 'Discover',
  active: 'Active this week',
  available: 'ideas to explore',
  openIdea: 'Open idea',
  needs: 'Looking for',
  signal: 'Current signal',
  signalCopy: 'Ideas related to reliable AI products are gaining activity.',
  saved: 'Following',
  recent: 'Recent',
  forYou: 'For you',
  result: 'results',
  selected: 'Preview',
  next: 'Next idea',
  join: 'See how to contribute',
  queue: 'Discover next',
  variantNames: {
    A: 'Living stream',
    B: 'Quiet index',
    C: 'Guided discovery',
  },
})

const sampleIdeas = computed(() => props.ideas.slice(0, 6))
const selectedIdea = computed(() => sampleIdeas.value[0])

function stageLabel(stage: string) {
  return t(`ideas.stage.${stage}`)
}

function ideaPath(idea: IdeaSummaryResponse) {
  return localePath(`/workspace/ideas/${idea.id}`)
}

async function selectVariant(direction: -1 | 1) {
  const index = variants.indexOf(currentVariant.value)
  const variant = variants[(index + direction + variants.length) % variants.length]
  await router.replace({ query: { ...route.query, variant } })
}

function handleKeydown(event: KeyboardEvent) {
  const target = event.target as HTMLElement | null
  if (target?.matches('input, textarea, [contenteditable="true"]')) return
  if (event.key === 'ArrowLeft') void selectVariant(-1)
  if (event.key === 'ArrowRight') void selectVariant(1)
}

onMounted(() => window.addEventListener('keydown', handleKeydown))
onBeforeUnmount(() => window.removeEventListener('keydown', handleKeydown))
</script>

<template>
  <div class="ideas-prototype">
    <section v-if="currentVariant === 'A'" class="prototype-a">
      <header class="prototype-heading">
        <div>
          <p class="prototype-kicker">{{ copy.prototype }}</p>
          <h1>{{ copy.title }}</h1>
          <p class="prototype-description">{{ copy.description }}</p>
        </div>
        <div class="prototype-stat">
          <strong>{{ total }}</strong>
          <span>{{ copy.available }}</span>
        </div>
      </header>

      <label class="prototype-search">
        <svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7" /><path d="m16 16 5 5" /></svg>
        <input type="search" :placeholder="copy.search">
        <kbd v-text="glyphs.command" />
      </label>

      <div class="prototype-a-layout">
        <main class="prototype-stream">
          <nav class="prototype-tabs" :aria-label="copy.discover">
            <button class="is-active" type="button">{{ copy.forYou }}</button>
            <button type="button">{{ copy.active }}</button>
            <button type="button">{{ copy.recent }}</button>
            <button type="button">{{ copy.saved }}</button>
          </nav>

          <article v-for="(idea, index) in sampleIdeas.slice(0, 4)" :key="idea.id" class="stream-idea">
            <div class="stream-index" v-text="String(index + 1).padStart(2, '0')" />
            <div class="stream-body">
              <div class="stream-meta">
                <KollioFeltMark active variant="status">{{ stageLabel(idea.stage) }}</KollioFeltMark>
                <span>{{ index % 2 ? copy.product : copy.ai }}</span>
              </div>
              <h2>{{ idea.title }}</h2>
              <p>{{ idea.pitch }}</p>
              <div class="stream-foot">
                <span><b>{{ copy.needs }}</b> {{ glyphs.dot }} {{ index % 2 ? copy.design : copy.engineering }}</span>
                <NuxtLink :to="ideaPath(idea)">{{ copy.openIdea }} <span aria-hidden="true" v-text="glyphs.right" /></NuxtLink>
              </div>
            </div>
          </article>
        </main>

        <aside class="prototype-radar">
          <div class="radar-title">
            <span>{{ copy.filters }}</span>
            <button type="button">{{ copy.all }}</button>
          </div>
          <fieldset>
            <legend>{{ copy.stage }}</legend>
            <label><input type="checkbox" checked> {{ copy.seed }}</label>
            <label><input type="checkbox"> {{ copy.iteration }}</label>
            <label><input type="checkbox"> {{ copy.formed }}</label>
          </fieldset>
          <fieldset>
            <legend>{{ copy.domain }}</legend>
            <label><input type="checkbox" checked> {{ copy.ai }}</label>
            <label><input type="checkbox"> {{ copy.product }}</label>
            <label><input type="checkbox"> {{ copy.infrastructure }}</label>
          </fieldset>
          <fieldset>
            <legend>{{ copy.profile }}</legend>
            <label><input type="checkbox"> {{ copy.engineering }}</label>
            <label><input type="checkbox"> {{ copy.data }}</label>
            <label><input type="checkbox"> {{ copy.growth }}</label>
          </fieldset>
          <div class="radar-signal">
            <span>{{ copy.signal }}</span>
            <p>{{ copy.signalCopy }}</p>
          </div>
        </aside>
      </div>
    </section>

    <section v-else-if="currentVariant === 'B'" class="prototype-b">
      <header class="index-head">
        <div>
          <p class="prototype-kicker">{{ copy.prototype }}</p>
          <h1>{{ copy.discover }}</h1>
        </div>
        <label class="index-search">
          <svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7" /><path d="m16 16 5 5" /></svg>
          <input type="search" :placeholder="copy.search">
        </label>
      </header>

      <div class="index-layout">
        <aside class="index-filters">
          <p>{{ copy.filters }}</p>
          <button class="is-active" type="button">{{ copy.all }} <span>{{ total }}</span></button>
          <button type="button">{{ copy.seed }} <span v-text="stageCounts.seed" /></button>
          <button type="button">{{ copy.iteration }} <span v-text="stageCounts.iteration" /></button>
          <button type="button">{{ copy.formed }} <span v-text="stageCounts.formed" /></button>
          <hr>
          <p>{{ copy.domain }}</p>
          <button type="button">{{ copy.ai }}</button>
          <button type="button">{{ copy.product }}</button>
          <button type="button">{{ copy.infrastructure }}</button>
        </aside>

        <main class="index-results">
          <header><span>{{ total }} {{ copy.result }}</span><span>{{ copy.recent }} {{ glyphs.down }}</span></header>
          <NuxtLink v-for="(idea, index) in sampleIdeas" :key="idea.id" :to="ideaPath(idea)" class="index-row">
            <span class="index-number">{{ String(index + 1).padStart(2, '0') }}</span>
            <span class="index-copy"><strong>{{ idea.title }}</strong><small>{{ idea.pitch }}</small></span>
            <span class="index-stage">{{ stageLabel(idea.stage) }}</span>
            <span aria-hidden="true" v-text="glyphs.external" />
          </NuxtLink>
        </main>
      </div>
    </section>

    <section v-else class="prototype-c">
      <header class="focus-head">
        <div>
          <p class="prototype-kicker">{{ copy.prototype }}</p>
          <h1>{{ copy.discover }}</h1>
        </div>
        <label class="focus-search">
          <svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7" /><path d="m16 16 5 5" /></svg>
          <input type="search" :placeholder="copy.search">
        </label>
      </header>

      <div v-if="selectedIdea" class="focus-layout">
        <main class="focus-card">
          <div class="focus-topline">
            <KollioFeltMark active variant="status">{{ stageLabel(selectedIdea.stage) }}</KollioFeltMark>
            <span>{{ String(1).padStart(2, '0') }} {{ glyphs.slash }} {{ Math.min(total, 99) }}</span>
          </div>
          <h2>{{ selectedIdea.title }}</h2>
          <p>{{ selectedIdea.pitch }}</p>
          <div class="focus-needs">
            <span>{{ copy.needs }}</span>
            <strong>{{ copy.engineering }}</strong>
            <strong>{{ copy.product }}</strong>
          </div>
          <div class="focus-actions">
            <NuxtLink :to="ideaPath(selectedIdea)">{{ copy.join }} <span aria-hidden="true" v-text="glyphs.right" /></NuxtLink>
            <button type="button">{{ copy.next }} <span aria-hidden="true" v-text="glyphs.down" /></button>
          </div>
        </main>

        <aside class="focus-queue">
          <header>{{ copy.queue }}</header>
          <NuxtLink v-for="(idea, index) in sampleIdeas.slice(1, 5)" :key="idea.id" :to="ideaPath(idea)">
            <span v-text="String(index + 2).padStart(2, '0')" />
            <strong>{{ idea.title }}</strong>
          </NuxtLink>
          <div class="focus-signal">
            <span>{{ copy.signal }}</span>
            <p>{{ copy.signalCopy }}</p>
          </div>
        </aside>
      </div>
    </section>

    <div class="prototype-switcher" aria-label="Prototype variants">
      <button type="button" aria-label="Previous variant" @click="selectVariant(-1)" v-text="glyphs.left" />
      <span>{{ currentVariant }} {{ glyphs.dot }} {{ copy.variantNames[currentVariant] }}</span>
      <button type="button" aria-label="Next variant" @click="selectVariant(1)" v-text="glyphs.right" />
    </div>
  </div>
</template>

<style scoped>
.ideas-prototype { min-height: 100vh; color: var(--kollio-heading); }
.prototype-a, .prototype-b, .prototype-c { width: 100%; padding: clamp(24px, 3vw, 52px); }
.prototype-heading { display: flex; align-items: end; justify-content: space-between; gap: 32px; padding: 10px 0 36px; }
.prototype-kicker { color: var(--kollio-active-ink); font-size: .75rem; font-weight: 650; letter-spacing: .08em; text-transform: uppercase; }
.prototype-heading h1, .index-head h1, .focus-head h1 { max-width: 780px; margin-top: 12px; font-size: clamp(2.2rem, 4vw, 4.6rem); font-weight: 620; letter-spacing: -.065em; line-height: .98; text-wrap: balance; }
.prototype-description { max-width: 690px; margin-top: 18px; color: var(--ui-text-muted); font-size: clamp(1rem, 1.2vw, 1.15rem); line-height: 1.65; }
.prototype-stat { display: flex; flex: none; align-items: baseline; gap: 9px; color: var(--ui-text-muted); font-size: .8rem; }
.prototype-stat strong { color: var(--kollio-heading); font-size: 1.35rem; }
.prototype-search, .index-search, .focus-search { display: flex; min-height: 62px; align-items: center; gap: 14px; border: 1px solid var(--ui-border); border-radius: 20px; background: var(--ui-bg-elevated); padding: 0 20px; box-shadow: 0 18px 50px color-mix(in srgb, var(--kollio-active-ink) 7%, transparent); }
.prototype-search svg, .index-search svg, .focus-search svg { width: 21px; fill: none; stroke: currentColor; stroke-width: 1.7; color: var(--ui-text-muted); }
.prototype-search input, .index-search input, .focus-search input { min-width: 0; flex: 1; outline: none; background: transparent; color: var(--kollio-heading); font-size: .96rem; }
.prototype-search kbd { border: 1px solid var(--ui-border); border-radius: 7px; padding: 4px 7px; color: var(--ui-text-muted); font-size: .7rem; }
.prototype-a-layout { display: grid; grid-template-columns: minmax(0, 1fr) minmax(260px, 320px); gap: 22px; margin-top: 22px; align-items: start; }
.prototype-stream, .prototype-radar, .index-layout, .focus-card, .focus-queue { border: 1px solid var(--ui-border); border-radius: 24px; background: var(--ui-bg-elevated); }
.prototype-tabs { display: flex; gap: 28px; overflow-x: auto; border-bottom: 1px solid var(--ui-border); padding: 0 28px; }
.prototype-tabs button { position: relative; min-height: 64px; flex: none; color: var(--ui-text-muted); font-size: .86rem; }
.prototype-tabs button.is-active { color: var(--kollio-heading); font-weight: 600; }
.prototype-tabs button.is-active::after { position: absolute; right: -6px; bottom: 9px; left: -6px; height: 9px; border-radius: 60% 35% 55% 40%; background: color-mix(in srgb, var(--kollio-wash) 83%, transparent); content: ''; filter: blur(.5px); transform: rotate(-1.5deg); }
.stream-idea { display: grid; grid-template-columns: 42px minmax(0, 1fr); gap: 18px; border-bottom: 1px solid var(--ui-border); padding: 29px 30px 27px; }
.stream-idea:last-child { border-bottom: 0; }
.stream-index { padding-top: 3px; color: var(--ui-text-muted); font-size: .72rem; font-variant-numeric: tabular-nums; }
.stream-meta, .stream-foot { display: flex; align-items: center; justify-content: space-between; gap: 16px; color: var(--ui-text-muted); font-size: .73rem; }
.stream-meta > span:last-child { white-space: nowrap; }
.stream-body h2 { max-width: 810px; margin-top: 16px; font-size: clamp(1.2rem, 1.7vw, 1.58rem); font-weight: 610; letter-spacing: -.032em; line-height: 1.22; }
.stream-body > p { max-width: 850px; margin-top: 10px; color: var(--ui-text-muted); font-size: .88rem; line-height: 1.58; }
.stream-foot { margin-top: 21px; }
.stream-foot b { color: var(--kollio-heading); font-weight: 560; }
.stream-foot a { position: relative; z-index: 1; color: var(--kollio-active-ink); font-weight: 600; }
.stream-foot a::after { position: absolute; z-index: -1; right: -3px; bottom: -3px; left: -3px; height: 7px; border-radius: 50%; background: color-mix(in srgb, var(--kollio-wash) 75%, transparent); content: ''; transform: rotate(-1deg); }
.prototype-radar { position: sticky; top: 22px; overflow: hidden; }
.radar-title { display: flex; min-height: 68px; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--ui-border); padding: 0 22px; font-size: .9rem; font-weight: 600; }
.radar-title button { color: var(--ui-text-muted); font-size: .72rem; font-weight: 500; }
.prototype-radar fieldset { display: grid; gap: 12px; border-bottom: 1px solid var(--ui-border); padding: 21px 22px; }
.prototype-radar legend { margin-bottom: 13px; color: var(--ui-text-muted); font-size: .7rem; font-weight: 650; letter-spacing: .06em; text-transform: uppercase; }
.prototype-radar label { display: flex; align-items: center; gap: 10px; font-size: .82rem; }
.prototype-radar input { width: 15px; height: 15px; accent-color: var(--kollio-active-ink); }
.radar-signal { margin: 16px; border-radius: 17px; background: color-mix(in srgb, var(--kollio-wash) 38%, var(--ui-bg-elevated)); padding: 18px; }
.radar-signal span, .focus-signal span { color: var(--kollio-active-ink); font-size: .69rem; font-weight: 650; letter-spacing: .06em; text-transform: uppercase; }
.radar-signal p, .focus-signal p { margin-top: 8px; color: var(--ui-text-muted); font-size: .8rem; line-height: 1.5; }
.index-head, .focus-head { display: grid; grid-template-columns: minmax(280px, .8fr) minmax(320px, 1.2fr); align-items: end; gap: 48px; padding: 8px 0 38px; }
.index-head h1, .focus-head h1 { font-size: clamp(2.5rem, 4vw, 4.2rem); }
.index-search, .focus-search { min-height: 56px; box-shadow: none; }
.index-layout { display: grid; grid-template-columns: 220px minmax(0, 1fr); overflow: hidden; }
.index-filters { border-right: 1px solid var(--ui-border); padding: 28px 18px; }
.index-filters > p { margin: 0 10px 13px; color: var(--ui-text-muted); font-size: .68rem; font-weight: 650; letter-spacing: .07em; text-transform: uppercase; }
.index-filters button { display: flex; width: 100%; min-height: 42px; align-items: center; justify-content: space-between; border-radius: 12px; padding: 0 10px; color: var(--ui-text-muted); font-size: .82rem; text-align: left; }
.index-filters button.is-active { background: color-mix(in srgb, var(--kollio-wash) 42%, transparent); color: var(--kollio-heading); font-weight: 600; }
.index-filters button span { font-size: .7rem; font-weight: 500; }
.index-filters hr { margin: 22px 10px; border-color: var(--ui-border); }
.index-results > header { display: flex; min-height: 56px; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--ui-border); padding: 0 24px; color: var(--ui-text-muted); font-size: .72rem; }
.index-row { display: grid; min-height: 112px; grid-template-columns: 34px minmax(0, 1fr) 130px 20px; align-items: center; gap: 18px; border-bottom: 1px solid var(--ui-border); padding: 20px 25px; transition: background 160ms ease; }
.index-row:last-child { border-bottom: 0; }
.index-row:hover { background: color-mix(in srgb, var(--kollio-wash) 17%, transparent); }
.index-number, .index-stage { color: var(--ui-text-muted); font-size: .7rem; }
.index-copy { min-width: 0; }
.index-copy strong { display: block; font-size: 1rem; font-weight: 590; letter-spacing: -.018em; }
.index-copy small { display: block; overflow: hidden; margin-top: 7px; color: var(--ui-text-muted); font-size: .78rem; line-height: 1.45; text-overflow: ellipsis; white-space: nowrap; }
.focus-layout { display: grid; grid-template-columns: minmax(0, 1.55fr) minmax(290px, .65fr); gap: 22px; }
.focus-card { display: flex; min-height: 650px; flex-direction: column; justify-content: space-between; padding: clamp(34px, 5vw, 72px); }
.focus-topline { display: flex; align-items: center; justify-content: space-between; color: var(--ui-text-muted); font-size: .75rem; }
.focus-card h2 { max-width: 890px; margin-top: auto; padding-top: 70px; font-size: clamp(2.1rem, 4.2vw, 4.8rem); font-weight: 610; letter-spacing: -.068em; line-height: .98; text-wrap: balance; }
.focus-card > p { max-width: 820px; margin-top: 24px; color: var(--ui-text-muted); font-size: clamp(1rem, 1.35vw, 1.22rem); line-height: 1.62; }
.focus-needs { display: flex; flex-wrap: wrap; align-items: center; gap: 11px; margin-top: 35px; color: var(--ui-text-muted); font-size: .75rem; }
.focus-needs strong { border-bottom: 5px solid color-mix(in srgb, var(--kollio-wash) 72%, transparent); color: var(--kollio-heading); font-size: .78rem; font-weight: 580; }
.focus-actions { display: flex; align-items: center; justify-content: space-between; gap: 18px; margin-top: 54px; }
.focus-actions a { min-height: 52px; border-radius: 15px; background: var(--kollio-heading); padding: 16px 20px; color: white; font-size: .84rem; font-weight: 600; }
.focus-actions button { color: var(--ui-text-muted); font-size: .82rem; }
.focus-queue { overflow: hidden; }
.focus-queue > header { min-height: 65px; border-bottom: 1px solid var(--ui-border); padding: 23px; font-size: .86rem; font-weight: 600; }
.focus-queue > a { display: grid; min-height: 105px; grid-template-columns: 25px 1fr; gap: 12px; border-bottom: 1px solid var(--ui-border); padding: 21px 22px; }
.focus-queue > a span { color: var(--ui-text-muted); font-size: .66rem; }
.focus-queue > a strong { font-size: .84rem; font-weight: 560; line-height: 1.4; }
.focus-signal { margin: 18px; border-radius: 17px; background: color-mix(in srgb, var(--kollio-wash) 38%, var(--ui-bg-elevated)); padding: 19px; }
.prototype-switcher { position: fixed; z-index: 60; bottom: 20px; left: 50%; display: flex; min-height: 48px; align-items: center; gap: 18px; border: 1px solid color-mix(in srgb, white 15%, transparent); border-radius: 16px; background: var(--kollio-heading); padding: 5px 7px; color: white; box-shadow: 0 16px 40px rgb(37 34 41 / 24%); transform: translateX(-50%); }
.prototype-switcher button { display: grid; width: 38px; height: 38px; place-items: center; border-radius: 11px; font-size: 1rem; }
.prototype-switcher button:hover { background: rgb(255 255 255 / 10%); }
.prototype-switcher span { min-width: 150px; font-size: .76rem; font-weight: 600; text-align: center; }
@media (max-width: 1020px) {
  .prototype-a-layout, .focus-layout { grid-template-columns: 1fr; }
  .prototype-radar { position: static; display: grid; grid-template-columns: repeat(3, 1fr); }
  .radar-title, .radar-signal { grid-column: 1 / -1; }
  .prototype-radar fieldset { border-right: 1px solid var(--ui-border); }
  .focus-card { min-height: 580px; }
}
@media (max-width: 740px) {
  .prototype-a, .prototype-b, .prototype-c { padding: 24px 14px 90px; }
  .prototype-heading, .index-head, .focus-head { display: flex; align-items: stretch; flex-direction: column; gap: 24px; }
  .prototype-stat { display: none; }
  .prototype-search kbd { display: none; }
  .prototype-a-layout { margin-top: 14px; }
  .stream-idea { grid-template-columns: 1fr; padding: 24px 20px; }
  .stream-index { display: none; }
  .stream-foot { align-items: flex-start; flex-direction: column; }
  .prototype-radar { display: block; }
  .prototype-radar fieldset { border-right: 0; }
  .index-layout { grid-template-columns: 1fr; }
  .index-filters { display: flex; overflow-x: auto; border-right: 0; border-bottom: 1px solid var(--ui-border); padding: 13px; }
  .index-filters > p, .index-filters hr { display: none; }
  .index-filters button { width: auto; min-width: max-content; }
  .index-row { min-height: 128px; grid-template-columns: 24px minmax(0, 1fr) 18px; gap: 12px; padding: 19px 16px; }
  .index-stage { display: none; }
  .index-copy small { white-space: normal; }
  .focus-card { min-height: 620px; padding: 30px 23px; }
  .focus-card h2 { padding-top: 50px; }
  .prototype-switcher { bottom: 12px; }
}
</style>
