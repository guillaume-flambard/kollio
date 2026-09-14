import { expect, test } from '@playwright/test'
import type { ExperimentResponse, IdeaResponse, LearningResponse, OutcomeResponse } from '@kollio/api-client'
import fr from '../../i18n/locales/fr.json' with { type: 'json' }
import en from '../../i18n/locales/en.json' with { type: 'json' }

function ideaFor(): IdeaResponse {
  return {
    id: 'idea-one', slug: 'une-idee', title: 'Une idée à explorer',
    pitch: 'Un contenu original conservé dans les deux langues.',
    stage: 'seed', lang: 'fr', created_at: '2026-09-01T10:00:00Z',
    owner_id: 'owner-one', workspace_id: 'workspace-one', visibility: 'workspace',
    collaborators: [
      { id: 'owner-one', display_name: 'Propriétaire', participation: 'owner', business_function: 'direction', roles: [], bio: null, avatar_key: 'lilac' },
    ],
    sought_roles: [],
    join_requests: [],
  }
}

function experimentFor(status: string): ExperimentResponse {
  return {
    id: 'exp-1', idea_id: 'idea-one', title: 'Pilote Faktus',
    hypothesis: 'Les équipes adoptent le dépôt.', success_metric: 'Activation',
    baseline: '10', target: '40', status,
    started_at: null, ended_at: null, created_at: '2026-09-14T10:00:00Z',
  }
}

function learningDraft(text = 'Hypothesis: Les équipes adoptent le dépôt.'): LearningResponse {
  return {
    id: 'learning-1', experiment_id: 'exp-1', idea_id: 'idea-one', status: 'draft',
    text, outcome_ids: [], confirmed_by_id: null,
    created_at: '2026-09-14T10:00:00Z', updated_at: '2026-09-14T10:00:00Z',
  }
}

function outcomeFor(): OutcomeResponse {
  return {
    id: 'out-1', experiment_id: 'exp-1', metric: 'Activation', value: '25', unit: '%',
    observed_at: null, comment: null, qualitative: null, created_at: '2026-09-14T11:00:00Z',
  }
}

interface LoopState {
  experiments: ExperimentResponse[]
  outcomes: OutcomeResponse[]
  learning: LearningResponse | null
  posted: Record<string, unknown> | null
}

async function mockLoop(
  page: import('@playwright/test').Page,
  options: { subject?: string, experiments?: ExperimentResponse[], outcomes?: OutcomeResponse[], learning?: LearningResponse | null, ruleOnStatus?: boolean, listFails?: boolean } = {},
): Promise<LoopState> {
  const state: LoopState = {
    experiments: options.experiments ?? [],
    outcomes: options.outcomes ?? [],
    learning: options.learning ?? null,
    posted: null,
  }
  await page.route(/\/api\/session$/, route => route.fulfill({ json: { signedIn: true, subject: options.subject ?? 'owner-one' } }))
  await page.route(/\/api\/ideas\/idea-one$/, route => route.fulfill({ json: ideaFor() as unknown as IdeaResponse }))
  await page.route(/\/api\/ideas\/idea-one\/iterations$/, route => route.fulfill({ json: [] }))
  await page.route(/\/api\/workspaces\/workspace-one\/members$/, route => route.fulfill({ json: [] }))
  await page.route(/\/api\/ideas\/idea-one\/experiments$/, async (route) => {
    if (route.request().method() === 'POST') {
      state.posted = route.request().postDataJSON() as Record<string, unknown>
      const created = { ...experimentFor('proposed'), id: 'exp-new', title: String(state.posted.title) }
      state.experiments = [...state.experiments, created]
      await route.fulfill({ status: 201, json: created })
      return
    }
    if (options.listFails) {
      await route.fulfill({ status: 500, json: { detail: 'boom' } })
      return
    }
    await route.fulfill({ json: state.experiments })
  })
  await page.route(/\/api\/experiments\/[^/]+\/status$/, async (route) => {
    state.posted = route.request().postDataJSON() as Record<string, unknown>
    if (options.ruleOnStatus) {
      await route.fulfill({ status: 422, json: { detail: { code: 'experiment_rule', message: 'Cannot move an experiment' } } })
      return
    }
    const target = String(state.posted.status)
    state.experiments = state.experiments.map(experiment => ({ ...experiment, status: target }))
    if (target === 'completed') state.learning = learningDraft()
    await route.fulfill({ json: state.experiments[0] })
  })
  await page.route(/\/api\/experiments\/[^/]+\/outcomes$/, async (route) => {
    state.posted = route.request().postDataJSON() as Record<string, unknown>
    const recorded = outcomeFor()
    state.outcomes = [...state.outcomes, recorded]
    await route.fulfill({ status: 201, json: recorded })
  })
  await page.route(/\/api\/experiments\/[^/]+\/learnings$/, async (route) => {
    state.posted = route.request().postDataJSON() as Record<string, unknown>
    state.learning = { ...learningDraft(String(state.posted.text)), status: 'confirmed', confirmed_by_id: options.subject ?? 'owner-one' }
    await route.fulfill({ json: state.learning })
  })
  await page.route(/\/api\/experiments\/[^/]+$/, route => route.fulfill({
    json: { experiment: state.experiments[0], outcomes: state.outcomes, learning: state.learning },
  }))
  return state
}

for (const [locale, messages] of [['fr', fr], ['en', en]] as const) {
  test.describe(locale, () => {
    const prefix = locale === 'fr' ? '' : '/en'
    const labels = messages.ideas.experiments as unknown as {
      title: string
      empty: string
      newAction: string
      loadError: string
      retry: string
      ruleError: string
      status: Record<string, string>
      create: Record<string, string>
      actions: Record<string, string>
      outcomes: Record<string, string>
      learning: Record<string, string>
    }

    test('EXPERIMENT-01 shows the empty state to a member', async ({ page }) => {
      await mockLoop(page)
      await page.goto(`${prefix}/workspace/ideas/idea-one`)
      await expect(page.getByRole('heading', { name: labels.title, exact: true })).toBeVisible({ timeout: 15_000 })
      await expect(page.getByText(labels.empty)).toBeVisible()
      await expect(page.getByRole('button', { name: labels.newAction, exact: true })).toBeVisible()
    })

    test('EXPERIMENT-02 creates an experiment', async ({ page }) => {
      const state = await mockLoop(page)
      await page.goto(`${prefix}/workspace/ideas/idea-one`)
      await page.getByRole('button', { name: labels.newAction, exact: true }).click()
      await page.getByLabel(labels.create.name, { exact: true }).fill('Pilote Faktus')
      await page.getByLabel(labels.create.hypothesis, { exact: true }).fill('Les équipes adoptent le dépôt.')
      await page.getByLabel(labels.create.metric, { exact: true }).fill('Activation')
      await page.getByLabel(labels.create.baseline, { exact: true }).fill('10')
      await page.getByLabel(labels.create.target, { exact: true }).fill('40')
      await page.getByRole('button', { name: labels.create.submit, exact: true }).click()
      await expect(page.locator('.experiment-row')).toHaveAttribute('data-status', 'proposed')
      expect(state.posted).toEqual({
        title: 'Pilote Faktus',
        hypothesis: 'Les équipes adoptent le dépôt.',
        success_metric: 'Activation',
        baseline: '10',
        target: '40',
      })
    })

    test('EXPERIMENT-03 launches a proposed experiment', async ({ page }) => {
      const state = await mockLoop(page, { experiments: [experimentFor('proposed')] })
      await page.goto(`${prefix}/workspace/ideas/idea-one`)
      await page.getByRole('button', { name: labels.actions.start, exact: true }).click()
      await expect(page.locator('.experiment-detail')).toHaveAttribute('data-status', 'running')
      expect(state.posted).toEqual({ status: 'running' })
    })

    test('EXPERIMENT-04 records a result', async ({ page }) => {
      const state = await mockLoop(page, { experiments: [experimentFor('running')] })
      await page.goto(`${prefix}/workspace/ideas/idea-one`)
      await page.getByLabel(labels.outcomes.metric, { exact: true }).fill('Activation')
      await page.getByLabel(labels.outcomes.value, { exact: true }).fill('25')
      await page.getByLabel(labels.outcomes.unit, { exact: true }).fill('%')
      await page.getByRole('button', { name: labels.outcomes.add, exact: true }).click()
      await expect(page.getByText('Activation 25 %')).toBeVisible()
      expect(state.posted).toEqual({
        metric: 'Activation',
        value: '25',
        unit: '%',
        observed_at: null,
        comment: null,
        qualitative: null,
      })
    })

    test('EXPERIMENT-05 completes an experiment and drafts a learning', async ({ page }) => {
      const state = await mockLoop(page, { experiments: [experimentFor('running')] })
      await page.goto(`${prefix}/workspace/ideas/idea-one`)
      await page.getByRole('button', { name: labels.actions.complete, exact: true }).click()
      await expect(page.locator('.experiment-detail')).toHaveAttribute('data-status', 'completed')
      await expect(page.getByLabel(labels.learning.title, { exact: true })).toBeVisible()
      expect(state.posted).toEqual({ status: 'completed' })
    })

    test('EXPERIMENT-06 confirms the learning', async ({ page }) => {
      const state = await mockLoop(page, {
        experiments: [experimentFor('completed')],
        learning: learningDraft(),
      })
      await page.goto(`${prefix}/workspace/ideas/idea-one`)
      await page.getByLabel(labels.learning.title, { exact: true }).fill('Les équipes adoptent le dépôt, une fois sur deux.')
      await page.getByRole('button', { name: labels.learning.confirm, exact: true }).click()
      await expect(page.locator('.experiment-learning .experiment-status')).toHaveAttribute('data-status', 'confirmed')
      expect(state.posted).toEqual({ text: 'Les équipes adoptent le dépôt, une fois sur deux.', confirm: true })
    })

    test('EXPERIMENT-07 hides every write form from a non-member', async ({ page }) => {
      await mockLoop(page, {
        subject: 'member-nine',
        experiments: [experimentFor('running')],
        outcomes: [outcomeFor()],
        learning: { ...learningDraft('Ce que nous avons appris.'), status: 'confirmed' },
      })
      await page.goto(`${prefix}/workspace/ideas/idea-one`)
      await expect(page.locator('.experiment-row')).toHaveAttribute('data-status', 'running')
      await expect(page.getByText('Ce que nous avons appris.')).toBeVisible()
      await expect(page.getByRole('button', { name: labels.newAction, exact: true })).toHaveCount(0)
      await expect(page.getByLabel(labels.outcomes.metric, { exact: true })).toHaveCount(0)
      await expect(page.getByRole('button', { name: labels.learning.confirm, exact: true })).toHaveCount(0)
    })

    test('EXPERIMENT-08 explains a refused action in the locale', async ({ page }) => {
      await mockLoop(page, { experiments: [experimentFor('proposed')], ruleOnStatus: true })
      await page.goto(`${prefix}/workspace/ideas/idea-one`)
      await page.getByRole('button', { name: labels.actions.start, exact: true }).click()
      await expect(page.getByRole('alert').filter({ hasText: labels.ruleError })).toBeVisible()
    })

    test('EXPERIMENT-09 offers a retry when the list fails', async ({ page }) => {
      await mockLoop(page, { listFails: true })
      await page.goto(`${prefix}/workspace/ideas/idea-one`)
      await expect(page.getByText(labels.loadError)).toBeVisible()
      await expect(page.getByRole('button', { name: labels.retry, exact: true })).toBeVisible()
    })
  })
}
