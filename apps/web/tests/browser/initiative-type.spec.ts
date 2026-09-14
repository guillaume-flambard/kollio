import { expect, test } from '@playwright/test'
import type { IdeaResponse,IterationResponse, ProfileResponse, WorkspaceResponse } from '@kollio/api-client'
import fr from '../../i18n/locales/fr.json' with { type: 'json' }
import en from '../../i18n/locales/en.json' with { type: 'json' }

const workspaces: WorkspaceResponse[] = [{ id: 'workspace-one', name: 'Faktus', role: 'member' }]

const ownerProfile: ProfileResponse = {
  id: 'owner-one', display_name: 'Propriétaire', handle: 'owner', roles: ['dev'],
  bio: null, avatar_key: null, owned_ideas: [], memberships: [], contributions: [],
}

function idea(initiativeType: IdeaResponse['initiative_type']): IdeaResponse {
  return {
    id: 'idea-one', slug: 'une-initiative', title: 'Nouvelle campagne',
    pitch: 'Un contenu original conservé dans les deux langues.',
    stage: 'seed', initiative_type: initiativeType, lang: 'fr', created_at: '2026-09-01T10:00:00Z',
    owner_id: 'owner-one', workspace_id: 'workspace-one', visibility: 'workspace',
    collaborators: [], sought_roles: [], join_requests: [],
  }
}

const iterations: IterationResponse[] = [{
  id: 'i1', idea_id: 'idea-one', parent_id: null, author_id: 'owner-one',
  message: 'Dépôt initial', lang: 'fr',
  payload: { title: 'Nouvelle campagne', pitch: 'P', stage: 'seed' },
  branch: 'main', proposal_status: null, short_hash: 'deadbeef0001', revision: 1,
  created_at: '2026-09-01T10:00:00Z', analysis: null,
} as IterationResponse]

async function mockDetail(page: import('@playwright/test').Page, subject: string, initial: IdeaResponse['initiative_type']) {
  const state = { idea: idea(initial) }
  const patches: unknown[] = []
  await page.route(/\/api\/session$/, route => route.fulfill({ json: { signedIn: true, subject } }))
  await page.route(/\/api\/ideas\/idea-one$/, async (route) => {
    if (route.request().method() === 'PATCH') {
      const body = route.request().postDataJSON() as { initiative_type: IdeaResponse['initiative_type'] }
      patches.push(body)
      state.idea = { ...state.idea, initiative_type: body.initiative_type }
      return route.fulfill({ json: state.idea })
    }
    return route.fulfill({ json: state.idea })
  })
  await page.route(/\/api\/users\/owner-one$/, route => route.fulfill({ json: ownerProfile }))
  await page.route(/\/api\/ideas\/idea-one\/iterations$/, route => route.fulfill({ json: iterations }))
  return { state, patches }
}

for (const [locale, messages] of [['fr', fr], ['en', en]] as const) {
  test.describe(locale, () => {
    const prefix = locale === 'fr' ? '' : '/en'
    const labels = (messages.ideas as unknown as { initiativeType: Record<string, string> }).initiativeType
    const fieldLabel = (messages.ideas as unknown as { initiativeTypeLabel: string }).initiativeTypeLabel

    test('TYPE-01 deposits with the chosen initiative type', async ({ page }) => {
      const posts: unknown[] = []
      await page.route(/\/api\/session$/, route => route.fulfill({ json: { signedIn: true, subject: 'member-one' } }))
      await page.route(/\/api\/workspaces$/, route => route.fulfill({ json: workspaces }))
      await page.route(/\/api\/workspaces\/workspace-one\/ideas$/, (route) => {
        posts.push(route.request().postDataJSON())
        return route.fulfill({ status: 201, json: idea('campaign') })
      })
      await page.route(/\/api\/ideas\/idea-one$/, route => route.fulfill({ json: idea('campaign') }))

      await page.goto(`${prefix}/workspace/deposit`)
      await page.getByLabel(fieldLabel).selectOption('campaign')
      await page.getByLabel((messages.ideas.deposit as Record<string, string>).titleLabel).fill('Nouvelle campagne')
      await page.getByLabel((messages.ideas.deposit as Record<string, string>).pitchLabel).fill('Un pitch')
      await page.getByRole('button', { name: (messages.ideas.deposit as Record<string, string>).submit, exact: true }).click()

      await expect.poll(() => posts.length).toBeGreaterThan(0)
      expect(posts[0]).toMatchObject({ initiative_type: 'campaign' })
    })

    test('TYPE-02 the owner changes the type from the detail', async ({ page }) => {
      const { patches } = await mockDetail(page, 'owner-one', 'idea')
      await page.goto(`${prefix}/workspace/ideas/idea-one`)
      await page.getByLabel(fieldLabel).selectOption('pricing')
      await expect.poll(() => patches.length).toBeGreaterThan(0)
      expect(patches[0]).toMatchObject({ initiative_type: 'pricing' })
      await expect(page.getByLabel(fieldLabel)).toHaveValue('pricing')
    })

    test('TYPE-03 a non-owner sees the type without the selector', async ({ page }) => {
      await mockDetail(page, 'member-two', 'market')
      await page.goto(`${prefix}/workspace/ideas/idea-one`)
      await expect(page.getByText(labels.market!, { exact: true })).toBeVisible()
      await expect(page.getByLabel(fieldLabel)).toHaveCount(0)
    })
  })
}
