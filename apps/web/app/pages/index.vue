<script setup lang="ts">
const { t, locale } = useI18n()
const switchLocalePath = useSwitchLocalePath()
const localePath = useLocalePath()
const config = useRuntimeConfig()
const { data: session } = await useFetch('/api/session')
const authEnabled = config.public.authEnabled === true || String(config.public.authEnabled) === 'true'
const workspaceTarget = computed(() => session.value?.signedIn ? localePath('/workspace') : authEnabled ? '/sign-in' : localePath('/workspace'))
const outcomeItems = [
  { key: 'context', asset: 'shared-context' },
  { key: 'decisions', asset: 'explainable-decisions' },
  { key: 'ai', asset: 'controlled-ai' },
] as const

useSeoMeta({ title: () => t('landing.meta.title'), description: () => t('landing.meta.description') })
</script>

<template>
  <div class="landing-page">
    <header class="landing-nav">
      <NuxtLink :to="$localePath('/')" :aria-label="t('brand')"><KollioBrand /></NuxtLink>
      <nav class="landing-nav__links" :aria-label="t('navigation.label')">
        <a href="#product">{{ t('landing.navigation.platform') }}</a><a href="#teams">{{ t('landing.navigation.teams') }}</a><a href="#method">{{ t('landing.navigation.method') }}</a><a href="#trust">{{ t('landing.navigation.security') }}</a>
      </nav>
      <div class="landing-nav__actions">
        <NuxtLink :to="switchLocalePath(locale === 'fr' ? 'en' : 'fr')" class="landing-nav__language" :hreflang="locale === 'fr' ? 'en' : 'fr'">{{ t('language.switch') }}</NuxtLink>
        <a v-if="authEnabled" :href="session?.signedIn ? '/sign-out' : '/sign-in'" class="landing-nav__signin">{{ session?.signedIn ? t('auth.signOut') : t('auth.signIn') }}</a>
        <KollioPrimaryAction
          :to="authEnabled && !session?.signedIn ? undefined : workspaceTarget"
          :href="authEnabled && !session?.signedIn ? '/sign-in' : undefined"
          :label="session?.signedIn ? t('landing.navigation.workspace') : t('landing.navigation.demo')"
        />
      </div>
    </header>

    <main>
      <section class="landing-first-frame">
        <KollioLandingFrameDecoration />
        <section class="landing-hero">
          <div class="landing-hero__copy landing-reveal">
            <p class="landing-hero__eyebrow">{{ t('landing.hero.eyebrow') }}</p>
            <h1>{{ t('landing.hero.titleLead') }}<br><KollioFeltMark size="hero">{{ t('landing.hero.titleEmphasis') }}</KollioFeltMark></h1>
            <p class="landing-hero__description">{{ t('landing.hero.description') }}</p>
            <div class="landing-hero__actions">
              <KollioPrimaryAction
                :to="authEnabled && !session?.signedIn ? undefined : workspaceTarget"
                :href="authEnabled && !session?.signedIn ? '/sign-in' : undefined"
                :label="t('landing.hero.primaryAction')"
              />
              <a class="landing-secondary-action" href="#method">{{ t('landing.hero.secondaryAction') }}</a>
            </div>
          </div>
          <p class="landing-note landing-note--left" aria-hidden="true">{{ t('landing.hero.leftNote') }}</p>
          <p class="landing-note landing-note--right" aria-hidden="true">{{ t('landing.hero.rightNote') }}</p>
          <KollioHandDrawnArrow class="landing-arrow landing-arrow--left" />
          <KollioHandDrawnArrow class="landing-arrow landing-arrow--right" direction="down-left" />
        </section>

        <div class="landing-preview-wrap landing-reveal landing-reveal--delayed">
          <KollioLandingInitiativeFlow />
        </div>
      </section>

      <section id="method" class="landing-outcomes" :aria-label="t('landing.outcomes.label')">
        <article v-for="item in outcomeItems" :key="item.key">
          <KollioArtwork class="landing-outcome-asset" :name="item.asset" />
          <div><h2>{{ t(`landing.outcomes.${item.key}.title`) }}</h2><p>{{ t(`landing.outcomes.${item.key}.description`) }}</p></div>
        </article>
      </section>

      <p id="trust" class="landing-trust">{{ t('landing.trust') }}</p>

      <section id="teams" class="landing-method">
        <div class="landing-method__intro">
          <KollioArtwork class="landing-method__artwork" name="decision-memory" />
          <p>{{ t('landing.method.overline') }}</p>
          <h2>{{ t('landing.method.title') }}</h2>
          <p>{{ t('landing.method.description') }}</p>
        </div>
        <ol class="landing-method__steps">
          <li v-for="step in ['capture', 'challenge', 'decide']" :key="step">
            <span>{{ t(`landing.method.${step}.number`) }}</span>
            <div><h3>{{ t(`landing.method.${step}.title`) }}</h3><p>{{ t(`landing.method.${step}.description`) }}</p></div>
          </li>
        </ol>
      </section>

      <section class="landing-final-cta">
        <KollioArtwork class="landing-final-cta__artwork" name="team-alignment" />
        <p>{{ t('landing.finalCta.note') }}</p>
        <h2>{{ t('landing.finalCta.title') }}</h2>
        <KollioPrimaryAction
          :to="authEnabled && !session?.signedIn ? undefined : workspaceTarget"
          :href="authEnabled && !session?.signedIn ? '/sign-in' : undefined"
          :label="t('landing.finalCta.action')"
        />
      </section>
    </main>
  </div>
</template>

<style scoped>
.landing-page { min-height: 100vh; overflow: hidden; background: radial-gradient(circle at 8% 40%, color-mix(in srgb, var(--kollio-wash) 24%, transparent), transparent 18rem), radial-gradient(circle at 98% 74%, color-mix(in srgb, var(--kollio-question-wash) 31%, transparent), transparent 17rem), var(--ui-bg); color: var(--ui-text); }
.landing-reveal { animation: landing-enter 450ms cubic-bezier(.22, 1, .36, 1) both; }.landing-reveal--delayed { animation-delay: 80ms; animation-duration: 560ms; }
@keyframes landing-enter { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: translateY(0); } }
.landing-nav { display: grid; width: min(1440px, calc(100% - 48px)); min-height: 62px; grid-template-columns: 1fr auto 1fr; align-items: center; gap: 32px; margin-inline: auto; }
.landing-nav__links, .landing-nav__actions { display: flex; align-items: center; gap: 28px; }
.landing-nav__links a, .landing-nav__signin, .landing-nav__language { color: var(--ui-text); font-size: .88rem; font-weight: 500; text-decoration: none; }
.landing-nav__actions { justify-content: flex-end; gap: 20px; }.landing-nav__language { color: var(--ui-text-muted); }
.landing-first-frame { position: relative; min-height: 750px; padding-top: 1px; }
.landing-hero { position: relative; z-index: 1; width: min(1240px, calc(100% - 48px)); margin: 16px auto 8px; text-align: center; }
.landing-hero__copy { width: min(940px, 100%); margin-inline: auto; }.landing-hero__eyebrow { color: var(--kollio-active-ink); font-size: var(--kollio-text-small); font-weight: 600; }
.landing-hero h1 { position: relative; z-index: 0; margin-top: 10px; color: var(--kollio-heading); font-family: var(--font-display); font-size: clamp(2.75rem, 3.7vw, 3.5rem); font-weight: 700; letter-spacing: -.04em; line-height: .98; text-wrap: balance; }
.landing-hero__description { max-width: 690px; margin: 10px auto 0; color: var(--ui-text-muted); font-size: clamp(1.02rem, 1.5vw, 1.25rem); line-height: 1.45; text-wrap: balance; }
.landing-hero__actions { display: flex; justify-content: center; gap: 13px; margin-top: 14px; }
.landing-secondary-action { display: inline-flex; min-height: 48px; align-items: center; border: 1px solid var(--ui-border); border-radius: 12px; background: color-mix(in srgb, white 70%, transparent); padding: 0 20px; color: var(--kollio-heading); font-size: .9rem; font-weight: 600; text-decoration: none; transition: border-color 180ms ease, transform 180ms ease; }
.landing-secondary-action:hover { border-color: var(--kollio-active-wash); transform: translateY(-1px); }
.landing-note { position: absolute; width: 180px; color: var(--kollio-active-ink); font-family: var(--font-annotation); font-size: var(--kollio-text-lead); font-weight: 600; line-height: 1.15; opacity: .72; }
.landing-note--left { top: 88px; left: -16px; transform: rotate(-6deg); }.landing-note--right { top: 110px; right: -6px; transform: rotate(4deg); }
.landing-arrow { position: absolute; z-index: 2; width: 70px; height: 74px; opacity: .8; pointer-events: none; }
.landing-arrow--left { top: 160px; left: 108px; }.landing-arrow--right { top: 160px; right: -4px; }
.landing-preview-wrap { position: relative; z-index: 1; width: min(1426px, calc(100% - 160px)); margin: 10px auto 0; }
.landing-outcomes { display: grid; width: min(1320px, calc(100% - 48px)); grid-template-columns: repeat(3, 1fr); margin: 6px auto 0; }
.landing-outcomes article { display: flex; min-width: 0; align-items: center; gap: 20px; padding: 10px 28px; }.landing-outcomes article + article { border-left: 1px solid var(--ui-border); }
.landing-outcome-asset { width: clamp(82px, 7vw, 100px); height: clamp(82px, 7vw, 100px); flex: none; transition: transform 260ms cubic-bezier(.22, 1, .36, 1); }
.landing-outcomes h2 { color: var(--kollio-heading); font-size: 1.125rem; font-weight: 650; }.landing-outcomes p { max-width: 310px; margin-top: 5px; color: var(--ui-text-muted); font-size: .9375rem; line-height: 1.42; }
.landing-trust { display: flex; justify-content: center; margin: 22px auto 38px; color: var(--ui-text-muted); font-size: .75rem; }
.landing-method { display: grid; width: min(1240px, calc(100% - 48px)); grid-template-columns: minmax(0, .9fr) minmax(0, 1.1fr); gap: clamp(56px, 8vw, 128px); margin: 128px auto; }
.landing-method__intro > p:first-of-type { color: var(--kollio-active-ink); font-size: .78rem; font-weight: 650; }
.landing-method__artwork { width: min(360px, 82%); height: auto; margin: 0 0 18px -12px; }
.landing-method__intro h2 { max-width: 650px; margin-top: 14px; color: var(--kollio-heading); font-family: var(--font-display); font-size: var(--kollio-display-section); font-weight: 700; letter-spacing: -.04em; line-height: 1; text-wrap: balance; }
.landing-method__intro > p:last-child { max-width: 540px; margin-top: 24px; color: var(--ui-text-muted); font-size: var(--kollio-text-body); line-height: 1.65; }
.landing-method__steps { border-top: 1px solid var(--ui-border); }
.landing-method__steps li { display: grid; grid-template-columns: 48px 1fr; gap: 18px; border-bottom: 1px solid var(--ui-border); padding: 26px 4px; }
.landing-method__steps li > span { color: var(--kollio-active-ink); font-family: var(--font-mono); font-size: .76rem; }
.landing-method__steps h3 { color: var(--kollio-heading); font-size: var(--kollio-text-lead); font-weight: 650; }.landing-method__steps p { max-width: 520px; margin-top: 6px; color: var(--ui-text-muted); font-size: var(--kollio-text-small); line-height: 1.55; }
.landing-final-cta { display: grid; width: min(1240px, calc(100% - 48px)); justify-items: center; margin: 0 auto 32px; border-radius: var(--kollio-radius-xl); background: var(--kollio-action); padding: clamp(56px, 8vw, 96px) 24px; color: white; text-align: center; }
.landing-final-cta__artwork { width: clamp(150px, 17vw, 220px); height: auto; margin: -24px auto 18px; }
.landing-final-cta > p { color: color-mix(in srgb, white 70%, var(--kollio-wash)); font-family: var(--font-annotation); font-size: var(--kollio-text-lead); font-weight: 600; }.landing-final-cta h2 { max-width: 760px; margin: 12px auto 28px; font-family: var(--font-display); font-size: var(--kollio-display-cta); font-weight: 700; letter-spacing: -.04em; line-height: .98; text-wrap: balance; }.landing-final-cta :deep(.primary-action) { background: white; color: var(--kollio-heading); }.landing-final-cta :deep(.primary-action)::after { background: var(--kollio-wash); }
@media (max-width: 1120px) { .landing-nav { grid-template-columns: 1fr auto; }.landing-nav__links { display: none; }.landing-note, .landing-arrow { display: none; }.landing-preview-wrap { width: min(100% - 48px, 1426px); } }
@media (max-width: 960px) { .landing-outcomes { grid-template-columns: 1fr; }.landing-outcomes article { padding-inline: 12px; }.landing-outcomes article + article { border-top: 1px solid var(--ui-border); border-left: 0; }.landing-method { grid-template-columns: 1fr; gap: 54px; margin-block: 90px; } }
@media (max-width: 640px) { .landing-nav, .landing-hero, .landing-preview-wrap, .landing-outcomes, .landing-method, .landing-final-cta { width: min(100% - 28px, 1440px); }.landing-nav { min-height: 68px; }.landing-nav__signin, .landing-nav__language { display: none; }.landing-first-frame { min-height: 0; }.landing-hero { margin-top: 38px; }.landing-hero__actions { flex-direction: column; align-items: stretch; }.landing-secondary-action { justify-content: center; }.landing-outcomes article { padding-block: 18px; }.landing-trust { padding-inline: 22px; text-align: center; }.landing-method { margin-block: 74px; }.landing-method__artwork { margin-left: 0; }.landing-method__steps li { grid-template-columns: 38px 1fr; }.landing-final-cta { border-radius: var(--kollio-radius-lg); } }
@media (hover: hover) { .landing-outcome-asset:hover { transform: translateY(-3px) rotate(-1deg); } }
@media (prefers-reduced-motion: reduce) { .landing-reveal { animation: none; }.landing-outcome-asset { transition: none; } }
</style>
