<script setup lang="ts">
import type { ProfileResponse } from '@kollio/api-client'

definePageMeta({ layout: 'workspace', middleware: 'authenticated' })

const { t, locale } = useI18n()
const route = useRoute()
const requestFetch = useRequestFetch()
const localePath = useLocalePath()
const userId = String(route.params.userId)
const glyphs = Object.freeze({ back: '←', forward: '→' })
const dateFormatter = computed(() =>
  new Intl.DateTimeFormat(locale.value, { day: 'numeric', month: 'long', year: 'numeric' }),
)

const { data: profile, error } = await useAsyncData(`profile-${userId}`, () =>
  requestFetch<ProfileResponse>(`/api/users/${encodeURIComponent(userId)}`),
)

function ideaLink(id: string) {
  return localePath({ name: 'workspace-ideas-ideaId', params: { ideaId: id } })
}
</script>

<template>
  <div class="profile-shell">
    <NuxtLink class="profile-back" :to="localePath('/workspace/ideas')"><span aria-hidden="true" v-text="glyphs.back" /> {{ t('ideas.profile.back') }}</NuxtLink>

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
            <time :datetime="act.created_at">{{ dateFormatter.format(new Date(act.created_at)) }}</time>
          </li>
        </ul>
        <p v-else class="profile-empty">{{ t('ideas.profile.actsEmpty') }}</p>
      </section>
    </template>
  </div>
</template>

<style scoped>
.profile-shell { display: grid; gap: 26px; max-width: 640px; margin: 0 auto; padding: 22px 4px 48px; }
.profile-back { font-size: var(--kollio-text-small); color: var(--ui-text-muted); }
.profile-header { display: grid; gap: 10px; }
.profile-bio { margin: 0; color: var(--ui-text-muted); font-size: var(--kollio-text-small); }
.profile-roles { display: flex; flex-wrap: wrap; gap: 6px; margin: 0; padding: 0; list-style: none; }
.profile-roles li { border-radius: var(--kollio-radius-pill); padding: 4px 12px; background: var(--ui-bg-accented); font-size: var(--kollio-text-caption); font-weight: var(--kollio-weight-strong); }
.profile-section { display: grid; gap: 10px; }
.profile-section h2 { margin: 0; font-size: var(--kollio-text-caption); font-weight: var(--kollio-weight-display); letter-spacing: .08em; text-transform: uppercase; color: var(--ui-text-muted); }
.profile-section ul { display: grid; gap: 8px; margin: 0; padding: 0; list-style: none; }
.profile-section li { display: flex; flex-wrap: wrap; align-items: baseline; gap: 10px; border-bottom: 1px solid var(--ui-border); padding-bottom: 8px; font-size: var(--kollio-text-small); }
.profile-section li span { color: var(--ui-text-muted); font-size: var(--kollio-text-small); }
.profile-open { text-decoration: none; }
.profile-empty { margin: 0; color: var(--ui-text-muted); font-size: var(--kollio-text-small); }
.profile-error { display: grid; gap: 6px; color: var(--ui-error); }
</style>
