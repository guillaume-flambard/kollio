import { expect, test } from '@playwright/test'
import type { IdeaPageResponse, IdeaResponse, ProfileResponse, WorkspaceResponse } from '@kollio/api-client'
import fr from '../../i18n/locales/fr.json' with { type: 'json' }
import en from '../../i18n/locales/en.json' with { type: 'json' }

const profile: ProfileResponse = {
  id: 'owner-one',
  display_name: 'Propriétaire',
  handle: 'owner',
  roles: ['dev'],
  bio: 'Ships things.',
  avatar_key: 'lilac',
  owned_ideas: [{ id: 'idea-one', slug: 'une-idee', title: 'Une idée à explorer', stage: 'seed', lang: 'fr', created_at: '2026-09-01T10:00:00Z' }],
  memberships: [{ idea_id: 'idea-two', idea_title: 'Deuxième idée', role: 'dev' }],
  contributions: [{ idea_id: 'idea-one', idea_title: 'Une idée à explorer', message: 'Initial deposit', lang: 'fr', short_hash: 'abc123', created_at: '2026-09-01T10:00:00Z' }],
}

const idea: IdeaResponse = {
  id: 'idea-one', slug: 'une-idee', title: 'Une idée à explorer',
  pitch: 'Un contenu original conservé dans les deux langues.',
  stage: 'seed', lang: 'fr', created_at: '2026-09-01T10:00:00Z',
  owner_id: 'owner-one', workspace_id: 'workspace-one', visibility: 'workspace',
  collaborators: [
    { id: 'owner-one', display_name: 'Propriétaire', participation: 'owner', business_function: 'direction', roles: [], bio: null, avatar_key: 'lilac' },
  ],
  sought_roles: ['engineering'], join_requests: [],
}

const explorerPage: IdeaPageResponse = {
  items: [{ ...idea, collaborators: idea.collaborators, sought_roles: ['engineering'], realism_score: null, last_activity_at: null } as never],
  total: 1, limit: 5, offset: 0,
}

for (const [locale, messages] of [['fr', fr], ['en', en]] as const) {
  test.describe(locale, () => {
    const prefix = locale === 'fr' ? '' : '/en'
    const p = messages.ideas.profile as Record<string, string>

    test('PROFILE-01 opens a profile from the idea team panel', async ({ page }) => {
      await page.route(/\/api\/session$/, route => route.fulfill({ json: { signedIn: true, subject: 'member-two' } }))
      await page.route(/\/api\/ideas\/idea-one$/, route => route.fulfill({ json: idea }))
      await page.route(/\/api\/users\/owner-one$/, route => route.fulfill({ json: profile }))
      await page.goto(`${prefix}/workspace/ideas/idea-one`)
      await page.locator('#team').getByRole('link', { name: 'Propriétaire' }).click()
      await expect(page).toHaveURL(new RegExp(`${prefix}/workspace/people/owner-one$`))
      await expect(page.getByRole('heading', { name: p.ownedTitle })).toBeVisible()
      await expect(page.getByText('Ships things.')).toBeVisible()
      await expect(page.getByRole('link', { name: 'Une idée à explorer', exact: true })).toBeVisible()
      // The role/act placeholders and the date must resolve in the active locale.
      await expect(page.getByText(p.roleIn.replace('{idea}', 'Deuxième idée'))).toBeVisible()
      await expect(page.getByRole('link', { name: p.onIdea.replace('{idea}', 'Une idée à explorer'), exact: true })).toBeVisible()
      const expectedDate = new Intl.DateTimeFormat(locale, { day: 'numeric', month: 'long', year: 'numeric' }).format(new Date('2026-09-01T10:00:00Z'))
      await expect(page.locator('time').first()).toHaveText(expectedDate)
    })

    test('PROFILE-02 opens a profile from an explorer collaborator', async ({ page }) => {
      await page.route(/\/api\/session$/, route => route.fulfill({ json: { signedIn: true, subject: 'member-two' } }))
      await page.route(/\/api\/workspaces$/, route => route.fulfill({ json: [{ id: 'workspace-one', name: 'Team', role: 'member' }] } satisfies WorkspaceResponse[]))
      await page.route(/\/api\/workspaces\/workspace-one\/ideas\?*/, route => route.fulfill({ json: explorerPage }))
      await page.route(/\/api\/users\/owner-one$/, route => route.fulfill({ json: profile }))
      await page.goto(`${prefix}/workspace/ideas`)
      await page.locator('aside.idea-preview').getByRole('link', { name: 'Propriétaire' }).click()
      await expect(page).toHaveURL(new RegExp(`${prefix}/workspace/people/owner-one$`))
      await expect(page.getByRole('heading', { name: p.actsTitle })).toBeVisible()
    })
  })
}
