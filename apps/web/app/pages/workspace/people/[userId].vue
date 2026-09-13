<script setup lang="ts">
import type { ProfileResponse } from '@kollio/api-client'

definePageMeta({ layout: 'workspace', middleware: 'authenticated' })

const { t } = useI18n()
const route = useRoute()
const requestFetch = useRequestFetch()
const localePath = useLocalePath()
const userId = String(route.params.userId)
const glyphs = Object.freeze({ back: '←', forward: '→' })

const { data: profile, error } = await useAsyncData(`profile-${userId}`, () =>
  requestFetch<ProfileResponse>(`/api/users/${encodeURIComponent(userId)}`),
)

function ideaLink(id: string) {
  return localePath({ name: 'workspace-ideas-ideaId', params: { ideaId: id } })
}
</script>

<template>
  <div class="profile-shell">
    <NuxtLink class="profile-back" :to="localePath('/workspace')"><span aria-hidden="true" v-text="glyphs.back" /> {{ t('ideas.profile.back') }}</NuxtLink>

    <p v-if="error?.statusCode === 404" class="profile-error">
      <strong>{{ t('ideas.profile.notFound') }}</strong>
      <span>{{ t('ideas.profile.notFoundDescription') }}</span>
    </p>
    <p v-else-if="error" class="profile-error">
      <strong>{{ t('ideas.profile.loadError.title') }}</strong>
      <span>{{ t('ideas.profile.loadError.description') }}</span>
    </p>

    <template v-else-if="profile">
      <header class="profile-header">
        <KollioPersonRow :name="profile.display_name" :meta="profile.handle ? `@${profile.handle}` : ''" :avatar-key="profile.avatar_key || 'lilac'" />
        <p v-if="profile.bio" class="profile-bio">{{ profile.bio }}</p>
        <ul class="profile-roles" :aria-label="t('ideas.profile.rolesTitle')">
          <li v-for="role in profile.roles" :key="role">{{ t(`ideas.role.${role}`) }}</li>
        </ul>
      </header>

      <section class="profile-section">
        <h2>{{ t('ideas.profile.ownedTitle') }}</h2>
        <ul v-if="profile.owned_ideas.length" role="list">
          <li v-for="idea in profile.owned_ideas" :key="idea.id">
            <NuxtLink :to="ideaLink(idea.id)">{{ idea.title }}</NuxtLink>
            <span>{{ t(`ideas.stage.${idea.stage}`) }}</span>
          </li>
        </ul>
        <p v-else class="profile-empty">{{ t('ideas.profile.ownedEmpty') }}</p>
      </section>

      <section class="profile-section">
        <h2>{{ t('ideas.profile.teamsTitle') }}</h2>
        <ul v-if="profile.memberships.length" role="list">
          <li v-for="membership in profile.memberships" :key="`${membership.idea_id}-${membership.role}`">
            <strong>{{ t(`ideas.role.${membership.role}`) }}</strong>
            <span>{{ t('ideas.profile.roleIn', { idea: membership.idea_title }) }}</span>
            <NuxtLink class="profile-open" :to="ideaLink(membership.idea_id)"><span aria-hidden="true" v-text="glyphs.forward" /></NuxtLink>
          </li>
        </ul>
        <p v-else class="profile-empty">{{ t('ideas.profile.teamsEmpty') }}</p>
      </section>

      <section class="profile-section">
        <h2>{{ t('ideas.profile.actsTitle') }}</h2>
        <ul v-if="profile.contributions.length" role="list">
          <li v-for="act in profile.contributions" :key="`${act.idea_id}-${act.short_hash}`">
            <span class="profile-act-message">{{ act.message }}</span>
            <NuxtLink :to="ideaLink(act.idea_id)">{{ t('ideas.profile.onIdea', { idea: act.idea_title }) }}</NuxtLink>
            <time :datetime="act.created_at">{{ new Date(act.created_at).toLocaleDateString() }}</time>
          </li>
        </ul>
        <p v-else class="profile-empty">{{ t('ideas.profile.actsEmpty') }}</p>
      </section>
    </template>
  </div>
</template>

<style scoped>
.profile-shell { display: grid; gap: 26px; max-width: 640px; margin: 0 auto; padding: 22px 4px 48px; }
.profile-back { font-size: .85rem; color: var(--ui-text-muted); }
.profile-header { display: grid; gap: 10px; }
.profile-bio { margin: 0; color: var(--ui-text-muted); font-size: .92rem; }
.profile-roles { display: flex; flex-wrap: wrap; gap: 6px; margin: 0; padding: 0; list-style: none; }
.profile-roles li { border-radius: 999px; padding: 4px 12px; background: var(--kollio-surface-accented, #EEE8F2); font-size: .74rem; font-weight: 600; }
.profile-section { display: grid; gap: 10px; }
.profile-section h2 { margin: 0; font-size: .78rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--ui-text-muted); }
.profile-section ul { display: grid; gap: 8px; margin: 0; padding: 0; list-style: none; }
.profile-section li { display: flex; flex-wrap: wrap; align-items: baseline; gap: 10px; border-bottom: 1px solid var(--ui-border); padding-bottom: 8px; font-size: .9rem; }
.profile-section li span { color: var(--ui-text-muted); font-size: .82rem; }
.profile-open { text-decoration: none; }
.profile-empty { margin: 0; color: var(--ui-text-muted); font-size: .85rem; }
.profile-error { display: grid; gap: 6px; }
</style>
