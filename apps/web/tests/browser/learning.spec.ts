import { expect, test } from '@playwright/test'
import type { Page } from '@playwright/test'
import type {
  ExperimentDetailResponse,
  ExperimentResponse,
  IdeaPageResponse,
  LearningResponse,
  OutcomeResponse,
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

function makeExperiment(overrides: Partial<ExperimentResponse> = {}): ExperimentResponse {
  return {
    id: 'experiment-one',
    idea_id: 'idea-one',
    decision_space_id: 'space-one',
    option_id: 'option-one',
    title: 'Test the 20% raise',
    hypothesis: 'Churn stays flat while revenue grows.',
    success_metric: 'Churn rate',
    baseline: '10',
    target: '12',
    status: 'completed',
    started_at: '2026-09-18T09:00:00Z',
    ended_at: '2026-09-24T09:00:00Z',
    created_at: '2026-09-18T09:00:00Z',
    ...overrides,
  }
}

function makeOutcome(overrides: Partial<OutcomeResponse> = {}): OutcomeResponse {
  return {
    id: 'outcome-one',
    experiment_id: 'experiment-one',
    metric: 'Churn rate',
    value: '11',
    unit: '%',
    observed_at: '2026-09-24',
    comment: null,
    qualitative: null,
    created_at: '2026-09-24T09:00:00Z',
    ...overrides,
  }
}

function makeLearning(overrides: Partial<LearningResponse> = {}): LearningResponse {
  return {
    id: 'learning-one',
    experiment_id: 'experiment-one',
    idea_id: 'idea-one',
    status: 'draft',
    text: 'Hypothesis: Churn stays flat while revenue grows.',
    outcome_ids: ['outcome-one'],
    confirmed_by_id: null,
    created_at: '2026-09-24T09:00:00Z',
    updated_at: '2026-09-24T09:00:00Z',
    ...overrides,
  }
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
  } as unknown as IdeaPageResponse
}

type State = {
  experiments: ExperimentResponse[]
  outcomes: Record<string, OutcomeResponse[]>
  learnings: LearningResponse[]
  failLessons: boolean
  forbidWrite: boolean
}

function emptyState(overrides: Partial<State> = {}): State {
  return {
    experiments: [makeExperiment()],
    outcomes: { 'experiment-one': [makeOutcome()] },
    learnings: [],
    failLessons: false,
    forbidWrite: false,
    ...overrides,
  }
}

function detailFor(state: State, experiment: ExperimentResponse): ExperimentDetailResponse {
  const outcomes = state.outcomes[experiment.id] ?? []
  const learning = state.learnings.find(item => item.experiment_id === experiment.id) ?? null
  return {
    experiment,
    outcomes,
    learning,
  } as unknown as ExperimentDetailResponse
}

async function serveLearning(page: Page, state: State) {
  await page.route(`${base}/experiments`, route => route.fulfill({ json: state.experiments }))

  await page.route(`${base}/learnings`, async route => {
    if (state.failLessons) {
      await route.fulfill({ status: 500, json: { statusCode: 500, message: 'Boom' } })
      return
    }
    await route.fulfill({ json: state.learnings })
  })

  await page.route('**/api/experiments/*/learnings', async route => {
    if (state.forbidWrite) {
      await route.fulfill({ status: 403, json: { statusCode: 403, message: 'Forbidden' } })
      return
    }
    const segments = new URL(route.request().url()).pathname.split('/')
    const experimentId = segments[segments.length - 2] ?? ''
    const body = route.request().postDataJSON() as { text?: string | null; confirm?: boolean }
    const existing = state.learnings.find(item => item.experiment_id === experimentId)
    const confirmed = body.confirm === true
    const text = body.text ?? existing?.text ?? ''
    if (existing) {
      existing.text = text
      existing.status = confirmed ? 'confirmed' : 'draft'
      existing.confirmed_by_id = confirmed ? 'owner-one' : null
      existing.updated_at = '2026-09-25T09:00:00Z'
      await route.fulfill({ status: 200, json: existing })
      return
    }
    const created = makeLearning({
      id: `learning-${state.learnings.length + 1}`,
      experiment_id: experimentId,
      text,
      status: confirmed ? 'confirmed' : 'draft',
      confirmed_by_id: confirmed ? 'owner-one' : null,
    })
    state.learnings.push(created)
    await route.fulfill({ status: 200, json: created })
  })

  await page.route('**/api/experiments/*', async route => {
    const segments = new URL(route.request().url()).pathname.split('/')
    const experimentId = segments[segments.length - 1] ?? ''
    const experiment = state.experiments.find(item => item.id === experimentId) ?? makeExperiment()
    await route.fulfill({ json: detailFor(state, experiment) })
  })

  await page.route(/\/api\/workspaces\/workspace-one\/ideas(\?|$)/, route =>
    route.fulfill({ json: makeIdeas() }),
  )
}

for (const [locale, messages] of [
  ['fr', fr],
  ['en', en],
] as const) {
  test.describe(locale, () => {
    const prefix = locale === 'fr' ? '' : '/en'
    const copy = messages.decisionSpaces.learning
    const section = messages.decisionSpaces.section.learning

    async function openLearning(page: Page) {
      await page.goto(`${prefix}/workspace/decision-spaces/space-one/learning?workspace=workspace-one`)
      await expect(page.locator('section.learning > h2')).toHaveText(section.title)
    }

    function blocks(page: Page) {
      return page.locator('.learning-block')
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

    test('LEARNING-01 frames the section and says there is nothing yet', async ({ page }) => {
      const state = emptyState()
      await serveLearning(page, state)
      await openLearning(page)

      await expect(page.locator('.learning-empty-state h3')).toHaveText(copy.empty.title)
      await expect(page.locator('.learning-empty-state')).toContainText(copy.empty.body)
      await expect(blocks(page)).toHaveCount(0)
    })

    test('LEARNING-02 reads a proposed lesson with its text and where it came from', async ({
      page,
    }) => {
      const state = emptyState({ learnings: [makeLearning()] })
      await serveLearning(page, state)
      await openLearning(page)

      const proposed = blocks(page).nth(0)
      const lesson = proposed.locator('.lesson').first()

      await expect(proposed.locator('h3')).toHaveText(copy.proposed.title)
      await expect(proposed).toContainText(copy.proposed.intro)
      await expect(lesson.locator('.lesson-status')).toHaveText(copy.status.draft)
      await expect(lesson.locator('h4')).toHaveText('Test the 20% raise')
      await expect(lesson.locator('textarea')).toHaveValue(makeLearning().text)
      await expect(lesson.locator('.lesson-outcome')).toContainText('11')
      await expect(lesson.locator('.lesson-descent')).toContainText('Pricing v2')
    })

    test('LEARNING-03 confirms a proposed lesson', async ({ page }) => {
      const state = emptyState({ learnings: [makeLearning()] })
      await serveLearning(page, state)

      const posted: Array<Record<string, unknown>> = []
      page.on('request', request => {
        if (request.method() === 'POST' && request.url().endsWith('/learnings')) {
          posted.push(request.postDataJSON() as Record<string, unknown>)
        }
      })

      await openLearning(page)

      const proposed = blocks(page).nth(0)
      await proposed.locator('textarea').fill('Churn did not follow the price.')
      await proposed.getByRole('button', { name: copy.actions.confirm, exact: true }).click()

      await expect.poll(() => posted.length).toBe(1)
      expect(posted[0]).toEqual({ text: 'Churn did not follow the price.', confirm: true })

      const confirmed = blocks(page).nth(1)
      await expect(confirmed.locator('.lesson')).toHaveCount(1)
      await expect(confirmed.locator('.lesson-status')).toHaveText(copy.status.confirmed)
      await expect(confirmed.locator('.lesson-text')).toHaveText('Churn did not follow the price.')
      await expect(proposed.locator('.lesson')).toHaveCount(0)
    })

    test('LEARNING-04 saves a draft without confirming and says nothing is deleted', async ({
      page,
    }) => {
      const state = emptyState({ learnings: [makeLearning()] })
      await serveLearning(page, state)

      const posted: Array<Record<string, unknown>> = []
      page.on('request', request => {
        if (request.method() === 'POST' && request.url().endsWith('/learnings')) {
          posted.push(request.postDataJSON() as Record<string, unknown>)
        }
      })

      await openLearning(page)

      const proposed = blocks(page).nth(0)
      await proposed.locator('textarea').fill('Still unsure about the churn signal.')
      await proposed.getByRole('button', { name: copy.actions.save, exact: true }).click()

      await expect.poll(() => posted.length).toBe(1)
      expect(posted[0]).toEqual({ text: 'Still unsure about the churn signal.', confirm: false })

      await expect(proposed.locator('.lesson-status')).toHaveText(copy.status.draft)
      await expect(page.getByText(copy.notes.draftKept)).toBeVisible()
      await expect(page.getByText(copy.notes.neverAuto)).toBeVisible()
    })

    test('LEARNING-05 lists a confirmed lesson with the whole descent', async ({ page }) => {
      const state = emptyState({
        learnings: [
          makeLearning({
            status: 'confirmed',
            text: 'Churn did not follow the price.',
            confirmed_by_id: 'owner-one',
          }),
        ],
      })
      await serveLearning(page, state)
      await openLearning(page)

      const confirmed = blocks(page).nth(1)
      const lesson = confirmed.locator('.lesson').first()

      await expect(confirmed.locator('h3')).toHaveText(copy.confirmed.title)
      await expect(lesson.locator('.lesson-status')).toHaveText(copy.status.confirmed)
      await expect(lesson.locator('.lesson-text')).toHaveText('Churn did not follow the price.')

      const descent = lesson.locator('.lesson-descent')
      await expect(descent).toContainText(copy.card.outcome)
      await expect(descent).toContainText('11')
      await expect(descent).toContainText('Test the 20% raise')
      await expect(descent).toContainText('Pricing v2')
      await expect(descent).toContainText('Camille')
    })

    test('LEARNING-06 confirms nothing on its own', async ({ page }) => {
      const state = emptyState({ learnings: [makeLearning()] })
      await serveLearning(page, state)

      const posted: string[] = []
      page.on('request', request => {
        if (request.method() === 'POST') {
          posted.push(request.url())
        }
      })

      await openLearning(page)

      await expect(page.locator('.learning-note').first()).toHaveText(copy.notes.neverAuto)
      await expect(blocks(page).nth(1).locator('.lesson')).toHaveCount(0)
      expect(posted).toEqual([])
    })

    test('LEARNING-07 shows a refusal instead of pretending it worked', async ({ page }) => {
      const state = emptyState({ learnings: [makeLearning()], forbidWrite: true })
      await serveLearning(page, state)
      await openLearning(page)

      const proposed = blocks(page).nth(0)
      await proposed.getByRole('button', { name: copy.actions.confirm, exact: true }).click()

      await expect(page.locator('.learning-form-error')).toHaveText(copy.actions.confirmFailed)
      await expect(proposed.locator('.lesson-status')).toHaveText(copy.status.draft)
      await expect(page.locator('section.learning > h2')).toHaveText(section.title)
    })

    test('LEARNING-08 says so when the lessons could not be loaded', async ({ page }) => {
      const state = emptyState({ failLessons: true })
      await serveLearning(page, state)
      await openLearning(page)

      await expect(page.locator('.learning-error')).toHaveText(copy.loadFailed)
      await expect(page.locator('section.learning > h2')).toHaveText(section.title)
    })

    test('LEARNING-09 never judges the decision', async ({ page }) => {
      const state = emptyState({
        learnings: [
          makeLearning(),
          makeLearning({
            id: 'learning-two',
            status: 'confirmed',
            text: 'Churn did not follow the price.',
            confirmed_by_id: 'owner-one',
          }),
        ],
      })
      await serveLearning(page, state)
      await openLearning(page)

      const judged = page.locator(
        '.learning [class*="score"], .learning [class*="rank"], .learning [class*="rating"], .learning [class*="verdict"], .learning [class*="prediction"]',
      )
      await expect(judged).toHaveCount(0)
    })
  })
}
