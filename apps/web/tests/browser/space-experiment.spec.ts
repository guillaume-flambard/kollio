import { expect, test } from '@playwright/test'
import type { Page } from '@playwright/test'
import type {
  ExperimentDetailResponse,
  ExperimentResponse,
  IdeaPageResponse,
  LearningResponse,
  OutcomeResponse,
  ScenarioRunResponse,
  ScenarioVariableResponse,
  SensitivityResponse,
  WorkspaceMemberResponse,
  WorkspaceResponse,
} from '@kollio/api-client'
import fr from '../../i18n/locales/fr.json' with { type: 'json' }
import en from '../../i18n/locales/en.json' with { type: 'json' }

const workspaces: WorkspaceResponse[] = [{ id: 'workspace-one', name: 'Team', role: 'member' }]

const members: WorkspaceMemberResponse[] = [
  { id: 'owner-one', display_name: 'Camille', role: 'member' },
  { id: 'participant-one', display_name: 'Sam', role: 'member' },
]

const base = '/api/workspaces/workspace-one/decision-spaces/space-one'

function makeSpace(overrides: Record<string, unknown> = {}) {
  return {
    id: 'space-one',
    workspace_id: 'workspace-one',
    question: 'Which pricing should we pick?',
    description: null,
    owner_id: 'owner-one',
    status: 'TESTING',
    deadline: '2026-10-01',
    lang: 'en',
    created_at: '2026-09-17T09:00:00Z',
    updated_at: '2026-09-17T09:00:00Z',
    ...overrides,
  }
}

function makeSpaceDetail(overrides: Record<string, unknown> = {}) {
  return {
    ...makeSpace(overrides),
    participants: [
      { user_id: 'owner-one', created_at: '2026-09-17T09:00:00Z' },
      { user_id: 'participant-one', created_at: '2026-09-17T09:00:00Z' },
    ],
    history: [],
  }
}

function makeOption(overrides: Record<string, unknown> = {}) {
  return {
    id: 'option-one',
    space_id: 'space-one',
    title: 'Raise the entry price',
    proposal: 'Raise the entry price by 20%.',
    mechanism: null,
    upside: null,
    cost: null,
    risks: null,
    critical_assumptions: null,
    success_metrics: null,
    created_by: 'owner-one',
    lang: 'en',
    created_at: '2026-09-17T09:00:00Z',
    updated_at: '2026-09-17T09:00:00Z',
    ...overrides,
  }
}

function makeVariable(
  overrides: Partial<ScenarioVariableResponse> = {},
): ScenarioVariableResponse {
  return {
    id: 'variable-churn',
    space_id: 'space-one',
    name: 'Churn rate',
    unit: '%',
    low: '5',
    base: '10',
    high: '20',
    lang: 'en',
    created_at: '2026-09-17T09:00:00Z',
    updated_at: '2026-09-17T09:00:00Z',
    ...overrides,
  } as ScenarioVariableResponse
}

function makeRun(overrides: Partial<ScenarioRunResponse> = {}): ScenarioRunResponse {
  return {
    id: 'run-one',
    option_id: 'option-one',
    level: 'base',
    assumptions: 'The September spend holds.',
    created_by: 'owner-one',
    lang: 'en',
    created_at: '2026-09-17T09:00:00Z',
    updated_at: '2026-09-17T09:00:00Z',
    values: [{ variable_id: 'variable-churn', value: '10' }],
    ...overrides,
  } as ScenarioRunResponse
}

function makeExperiment(overrides: Partial<ExperimentResponse> = {}): ExperimentResponse {
  return {
    id: 'experiment-one',
    idea_id: 'idea-one',
    decision_space_id: 'space-one',
    option_id: 'option-one',
    title: 'Test the 20% raise',
    hypothesis: 'Churn stays flat at the higher price.',
    success_metric: 'Churn rate',
    baseline: '10',
    target: '12',
    status: 'proposed',
    started_at: null,
    ended_at: null,
    created_at: '2026-09-17T09:00:00Z',
    ...overrides,
  } as ExperimentResponse
}

function makeOutcome(overrides: Partial<OutcomeResponse> = {}): OutcomeResponse {
  return {
    id: 'outcome-one',
    experiment_id: 'experiment-one',
    metric: 'Churn rate',
    value: '11',
    unit: '%',
    observed_at: '2026-09-24',
    comment: 'Held for a week.',
    qualitative: null,
    created_at: '2026-09-24T09:00:00Z',
    ...overrides,
  } as OutcomeResponse
}

function makeLearning(overrides: Partial<LearningResponse> = {}): LearningResponse {
  return {
    id: 'learning-one',
    experiment_id: 'experiment-one',
    idea_id: 'idea-one',
    status: 'draft',
    text: 'Churn did not follow the price.',
    outcome_ids: [],
    confirmed_by_id: null,
    created_at: '2026-09-24T09:00:00Z',
    updated_at: '2026-09-24T09:00:00Z',
    ...overrides,
  } as LearningResponse
}

function makeSensitivity(overrides: Partial<SensitivityResponse> = {}): SensitivityResponse {
  return {
    criterion: { metric_variable_id: 'variable-churn', direction: 'above', threshold: '100' },
    ranked: [],
    incomplete_run_ids: [],
    evidence: { for_count: 0, against_count: 0 },
    ...overrides,
  } as SensitivityResponse
}

function makeIdeas(): IdeaPageResponse {
  return {
    items: [
      {
        id: 'idea-one',
        title: 'Pricing v2',
        initiative_type: 'growth',
        lang: 'en',
        created_at: '2026-09-17T09:00:00Z',
      },
    ],
    limit: 100,
    offset: 0,
    total: 1,
  } as IdeaPageResponse
}

type State = {
  options: Array<Record<string, unknown>>
  variables: ScenarioVariableResponse[]
  runs: ScenarioRunResponse[]
  sensitivity: SensitivityResponse
  ideas: IdeaPageResponse
  experiments: ExperimentResponse[]
  outcomes: Record<string, OutcomeResponse[]>
  learnings: Record<string, LearningResponse | null>
  failOptions: boolean
  forbidStatus: boolean
}

function emptyState(overrides: Partial<State> = {}): State {
  return {
    options: [makeOption()],
    variables: [makeVariable()],
    runs: [],
    sensitivity: makeSensitivity(),
    ideas: makeIdeas(),
    experiments: [],
    outcomes: {},
    learnings: {},
    failOptions: false,
    forbidStatus: false,
    ...overrides,
  }
}

function detailFor(state: State, experiment: ExperimentResponse): ExperimentDetailResponse {
  return {
    experiment,
    outcomes: state.outcomes[experiment.id] ?? [],
    learning: state.learnings[experiment.id] ?? null,
  } as ExperimentDetailResponse
}

async function serveExperiment(page: Page, state: State) {
  await page.route(`${base}/options`, route =>
    state.failOptions
      ? route.fulfill({ status: 500, json: { statusCode: 500, message: 'Boom' } })
      : route.fulfill({ json: { items: state.options } }),
  )

  await page.route(`${base}/scenario-variables`, async route => {
    if (route.request().method() === 'POST') {
      const body = route.request().postDataJSON() as Record<string, unknown>
      const created = makeVariable({
        id: `variable-${state.variables.length + 1}`,
        name: String(body.name),
        unit: body.unit === null ? null : String(body.unit),
        low: String(body.low),
        base: String(body.base),
        high: String(body.high),
      })
      state.variables.push(created)
      await route.fulfill({ status: 201, json: created })
      return
    }
    await route.fulfill({ json: { items: state.variables } })
  })

  await page.route(`${base}/scenario-variables/*`, async route => {
    const variableId = new URL(route.request().url()).pathname.split('/').pop() as string
    if (route.request().method() === 'PATCH') {
      const body = route.request().postDataJSON() as Record<string, unknown>
      const variable = state.variables.find(item => item.id === variableId)
      if (variable) {
        variable.name = String(body.name)
        variable.low = String(body.low)
        variable.base = String(body.base)
        variable.high = String(body.high)
      }
      await route.fulfill({ json: variable ?? makeVariable() })
      return
    }
    state.variables = state.variables.filter(item => item.id !== variableId)
      await route.fulfill({ status: 204 })
  })

  await page.route(`${base}/options/option-one/scenario-runs`, async route => {
    if (route.request().method() === 'POST') {
      const body = route.request().postDataJSON() as Record<string, unknown>
      const created = makeRun({
        id: `run-${state.runs.length + 1}`,
        level: String(body.level) as ScenarioRunResponse['level'],
        assumptions: String(body.assumptions),
        values: (body.values ?? []) as ScenarioRunResponse['values'],
      })
      state.runs.push(created)
      await route.fulfill({ status: 201, json: created })
      return
    }
    await route.fulfill({ json: { items: state.runs } })
  })

  await page.route(`${base}/options/option-one/scenario-runs/*`, async route => {
    const runId = new URL(route.request().url()).pathname.split('/').pop() as string
    state.runs = state.runs.filter(item => item.id !== runId)
      await route.fulfill({ status: 204 })
  })

  await page.route(/\/space-one\/options\/option-one\/sensitivity(\?|$)/, route =>
    route.fulfill({ json: state.sensitivity }),
  )

  await page.route(`${base}/experiments`, async route => {
    if (route.request().method() === 'POST') {
      const body = route.request().postDataJSON() as Record<string, unknown>
      const created = makeExperiment({
        id: `experiment-${state.experiments.length + 1}`,
        idea_id: String(body.idea_id),
        option_id: body.option_id === null ? null : String(body.option_id),
        title: String(body.title),
        hypothesis: String(body.hypothesis),
        success_metric: String(body.success_metric),
        baseline: body.baseline === null ? null : String(body.baseline),
        target: body.target === null ? null : String(body.target),
      })
      state.experiments.push(created)
      await route.fulfill({ status: 201, json: created })
      return
    }
    await route.fulfill({ json: state.experiments })
  })

  await page.route('**/api/experiments/*/status', async route => {
    if (state.forbidStatus) {
      await route.fulfill({ status: 403, json: { statusCode: 403, message: 'Forbidden' } })
      return
    }
    const experimentId = new URL(route.request().url()).pathname.split('/').slice(-2, -1)[0]
    const body = route.request().postDataJSON() as Record<string, unknown>
    const target = String(body.status)
    const experiment = state.experiments.find(item => item.id === experimentId)
    if (experiment) {
      experiment.status = target
      if (target === 'running') {
        experiment.started_at = '2026-09-20T09:00:00Z'
      }
      if (target === 'completed' || target === 'cancelled') {
        experiment.ended_at = '2026-09-24T09:00:00Z'
      }
      if (target === 'completed') {
        state.learnings[experiment.id] = makeLearning()
      }
    }
    await route.fulfill({ json: experiment ?? makeExperiment() })
  })

  await page.route('**/api/experiments/*/outcomes', async route => {
    const experimentId = new URL(route.request().url()).pathname.split('/').slice(-2, -1)[0]
    const body = route.request().postDataJSON() as Record<string, unknown>
    const created = makeOutcome({
      experiment_id: experimentId,
      metric: String(body.metric),
      value: String(body.value),
      unit: body.unit === null ? null : String(body.unit),
      observed_at: body.observed_at === null ? null : String(body.observed_at),
      comment: body.comment === null ? null : String(body.comment),
    })
    state.outcomes[experimentId] = [...(state.outcomes[experimentId] ?? []), created]
    await route.fulfill({ status: 201, json: created })
  })

  await page.route('**/api/experiments/*', async route => {
    const experimentId = new URL(route.request().url()).pathname.split('/').pop() as string
    const experiment = state.experiments.find(item => item.id === experimentId)
    await route.fulfill({ json: experiment ? detailFor(state, experiment) : detailFor(state, makeExperiment()) })
  })

  await page.route(/\/api\/workspaces\/workspace-one\/ideas(\?|$)/, route =>
    route.fulfill({ json: state.ideas }),
  )
}

for (const [locale, messages] of [
  ['fr', fr],
  ['en', en],
] as const) {
  test.describe(locale, () => {
    const prefix = locale === 'fr' ? '' : '/en'
    const copy = messages.decisionSpaces.experiment
    const section = messages.decisionSpaces.section.experiment

    async function openExperiment(page: Page) {
      await page.goto(
        `${prefix}/workspace/decision-spaces/space-one/experiment?workspace=workspace-one`,
      )
      await expect(page.locator('section.experiment > h2')).toHaveText(section.title)
    }

    function blocks(page: Page) {
      return page.locator('.experiment-block')
    }

    function plural(template: string, count: number) {
      const forms = template.split(' | ')
      const form = count === 1 ? forms[0] : forms[forms.length - 1]
      return form.replace('{count}', String(count))
    }

    function variableForm(page: Page) {
      return blocks(page).nth(0).locator('.experiment-form')
    }

    function runForm(page: Page) {
      return blocks(page).nth(1).locator('.experiment-form')
    }

    function experimentForm(page: Page) {
      return blocks(page).nth(3).locator('.experiment-form')
    }

    test.beforeEach(async ({ page }) => {
      await page.route('**/api/session', route =>
        route.fulfill({ json: { signedIn: true, subject: 'member-two' } }),
      )
      await page.route('**/api/workspaces', route => route.fulfill({ json: workspaces }))
      await page.route('**/api/workspaces/workspace-one/members', route =>
        route.fulfill({ json: members }),
      )
      await page.route('**/api/workspaces/workspace-one/decision-spaces/*', route =>
        route.fulfill({ json: makeSpaceDetail() }),
      )
    })

    test('EXPERIMENT-01 frames the section and says there is nothing to try yet', async ({
      page,
    }) => {
      await serveExperiment(page, emptyState({ options: [] }))
      await openExperiment(page)

      await expect(page.locator('.experiment-intro')).toHaveText(section.body)
      await expect(page.locator('.experiment-empty-state h3')).toHaveText(copy.empty.title)
      await expect(page.locator('.experiment-empty-state p')).toHaveText(copy.empty.body)
      await expect(blocks(page)).toHaveCount(0)
    })

    test('EXPERIMENT-02 lists the declared ranges and says what is still empty', async ({
      page,
    }) => {
      await serveExperiment(
        page,
        emptyState({
          variables: [
            makeVariable(),
            makeVariable({ id: 'variable-price', name: 'Price', unit: '€', low: '80', base: '100', high: '140' }),
          ],
        }),
      )
      await openExperiment(page)

      const listed = page.locator('.variable-list .variable')
      await expect(listed).toHaveCount(2)
      await expect(listed.first().locator('.variable-range')).toHaveText(
        copy.variables.range.replace('{low}', '5').replace('{high}', '20'),
      )
      await expect(listed.first().locator('.variable-base')).toHaveText(
        copy.variables.base.replace('{value}', '10'),
      )
      await expect(blocks(page).nth(1).locator('.experiment-empty')).toHaveText(copy.runs.empty)
      await expect(blocks(page).nth(2).locator('.experiment-empty')).toHaveText(
        copy.sensitivity.empty,
      )
      await expect(blocks(page).nth(3).locator('.experiment-empty')).toHaveText(
        copy.experiments.empty,
      )
    })

    test('EXPERIMENT-03 adds a range', async ({ page }) => {
      const posted: Array<Record<string, unknown>> = []
      page.on('request', request => {
        if (request.method() === 'POST' && request.url().endsWith('/scenario-variables')) {
          posted.push(request.postDataJSON() as Record<string, unknown>)
        }
      })
      await serveExperiment(page, emptyState())
      await openExperiment(page)

      await page
        .getByRole('button', { name: copy.variables.create, exact: true })
        .click()
      const fields = variableForm(page).locator('input[type="text"]')
      await fields.nth(0).fill('Average basket')
      await fields.nth(1).fill('€')
      await fields.nth(2).fill('30')
      await fields.nth(3).fill('50')
      await fields.nth(4).fill('70')
      await page
        .getByRole('button', { name: copy.variables.form.submit, exact: true })
        .click()

      await expect.poll(() => posted.length).toBe(1)
      expect(posted[0]).toMatchObject({
        name: 'Average basket',
        unit: '€',
        low: 30,
        base: 50,
        high: 70,
      })
      await expect(page.locator('.variable-list .variable')).toHaveCount(2)
      await expect(page.locator('.variable-list .variable').nth(1)).toContainText('Average basket')
    })

    test('EXPERIMENT-04 edits a range', async ({ page }) => {
      const patched: Array<Record<string, unknown>> = []
      page.on('request', request => {
        if (request.method() === 'PATCH') {
          patched.push(request.postDataJSON() as Record<string, unknown>)
        }
      })
      await serveExperiment(page, emptyState())
      await openExperiment(page)

      await page
        .locator('.variable-list .variable')
        .first()
        .locator('.variable-actions button')
        .first()
        .click()
      const fields = variableForm(page).locator('input[type="text"]')
      await fields.nth(0).fill('Churn rate')
      await fields.nth(2).fill('4')
      await fields.nth(3).fill('9')
      await fields.nth(4).fill('18')
      await page.getByRole('button', { name: copy.variables.form.save, exact: true }).click()

      await expect.poll(() => patched.length).toBe(1)
      expect(patched[0]).toMatchObject({ name: 'Churn rate', low: 4, base: 9, high: 18 })
      await expect(page.locator('.variable-list .variable').first().locator('.variable-range')).toHaveText(
        copy.variables.range.replace('{low}', '4').replace('{high}', '18'),
      )
    })

    test('EXPERIMENT-05 deletes a range', async ({ page }) => {
      const deleted: string[] = []
      page.on('request', request => {
        if (request.method() === 'DELETE') {
          deleted.push(request.url())
        }
      })
      await serveExperiment(
        page,
        emptyState({
          variables: [makeVariable(), makeVariable({ id: 'variable-price', name: 'Price' })],
        }),
      )
      await openExperiment(page)

      await page
        .locator('.variable-list .variable')
        .first()
        .locator('.variable-actions button')
        .nth(1)
        .click()

      await expect.poll(() => deleted.length).toBe(1)
      await expect(page.locator('.variable-list .variable')).toHaveCount(1)
      await expect(page.locator('.variable-list .variable')).not.toContainText('Churn rate')
    })

    test('EXPERIMENT-06 refuses a range without a name', async ({ page }) => {
      const posted: string[] = []
      page.on('request', request => {
        if (request.method() === 'POST') {
          posted.push(request.url())
        }
      })
      await serveExperiment(page, emptyState())
      await openExperiment(page)

      await page
        .getByRole('button', { name: copy.variables.create, exact: true })
        .click()
      const fields = variableForm(page).locator('input[type="text"]')
      await fields.nth(2).fill('30')
      await fields.nth(3).fill('50')
      await fields.nth(4).fill('70')
      await page
        .getByRole('button', { name: copy.variables.form.submit, exact: true })
        .click()

      await expect(page.getByRole('alert')).toHaveText(copy.variables.form.nameRequired)
      expect(posted).toEqual([])
    })

    test('EXPERIMENT-07 refuses an unordered range', async ({ page }) => {
      const posted: string[] = []
      page.on('request', request => {
        if (request.method() === 'POST') {
          posted.push(request.url())
        }
      })
      await serveExperiment(page, emptyState())
      await openExperiment(page)

      await page
        .getByRole('button', { name: copy.variables.create, exact: true })
        .click()
      const fields = variableForm(page).locator('input[type="text"]')
      await fields.nth(0).fill('Average basket')
      await fields.nth(2).fill('90')
      await fields.nth(3).fill('50')
      await fields.nth(4).fill('10')
      await page
        .getByRole('button', { name: copy.variables.form.submit, exact: true })
        .click()

      await expect(page.getByRole('alert')).toHaveText(copy.variables.form.rangeInvalid)
      expect(posted).toEqual([])
    })

    test('EXPERIMENT-08 declares a run on the chosen option', async ({ page }) => {
      const posted: Array<Record<string, unknown>> = []
      page.on('request', request => {
        if (request.method() === 'POST' && request.url().endsWith('/scenario-runs')) {
          posted.push(request.postDataJSON() as Record<string, unknown>)
        }
      })
      await serveExperiment(page, emptyState())
      await openExperiment(page)

      await page.getByRole('button', { name: copy.runs.create, exact: true }).click()
      await runForm(page).locator('select').first().selectOption('pessimistic')
      await runForm(page).locator('textarea').fill('Spend drops by a fifth.')
      await runForm(page).locator('fieldset.experiment-values input').first().fill('20')
      await page.getByRole('button', { name: copy.runs.form.submit, exact: true }).click()

      await expect.poll(() => posted.length).toBe(1)
      expect(posted[0]).toMatchObject({
        level: 'pessimistic',
        assumptions: 'Spend drops by a fifth.',
        values: [{ variable_id: 'variable-churn', value: 20 }],
      })
      const run = page.locator('.run-list .run')
      await expect(run).toHaveCount(1)
      await expect(run.first().locator('.run-assumptions')).toHaveText('Spend drops by a fifth.')
    })

    test('EXPERIMENT-09 refuses a run without assumptions', async ({ page }) => {
      const posted: string[] = []
      page.on('request', request => {
        if (request.method() === 'POST') {
          posted.push(request.url())
        }
      })
      await serveExperiment(page, emptyState())
      await openExperiment(page)

      await page.getByRole('button', { name: copy.runs.create, exact: true }).click()
      await runForm(page).locator('fieldset.experiment-values input').first().fill('20')
      await page.getByRole('button', { name: copy.runs.form.submit, exact: true }).click()

      await expect(page.getByRole('alert')).toHaveText(copy.runs.form.assumptionsRequired)
      expect(posted).toEqual([])
    })

    test('EXPERIMENT-10 reads where the criterion flips and what is missing', async ({ page }) => {
      const reads: string[] = []
      page.on('request', request => {
        if (request.url().includes('/sensitivity?')) {
          reads.push(request.url())
        }
      })
      await serveExperiment(
        page,
        emptyState({
          variables: [
            makeVariable({ id: 'variable-churn', name: 'Churn rate' }),
            makeVariable({ id: 'variable-price', name: 'Price' }),
          ],
          runs: [
            makeRun({ id: 'run-one', level: 'base' }),
            makeRun({ id: 'run-two', level: 'pessimistic' }),
          ],
          sensitivity: makeSensitivity({
            ranked: [
              {
                variable_id: 'variable-price',
                status: 'found',
                interval: ['80', '110'],
                crossing: '95',
                crossings: 1,
                slope_min: '-2',
                slope_max: '-1',
                travel: null,
              },
            ],
            incomplete_run_ids: ['run-two'],
            evidence: { for_count: 2, against_count: 1 },
          }),
        }),
      )
      await openExperiment(page)

      const reading = page.locator('.sensitivity-list .sensitivity').first()
      await expect(reading).toHaveCount(1)
      await expect(reading.locator('.sensitivity-status')).toHaveText(
        copy.sensitivity.status.found,
      )
      await expect(reading.locator('.sensitivity-crossing')).toHaveText(
        copy.sensitivity.crossing.replace('{value}', '95'),
      )
      await expect(reading.locator('.sensitivity-interval')).toHaveText(
        copy.sensitivity.interval.replace('{low}', '80').replace('{high}', '110'),
      )
      await expect(reading.locator('.sensitivity-crossings')).toHaveText(
        plural(copy.sensitivity.crossings, 1),
      )
      await expect(page.locator('.sensitivity-evidence')).toHaveText(
        copy.sensitivity.evidence.replace('{pour}', '2').replace('{contre}', '1'),
      )
      await expect(page.locator('.sensitivity-incomplete')).toHaveText(
        plural(copy.sensitivity.incomplete, 1),
      )
      await expect(blocks(page).nth(2).locator('.experiment-hint').last()).toHaveText(
        copy.sensitivity.noVerdict,
      )

      await page.locator('.experiment-sensitivity-criteria select').nth(1).selectOption('below')
      await expect
        .poll(() => reads.some(url => url.includes('direction=below')))
        .toBe(true)
    })

    test('EXPERIMENT-11 says when no point straddles the threshold and when there are too few', async ({
      page,
    }) => {
      await serveExperiment(
        page,
        emptyState({
          variables: [
            makeVariable({ id: 'variable-churn', name: 'Churn rate' }),
            makeVariable({ id: 'variable-price', name: 'Price' }),
          ],
          runs: [makeRun({ id: 'run-one' }), makeRun({ id: 'run-two' })],
          sensitivity: makeSensitivity({
            ranked: [
              {
                variable_id: 'variable-price',
                status: 'beyond_declared_range',
                crossings: 0,
                travel: 'down',
              },
              { variable_id: 'variable-churn', status: 'insufficient_points', crossings: 0 },
            ],
          }),
        }),
      )
      await openExperiment(page)

      const readings = page.locator('.sensitivity-list .sensitivity')
      await expect(readings).toHaveCount(2)
      await expect(readings.nth(0).locator('.sensitivity-status')).toHaveText(
        copy.sensitivity.status.beyond_declared_range,
      )
      await expect(readings.nth(0).locator('.sensitivity-travel')).toHaveText(
        copy.sensitivity.travel.down,
      )
      await expect(readings.nth(1).locator('.sensitivity-status')).toHaveText(
        copy.sensitivity.status.insufficient_points,
      )
    })

    test('EXPERIMENT-12 turns the reasoning into an experiment', async ({ page }) => {
      const posted: Array<Record<string, unknown>> = []
      page.on('request', request => {
        if (request.method() === 'POST' && request.url().endsWith('/experiments')) {
          posted.push(request.postDataJSON() as Record<string, unknown>)
        }
      })
      await serveExperiment(page, emptyState())
      await openExperiment(page)

      await page.getByRole('button', { name: copy.experiments.create, exact: true }).click()
      const form = experimentForm(page)
      await form.locator('select').nth(0).selectOption('idea-one')
      await form.locator('input[type="text"]').nth(0).fill('Test the 20% raise')
      await form.locator('textarea').fill('Churn stays flat at the higher price.')
      await form.locator('input[type="text"]').nth(1).fill('Churn rate')
      await form.locator('input[type="text"]').nth(2).fill('10')
      await form.locator('input[type="text"]').nth(3).fill('12')
      await page.getByRole('button', { name: copy.experiments.form.submit, exact: true }).click()

      await expect.poll(() => posted.length).toBe(1)
      expect(posted[0]).toMatchObject({
        idea_id: 'idea-one',
        option_id: null,
        title: 'Test the 20% raise',
        hypothesis: 'Churn stays flat at the higher price.',
        success_metric: 'Churn rate',
        baseline: '10',
        target: '12',
      })
      const tracked = page.locator('.experiment-list .tracked')
      await expect(tracked).toHaveCount(1)
      await expect(tracked.first().locator('h4')).toHaveText('Test the 20% raise')
      await expect(tracked.first().locator('.tracked-status')).toHaveText(
        copy.experiments.status.proposed,
      )
    })

    test('EXPERIMENT-13 refuses an experiment without a title', async ({ page }) => {
      const posted: string[] = []
      page.on('request', request => {
        if (request.method() === 'POST') {
          posted.push(request.url())
        }
      })
      await serveExperiment(page, emptyState())
      await openExperiment(page)

      await page.getByRole('button', { name: copy.experiments.create, exact: true }).click()
      await experimentForm(page).locator('select').nth(0).selectOption('idea-one')
      await experimentForm(page).locator('textarea').fill('Churn stays flat.')
      await page.getByRole('button', { name: copy.experiments.form.submit, exact: true }).click()

      await expect(page.getByRole('alert')).toHaveText(copy.experiments.form.titleRequired)
      expect(posted).toEqual([])
    })

    test('EXPERIMENT-14 offers only the transitions the lifecycle allows', async ({ page }) => {
      const posted: Array<Record<string, unknown>> = []
      page.on('request', request => {
        if (request.method() === 'POST' && request.url().endsWith('/status')) {
          posted.push(request.postDataJSON() as Record<string, unknown>)
        }
      })
      await serveExperiment(page, emptyState({ experiments: [makeExperiment()] }))
      await openExperiment(page)

      const actions = page.locator('.tracked-actions button')
      await expect(actions).toHaveCount(3)
      await expect(actions.nth(0)).toHaveText(copy.experiments.start)
      await expect(actions.nth(1)).toHaveText(copy.experiments.abandon)

      await actions.nth(0).click()
      await expect.poll(() => posted.length).toBe(1)
      expect(posted[0]).toEqual({ status: 'running' })
      await expect(page.locator('.tracked-status')).toHaveText(copy.experiments.status.running)
      await expect(page.locator('.tracked-actions button').nth(0)).toHaveText(
        copy.experiments.complete,
      )
    })

    test('EXPERIMENT-15 completes a running experiment and reads the proposed learning', async ({
      page,
    }) => {
      await serveExperiment(
        page,
        emptyState({ experiments: [makeExperiment({ status: 'running' })] }),
      )
      await openExperiment(page)

      await page
        .getByRole('button', { name: copy.experiments.complete, exact: true })
        .click()

      await expect(page.locator('.tracked-status')).toHaveText(copy.experiments.status.completed)
      const learning = page.locator('.tracked-learning')
      await expect(learning.locator('h5')).toHaveText(copy.experiments.learning)
      await expect(learning.locator('.learning-text')).toHaveText('Churn did not follow the price.')
      await expect(learning.locator('small')).toHaveText(copy.experiments.learningHint)
      await expect(learning.locator('button')).toHaveCount(0)
    })

    test('EXPERIMENT-16 sets the observed outcome beside what was expected', async ({ page }) => {
      const posted: Array<Record<string, unknown>> = []
      page.on('request', request => {
        if (request.method() === 'POST' && request.url().endsWith('/outcomes')) {
          posted.push(request.postDataJSON() as Record<string, unknown>)
        }
      })
      await serveExperiment(
        page,
        emptyState({ experiments: [makeExperiment({ status: 'running' })] }),
      )
      await openExperiment(page)

      const fields = page.locator('.tracked-fields')
      await expect(fields.locator('dt').last()).toHaveText(copy.experiments.expected)
      await expect(fields.locator('dd').last()).toHaveText('12')

      await page
        .getByRole('button', { name: copy.experiments.recordOutcome, exact: true })
        .click()
      const form = page.locator('.tracked .experiment-form')
      await form.locator('input[type="text"]').nth(0).fill('Churn rate')
      await form.locator('input[type="text"]').nth(1).fill('11')
      await form.locator('input[type="text"]').nth(2).fill('%')
      await form.locator('textarea').fill('Held for a week.')
      await page.getByRole('button', { name: copy.experiments.outcome.submit, exact: true }).click()

      await expect.poll(() => posted.length).toBe(1)
      expect(posted[0]).toMatchObject({ metric: 'Churn rate', value: '11', unit: '%' })
      const outcome = page.locator('.tracked-observed .outcome-list .outcome')
      await expect(outcome).toHaveCount(1)
      await expect(outcome.first().locator('.outcome-value')).toHaveText('11')
      await expect(outcome.first().locator('.outcome-metric')).toHaveText('Churn rate')
    })

    test('EXPERIMENT-17 shows a refusal instead of pretending it worked', async ({ page }) => {
      await serveExperiment(
        page,
        emptyState({ experiments: [makeExperiment({ status: 'running' })], forbidStatus: true }),
      )
      await openExperiment(page)

      await page
        .getByRole('button', { name: copy.experiments.complete, exact: true })
        .click()

      await expect(page.getByRole('alert')).toHaveText(copy.experiments.form.forbidden)
      await expect(page.locator('.tracked-status')).toHaveText(copy.experiments.status.running)
      await expect(page.locator('section.experiment > h2')).toHaveText(section.title)
    })

    test('EXPERIMENT-18 never forecasts', async ({ page }) => {
      await serveExperiment(
        page,
        emptyState({
          runs: [makeRun()],
          experiments: [makeExperiment({ status: 'running' })],
          sensitivity: makeSensitivity({
            ranked: [
              { variable_id: 'variable-churn', status: 'found', crossing: '95', crossings: 1 },
            ],
          }),
        }),
      )
      await openExperiment(page)

      const judged = page.locator(
        '.experiment [class*="score"], .experiment [class*="rank"], .experiment [class*="rating"], .experiment [class*="forecast"], .experiment [class*="predict"], .experiment [class*="probab"]',
      )
      await expect(judged).toHaveCount(0)
      await expect(blocks(page).nth(2).locator('.experiment-hint').last()).toHaveText(
        copy.sensitivity.noVerdict,
      )
    })

    test('EXPERIMENT-19 says so when the section could not be read', async ({ page }) => {
      await serveExperiment(page, emptyState({ failOptions: true }))
      await openExperiment(page)

      await expect(page.getByRole('alert')).toHaveText(copy.loadFailed)
      await expect(page.locator('section.experiment > h2')).toHaveText(section.title)
    })
  })
}
