import { expect, test } from '@playwright/test'
import type { Page } from '@playwright/test'
import type {
  ChallengeFindingResponse,
  ChallengeRunResponse,
  DecisionResponse,
  OptionResponse,
  SrcModulesBranchesApiSchemasContributionResponse as ContributionResponse,
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

type State = {
  options: OptionResponse[]
  contributions: ContributionResponse[]
  runs: ChallengeRunResponse[]
  findings: ChallengeFindingResponse[]
  record: DecisionResponse | null
  versions: DecisionResponse[]
  failVersions: boolean
  forbidCommit: boolean
}

function makeSpace(overrides: Record<string, unknown> = {}) {
  return {
    id: 'space-one',
    workspace_id: 'workspace-one',
    question: 'Which pricing should we pick?',
    description: null,
    owner_id: 'owner-one',
    status: 'READY_TO_DECIDE',
    deadline: '2026-10-01',
    lang: 'en',
    created_at: '2026-09-17T09:00:00Z',
    updated_at: '2026-09-17T09:00:00Z',
    ...overrides,
  }
}

function makeDetail(overrides: Record<string, unknown> = {}) {
  return {
    ...makeSpace(overrides),
    participants: [
      { user_id: 'owner-one', created_at: '2026-09-17T09:00:00Z' },
      { user_id: 'participant-one', created_at: '2026-09-17T09:05:00Z' },
    ],
    history: [],
  }
}

function makeOption(overrides: Partial<OptionResponse> = {}): OptionResponse {
  return {
    id: 'option-one',
    space_id: 'space-one',
    title: 'Raise the entry price',
    proposal: 'Raise the entry price by 20% on the next renewal cycle.',
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

function makeContribution(overrides: Partial<ContributionResponse> = {}): ContributionResponse {
  return {
    id: 'contribution-one',
    space_id: 'space-one',
    branch_id: 'branch-one',
    kind: 'claim',
    title: 'Churn does not follow price',
    body: null,
    author_id: 'owner-one',
    source: null,
    tool_model: null,
    transformation_history: null,
    status: 'confirmed',
    lang: 'en',
    created_at: '2026-09-17T09:00:00Z',
    updated_at: '2026-09-17T09:00:00Z',
    ...overrides,
  }
}

function makeRun(overrides: Partial<ChallengeRunResponse> = {}): ChallengeRunResponse {
  return {
    id: 'run-one',
    space_id: 'space-one',
    option_id: 'option-one',
    status: 'COMPLETED',
    opened_by: 'owner-one',
    model: 'fake-critic',
    failure_reason: null,
    lang: 'en',
    created_at: '2026-09-17T09:10:00Z',
    updated_at: '2026-09-17T09:12:00Z',
    ...overrides,
  }
}

function makeFinding(overrides: Partial<ChallengeFindingResponse> = {}): ChallengeFindingResponse {
  return {
    id: 'finding-one',
    run_id: 'run-one',
    kind: 'unsupported_assumption',
    severity: 'medium',
    detail: 'Nothing supports the claim that churn stays flat.',
    origin: 'critic',
    status: 'proposed',
    contribution_id: null,
    lang: 'en',
    created_at: '2026-09-17T09:12:00Z',
    updated_at: '2026-09-17T09:12:00Z',
    ...overrides,
  }
}

function makeRecord(overrides: Partial<DecisionResponse> = {}): DecisionResponse {
  return {
    id: 'decision-one',
    space_id: 'space-one',
    version: 1,
    selected_option_id: 'option-one',
    rationale: 'Churn is flat, so the raise is safe.',
    critical_assumptions: null,
    uncertainty: null,
    success_criteria: null,
    revisit_triggers: null,
    reviewer_ids: ['owner-one'],
    decided_by: 'owner-one',
    lang: 'en',
    created_at: '2026-09-17T09:30:00Z',
    rejected_option_ids: [],
    arguments: [],
    ...overrides,
  }
}

function coverageFor(findings: ChallengeFindingResponse[]) {
  const all = [
    'unsupported_assumption',
    'contradictory_evidence',
    'hidden_dependency',
    'failure_mode',
    'causal_claim',
    'missing_success_criteria',
  ] as const
  const covered = all.filter(kind =>
    findings.some(finding => finding.kind === kind && finding.status !== 'dismissed'))
  const uncovered = all.filter(kind => !covered.includes(kind))
  return { covered: [...covered], uncovered: [...uncovered] }
}

async function serveDecision(page: Page, state: State) {
  await page.route('**/api/workspaces/workspace-one/decision-spaces/space-one/options', route =>
    route.fulfill({ json: { items: state.options } }))
  await page.route('**/api/workspaces/workspace-one/decision-spaces/space-one/contributions', route =>
    route.fulfill({ json: { items: state.contributions } }))

  await page.route('**/api/workspaces/workspace-one/decision-spaces/space-one/options/*/challenges', async (route) => {
    const segments = new URL(route.request().url()).pathname.split('/')
    const optionId = segments[segments.length - 2] ?? ''
    const runs = state.runs.filter(run => run.option_id === optionId)
    const runIds = new Set(runs.map(run => run.id))
    const findings = state.findings.filter(finding => runIds.has(finding.run_id))
    if (route.request().method() === 'POST') {
      const created = makeRun({
        id: `run-${state.runs.length + 1}`,
        option_id: optionId,
        status: 'RUNNING',
        model: null,
        created_at: `2026-09-17T10:0${state.runs.length}:00Z`,
        updated_at: `2026-09-17T10:0${state.runs.length}:00Z`,
      })
      state.runs.push(created)
      await route.fulfill({ status: 201, json: created })
      return
    }
    await route.fulfill({ json: { runs, findings, coverage: coverageFor(findings) } })
  })

  await page.route('**/api/workspaces/workspace-one/decision-spaces/space-one/options/*/challenges/*/findings/*/resolution', async (route) => {
    const segments = new URL(route.request().url()).pathname.split('/')
    const findingId = segments[segments.length - 2] ?? ''
    const body = route.request().postDataJSON() as { resolution: 'confirmed' | 'dismissed' }
    const finding = state.findings.find(entry => entry.id === findingId)
    if (finding) {
      finding.status = body.resolution
    }
    await route.fulfill({ json: finding })
  })

  await page.route('**/api/workspaces/workspace-one/decision-spaces/space-one/decision/versions', route =>
    state.failVersions
      ? route.fulfill({ status: 500, json: { statusCode: 500, message: 'Boom' } })
      : route.fulfill({ json: { items: state.versions } }))

  await page.route('**/api/workspaces/workspace-one/decision-spaces/space-one/decision', async (route) => {
    if (route.request().method() === 'POST') {
      if (state.forbidCommit) {
        await route.fulfill({ status: 403, json: { statusCode: 403, message: 'Forbidden' } })
        return
      }
      const body = route.request().postDataJSON() as Record<string, unknown>
      const version = state.versions.length + 1
      const created = makeRecord({
        id: `decision-${version}`,
        version,
        rationale: body.rationale as string,
        selected_option_id: body.selected_option_id as string,
        critical_assumptions: (body.critical_assumptions as string | null) ?? null,
        uncertainty: (body.uncertainty as string | null) ?? null,
        success_criteria: (body.success_criteria as string | null) ?? null,
        revisit_triggers: (body.revisit_triggers as DecisionResponse['revisit_triggers']) ?? null,
        rejected_option_ids: (body.rejected_option_ids as string[]) ?? [],
        arguments: (body.arguments as DecisionResponse['arguments']) ?? [],
        created_at: `2026-09-17T1${version}:00:00Z`,
      })
      state.record = created
      state.versions = [created, ...state.versions]
      await route.fulfill({ status: 201, json: created })
      return
    }
    await route.fulfill({ json: state.record })
  })
}

function emptyState(overrides: Partial<State> = {}): State {
  return {
    options: [makeOption()],
    contributions: [makeContribution()],
    runs: [],
    findings: [],
    record: null,
    versions: [],
    failVersions: false,
    forbidCommit: false,
    ...overrides,
  }
}

for (const [locale, messages] of [['fr', fr], ['en', en]] as const) {
  test.describe(locale, () => {
    const prefix = locale === 'fr' ? '' : '/en'
    const copy = messages.decisionSpaces.decision

    async function openDecision(page: Page) {
      await page.goto(`${prefix}/workspace/decision-spaces/space-one/decision?workspace=workspace-one`)
      await expect(page.locator('section.decision > h2')).toHaveText(messages.decisionSpaces.section.decision.title)
    }

    test.beforeEach(async ({ page }) => {
      await page.route('**/api/session', route => route.fulfill({ json: { signedIn: true, subject: 'member-two' } }))
      await page.route('**/api/workspaces', route => route.fulfill({ json: workspaces }))
      await page.route('**/api/workspaces/workspace-one/members', route => route.fulfill({ json: members }))
      await page.route('**/api/workspaces/workspace-one/decision-spaces/*', route =>
        route.fulfill({ json: makeDetail() }))
    })

    test('DECISION-01 says there is no option to challenge', async ({ page }) => {
      await serveDecision(page, emptyState({ options: [] }))

      await openDecision(page)

      await expect(page.getByRole('heading', { name: copy.empty.title })).toBeVisible()
      await expect(page.getByText(copy.empty.body)).toBeVisible()
    })

    test('DECISION-02 opens a challenge on a chosen option', async ({ page }) => {
      const state = emptyState()
      const posted: string[] = []
      await serveDecision(page, state)
      page.on('request', (request) => {
        if (request.method() === 'POST' && request.url().endsWith('/challenges')) {
          posted.push(request.url())
        }
      })

      await openDecision(page)
      await page.getByRole('button', { name: copy.challenge.open, exact: true }).click()

      await expect(page.locator('.run-status')).toHaveText(copy.challenge.status.RUNNING)
      expect(posted).toHaveLength(1)
      expect(posted[0]).toContain('/options/option-one/challenges')
    })

    test('DECISION-03 lists the findings with their kind, severity and status', async ({ page }) => {
      const state = emptyState({
        runs: [makeRun()],
        findings: [
          makeFinding(),
          makeFinding({
            id: 'finding-two',
            kind: 'contradictory_evidence',
            severity: 'high',
            detail: 'Two invoices contradict the claim.',
          }),
        ],
      })
      await serveDecision(page, state)

      await openDecision(page)

      await expect(page.locator('.run-status')).toHaveText(copy.challenge.status.COMPLETED)
      await expect(page.locator('.run-model')).toHaveText(copy.challenge.model.replace('{name}', 'fake-critic'))
      await expect(page.locator('.finding')).toHaveCount(2)
      await expect(page.locator('.finding').first().locator('.finding-kind'))
        .toHaveText(copy.challenge.kind.unsupported_assumption)
      await expect(page.locator('.finding').first().locator('.finding-severity'))
        .toHaveText(copy.challenge.severity.medium)
      await expect(page.locator('.finding').first().locator('.finding-status'))
        .toHaveText(copy.challenge.findingStatus.proposed)
      await expect(page.locator('.finding').nth(1).locator('.finding-kind'))
        .toHaveText(copy.challenge.kind.contradictory_evidence)
      await expect(page.locator('.finding').first()
        .getByRole('button', { name: copy.challenge.confirm, exact: true })).toBeVisible()
      await expect(page.locator('.decision-note')).toHaveText(copy.challenge.criticNote)
    })

    test('DECISION-04 a member settles findings and a reload keeps them', async ({ page }) => {
      const state = emptyState({
        runs: [makeRun()],
        findings: [makeFinding(), makeFinding({ id: 'finding-two', detail: 'A second objection.' })],
      })
      const posted: Record<string, unknown>[] = []
      await serveDecision(page, state)
      page.on('request', (request) => {
        if (request.method() === 'POST' && request.url().endsWith('/resolution')) {
          posted.push(request.postDataJSON() as Record<string, unknown>)
        }
      })

      await openDecision(page)
      await page.locator('.finding').first()
        .getByRole('button', { name: copy.challenge.confirm, exact: true }).click()
      await expect(page.locator('.finding').first().locator('.finding-status'))
        .toHaveText(copy.challenge.findingStatus.confirmed)

      await page.locator('.finding').nth(1)
        .getByRole('button', { name: copy.challenge.dismiss, exact: true }).click()
      await expect(page.locator('.finding').nth(1).locator('.finding-status'))
        .toHaveText(copy.challenge.findingStatus.dismissed)

      expect(posted).toEqual([{ resolution: 'confirmed' }, { resolution: 'dismissed' }])

      await page.reload()
      await expect(page.locator('.finding').first().locator('.finding-status'))
        .toHaveText(copy.challenge.findingStatus.confirmed)
      await expect(page.locator('.finding').nth(1).locator('.finding-status'))
        .toHaveText(copy.challenge.findingStatus.dismissed)
    })

    test('DECISION-05 a failed run says why and can be retried', async ({ page }) => {
      const state = emptyState({
        runs: [makeRun({ status: 'FAILED', model: null, failure_reason: 'The Critic could not answer: RuntimeError' })],
      })
      const posted: string[] = []
      await serveDecision(page, state)
      page.on('request', (request) => {
        if (request.method() === 'POST' && request.url().endsWith('/challenges')) {
          posted.push(request.url())
        }
      })

      await openDecision(page)

      await expect(page.locator('.run-status')).toHaveText(copy.challenge.status.FAILED)
      await expect(page.locator('.run-failure')).toHaveText(
        copy.challenge.failure.replace('{reason}', 'The Critic could not answer: RuntimeError'),
      )
      await expect(page.locator('.finding')).toHaveCount(0)
      await expect(page.getByText(copy.challenge.findingsEmpty)).toBeVisible()

      await page.getByRole('button', { name: copy.challenge.retry, exact: true }).click()

      await expect(page.locator('.run-status')).toHaveText(copy.challenge.status.RUNNING)
      expect(posted).toHaveLength(1)
    })

    test('DECISION-06 commits a record with its rationale and its triggers', async ({ page }) => {
      const state = emptyState()
      let posted: Record<string, unknown> | undefined
      await serveDecision(page, state)
      page.on('request', (request) => {
        if (request.method() === 'POST' && request.url().endsWith('/decision')) {
          posted = request.postDataJSON() as Record<string, unknown>
        }
      })

      await openDecision(page)
      await expect(page.getByText(copy.record.empty)).toBeVisible()

      await page.locator('.decision-form textarea').first().fill('Churn is flat, so the raise is safe.')
      await page.locator('.trigger-row input[type="text"]').first().fill('Churn rate')
      await page.getByRole('button', { name: copy.record.form.submit, exact: true }).click()

      expect(posted).toMatchObject({
        selected_option_id: 'option-one',
        rationale: 'Churn is flat, so the raise is safe.',
        rejected_option_ids: [],
        arguments: [],
        revisit_triggers: [{ metric: 'Churn rate', direction: null, threshold: null, note: null }],
      })
      await expect(page.locator('.record-fields dd').nth(1)).toHaveText('Churn is flat, so the raise is safe.')
      await expect(page.locator('.record-fields dd').last()).toHaveText('Churn rate')

      await page.reload()
      await expect(page.locator('.record-version')).toHaveText(copy.record.version.replace('{number}', '1'))
      await expect(page.locator('.record-fields dd').nth(1)).toHaveText('Churn is flat, so the raise is safe.')
    })

    test('DECISION-07 a second version keeps the first readable', async ({ page }) => {
      const first = makeRecord({ rationale: 'Raise the price now.' })
      const state = emptyState({ record: first, versions: [first] })
      await serveDecision(page, state)

      await openDecision(page)
      await expect(page.locator('.version')).toHaveCount(1)

      await page.locator('.decision-form textarea').first().fill('Hold the price for two quarters.')
      await page.getByRole('button', { name: copy.record.form.submit, exact: true }).click()

      await expect(page.locator('.version')).toHaveCount(2)
      await expect(page.locator('.version').first()).toContainText('Hold the price for two quarters.')
      await expect(page.locator('.version').nth(1)).toContainText('Raise the price now.')
      await expect(page.locator('.record-version')).toHaveText(copy.record.version.replace('{number}', '2'))
    })

    test('DECISION-08 never publishes a verdict, a score or a ranking', async ({ page }) => {
      const state = emptyState({
        runs: [makeRun()],
        findings: [makeFinding()],
      })
      await serveDecision(page, state)

      await openDecision(page)

      const judged = page.locator(
        '.decision [class*="score"], .decision [class*="rank"], .decision [class*="rating"], .decision [data-score], .decision [data-rank]',
      )
      await expect(judged).toHaveCount(0)
      await expect(page.locator('.decision-note')).toBeVisible()
    })

    test('DECISION-09 refuses a member who is not a participant', async ({ page }) => {
      const state = emptyState({ forbidCommit: true })
      await serveDecision(page, state)

      await openDecision(page)
      await page.locator('.decision-form textarea').first().fill('A rationale from an outsider.')
      await page.getByRole('button', { name: copy.record.form.submit, exact: true }).click()

      await expect(page.getByRole('alert')).toHaveText(copy.record.form.forbidden)
      await expect(page.locator('section.decision > h2')).toHaveText(messages.decisionSpaces.section.decision.title)
    })

    test('DECISION-10 says so when a read failed', async ({ page }) => {
      const state = emptyState({ failVersions: true })
      await serveDecision(page, state)

      await openDecision(page)

      await expect(page.getByRole('alert')).toHaveText(copy.loadFailed)
      await expect(page.locator('section.decision > h2')).toHaveText(messages.decisionSpaces.section.decision.title)
    })

    test('DECISION-11 offers the commit form only when the space is ready', async ({ page }) => {
      const state = emptyState()
      await serveDecision(page, state)
      await page.route('**/api/workspaces/workspace-one/decision-spaces/*', route =>
        route.fulfill({ json: makeDetail({ status: 'EXPLORING' }) }))

      await openDecision(page)

      await expect(page.locator('.decision-form')).toHaveCount(0)
      await expect(page.getByText(
        copy.record.notReady.replace('{status}', messages.decisionSpaces.status.EXPLORING),
      )).toBeVisible()
    })
  })
}
