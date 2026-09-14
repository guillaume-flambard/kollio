import { expect, test } from '@playwright/test'
import type { IdeaResponse, JoinRequestResponse } from '@kollio/api-client'
import fr from '../../i18n/locales/fr.json' with { type: 'json' }
import en from '../../i18n/locales/en.json' with { type: 'json' }

function ideaFor(viewer: 'owner' | 'member'): IdeaResponse {
  const base: IdeaResponse = {
    id: 'idea-one', slug: 'une-idee', title: 'Une idée à explorer',
    pitch: 'Un contenu original conservé dans les deux langues.',
    stage: 'seed', lang: 'fr', created_at: '2026-09-01T10:00:00Z',
    owner_id: 'owner-one', workspace_id: 'workspace-one', visibility: 'workspace',
    collaborators: [
      { id: 'owner-one', display_name: 'Propriétaire', participation: 'owner', business_function: 'direction', roles: [], bio: null, avatar_key: 'lilac' },
    ],
    sought_roles: ['engineering'],
    join_requests: [],
  }
  if (viewer === 'member') {
    base.join_requests = [
      { id: 'join-2', idea_id: 'idea-one', requester_id: 'member-two', business_function: 'marketing',
        note: 'Ten years of growth.', status: 'pending', rationale: null,
        created_at: '2026-09-12T09:00:00Z' },
    ] as never
  }
  return base
}

const ownerRequests: JoinRequestResponse[] = [{
  id: 'join-1', idea_id: 'idea-one', requester_id: 'member-two', business_function: 'product',
  note: 'Je dessine les écrans.', status: 'pending', rationale: null,
  created_at: '2026-09-12T08:00:00Z',
}]

const colleagues = [
  { id: 'owner-one', display_name: 'Propriétaire', role: 'admin' },
  { id: 'member-two', display_name: 'Thomas', role: 'member' },
]

async function mockColleagues(page: import('@playwright/test').Page) {
  await page.route(/\/api\/workspaces\/workspace-one\/members$/, route => route.fulfill({ json: colleagues }))
}

for (const [locale, messages] of [['fr', fr], ['en', en]] as const) {
  test.describe(locale, () => {
    const prefix = locale === 'fr' ? '' : '/en'
    const team = messages.ideas.detail.team as Record<string, string>

    test('TEAM-01 shows the team with pending application to the owner', async ({ page }) => {
      await mockColleagues(page)
      await page.route(/\/api\/session$/, route => route.fulfill({ json: { signedIn: true, subject: 'owner-one' } }))
      await page.route(/\/api\/ideas\/idea-one$/, route => route.fulfill({
        json: { ...ideaFor('owner'), join_requests: ownerRequests } as unknown as IdeaResponse,
      }))
      await page.goto(`${prefix}/workspace/ideas/idea-one`)
      await expect(page.getByRole('heading', { name: team.title, exact: true })).toBeVisible()
      await expect(page.getByRole('button', { name: team.accept, exact: true }).first()).toBeEnabled()
      await expect(page.getByText(team.pending)).toBeVisible()
    })

    test('TEAM-07 lets the owner add a colleague directly', async ({ page }) => {
      let posted: Record<string, unknown> | null = null
      await page.route(/\/api\/session$/, route => route.fulfill({ json: { signedIn: true, subject: 'owner-one' } }))
      await page.route(/\/api\/ideas\/idea-one$/, route => route.fulfill({ json: ideaFor('owner') as unknown as IdeaResponse }))
      await mockColleagues(page)
      await page.route(/\/api\/ideas\/idea-one\/members$/, async route => {
        posted = route.request().postDataJSON() as Record<string, unknown>
        await route.fulfill({ status: 201, json: { id: 'member-two', display_name: 'Thomas', participation: 'decision_maker', business_function: 'sales', roles: [] } })
      })
      await page.goto(`${prefix}/workspace/ideas/idea-one`)
      await expect(page.getByRole('heading', { name: team.title, exact: true })).toBeVisible()
      await page.getByLabel(team.addTitle, { exact: true }).selectOption('member-two')
      await page.getByLabel(team.addParticipation, { exact: true }).selectOption('decision_maker')
      await page.getByLabel(team.addFunction, { exact: true }).selectOption('sales')
      await page.getByRole('button', { name: team.add, exact: true }).click()
      await expect(page.getByText(team.added)).toBeVisible()
      expect(posted).toEqual({ user_id: 'member-two', participation: 'decision_maker', function: 'sales' })
    })

    test('TEAM-08 hides the add form from a member', async ({ page }) => {
      await page.route(/\/api\/session$/, route => route.fulfill({ json: { signedIn: true, subject: 'member-nine' } }))
      await page.route(/\/api\/ideas\/idea-one$/, route => route.fulfill({ json: ideaFor('member') as unknown as IdeaResponse }))
      await page.goto(`${prefix}/workspace/ideas/idea-one`)
      await expect(page.getByRole('heading', { name: team.title, exact: true })).toBeVisible()
      await expect(page.getByLabel(team.addTitle, { exact: true })).toHaveCount(0)
    })

    test('TEAM-02 lets the owner reject with a rationale', async ({ page }) => {
      const ownerPending: JoinRequestResponse = { ...ownerRequests[0] }
      await page.route(/\/api\/session$/, route => route.fulfill({ json: { signedIn: true, subject: 'owner-one' } }))
      await page.route(/\/api\/ideas\/idea-one$/, route => route.fulfill({
        json: {
          ...ideaFor('owner'),
          join_requests: [ownerPending],
        } as unknown as IdeaResponse,
      }))
      await page.route(/\/api\/ideas\/idea-one\/join-requests\/join-1\/reject$/, async route => {
        ownerPending.status = 'rejected'
        ownerPending.rationale = 'Team full on design.'
        await route.fulfill({ json: ownerPending })
      })
      await page.goto(`${prefix}/workspace/ideas/idea-one`)
      await page.getByRole('button', { name: team.reject, exact: true }).click()
      await page.getByPlaceholder(team.rejectReason).fill('Team full on design.')
      await page.getByPlaceholder(team.rejectReason).press('Enter')
      await expect(page.getByText(/Team full on design/)).toBeVisible()
    })

    test('TEAM-03 lets a member apply to join', async ({ page }) => {
      await page.route(/\/api\/session$/, route => route.fulfill({ json: { signedIn: true, subject: 'member-two' } }))
      await page.route(/\/api\/ideas\/idea-one$/, route => route.fulfill({ json: ideaFor('member') as unknown as IdeaResponse }))
      await page.goto(`${prefix}/workspace/ideas/idea-one`)
      await expect(page.getByRole('heading', { name: team.membersTitle })).toBeVisible()
      await expect(page.getByText(team.pending)).toBeVisible()
    })
  })
}
