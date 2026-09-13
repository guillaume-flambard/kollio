<template>
  <svg class="landing-frame-decoration" viewBox="0 0 1600 820" preserveAspectRatio="none" aria-hidden="true">
    <defs>
      <filter id="paper-noise" x="-10%" y="-10%" width="120%" height="120%">
        <feTurbulence type="fractalNoise" baseFrequency="0.035 0.11" numOctaves="3" seed="8" result="noise" />
        <feDisplacementMap in="SourceGraphic" in2="noise" scale="7" />
      </filter>
    </defs>

    <path class="wash wash--lilac" filter="url(#paper-noise)" d="M-34 38 5 37 87 166l84 159-1 118-86-41-56-116-62-50Z" />
    <g class="plant">
      <path class="plant__stem" d="M-6 401c34-61 59-130 72-212" />
      <path class="plant__leaf" d="M20 340C3 305 8 278 46 257c13 37 3 63-26 83Z" />
      <path class="plant__leaf" d="M53 270c9-39 32-59 73-55-4 39-28 58-73 55Z" />
      <path class="plant__leaf" d="M66 196c-11-35-2-59 30-76 13 32 4 58-30 76Z" />
    </g>

    <path class="wash wash--coral" filter="url(#paper-noise)" d="m1544 671 64-27 32 67-22 105-66 8-42-49Z" />

  </svg>
</template>

<style scoped>
.landing-frame-decoration { position: absolute; z-index: 0; inset: 0; width: 100%; height: 100%; overflow: visible; pointer-events: none; }
.wash { opacity: .84; }
.wash--lilac { fill: color-mix(in srgb, var(--kollio-wash) 86%, white); }
.wash--coral { fill: color-mix(in srgb, var(--kollio-question) 82%, white); }
.plant__stem { fill: none; stroke: var(--kollio-verified); stroke-linecap: round; stroke-width: 5; }
.plant__leaf { fill: color-mix(in srgb, var(--kollio-verified) 88%, white); stroke: color-mix(in srgb, var(--kollio-verified) 75%, var(--kollio-heading)); stroke-width: 1; }
@media (max-width: 1120px) { .landing-frame-decoration { display: none; } }
</style>
