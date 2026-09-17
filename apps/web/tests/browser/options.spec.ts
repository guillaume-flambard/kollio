import { expect, test } from '@playwright/test'
import type { Page } from '@playwright/test'
import type {
  OptionDetailResponse,
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

type OptionsState = {
  options: OptionDetailResponse[]
  contributions: ContributionResponse[]
}

function makeSpace(overrides: Record<string, unknown> = {}) {
  return {
    id: 'space-one',
    workspace_id: 'workspace-one',
    question: 'Which pricing should we pick?',
    description: null,
    owner_id: 'owner-one',
    status: 'EXPLORING',
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

function makeOption(overrides: Partial<OptionDetailResponse> = {}): OptionDetailResponse {
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
    evidence: [],
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

function evidenceCount(messages: typeof fr, support: number, against: number) {
  return messages.decisionSpaces.options.list.evidence
    .replace('{for}', String(support))
    .replace('{against}', String(against))
}

function createdBy(messages: typeof fr, name: string) {
  return messages.decisionSpaces.options.list.createdBy.replace('{name}', name)
}

async function serveOptions(page: Page, state: OptionsState) {
  await page.route('**/api/workspaces/workspace-one/decision-spaces/space-one/options', async (route) => {
    if (route.request().method() === 'POST') {
      const body = route.request().postDataJSON() as Record<string, string | null>
      const created = makeOption({
        id: 'option-new',
        title: body.title ?? '',
        proposal: body.proposal ?? '',
        mechanism: body.mechanism ?? null,
        upside: body.upside ?? null,
        cost: body.cost ?? null,
        risks: body.risks ?? null,
        critical_assumptions: body.critical_assumptions ?? null,
        success_metrics: body.success_metrics ?? null,
      })
      state.options.push(created)
      await route.fulfill({ status: 201, json: created })
      return
    }
    await route.fulfill({ json: { items: state.options } })
  })

  await page.route('**/api/workspaces/workspace-one/decision-spaces/space-one/options/*', async (route) => {
    const segments = new URL(route.request().url()).pathname.split('/')
    const optionId = segments[segments.length - 1] ?? ''
    const option = state.options.find(entry => entry.id === optionId)
    if (!option) {
      await route.fulfill({ status: 404, json: { statusCode: 404, message: 'Not found' } })
      return
    }
    if (route.request().method() === 'PATCH') {
      const body = route.request().postDataJSON() as Record<string, string | null>
      Object.assign(option, body)
      option.updated_at = '2026-09-17T10:00:00Z'
      await route.fulfill({ json: option })
      return
    }
    if (route.request().method() === 'DELETE') {
      state.options = state.options.filter(entry => entry.id !== optionId)
      await route.fulfill({ status: 204, body: '' })
      return
    }
    await route.fulfill({ json: option })
  })

  await page.route('**/api/workspaces/workspace-one/decision-spaces/space-one/options/*/evidence', async (route) => {
    const segments = new URL(route.request().url()).pathname.split('/')
    const optionId = segments[segments.length - 2] ?? ''
    const option = state.options.find(entry => entry.id === optionId)
    const body = route.request().postDataJSON() as { contribution_id: string, side: 'for' | 'against' }
    option?.evidence.push({
      contribution_id: body.contribution_id,
      side: body.side,
      created_at: '2026-09-17T10:00:00Z',
    })
    await route.fulfill({ status: 201, json: option })
  })

  await page.route('**/api/workspaces/workspace-one/decision-spaces/space-one/options/*/evidence/*', async (route) => {
    const segments = new URL(route.request().url()).pathname.split('/')
    const optionId = segments[segments.length - 3] ?? ''
    const contributionId = segments[segments.length - 1] ?? ''
    const option = state.options.find(entry => entry.id === optionId)
    if (option) {
      option.evidence = option.evidence.filter(link => link.contribution_id !== contributionId)
    }
    await route.fulfill({ json: option })
  })

  await page.route('**/api/workspaces/workspace-one/decision-spaces/space-one/contributions', route =>
    route.fulfill({ json: { items: state.contributions } }))
}

for (const [locale, messages] of [['fr', fr], ['en', en]] as const) {
  test.describe(locale, () => {
    const prefix = locale === 'fr' ? '' : '/en'
    const copy = messages.decisionSpaces.options
    const createForm = (page: Page) =>
      page.locator('form.options-form').filter({
        has: page.getByRole('heading', { name: copy.form.newTitle }),
      })
    const editForm = (page: Page) =>
      page.locator('form.options-form').filter({
        has: page.getByRole('heading', { name: copy.form.editTitle }),
      })
    const linkForm = (page: Page) =>
      page.locator('form.options-form').filter({
        has: page.getByRole('heading', { name: copy.actions.link }),
      })

    async function openOptions(page: Page) {
      await page.goto(`${prefix}/workspace/decision-spaces/space-one/options?workspace=workspace-one`)
      await expect(page.locator('section.options > h2')).toHaveText(messages.decisionSpaces.section.options.title)
    }

    test.beforeEach(async ({ page }) => {
      await page.route('**/api/session', route => route.fulfill({ json: { signedIn: true, subject: 'member-two' } }))
      await page.route('**/api/workspaces', route => route.fulfill({ json: workspaces }))
      await page.route('**/api/workspaces/workspace-one/members', route => route.fulfill({ json: members }))
      await page.route('**/api/workspaces/workspace-one/decision-spaces/*', route => route.fulfill({ json: makeDetail() }))
    })

    test('OPTIONS-01 says the space has no option yet', async ({ page }) => {
      await serveOptions(page, { options: [], contributions: [] })

      await openOptions(page)

      await expect(page.getByRole('heading', { name: copy.empty.title })).toBeVisible()
      await expect(page.getByText(copy.empty.body)).toBeVisible()
      await expect(page.getByRole('button', { name: copy.form.create, exact: true })).toBeVisible()
    })

    test('OPTIONS-02 creates an option with only a title and a proposal', async ({ page }) => {
      const state: OptionsState = { options: [], contributions: [] }
      let posted: Record<string, unknown> | undefined
      await serveOptions(page, state)
      page.on('request', (request) => {
        if (request.method() === 'POST' && request.url().endsWith('/options')) {
          posted = request.postDataJSON() as Record<string, unknown>
        }
      })

      await openOptions(page)
      await page.getByRole('button', { name: copy.form.create, exact: true }).click()
      await createForm(page).locator('input[type="text"]').fill('Charge more')
      await createForm(page).locator('textarea').first().fill('Raise the entry price by 20%.')
      await createForm(page).getByRole('button', { name: copy.form.submit }).click()

      await expect(page.locator('li.option h4')).toHaveText('Charge more')
      expect(posted).toEqual({
        title: 'Charge more',
        proposal: 'Raise the entry price by 20%.',
        mechanism: null,
        upside: null,
        cost: null,
        risks: null,
        critical_assumptions: null,
        success_metrics: null,
      })
      const option = page.locator('li.option').first()
      await expect(option.locator('.option-fields')).toHaveCount(0)
      await expect(option.locator('.option-evidence-count')).toHaveText(copy.list.noEvidence)
      await expect(option.locator('.option-meta')).toHaveText(createdBy(messages, 'Camille'))
    })

    test('OPTIONS-03 keeps the optional fields a member did provide', async ({ page }) => {
      const state: OptionsState = { options: [], contributions: [] }
      let posted: Record<string, unknown> | undefined
      await serveOptions(page, state)
      page.on('request', (request) => {
        if (request.method() === 'POST' && request.url().endsWith('/options')) {
          posted = request.postDataJSON() as Record<string, unknown>
        }
      })

      await openOptions(page)
      await page.getByRole('button', { name: copy.form.create, exact: true }).click()
      const form = createForm(page)
      await form.locator('input[type="text"]').fill('Charge more')
      await form.locator('textarea').nth(0).fill('Raise the entry price by 20%.')
      await form.locator('textarea').nth(1).fill('Raise it in two steps, six months apart.')
      await form.locator('textarea').nth(3).fill('Two weeks of engineering.')
      await form.getByRole('button', { name: copy.form.submit }).click()

      expect(posted).toMatchObject({
        mechanism: 'Raise it in two steps, six months apart.',
        cost: 'Two weeks of engineering.',
        upside: null,
        risks: null,
      })
      const fields = page.locator('li.option .option-fields')
      await expect(fields.locator('div')).toHaveCount(2)
      await expect(fields.locator('dt').first()).toHaveText(copy.fields.mechanism)
      await expect(fields.locator('dd').first()).toHaveText('Raise it in two steps, six months apart.')
      await expect(fields.locator('dt').nth(1)).toHaveText(copy.fields.cost)
    })

    test('OPTIONS-04 refuses an option without a title', async ({ page }) => {
      const state: OptionsState = { options: [], contributions: [] }
      const posted: string[] = []
      await serveOptions(page, state)
      page.on('request', (request) => {
        if (request.method() === 'POST') posted.push(request.url())
      })

      await openOptions(page)
      await page.getByRole('button', { name: copy.form.create, exact: true }).click()
      await createForm(page).locator('input[type="text"]').fill('   ')
      await createForm(page).locator('textarea').first().fill('Raise the entry price by 20%.')
      await createForm(page).getByRole('button', { name: copy.form.submit }).click()

      await expect(createForm(page).getByRole('alert')).toHaveText(copy.form.nameRequired)
      expect(posted).toHaveLength(0)
    })

    test('OPTIONS-05 refuses an option without a proposal', async ({ page }) => {
      const state: OptionsState = { options: [], contributions: [] }
      const posted: string[] = []
      await serveOptions(page, state)
      page.on('request', (request) => {
        if (request.method() === 'POST') posted.push(request.url())
      })

      await openOptions(page)
      await page.getByRole('button', { name: copy.form.create, exact: true }).click()
      await createForm(page).locator('input[type="text"]').fill('Charge more')
      await createForm(page).getByRole('button', { name: copy.form.submit }).click()

      await expect(createForm(page).getByRole('alert')).toHaveText(copy.form.proposalRequired)
      expect(posted).toHaveLength(0)
    })

    test('OPTIONS-06 edits an option and the change is read back', async ({ page }) => {
      const state: OptionsState = {
        options: [makeOption({ mechanism: 'Raise it in one step.' })],
        contributions: [],
      }
      let patched: Record<string, unknown> | undefined
      await serveOptions(page, state)
      page.on('request', (request) => {
        if (request.method() === 'PATCH') patched = request.postDataJSON() as Record<string, unknown>
      })

      await openOptions(page)
      await expect(page.locator('li.option .option-fields dd').first()).toHaveText('Raise it in one step.')
      await page.locator('.option-actions button').first().click()
      await editForm(page).locator('textarea').nth(1).fill('Raise it in two steps.')
      await editForm(page).getByRole('button', { name: copy.form.save }).click()

      expect(patched).toMatchObject({ mechanism: 'Raise it in two steps.' })
      await expect(page.locator('li.option .option-fields dd').first()).toHaveText('Raise it in two steps.')
      await expect(editForm(page)).toHaveCount(0)
    })

    test('OPTIONS-07 links a confirmed contribution as evidence against', async ({ page }) => {
      const contribution = makeContribution()
      const state: OptionsState = { options: [makeOption()], contributions: [contribution] }
      let posted: Record<string, unknown> | undefined
      await serveOptions(page, state)
      page.on('request', (request) => {
        if (request.method() === 'POST' && request.url().endsWith('/evidence')) {
          posted = request.postDataJSON() as Record<string, unknown>
        }
      })

      await openOptions(page)
      await page.locator('.option-actions button').nth(1).click()
      const form = linkForm(page)
      await form.locator('select').nth(0).selectOption(contribution.id)
      await form.locator('select').nth(1).selectOption('against')
      await form.getByRole('button', { name: copy.evidence.add, exact: true }).click()

      expect(posted).toEqual({ contribution_id: contribution.id, side: 'against' })
      const sides = page.locator('.option-evidence-list > div')
      await expect(sides.nth(1).locator('.option-evidence-title')).toHaveText(contribution.title)
      await expect(sides.nth(0).getByText(copy.evidence.empty)).toBeVisible()
      await expect(page.locator('.option-evidence-count')).toHaveText(evidenceCount(messages, 0, 1))
    })

    test('OPTIONS-08 offers only the confirmed contributions', async ({ page }) => {
      const contribution = makeContribution()
      const suggested = makeContribution({ id: 'contribution-two', title: 'Maybe churn is price sensitive', status: 'suggested' })
      const state: OptionsState = { options: [makeOption()], contributions: [contribution, suggested] }
      await serveOptions(page, state)

      await openOptions(page)
      await page.locator('.option-actions button').nth(1).click()

      const candidates = linkForm(page).locator('select').first().locator('option')
      await expect(candidates).toHaveCount(2)
      await expect(candidates.nth(1)).toHaveText(contribution.title)
    })

    test('OPTIONS-09 says there is nothing left to link', async ({ page }) => {
      const contribution = makeContribution()
      const state: OptionsState = {
        options: [makeOption({
          evidence: [{ contribution_id: contribution.id, side: 'for', created_at: '2026-09-17T09:30:00Z' }],
        })],
        contributions: [contribution],
      }
      await serveOptions(page, state)

      await openOptions(page)
      await page.locator('.option-actions button').nth(1).click()

      await expect(linkForm(page).getByText(copy.evidence.noCandidates)).toBeVisible()
      await expect(linkForm(page).locator('select')).toHaveCount(0)
    })

    test('OPTIONS-10 unlinks a contribution and the option says so', async ({ page }) => {
      const contribution = makeContribution()
      const state: OptionsState = {
        options: [makeOption({
          evidence: [{ contribution_id: contribution.id, side: 'for', created_at: '2026-09-17T09:30:00Z' }],
        })],
        contributions: [contribution],
      }
      const deleted: string[] = []
      await serveOptions(page, state)
      page.on('request', (request) => {
        if (request.method() === 'DELETE') deleted.push(request.url())
      })

      await openOptions(page)
      const sides = page.locator('.option-evidence-list > div')
      await expect(sides.nth(0).locator('.option-evidence-title')).toHaveText(contribution.title)

      await sides.nth(0).locator('button').click()

      expect(deleted.some(url => url.endsWith(`/evidence/${contribution.id}`))).toBe(true)
      await expect(sides.nth(0).getByText(copy.evidence.empty)).toBeVisible()
      await expect(page.locator('.option-evidence-count')).toHaveText(copy.list.noEvidence)
    })

    test('OPTIONS-11 deletes an option and the space keeps rendering', async ({ page }) => {
      const state: OptionsState = { options: [makeOption()], contributions: [] }
      await serveOptions(page, state)

      await openOptions(page)
      await expect(page.locator('li.option')).toHaveCount(1)

      await page.locator('.option-actions button').nth(2).click()

      await expect(page.locator('li.option')).toHaveCount(0)
      await expect(page.getByRole('heading', { name: copy.empty.title })).toBeVisible()
      await expect(page.locator('section.options > h2')).toHaveText(messages.decisionSpaces.section.options.title)
    })

    test('OPTIONS-12 never scores, ranks or rates an option', async ({ page }) => {
      const state: OptionsState = {
        options: [
          makeOption({ id: 'option-one', title: 'Raise the entry price' }),
          makeOption({ id: 'option-two', title: 'Hold the price and bundle support' }),
        ],
        contributions: [],
      }
      await serveOptions(page, state)

      await openOptions(page)
      await expect(page.locator('li.option')).toHaveCount(2)

      const scored = page.locator(
        '.options [class*="score"], .options [class*="rank"], .options [class*="rating"], .options [data-score], .options [data-rank]',
      )
      await expect(scored).toHaveCount(0)
      await expect(page.locator('.option-evidence-count')).toHaveText([
        copy.list.noEvidence,
        copy.list.noEvidence,
      ])
      await expect(page.locator('.option-meta')).toHaveCount(2)
    })

    test('OPTIONS-13 says so when the options could not be read', async ({ page }) => {
      await page.route('**/api/workspaces/workspace-one/decision-spaces/space-one/options', route =>
        route.fulfill({ status: 500, json: { statusCode: 500, message: 'Boom' } }))
      await page.route('**/api/workspaces/workspace-one/decision-spaces/space-one/contributions', route =>
        route.fulfill({ json: { items: [] } }))

      await openOptions(page)

      await expect(page.getByRole('alert')).toHaveText(copy.loadFailed)
      await expect(page.getByText(messages.decisionSpaces.section.options.body)).toBeVisible()
    })
  })
}
