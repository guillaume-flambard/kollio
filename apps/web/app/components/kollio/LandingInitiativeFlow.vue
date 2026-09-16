<script setup lang="ts">
const { t } = useI18n()
</script>

<template>
  <section id="product" class="initiative-preview" :aria-label="t('landing.preview.label')">
    <header class="initiative-preview__header">
      <div class="initiative-preview__title">
        <span class="initiative-preview__mark" aria-hidden="true">
          <svg viewBox="0 0 28 28"><path d="M13 24c0-8 1-14 5-20" /><path d="M15 12c-5-1-8 2-8 7 5 1 8-2 8-7ZM17 8c1-5 4-7 8-6 0 5-3 7-8 6Z" /></svg>
        </span>
        <strong>{{ t('landing.preview.workspace') }}</strong>
        <span>{{ t('landing.preview.count') }}</span>
      </div>
      <div class="initiative-preview__search" aria-hidden="true">
        <KollioLandingGlyph name="search" />
        {{ t('landing.preview.search') }}
      </div>
      <svg class="initiative-preview__filters" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h10M18 7h2M4 17h2M10 17h10M14 4v6M7 14v6" /></svg>
    </header>

    <div class="initiative-flow">
      <KollioRelationshipConnector path="M357 106 C430 106 444 123 539 123" :start-x="357" :start-y="106" :end-x="539" :end-y="123" />
      <KollioRelationshipConnector path="M357 186 C426 186 448 244 539 244" :start-x="357" :start-y="186" :end-x="539" :end-y="244" muted :show-end="false" />
      <KollioRelationshipConnector path="M357 266 C425 266 455 244 539 244" :start-x="357" :start-y="266" :end-x="539" :end-y="244" muted />
      <KollioRelationshipConnector path="M900 123 C958 123 968 139 1023 139" :start-x="900" :start-y="123" :end-x="1023" :end-y="139" />
      <KollioRelationshipConnector path="M900 244 C970 244 957 139 1023 139" :start-x="900" :start-y="244" :end-x="1023" :end-y="139" muted :show-end="false" />

      <section class="initiative-stage" aria-labelledby="landing-signal-title">
        <header class="initiative-stage__header">
          <span class="initiative-stage__dot initiative-stage__dot--signal" />
          <div><h2 id="landing-signal-title">{{ t('landing.preview.signal.title') }}</h2><p>{{ t('landing.preview.signal.description') }}</p></div>
        </header>
        <div class="initiative-stack">
          <article class="initiative-card initiative-card--selected"><KollioLandingFlowIllustration stage="signal" /><strong><KollioFeltMark>{{ t('landing.preview.signal.primary') }}</KollioFeltMark></strong><span class="inline-arrow" aria-hidden="true" /></article>
          <article class="initiative-card initiative-card--quiet"><KollioLandingFlowIllustration stage="evidence" /><span>{{ t('landing.preview.signal.secondary') }}</span></article>
          <article class="initiative-card initiative-card--quiet"><KollioLandingFlowIllustration stage="question" /><span>{{ t('landing.preview.signal.tertiary') }}</span></article>
        </div>
      </section>

      <section class="initiative-stage" aria-labelledby="landing-validation-title">
        <header class="initiative-stage__header">
          <span class="initiative-stage__dot initiative-stage__dot--validation" />
          <div><h2 id="landing-validation-title">{{ t('landing.preview.validation.title') }}</h2><p>{{ t('landing.preview.validation.description') }}</p></div>
        </header>
        <div class="initiative-stack">
          <article class="validation-card">
            <KollioLandingFlowIllustration class="validation-card__thumbnail" stage="evidence" format="thumbnail" />
            <div class="validation-card__label"><KollioLandingFlowIllustration stage="evidence" /><strong>{{ t('landing.preview.validation.evidence') }}</strong></div>
            <p>{{ t('landing.preview.validation.evidenceCopy') }}</p><small>{{ t('landing.preview.validation.source') }}</small>
          </article>
          <article class="validation-card">
            <div class="validation-card__label"><KollioLandingFlowIllustration stage="question" /><strong>{{ t('landing.preview.validation.question') }}</strong></div>
            <p>{{ t('landing.preview.validation.questionCopy') }}</p>
            <div class="validation-card__owner"><span class="demo-avatar demo-avatar--rose" aria-hidden="true" /><span><strong>{{ t('landing.preview.validation.owner') }}</strong><small>{{ t('landing.preview.validation.role') }}</small></span></div>
          </article>
        </div>
      </section>

      <section class="initiative-stage" aria-labelledby="landing-decision-title">
        <header class="initiative-stage__header">
          <span class="initiative-stage__dot initiative-stage__dot--decision" />
          <div><h2 id="landing-decision-title">{{ t('landing.preview.decision.title') }}</h2><p>{{ t('landing.preview.decision.description') }}</p></div>
        </header>
        <article class="decision-card">
          <div class="decision-card__label"><KollioLandingFlowIllustration stage="decision" /><strong>{{ t('landing.preview.decision.documented') }}</strong></div>
          <p>{{ t('landing.preview.decision.copy') }}</p>
          <a href="#method">{{ t('landing.preview.decision.open') }} <span class="inline-arrow" aria-hidden="true" /></a>
        </article>
        <div class="decision-team"><strong>{{ t('landing.preview.decision.team') }}</strong><div class="decision-team__people" :aria-label="t('landing.preview.decision.team')"><span class="demo-avatar demo-avatar--rose" /><span class="demo-avatar demo-avatar--sage" /><span class="demo-avatar demo-avatar--ochre" /><span class="demo-avatar demo-avatar--coral" /><span class="decision-team__more">{{ t('landing.preview.decision.morePeople') }}</span></div></div>
        <p class="decision-note">{{ t('landing.preview.decision.note') }}</p>
      </section>
    </div>
  </section>
</template>

<style scoped>
.initiative-preview { overflow: hidden; border-radius: var(--kollio-radius-xl); background: color-mix(in srgb, var(--ui-bg-elevated) 96%, transparent); box-shadow: 0 28px 80px color-mix(in srgb, var(--kollio-active-ink) 9%, transparent); }
.initiative-preview__header { display: grid; min-height: 68px; grid-template-columns: 1fr minmax(220px, 280px) 24px; align-items: center; gap: 18px; border-bottom: 1px solid var(--ui-border); padding: 12px 22px; }
.initiative-preview__title { display: flex; align-items: center; gap: 9px; color: var(--kollio-heading); font-size: .9rem; }
.initiative-preview__title > span:last-child { color: var(--ui-text-muted); }
.initiative-preview__mark { display: grid; width: 34px; height: 34px; place-items: center; border-radius: 10px; background: color-mix(in srgb, var(--kollio-verified) 14%, white); color: var(--kollio-verified); }
.initiative-preview__mark svg { width: 27px; height: 27px; overflow: visible; }.initiative-preview__mark path:first-child { fill: none; stroke: currentColor; stroke-linecap: round; stroke-width: 1.5; }.initiative-preview__mark path:not(:first-child) { fill: currentColor; opacity: .85; }
.initiative-preview__search { display: flex; width: 100%; align-items: center; gap: 9px; border: 1px solid var(--ui-border); border-radius: var(--kollio-radius-sm); padding: 10px 13px; color: var(--ui-text-muted); font-size: var(--kollio-text-caption); }
.initiative-preview__search svg { width: 16px; height: 16px; }
.initiative-preview__filters { width: 20px; height: 20px; fill: none; stroke: var(--kollio-active-ink); stroke-linecap: round; stroke-width: 1.5; }
.initiative-flow { position: relative; display: grid; height: 348px; min-height: 0; grid-template-columns: 1.08fr 1.02fr .9fr; padding: 0 18px 16px; }
.initiative-stage { position: relative; z-index: 1; min-width: 0; padding: 19px 17px 8px; }
.initiative-stage:first-of-type { padding-left: 13px; }
.initiative-stage:nth-of-type(2) { padding-left: 24px; }
.initiative-stage:nth-of-type(3) { padding-left: 35px; }
.initiative-stage + .initiative-stage { border-left: 1px solid var(--ui-border); }
.initiative-stage__header { display: flex; min-height: 56px; align-items: flex-start; gap: 11px; }
.initiative-stage__header h2 { color: var(--kollio-heading); font-size: var(--kollio-text-lead); font-weight: var(--kollio-weight-display); }
.initiative-stage__header p { margin-top: 3px; color: var(--ui-text-muted); font-size: var(--kollio-text-small); }
.initiative-stage__dot { width: 17px; height: 17px; flex: none; margin-top: 2px; border-radius: 50%; background: var(--kollio-wash); box-shadow: 0 0 0 5px color-mix(in srgb, var(--kollio-wash) 18%, transparent); }
.initiative-stage__dot--validation { background: var(--kollio-verified); }
.initiative-stage__dot--decision { background: var(--kollio-question); }
.initiative-stack { display: grid; gap: 10px; }
.initiative-stage:first-of-type .initiative-stack { max-width: 326px; gap: 19px; }
.initiative-stage:nth-of-type(2) .initiative-stack { max-width: 357px; gap: 7px; margin-top: -5px; }
.initiative-stage:nth-of-type(3) .decision-card { max-width: 370px; }
.initiative-card, .validation-card, .decision-card { border: 1px solid color-mix(in srgb, var(--ui-border) 78%, transparent); border-radius: var(--kollio-radius-md); background: color-mix(in srgb, var(--ui-bg-elevated) 92%, var(--ui-bg-muted)); }
.initiative-card { display: grid; min-height: 61px; grid-template-columns: 30px minmax(0, 1fr) auto; align-items: center; gap: 11px; padding: 10px 14px; color: var(--kollio-heading); font-size: var(--kollio-text-small); line-height: 1.25; }
.initiative-card--selected { position: relative; border-color: color-mix(in srgb, var(--kollio-active-ink) 42%, var(--ui-border)); background: var(--ui-bg-elevated); }
.initiative-card--selected strong { position: relative; z-index: 1; }
.initiative-card--quiet { color: var(--ui-text-muted); }
.inline-arrow::before { content: '→'; }
.validation-card, .decision-card { min-height: 108px; padding: 13px 16px; }
.validation-card:first-child { height: 105px; min-height: 105px; padding-block: 10px; }
.validation-card { position: relative; }
.validation-card:first-child { padding-right: 88px; }
.validation-card__thumbnail { position: absolute; top: 16px; right: 14px; }
.validation-card__label, .decision-card__label { display: flex; align-items: center; gap: 8px; color: var(--kollio-active-ink); font-size: .875rem; }
.validation-card__label > svg, .decision-card__label svg { width: 18px; height: 18px; }
.validation-card p, .decision-card p { margin-top: 7px; color: var(--ui-text); font-size: var(--kollio-text-small); line-height: 1.38; }
.validation-card small { display: block; margin-top: 7px; color: var(--ui-text-muted); font-size: var(--kollio-text-micro); }
.validation-card__owner { display: flex; align-items: center; gap: 8px; margin-top: 8px; }
.validation-card__owner span:last-child { display: grid; color: var(--kollio-heading); font-size: var(--kollio-text-micro); }
.validation-card__owner small { margin: 1px 0 0; }
.decision-check { display: grid; width: 25px; height: 25px; place-items: center; color: var(--kollio-question); }.decision-check svg { width: 25px; height: 25px; }
.decision-card a { display: inline-flex; min-height: 44px; align-items: center; gap: var(--kollio-space-sm); margin-top: var(--kollio-space-sm); color: var(--kollio-active-ink); font-size: var(--kollio-text-micro); font-weight: var(--kollio-weight-strong); }
.decision-team { margin-top: 20px; font-size: .72rem; }
.decision-team__people { display: flex; align-items: center; margin-top: 9px; padding-left: 7px; }
.demo-avatar { display: inline-block; width: 30px; height: 30px; margin-left: -7px; border: 2px solid white; border-radius: 50%; background-color: var(--kollio-wash); background-image: url('/avatars/collaborator-sprite.webp'); background-size: 300% 200%; }
.demo-avatar--rose { background-position: 50% 0; }.demo-avatar--sage { background-position: 100% 100%; }.demo-avatar--ochre { background-position: 100% 0; }.demo-avatar--coral { background-position: 50% 100%; }
.decision-team__more { display: grid; width: 30px; height: 30px; place-items: center; margin-left: -7px; border: 2px solid white; border-radius: 50%; background: var(--ui-bg-muted); color: var(--ui-text-muted); font-size: var(--kollio-text-micro); }
.decision-note { position: relative; margin: -26px 0 0 132px; color: var(--kollio-active-ink); font-family: var(--font-annotation); font-size: 1rem; font-weight: var(--kollio-weight-strong); line-height: 1.1; transform: rotate(-3deg); }
@media (max-width: 900px) { .initiative-flow { height: auto; min-height: 0; grid-template-columns: 1fr; padding: 0 16px 16px; }.initiative-flow :deep(.relationship-connector) { display: none; }.initiative-stage, .initiative-stage:first-of-type, .initiative-stage:nth-of-type(2), .initiative-stage:nth-of-type(3) { padding-inline: 8px; }.initiative-stage + .initiative-stage { border-top: 1px solid var(--ui-border); border-left: 0; }.initiative-stack, .initiative-stage:first-of-type .initiative-stack, .initiative-stage:nth-of-type(2) .initiative-stack { max-width: none; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; margin-top: 0; }.initiative-stage:nth-of-type(3) .decision-card { max-width: none; }.initiative-card--quiet:last-child { display: none; }.decision-note { margin-left: 150px; } }
@media (max-width: 560px) { .initiative-preview { border-radius: var(--kollio-radius-lg); }.initiative-preview__header { grid-template-columns: 1fr; padding-inline: 16px; }.initiative-preview__search, .initiative-preview__filters { display: none; }.initiative-stack, .initiative-stage .initiative-stack, .initiative-stage:first-of-type .initiative-stack, .initiative-stage:nth-of-type(2) .initiative-stack { grid-template-columns: 1fr; }.initiative-card--quiet { display: none; }.decision-note { margin: 13px 0 0; transform: none; }.validation-card:first-child { height: auto; min-height: 108px; padding-right: 76px; }.validation-card__thumbnail { width: 54px; height: 46px; } }
</style>
