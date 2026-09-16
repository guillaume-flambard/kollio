import { expect, test } from '@playwright/test'
import type { CompanyContextResponse, ExperimentResponse, IdeaResponse, WorkspaceResponse } from '@kollio/api-client'
import en from '../../i18n/locales/en.json' with { type: 'json' }

// #78 responsive guard: the golden-path screens must hold at the widths a
// member actually uses (phone, tablet) with no horizontal overflow and the
// primary control reachable. Data is the minimal shape each screen needs.

const workspaces: WorkspaceResponse[] = [{ id: 'workspace-one', name: 'Faktus', role: 'member' }]

function idea(): IdeaResponse {
  return {
    id: 'idea-one', slug: 'une-idee', title: 'Une idée à explorer',
    pitch: 'Un contenu original conservé dans les deux langues. Voici une phrase assez longue pour pousser la largeur du texte et vérifier qu’elle ne déborde pas.',
    stage: 'seed', lang: 'fr', created_at: '2026-09-01T10:00:00Z',
    owner_id: 'owner-one', workspace_id: 'workspace-one', visibility: 'workspace',
    collaborators: [
      { id: 'owner-one', display_name: 'Propriétaire', participation: 'owner', business_function: 'direction', roles: [], bio: null, avatar_key: 'lilac' },
    ],
    sought_roles: [], join_requests: [],
  }
}

function experiments(): ExperimentResponse[] {
  return [{
    id: 'exp-1', idea_id: 'idea-one', title: 'Pilote Faktus',
    hypothesis: 'Les équipes adoptent le dépôt.', success_metric: 'Activation',
    baseline: '10', target: '40', status: 'running',
    started_at: null, ended_at: null, created_at: '2026-09-14T10:00:00Z',
  }]
}

function context(): CompanyContextResponse {
  return {
    profile: { name: 'Faktus', description: 'B2B marketing', business_model: null, products_services: null, customer_segments: null, markets: null, structure: null, lang: 'fr' },
    objectives: [{ id: 'obj-1', title: 'Cinq pilotes payants', state: 'active', priority: true, lang: 'fr' }],
    constraints: [{ id: 'con-1', title: 'Autofinancé, pas de recrutement terrain', detail: null, state: 'active', lang: 'fr' }],
    principles: [{ id: 'pri-1', title: 'Pas de croissance par la remise', detail: null, state: 'active', lang: 'fr' }],
    metrics: [{ id: 'met-1', name: 'Taux d’activation', value: '32', unit: '%', observed_at: null, source: null, state: 'active', lang: 'fr' }],
  }
}

async function expectNoHorizontalOverflow(page: import('@playwright/test').Page) {
  const overflow = await page.evaluate(() =>
    document.documentElement.scrollWidth - document.documentElement.clientWidth)
  expect(overflow).toBeLessThanOrEqual(1)
}

async function mockIdeaDetail(page: import('@playwright/test').Page) {
  await page.route(/\/api\/session$/, route => route.fulfill({ json: { signedIn: true, subject: 'owner-one' } }))
  await page.route(/\/api\/ideas\/idea-one$/, route => route.fulfill({ json: idea() }))
  await page.route(/\/api\/ideas\/idea-one\/iterations$/, route => route.fulfill({ json: [] }))
  await page.route(/\/api\/ideas\/idea-one\/experiments$/, route => route.fulfill({ json: experiments() }))
  await page.route(/\/api\/experiments\/exp-1$/, route => route.fulfill({
    json: { experiment: experiments()[0], outcomes: [], learning: null },
  }))
  await page.route(/\/api\/workspaces\/workspace-one\/members$/, route => route.fulfill({ json: [] }))
  await page.route(/\/api\/users\/owner-one$/, route => route.fulfill({
    json: { id: 'owner-one', display_name: 'Propriétaire', handle: 'owner', roles: [], bio: null, avatar_key: null, owned_ideas: [], memberships: [], contributions: [] },
  }))
}

for (const width of [375, 768]) {
  test.describe(`${width}px`, () => {
    test.use({ viewport: { width, height: 812 } })

    test(`RESP-${width} idea detail keeps experiments reachable with no overflow`, async ({ page }) => {
      await mockIdeaDetail(page)
      // Synchronise on the data response: on a cold dev server the first
      // navigation pays the whole compile cost before the panel can render.
      const experimentsLoaded = page.waitForResponse(r => r.url().includes('/api/ideas/idea-one/experiments'))
      await page.goto('/workspace/ideas/idea-one')
      await experimentsLoaded
      await expect(page.getByRole('heading', { name: 'Expériences', exact: true })).toBeVisible()
      await expect(page.locator('.experiment-row')).toHaveCount(1)
      await expectNoHorizontalOverflow(page)
    })

    test(`RESP-${width} onboarding wizard holds without overflow`, async ({ page }) => {
      await page.route(/\/api\/session$/, route => route.fulfill({ json: { signedIn: true, subject: 'owner-one' } }))
      await page.route(/\/api\/workspaces$/, route => route.fulfill({ json: workspaces }))
      await page.route(/\/api\/workspaces\/workspace-one\/company-context$/, route => route.fulfill({ json: context() }))
      await page.goto('/workspace/settings')
      await expect(page.getByRole('heading', { name: 'Amorcer le contexte de l’entreprise', exact: true })).toBeVisible()
      await expectNoHorizontalOverflow(page)
    })

    test(`RESP-${width} deposit form holds without overflow`, async ({ page }) => {
      await page.goto('/workspace/deposit')
      await expect(page.getByRole('heading', { name: 'Déposer une initiative', exact: true })).toBeVisible()
      await expectNoHorizontalOverflow(page)
    })
  })
}

test.describe('english deposit form', () => {
  test.use({ viewport: { width: 375, height: 812 } })

  test('RESP-deposit-en form holds without overflow', async ({ page }) => {
    await page.goto('/en/workspace/deposit')
    await expect(page.getByRole('heading', { name: en.ideas.deposit.title, exact: true })).toBeVisible()
    await expectNoHorizontalOverflow(page)
  })
})

test.describe('workspace navigation adapts', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/session', route => route.fulfill({ json: { signedIn: true, subject: 'member-two' } }))
    await page.route('**/api/workspaces', route => route.fulfill({ json: workspaces }))
    await page.route(/\/api\/workspaces\/workspace-one\/ideas(\?.*)?$/, route => route.fulfill({
      json: { items: [], total: 0, limit: 5, offset: 0 },
    }))
  })

  test('NAV-mobile exposes every destination from the top bar at 375px', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 })
    const listResponse = page.waitForResponse(r => r.url().includes('/api/workspaces/workspace-one/ideas'))
    await page.goto('/workspace')
    await listResponse
    await expect(page.locator('.workspace-rail')).toBeHidden()

    const menu = page.getByRole('button', { name: 'Ouvrir la navigation' })
    await expect(menu).toBeVisible()
    await menu.click()

    const dialog = page.getByRole('dialog', { name: 'Navigation principale' })
    await expect(dialog).toBeVisible()
    await expect(dialog.getByRole('link', { name: 'Initiatives' })).toBeVisible()
    await expect(dialog.getByRole('link', { name: 'Contexte entreprise' })).toBeVisible()
    await expect(dialog.locator('[aria-disabled="true"]')).toHaveCount(0)
    await expectNoHorizontalOverflow(page)
  })

  test('NAV-mobile filter strip fits without clipping at 375px', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 })
    const listResponse = page.waitForResponse(r => r.url().includes('/api/workspaces/workspace-one/ideas'))
    await page.goto('/workspace')
    await listResponse
    const rail = page.locator('.ideas-filter-rail')
    await expect(rail).toBeVisible()
    const clipped = await rail.evaluate(element => element.scrollWidth - element.clientWidth)
    expect(clipped).toBeLessThanOrEqual(1)
    await expect(page.getByRole('button', { name: /Équipe formée/ })).toBeVisible()
  })

  test('NAV-desktop keeps the persistent rail at 1440px', async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
    const listResponse = page.waitForResponse(r => r.url().includes('/api/workspaces/workspace-one/ideas'))
    await page.goto('/workspace')
    await listResponse
    await expect(page.locator('.workspace-rail')).toBeVisible()
    await expect(page.getByRole('button', { name: 'Ouvrir la navigation' })).toHaveCount(0)
  })
})

test.describe('narration on phone', () => {
  test.use({ viewport: { width: 375, height: 812 } })

  test('RESP-narration running analysis fits a phone width', async ({ page }) => {
    await page.route(/\/api\/workspaces$/, route => route.fulfill({ json: workspaces }))
    await page.route(/\/api\/workspaces\/workspace-one\/ideas$/, route => route.fulfill({
      status: 201, json: { ...idea(), id: 'idea-deposit-1', analysis: undefined },
    }))
    await page.route(/\/api\/ideas\/idea-deposit-1$/, route => route.fulfill({
      json: { ...idea(), id: 'idea-deposit-1', analysis: { state: 'running', progress: {
        profile: 'Faktus',
        objectives: ['Cinq pilotes', 'Activer vite', 'Une experience par semaine', 'Un autre but'],
        constraints: ['Pas de recrutement'], learnings: [], sources: [], areas: 5,
      } } },
    }))
    await page.goto('/workspace/deposit')
    await page.getByLabel('Titre de l’initiative').fill('Une idée')
    await page.getByLabel('Pitch').fill('Un contenu.')
    await page.getByRole('button', { name: 'Déposer l’initiative', exact: true }).click()
    await expect(page.getByText('Lecture du contexte de Faktus')).toBeVisible()
    await expectNoHorizontalOverflow(page)
  })
})
