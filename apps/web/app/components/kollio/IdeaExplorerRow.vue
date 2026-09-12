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
}>()

defineEmits<{ select: [] }>()

const collaborators = computed(() => props.idea.collaborators ?? [])

function initials(name: string) {
  return name.split(/\s+/).slice(0, 2).map(part => part.charAt(0)).join('').toUpperCase()
}
</script>

<template>
  <button type="button" class="explorer-row" :class="{ 'is-selected': selected }" :aria-pressed="selected" @click="$emit('select')">
    <span class="explorer-row-avatar" :data-avatar="collaborators[0]?.avatar_key || 'lilac'" aria-hidden="true">
      {{ initials(collaborators[0]?.display_name || idea.title) }}
    </span>
    <span class="explorer-row-copy">
      <strong>{{ idea.title }}</strong>
      <span class="explorer-row-pitch">{{ idea.pitch }}</span>
      <span class="explorer-row-topics">
        <span v-if="domainLabel">{{ domainLabel }}</span>
        <span>{{ stageLabel }}</span>
        <span v-if="expertiseLabel">{{ expertiseLabel }}</span>
      </span>
    </span>
    <span class="explorer-row-activity">
      <KollioAvatarStack v-if="collaborators.length" :people="collaborators" :label="avatarLabel" />
      <span>{{ contributorLabel }}</span>
      <time :datetime="idea.created_at">{{ dateLabel }}</time>
    </span>
  </button>
</template>

<style scoped>
.explorer-row { position: relative; display: grid; width: 100%; min-height: 128px; grid-template-columns: 54px minmax(0, 1fr) 126px; align-items: center; gap: 18px; border-bottom: 1px solid var(--ui-border); padding: 19px 22px; text-align: left; transition: background 180ms ease, transform 220ms cubic-bezier(.16, 1, .3, 1); }
.explorer-row::before { position: absolute; right: 7px; bottom: 5px; left: 7px; height: calc(100% - 10px); border-bottom: 1.5px solid transparent; border-left: 1.5px solid transparent; border-radius: 0 0 0 17px; content: ''; pointer-events: none; transition: border-color 180ms ease, background 180ms ease; }
.explorer-row:hover, .explorer-row:focus-visible { background: color-mix(in srgb, var(--kollio-wash) 13%, transparent); }
.explorer-row:focus-visible { outline: 2px solid color-mix(in srgb, var(--kollio-active-ink) 52%, transparent); outline-offset: -3px; }
.explorer-row.is-selected { background: color-mix(in srgb, var(--kollio-wash) 24%, transparent); }
.explorer-row.is-selected::before { border-color: color-mix(in srgb, var(--kollio-active-ink) 82%, transparent); box-shadow: -2px 1px 0 color-mix(in srgb, var(--kollio-active-ink) 17%, transparent); transform: rotate(.08deg); }
.explorer-row-avatar { display: grid; width: 48px; height: 48px; place-items: center; border-radius: 50%; background: linear-gradient(145deg, var(--kollio-wash), color-mix(in srgb, var(--kollio-wash) 32%, white)); color: var(--kollio-heading); font-size: .72rem; font-weight: 720; }
.explorer-row-avatar[data-avatar='rose'] { background: color-mix(in srgb, var(--kollio-question-wash) 72%, white); }
.explorer-row-avatar[data-avatar='ochre'] { background: color-mix(in srgb, var(--ui-warning) 28%, white); }
.explorer-row-avatar[data-avatar='citron'] { background: color-mix(in srgb, var(--kollio-verified) 34%, white); }
.explorer-row-avatar[data-avatar='coral'] { background: color-mix(in srgb, var(--ui-error) 16%, white); }
.explorer-row-avatar[data-avatar='sage'] { background: color-mix(in srgb, var(--ui-success) 18%, white); }
.explorer-row-copy { min-width: 0; }
.explorer-row-copy strong { display: block; color: var(--kollio-heading); font-size: 1rem; font-weight: 650; letter-spacing: -.025em; line-height: 1.25; }
.explorer-row-pitch { display: -webkit-box; overflow: hidden; margin-top: 6px; color: var(--ui-text-muted); font-size: .76rem; line-height: 1.45; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }
.explorer-row-topics { display: flex; overflow: hidden; align-items: center; gap: 0; margin-top: 9px; color: var(--ui-text-muted); font-size: .67rem; white-space: nowrap; }
.explorer-row-topics span { overflow: hidden; text-overflow: ellipsis; }
.explorer-row-topics span + span::before { margin: 0 10px; color: var(--kollio-active-ink); content: '•'; }
.explorer-row-activity { display: grid; align-content: center; justify-items: start; gap: 4px; color: var(--ui-text-muted); font-size: .66rem; line-height: 1.25; }
.explorer-row-activity :deep(.avatar-stack) { margin-bottom: 3px; }
@media (max-width: 760px) {
  .explorer-row { grid-template-columns: 44px minmax(0, 1fr); min-height: 118px; gap: 14px; padding: 17px 16px; }
  .explorer-row-avatar { width: 42px; height: 42px; }
  .explorer-row-activity { display: none; }
}
</style>
