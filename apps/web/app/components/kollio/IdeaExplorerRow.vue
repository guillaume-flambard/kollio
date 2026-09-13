<script setup lang="ts">
import type { IdeaSummaryResponse } from '@kollio/api-client'

const props = defineProps<{
  idea: IdeaSummaryResponse
  selected: boolean
  stageLabel: string
  dateLabel: string
  contributorLabel: string
  avatarLabel: string
  expertiseLabel?: string
  domainLabel?: string
  realismLabel?: string
  rolesLabel?: string
  profileLinks?: boolean
}>()

defineEmits<{ select: [] }>()

const collaborators = computed(() => props.idea.collaborators ?? [])

function initials(name: string) {
  return name.split(/\s+/).slice(0, 2).map(part => part.charAt(0)).join('').toUpperCase()
}
</script>

<template>
  <button type="button" class="explorer-row" :class="{ 'is-selected': selected }" :aria-pressed="selected" @click="$emit('select')">
    <svg class="explorer-row-selection" viewBox="0 0 1000 136" preserveAspectRatio="none" aria-hidden="true">
      <path d="M15 8C8 38 8 101 18 125C232 132 696 131 988 127" />
      <path d="M18 12C12 42 12 98 21 122C270 128 704 128 972 125" />
    </svg>
    <span class="explorer-row-avatar" :data-avatar="collaborators[0]?.avatar_key || 'lilac'" aria-hidden="true">
      {{ initials(collaborators[0]?.display_name || idea.title) }}
    </span>
    <span class="explorer-row-copy">
      <strong>{{ idea.title }}</strong>
      <span class="explorer-row-pitch">{{ idea.pitch }}</span>
      <span class="explorer-row-topics">
        <span v-if="realismLabel" class="explorer-row-realism">{{ realismLabel }}</span>
        <span>{{ stageLabel }}</span>
        <span v-if="rolesLabel">{{ rolesLabel }}</span>
        <span v-if="domainLabel">{{ domainLabel }}</span>
        <span v-if="expertiseLabel">{{ expertiseLabel }}</span>
      </span>
    </span>
    <span class="explorer-row-activity">
      <KollioAvatarStack v-if="collaborators.length" :people="collaborators" :label="avatarLabel" :profile-links="profileLinks" />
      <span>{{ contributorLabel }}</span>
      <time :datetime="idea.created_at">{{ dateLabel }}</time>
    </span>
  </button>
</template>

<style scoped>
.explorer-row { position: relative; display: grid; width: 100%; min-height: 136px; grid-template-columns: 58px minmax(0, 1fr) 132px; align-items: center; gap: 18px; border-bottom: 1px solid var(--ui-border); padding: 20px 24px; text-align: left; transition: background 180ms ease, transform 220ms cubic-bezier(.16, 1, .3, 1); }
.explorer-row-selection { position: absolute; z-index: 0; inset: 6px 8px 8px 6px; width: calc(100% - 14px); height: calc(100% - 14px); fill: none; stroke: var(--kollio-connector); stroke-linecap: round; stroke-linejoin: round; stroke-width: 1.2; opacity: 0; pointer-events: none; transition: opacity 180ms ease; }
.explorer-row-selection path { vector-effect: non-scaling-stroke; }
.explorer-row-selection path:last-child { stroke-width: .65; opacity: .22; }
.explorer-row:hover, .explorer-row:focus-visible { background: color-mix(in srgb, var(--kollio-wash) 13%, transparent); }
.explorer-row:focus-visible { outline: 2px solid color-mix(in srgb, var(--kollio-active-ink) 52%, transparent); outline-offset: -3px; }
.explorer-row.is-selected { background: transparent; }
.explorer-row.is-selected::before { position: absolute; z-index: 0; inset: 6px 8px 8px 6px; border-radius: 12px; background: color-mix(in srgb, var(--kollio-wash) 24%, transparent); content: ''; }
.explorer-row.is-selected .explorer-row-selection { opacity: .9; }
.explorer-row > :not(.explorer-row-selection) { position: relative; z-index: 1; }
.explorer-row-avatar { display: grid; width: 54px; height: 54px; place-items: center; overflow: hidden; border: 2px solid var(--ui-bg-elevated); border-radius: 50%; background-color: var(--kollio-wash); background-image: url('/avatars/collaborator-sprite.webp'); background-position: 0 0; background-size: 300% 200%; color: transparent; font-size: .72rem; font-weight: 720; }
.explorer-row-avatar[data-avatar='rose'] { background-position: 50% 0; }
.explorer-row-avatar[data-avatar='ochre'] { background-position: 100% 0; }
.explorer-row-avatar[data-avatar='citron'] { background-position: 0 100%; }
.explorer-row-avatar[data-avatar='coral'] { background-position: 50% 100%; }
.explorer-row-avatar[data-avatar='sage'] { background-position: 100% 100%; }
.explorer-row-copy { min-width: 0; }
.explorer-row-copy strong { display: block; color: var(--kollio-heading); font-size: 1.08rem; font-weight: 650; letter-spacing: -.025em; line-height: 1.25; }
.explorer-row-pitch { display: -webkit-box; overflow: hidden; margin-top: 7px; color: var(--ui-text-muted); font-size: .82rem; line-height: 1.46; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }
.explorer-row-topics { display: flex; overflow: hidden; align-items: center; gap: 0; margin-top: 10px; color: var(--ui-text-muted); font-size: .72rem; white-space: nowrap; }
.explorer-row-topics span { overflow: hidden; text-overflow: ellipsis; }
.explorer-row-topics span + span::before { margin: 0 10px; color: var(--kollio-active-ink); content: '•'; }
.explorer-row-realism { font-weight: 600; color: var(--kollio-active-ink); }
.explorer-row-activity { display: grid; align-content: center; justify-items: start; gap: 5px; color: var(--ui-text-muted); font-size: .71rem; line-height: 1.25; }
.explorer-row-activity :deep(.avatar-stack) { margin-bottom: 3px; }
@media (max-width: 760px) {
  .explorer-row { grid-template-columns: 44px minmax(0, 1fr); min-height: 118px; gap: 14px; padding: 17px 16px; }
  .explorer-row-avatar { width: 42px; height: 42px; }
  .explorer-row-activity { display: none; }
}
</style>
