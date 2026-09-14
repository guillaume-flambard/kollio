import { expect, test } from '@playwright/test'
import type { IdeaResponse, IterationResponse, ProfileResponse } from '@kollio/api-client'
import fr from '../../i18n/locales/fr.json' with { type: 'json' }
import en from '../../i18n/locales/en.json' with { type: 'json' }

const ownerProfile: ProfileResponse = {
  id: 'owner-one', display_name: 'Propriétaire', handle: 'owner', roles: ['dev'],
  bio: null, avatar_key: null, owned_ideas: [], memberships: [], contributions: [],
}

function baseIteration(overrides: Partial<IterationResponse>): IterationResponse {
  return {
    id: 'i1', idea_id: 'idea-one', parent_id: null, author_id: 'owner-one',
    message: 'Initial deposit', lang: 'fr',
    payload: { title: 'Une idée', pitch: 'P', stage: 'seed' },
    branch: 'main', proposal_status: null, short_hash: 'deadbeef0001', revision: 1,
    created_at: '2026-09-01T10:00:00Z', analysis: null, rationale: null, ...overrides,
  } as IterationResponse
}

const idea: IdeaResponse = {
  id: 'idea-one', slug: 'une-idee', title: 'Une idée à explorer',
  pitch: 'Un contenu original.',
  stage: 'seed', lang: 'fr', created_at: '2026-09-01T10:00:00Z',
  owner_id: 'owner-one', workspace_id: 'workspace-one', visibility: 'workspace',
  collaborators: [], sought_roles: [], join_requests: [],
}

function initialHistory(): IterationResponse[] {
  return [
    baseIteration({}),
    baseIteration({
      id: 'p1', revision: 2, parent_id: 'i1', branch: 'proposal/offline',
      message: 'Mode hors ligne', proposal_status: 'pending', author_id: 'member-two',
      short_hash: 'cafe0002beef',
    }),
  ]
}

for (const [locale, messages] of [['fr', fr], ['en', en]] as const) {
  test.describe(locale, () => {
    const prefix = locale === 'fr' ? '' : '/en'
    const it = messages.ideas.iterations as Record<string, string>

    async function mockApi(page: import('@playwright/test').Page, history: IterationResponse[]) {
      await page.route(/\/api\/session$/, route => route.fulfill({ json: { signedIn: true, subject: 'owner-one' } }))
      await page.route(/\/api\/ideas\/idea-one$/, route => route.fulfill({ json: idea }))
      await page.route(/\/api\/users\/owner-one$/, route => route.fulfill({ json: ownerProfile }))
      await page.route(/\/api\/ideas\/idea-one\/iterations(\/.*)?$/, (route) => {
        const url = route.request().url()
        if (route.request().method() === 'GET') return route.fulfill({ json: history })
        if (url.endsWith('/accept')) {
          history.splice(1, 0, baseIteration({
            id: 'm2', revision: 2, parent_id: 'i1', message: 'Mode hors ligne',
            short_hash: 'cafe0002beef',
          }))
          history[history.length - 1]!.proposal_status = 'accepted'
          return route.fulfill({ json: history[1] })
        }
        if (url.endsWith('/reject')) {
          const body = route.request().postDataJSON() as { rationale?: string }
          history[history.length - 1]!.proposal_status = 'rejected'
          history[history.length - 1]!.rationale = body?.rationale ?? null
          return route.fulfill({ json: history[history.length - 1] })
        }
        if (url.endsWith('/rollback')) {
          const body = route.request().postDataJSON() as { message?: string }
          history.push(baseIteration({
            id: 'rb', revision: history.length + 1, parent_id: 'i1',
            message: body?.message ?? 'Rollback', short_hash: 'feed0003beef',
          }))
          return route.fulfill({ status: 201, json: history[history.length - 1] })
        }
        return route.fulfill({ status: 400, json: { detail: 'bad' } })
      })
    }

    test('OWNER-01 accepts a pending proposal onto main', async ({ page }) => {
      await mockApi(page, initialHistory())
      await page.goto(`${prefix}/workspace/ideas/idea-one`)
      await page.locator('[data-accept="p1"]').click()
      await expect(page.locator('.iteration-timeline').getByText('Mode hors ligne').first()).toBeVisible()
      await expect(page.locator('[data-line="main"]')).toHaveCount(2)
      await expect(page.locator('[data-line="branch"]').getByText(it.accepted)).toBeVisible()
    })

    test('OWNER-02 rejects with a visible rationale', async ({ page }) => {
      await mockApi(page, initialHistory())
      await page.goto(`${prefix}/workspace/ideas/idea-one`)
      await page.locator('[data-reject-toggle="p1"]').click()
      await page.getByPlaceholder(it.rationalePlaceholder).fill('Ce sera sur la ligne principale.')
      await page.locator('.iteration-reject-form button[type=submit]').click()
      await expect(page.locator('.iteration-timeline').getByText(it.rejected)).toBeVisible()
      await expect(page.getByText('Ce sera sur la ligne principale.')).toBeVisible()
    })

    test('OWNER-03 rolls back to an earlier iteration', async ({ page }) => {
      await mockApi(page, initialHistory())
      await page.goto(`${prefix}/workspace/ideas/idea-one`)
      await page.locator('[data-rollback="i1"]').click()
      await expect(page.locator('.iteration-timeline').getByText(it.rollbackMessage.replace('{hash}', 'deadbeef0001'))).toBeVisible()
    })
  })
}

test('MEMBER-04 never sees owner actions', async ({ page }) => {
  const history = initialHistory()
  await page.route(/\/api\/session$/, route => route.fulfill({ json: { signedIn: true, subject: 'member-two' } }))
  await page.route(/\/api\/ideas\/idea-one$/, route => route.fulfill({ json: idea }))
  await page.route(/\/api\/users\/owner-one$/, route => route.fulfill({ json: ownerProfile }))
  await page.route(/\/api\/ideas\/idea-one\/iterations(\/.*)?$/, route =>
    route.fulfill({ json: history }))
  await page.goto('/workspace/ideas/idea-one')
  await expect(page.locator('[data-accept]')).toHaveCount(0)
  await expect(page.locator('[data-rollback]')).toHaveCount(0)
})
