<script setup lang="ts">
import type { IdeaSummaryResponse } from '@kollio/api-client'

const props = defineProps<{
  idea: IdeaSummaryResponse
  stageLabel: string
  openLabel: string
  contributorTitle: string
  expertiseTitle: string
  closeLabel: string
  to: string
  mobileOpen: boolean
  profileLinks?: boolean
}>()

defineEmits<{ close: [] }>()

const collaborators = computed(() => props.idea.collaborators ?? [])
const roleKeys = computed(() => Array.from(new Set(collaborators.value.flatMap(person => person.roles))).slice(0, 3))
</script>

<template>
  <aside class="idea-preview" :class="{ 'is-mobile-open': mobileOpen }" :aria-label="$t('ideas.explorer.preview')">
    <header class="idea-preview-toolbar">
      <KollioSketchAnnotation kind="swash" active :animated="false">{{ stageLabel }}</KollioSketchAnnotation>
      <button type="button" class="idea-preview-close" :aria-label="closeLabel" @click="$emit('close')">
        <svg aria-hidden="true" viewBox="0 0 24 24"><path d="m6 6 12 12M18 6 6 18" /></svg>
      </button>
    </header>
    <div class="idea-preview-content">
      <h2>{{ idea.title }}</h2>
      <p>{{ idea.pitch }}</p>
      <section>
        <h3>{{ contributorTitle }}</h3>
        <KollioAvatarStack v-if="collaborators.length" :people="collaborators" :label="contributorTitle" :profile-links="profileLinks" class="idea-preview-avatars" />
        <p v-else class="idea-preview-empty">{{ $t('ideas.explorer.noContributors') }}</p>
      </section>
      <section v-if="roleKeys.length">
        <h3>{{ expertiseTitle }}</h3>
        <ul class="idea-preview-roles">
          <li v-for="(role, index) in roleKeys" :key="role">
            <span class="idea-preview-role-icon" aria-hidden="true">
              <svg v-if="index === 0" viewBox="0 0 24 24"><circle cx="11" cy="11" r="6" /><path d="m16 16 4 4" /></svg>
              <svg v-else-if="index === 1" viewBox="0 0 24 24"><path d="M12 3v3m0 12v3M3 12h3m12 0h3M6 6l2 2m8 8 2 2m0-12-2 2M8 16l-2 2" /><circle cx="12" cy="12" r="4" /></svg>
              <svg v-else viewBox="0 0 24 24"><path d="M16 20a4 4 0 0 0-8 0M12 13a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm7 7a3 3 0 0 0-3-3M5 20a3 3 0 0 1 3-3" /></svg>
            </span>
            <span><strong>{{ $t(`ideas.detail.roles.${role}`) }}</strong><small>{{ collaborators.find(person => person.roles.includes(role))?.display_name }}</small></span>
          </li>
        </ul>
      </section>
    </div>
    <footer><KollioPrimaryAction :to="to" :label="openLabel" /></footer>
  </aside>
</template>

<style scoped>
.idea-preview { display: flex; min-width: 0; min-height: 704px; flex-direction: column; border-left: 1px solid var(--ui-border); background: var(--ui-bg-elevated); }
.idea-preview-toolbar { display: flex; min-height: 64px; align-items: center; justify-content: space-between; padding: 0 18px 0 26px; }
.idea-preview-toolbar :deep(.sketch-annotation--swash) { --sketch-opacity: .65; color: var(--kollio-active-ink); font-size: var(--kollio-text-caption); font-weight: var(--kollio-weight-strong); }
.idea-preview-close { display: grid; width: 38px; height: 38px; place-items: center; border: 1px solid var(--ui-border); border-radius: var(--kollio-radius-sm); color: var(--ui-text-muted); }
.idea-preview-close svg { width: 17px; fill: none; stroke: currentColor; stroke-linecap: round; stroke-width: 1.7; }
.idea-preview-content { min-height: 0; flex: 1; overflow-y: auto; padding: 6px 28px 26px; }
.idea-preview-content > h2 { color: var(--kollio-heading); font-size: var(--kollio-text-headline); font-weight: var(--kollio-weight-display); letter-spacing: -.045em; line-height: 1.08; text-wrap: balance; }
.idea-preview-content > p { display: -webkit-box; overflow: hidden; margin-top: 22px; color: var(--ui-text-muted); font-size: var(--kollio-text-small); line-height: 1.55; -webkit-box-orient: vertical; -webkit-line-clamp: 7; }
.idea-preview-content section { margin-top: 30px; }
.idea-preview-content h3 { margin-bottom: 15px; color: var(--kollio-heading); font-size: var(--kollio-text-body); font-weight: var(--kollio-weight-display); }
.idea-preview-avatars :deep(li) { width: 46px; height: 46px; font-size: var(--kollio-text-micro); }
.idea-preview-empty { color: var(--ui-text-muted); font-size: var(--kollio-text-caption); }
.idea-preview-roles { display: grid; gap: 14px; }
.idea-preview-roles li { display: grid; grid-template-columns: 28px minmax(0, 1fr); gap: 10px; }
.idea-preview-role-icon { display: grid; width: 25px; height: 25px; place-items: center; color: var(--kollio-active-ink); }
.idea-preview-role-icon svg { width: 21px; fill: none; stroke: currentColor; stroke-linecap: round; stroke-linejoin: round; stroke-width: 1.55; }
.idea-preview-roles strong, .idea-preview-roles small { display: block; }
.idea-preview-roles strong { color: var(--kollio-active-ink); font-size: var(--kollio-text-caption); font-weight: var(--kollio-weight-strong); }
.idea-preview-roles small { margin-top: 3px; overflow: hidden; color: var(--ui-text-muted); font-size: var(--kollio-text-micro); text-overflow: ellipsis; white-space: nowrap; }
.idea-preview footer { padding: 0 24px 22px; }
.idea-preview footer :deep(.primary-action) { width: 100%; justify-content: center; }
@media (min-width: 1181px) { .idea-preview-close { display: none; } }
@media (min-width: 1181px) { .idea-preview { height: clamp(660px, calc(100vh - 260px), 760px); min-height: 0; align-self: start; } }
@media (max-width: 1180px) {
  .idea-preview { position: fixed; z-index: 70; top: 16px; right: 16px; bottom: 16px; width: min(390px, calc(100vw - 32px)); min-height: 0; border: 1px solid var(--ui-border); border-radius: var(--kollio-radius-xl); box-shadow: 0 26px 90px color-mix(in srgb, var(--kollio-heading) 20%, transparent); opacity: 0; pointer-events: none; transform: translateX(28px); transition: opacity 180ms ease, transform 240ms cubic-bezier(.16, 1, .3, 1); }
  .idea-preview.is-mobile-open { opacity: 1; pointer-events: auto; transform: translateX(0); }
}
@media (max-width: 620px) { .idea-preview { inset: 0; width: 100%; border: 0; border-radius: 0; } .idea-preview-content { padding-inline: 22px; } }
</style>
