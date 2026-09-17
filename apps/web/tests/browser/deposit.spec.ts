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

const running: IdeaResponse['analysis'] = {
  state: 'running',
  iteration_id: null,
  realism_score: null,
  constraints: {},
  contradictions: [],
  locale: null,
  model: null,
  created_at: null,
  progress: {
    profile: 'Faktus',
    objectives: [
      'Signer cinq pilotes payants',
      'Passer sous un jour pour le premier apprentissage',
      'Une experience par equipe et par semaine',
      'Un quatrieme objectif',
    ],
    constraints: ['Autofinance, pas de recrutement terrain', 'Equipe produit de deux personnes'],
    learnings: [{ id: 'learning:1', text: 'La refonte tarifaire a gagne 12% d’essais mais pas de conversion payante.' }],
    sources: [{ id: 'ev-1', url: 'kollio://evidence/ev-1', snippet: '18 des 40 sessions visuelles se sont terminees hors ligne.' }],
    areas: 5,
  },
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
      await page.goto(`${prefix}/workspace/ideas`)
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

    test('DEPOSIT-03 narrates the real inputs the running analysis is weighing', async ({ page }) => {
      const narration = (messages.ideas.deposit as unknown as { narration: Record<string, string> }).narration
      const more = narration.more.replace('{count}', '1')
      await mockIo(page, running)
      await page.goto(`${prefix}/workspace/deposit`)
      await page.getByLabel(deposit.titleLabel).fill('Vélos en libre-service')
      await page.getByLabel(deposit.pitchLabel).fill('Une flotte coopérative.')
      await page.getByRole('button', { name: deposit.submit, exact: true }).click()

      // Real company facts, not generic stage names.
      await expect(page.getByText('Faktus')).toBeVisible()
      await expect(page.getByText('Signer cinq pilotes payants')).toBeVisible()
      await expect(page.getByText('Autofinance, pas de recrutement terrain')).toBeVisible()
      await expect(page.getByText(/refonte tarifaire/)).toBeVisible()
      await expect(page.getByText(/sessions visuelles/)).toBeVisible()
      // Objectives are capped, the overflow is counted honestly.
      await expect(page.getByText('Un quatrieme objectif')).toHaveCount(0)
      await expect(page.getByText(more)).toBeVisible()
      // Seven real groups (context, objectives, constraints, learnings, sources, areas, deciding).
      await expect(page.locator('.narration-group')).toHaveCount(7)
      await expect(page.locator('.narration-group[data-current="true"]')).toHaveCount(1)
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

    test('DEPOSIT-06 surfaces a terminal timeout with a retry action', async ({ page }) => {
      await mockIo(page, running)
      await page.goto(`${prefix}/workspace/deposit`)
      await page.getByLabel(deposit.titleLabel).fill('Vélos en libre-service')
      await page.getByLabel(deposit.pitchLabel).fill('Une flotte coopérative.')
      await page.getByRole('button', { name: deposit.submit, exact: true }).click()
      await expect(page.getByRole('heading', { name: deposit.timeoutTitle, exact: true })).toBeVisible({ timeout: 20_000 })
      await expect(page.getByText(deposit.timeoutBody)).toBeVisible()
      await page.getByRole('button', { name: deposit.timeoutRetry, exact: true }).click()
      await expect(page.getByRole('heading', { name: deposit.timeoutTitle, exact: true })).toHaveCount(0)
      await expect(page.locator('.narration-group')).toHaveCount(7)
    })
  })
}
