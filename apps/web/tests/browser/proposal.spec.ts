import { expect, test } from '@playwright/test'
import type { IdeaResponse, IterationResponse, ProfileResponse } from '@kollio/api-client'
import fr from '../../i18n/locales/fr.json' with { type: 'json' }
import en from '../../i18n/locales/en.json' with { type: 'json' }

const owner: ProfileResponse = {
  id: 'owner-one', display_name: 'Propriétaire', handle: 'owner', roles: ['dev'],
  bio: null, avatar_key: null, owned_ideas: [], memberships: [], contributions: [],
}

const idea: IdeaResponse = {
  id: 'idea-one', slug: 'une-idee', title: 'Une idée à explorer',
  pitch: 'Un contenu original.',
  stage: 'seed', lang: 'fr', created_at: '2026-09-01T10:00:00Z',
  owner_id: 'owner-one', workspace_id: 'workspace-one', visibility: 'workspace',
  collaborators: [], sought_roles: [], join_requests: [],
}

function baseIteration(overrides: Partial<IterationResponse>): IterationResponse {
  return {
    id: 'i1', idea_id: 'idea-one', parent_id: null, author_id: 'owner-one',
    message: 'Initial deposit', lang: 'fr',
    payload: { title: 'Une idée', pitch: 'P', stage: 'seed' },
    branch: 'main', proposal_status: null, short_hash: 'deadbeefcafe', revision: 1,
    created_at: '2026-09-01T10:00:00Z', analysis: null, ...overrides,
  } as IterationResponse
}

for (const [locale, messages] of [['fr', fr], ['en', en]] as const) {
  test.describe(locale, () => {
    const prefix = locale === 'fr' ? '' : '/en'
    const it = messages.ideas.iterations as Record<string, string>

    test('PROPOSE-01 sends a pending proposal visible in the timeline', async ({ page }) => {
      const proposals: IterationResponse[] = [baseIteration({})]
      await page.route(/\/api\/session$/, route => route.fulfill({ json: { signedIn: true, subject: 'member-two' } }))
      await page.route(/\/api\/ideas\/idea-one$/, route => route.fulfill({ json: idea }))
      await page.route(/\/api\/users\/owner-one$/, route => route.fulfill({ json: owner }))
      await page.route(/\/api\/ideas\/idea-one\/iterations$/, (route) => {
        if (route.request().method() !== 'POST') return route.fulfill({ json: proposals })
        proposals.push(baseIteration({
          id: 'p1', revision: 2, parent_id: 'i1', branch: 'proposal/offline',
          message: 'Commencer par le mode hors ligne', proposal_status: 'pending',
          author_id: 'member-two',
        }))
        return route.fulfill({ status: 201, json: proposals[proposals.length - 1] })
      })
      await page.goto(`${prefix}/workspace/ideas/idea-one`)
      await page.getByRole('button', { name: it.propose }).click()
      await page.getByLabel(it.message).fill('Commencer par le mode hors ligne')
      await page.getByRole('button', { name: it.send, exact: true }).click()
      await expect(page.locator('[data-line="branch"]')).toBeVisible()
      await expect(page.getByText(it.pending)).toBeVisible()
    })

    test('PROPOSE-02 surfaces the stale-head conflict', async ({ page }) => {
      await page.route(/\/api\/session$/, route => route.fulfill({ json: { signedIn: true, subject: 'member-two' } }))
      await page.route(/\/api\/ideas\/idea-one$/, route => route.fulfill({ json: idea }))
      await page.route(/\/api\/users\/owner-one$/, route => route.fulfill({ json: owner }))
      await page.route(/\/api\/ideas\/idea-one\/iterations$/, route =>
        route.fulfill({ status: 409, json: { detail: 'conflict' } }))
      await page.goto(`${prefix}/workspace/ideas/idea-one`)
      await page.getByRole('button', { name: it.propose }).click()
      await page.getByLabel(it.message).fill('Trop tard')
      await page.getByRole('button', { name: it.send, exact: true }).click()
      await expect(page.getByRole('alert').filter({ hasText: it.conflict })).toBeVisible()
    })
  })
}
