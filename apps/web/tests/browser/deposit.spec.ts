import { expect, test } from '@playwright/test'
import type { IdeaResponse } from '@kollio/api-client'
import fr from '../../i18n/locales/fr.json' with { type: 'json' }
import en from '../../i18n/locales/en.json' with { type: 'json' }

const workspaces = [{ id: 'workspace-one', name: 'Team', role: 'member' }]

function depositedIdea(lang: 'fr' | 'en'): IdeaResponse {
  return {
    id: 'idea-deposit-1', slug: `idee-deposee-${lang}`, title: 'Vélos en libre-service',
    pitch: 'Une flotte coopérative pour les trajets quotidiens.',
    stage: 'seed', lang, created_at: '2026-09-13T10:00:00Z',
    owner_id: 'member-one', workspace_id: 'workspace-one', visibility: 'workspace',
    collaborators: [],
  }
}

const resolved: IdeaResponse['analysis'] = {
  state: 'resolved',
  iteration_id: 'iteration-1',
  realism_score: 62,
  constraints: {
    concurrence: { score: 70, note: 'La marché montre des desks concurrents, l’opportunité demeure.' },
    cout: { score: 55, note: 'Le coût de flotte reste le premier poste, à aplatir par le mutualisé.' },
  },
  contradictions: [],
  locale: 'fr',
  model: 'test-model',
  created_at: '2026-09-13T10:01:00Z',
}

const explained = {
  ...resolved,
  constraints: {
    concurrence: {
      score: 70,
      note: 'La marché montre des desks concurrents, l’opportunité demeure.',
      basis: 'assumed',
      gap: null,
    },
    cout: {
      score: null,
      note: 'La flotte reste le premier poste de coût.',
      basis: 'unknown',
      gap: 'Aucun devis fournisseur.',
    },
  },
  contradictions: [
    {
      target: 'constraint',
      ref_id: 'constraint:2',
      detail: 'La remise casse la marge brute.',
    },
  ],
} as unknown as IdeaResponse['analysis']

async function mockIo(
  page: import('@playwright/test').Page,
  analysis: IdeaResponse['analysis'],
) {
  await page.route(/^http:\/\/127\.0\.0\.1:3197\/api\//, async (route) => {
    const url = new URL(route.request().url())
    if (url.pathname === '/api/workspaces') return route.fulfill({ json: workspaces })
    if (url.pathname === '/api/workspaces/workspace-one/ideas' && route.request().method() === 'POST') {
      const body = route.request().postDataJSON() as { lang?: 'fr' | 'en' }
      return route.fulfill({ status: 201, json: { ...depositedIdea(body.lang ?? 'fr'), analysis: undefined } })
    }
    if (url.pathname === '/api/ideas/idea-deposit-1') {
      return route.fulfill({ json: { ...depositedIdea('fr'), analysis } })
    }
    return route.fulfill({ status: 404, json: { statusCode: 404, message: 'Not found' } })
  })
}

for (const [locale, messages] of [['fr', fr], ['en', en]] as const) {
  test.describe(locale, () => {
    const prefix = locale === 'fr' ? '' : '/en'
    const deposit = messages.ideas.deposit as Record<string, string>

    test('DEPOSIT-01 goes from the explorer action to the form', async ({ page }) => {
      await mockIo(page, resolved)
      await page.goto(`${prefix}/workspace`)
      await page.getByRole('link', { name: new RegExp(messages.ideas.explorer.create) }).click()
      await expect(page).toHaveURL(new RegExp(`${prefix}/workspace/deposit$`))
      await expect(page.getByRole('heading', { name: deposit.title, exact: true })).toBeVisible()
    })

    test('DEPOSIT-02 submits and shows the resolved verdict with notes', async ({ page }) => {
      await mockIo(page, resolved)
      await page.goto(`${prefix}/workspace/deposit`)
      await page.getByLabel(deposit.titleLabel).fill('Vélos en libre-service')
      await page.getByLabel(deposit.pitchLabel).fill('Une flotte coopérative.')
      await page.getByRole('button', { name: deposit.submit, exact: true }).click()
      await expect(page.getByRole('heading', { name: deposit.resolvedTitle, exact: true })).toBeVisible()
      await expect(page.getByText('62', { exact: true })).toBeVisible()
      await expect(page.getByRole('link', { name: deposit.openIdea, exact: true })).toBeVisible()
    })

    test('DEPOSIT-05 explains the basis, the missing evidence and the contradictions', async ({ page }) => {
      const analysis = messages.ideas.analysis as {
        basis: Record<string, string>
        gapLine: string
        contradictionsTitle: string
        contradictionTarget: Record<string, string>
      }
      await mockIo(page, explained)
      await page.goto(`${prefix}/workspace/deposit`)
      await page.getByLabel(deposit.titleLabel).fill('Vélos en libre-service')
      await page.getByLabel(deposit.pitchLabel).fill('Une flotte coopérative.')
      await page.getByRole('button', { name: deposit.submit, exact: true }).click()
      await expect(page.getByText(analysis.basis.assumed, { exact: true })).toBeVisible()
      await expect(page.getByText(analysis.basis.unknown, { exact: true })).toBeVisible()
      await expect(page.getByText('Aucun devis fournisseur.')).toBeVisible()
      await expect(
        page.getByRole('heading', { name: analysis.contradictionsTitle, exact: true }),
      ).toBeVisible()
      await expect(page.getByText('La remise casse la marge brute.')).toBeVisible()
    })

    test('DEPOSIT-03 narrates the analysis while it runs, before the verdict', async ({ page }) => {
      const narration = (messages.ideas.deposit as unknown as { narration: Record<string, string> }).narration
      await mockIo(page, undefined)
      await page.goto(`${prefix}/workspace/deposit`)
      await page.getByLabel(deposit.titleLabel).fill('Vélos en libre-service')
      await page.getByLabel(deposit.pitchLabel).fill('Une flotte coopérative.')
      await page.getByRole('button', { name: deposit.submit, exact: true }).click()
      // The bare "running" line is replaced by a narrated build-up of what Kollio is doing.
      await expect(page.getByText(deposit.running)).toBeVisible()
      for (const label of [narration.context, narration.fit, narration.reuse, narration.weigh, narration.decide]) {
        await expect(page.getByText(label)).toBeVisible()
      }
      await expect(page.locator('.narration-step')).toHaveCount(5)
      await expect(page.locator('.narration-step[data-current="true"]')).toHaveCount(1)
      // No verdict yet.
      await expect(page.getByRole('heading', { name: deposit.resolvedTitle, exact: true })).toHaveCount(0)
    })

    test('DEPOSIT-04 shows the honest abstention without a fake score', async ({ page }) => {
      await mockIo(page, { state: 'abstained' })
      await page.goto(`${prefix}/workspace/deposit`)
      await page.getByLabel(deposit.titleLabel).fill('Vélos en libre-service')
      await page.getByLabel(deposit.pitchLabel).fill('Une flotte coopérative.')
      await page.getByRole('button', { name: deposit.submit, exact: true }).click()
      await expect(page.getByRole('heading', { name: deposit.abstainedTitle, exact: true })).toBeVisible()
      await expect(page.getByText('62', { exact: true })).toHaveCount(0)
    })
  })
}
