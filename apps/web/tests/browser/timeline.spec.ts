import { expect, test } from '@playwright/test'
import type { IdeaResponse, IterationResponse, ProfileResponse } from '@kollio/api-client'
import fr from '../../i18n/locales/fr.json' with { type: 'json' }
import en from '../../i18n/locales/en.json' with { type: 'json' }

const owner: ProfileResponse = {
  id: 'owner-one', display_name: 'Propriétaire', handle: 'owner', roles: ['dev'],
  bio: null, avatar_key: null, owned_ideas: [], memberships: [], contributions: [],
}

function baseIteration(overrides: Partial<IterationResponse>): IterationResponse {
  return {
    id: 'i1', idea_id: 'idea-one', parent_id: null, author_id: 'owner-one',
    message: 'Initial deposit', lang: 'en',
    payload: { title: 'Une idée', pitch: 'P', stage: 'seed' },
    branch: 'main', proposal_status: null, short_hash: 'deadbeefcafe', revision: 1,
    created_at: '2026-09-01T10:00:00Z', analysis: null, ...overrides,
  } as IterationResponse
}

const idea: IdeaResponse = {
  id: 'idea-one', slug: 'une-idee', title: 'Une idée à explorer',
  pitch: 'Un contenu original conservé dans les deux langues.',
  stage: 'seed', lang: 'fr', created_at: '2026-09-01T10:00:00Z',
  owner_id: 'owner-one', workspace_id: 'workspace-one', visibility: 'workspace',
  collaborators: [{ id: 'member-two', display_name: 'Camille', participation: 'contributor', business_function: 'engineering', roles: ['engineering'], bio: null, avatar_key: 'sage' }],
  sought_roles: [], join_requests: [],
}

for (const [locale, messages] of [['fr', fr], ['en', en]] as const) {
  test.describe(locale, () => {
    const prefix = locale === 'fr' ? '' : '/en'

    test('TIMELINE-01 renders the real append-only history', async ({ page }) => {
      await page.route(/\/api\/session$/, route => route.fulfill({ json: { signedIn: true, subject: 'member-two' } }))
      await page.route(/\/api\/ideas\/idea-one$/, route => route.fulfill({ json: idea }))
      await page.route(/\/api\/users\/owner-one$/, route => route.fulfill({ json: owner }))
      await page.route(/\/api\/ideas\/idea-one\/iterations$/, route => route.fulfill({
        json: [
          baseIteration({ id: 'i2', revision: 2, message: 'Narrow the fleet', parent_id: 'i1' }),
          baseIteration({ id: 'p1', revision: 3, branch: 'proposal/offline', message: 'Offline app first',
            proposal_status: 'pending', author_id: 'member-two',
            analysis: { state: 'running', constraints: {} } as never }),
          baseIteration({ id: 'i1', revision: 1, message: 'Initial deposit',
            analysis: { state: 'resolved', realism_score: 62, constraints: {} } as never }),
        ],
      }))
      const ideaResponse = page.waitForResponse(r => /\/api\/ideas\/idea-one\/iterations$/.test(r.url()))
      await page.goto(`${prefix}/workspace/ideas/idea-one`)
      await ideaResponse
      const timeline = page.locator('.iteration-timeline')
      await expect(timeline.locator('[data-line="main"]')).toHaveCount(2)
      await expect(timeline.locator('time').first()).toHaveAttribute('datetime', '2026-09-01T10:00:00Z')
      await expect(timeline.getByText('Narrow the fleet')).toBeVisible()
      await expect(timeline.getByText('Propriétaire').first()).toBeVisible()
      await expect(timeline.locator('[data-line="branch"]')).toHaveCount(1)
      await expect(timeline.getByText(messages.ideas.iterations.pending)).toBeVisible()
      await expect(timeline.getByText(messages.ideas.iterations.analysisResolved)).toBeVisible()
      await expect(timeline.getByText(messages.ideas.iterations.analysisRunning)).toBeVisible()
    })
  })
}
