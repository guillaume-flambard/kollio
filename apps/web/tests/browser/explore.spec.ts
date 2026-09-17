import { expect, test } from '@playwright/test'
import type {
  BranchResponse,
  DecisionSpaceDetailResponse,
  DecisionSpaceResponse,
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

const branchesPath = '**/api/workspaces/workspace-one/decision-spaces/space-one/branches'
const contributionsPath = '**/api/workspaces/workspace-one/decision-spaces/space-one/contributions'
const confirmationPath = '**/api/workspaces/workspace-one/decision-spaces/space-one/contributions/*/confirmation'

function makeSpace(overrides: Partial<DecisionSpaceResponse> = {}): DecisionSpaceResponse {
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

function makeDetail(overrides: Partial<DecisionSpaceResponse> = {}): DecisionSpaceDetailResponse {
  return {
    ...makeSpace(overrides),
    participants: [{ user_id: 'owner-one', created_at: '2026-09-17T09:00:00Z' }],
    history: [],
  }
}

function makeBranch(overrides: Partial<BranchResponse> = {}): BranchResponse {
  return {
    id: 'branch-one',
    space_id: 'space-one',
    title: 'What the September test taught us',
    summary: 'Three calls, one clear objection, and a spreadsheet nobody read.',
    source_idea_id: null,
    visibility: 'private',
    created_by: 'owner-one',
    lang: 'en',
    created_at: '2026-09-17T09:00:00Z',
    updated_at: '2026-09-17T09:00:00Z',
    ...overrides,
  }
}

function makeContribution(
  overrides: Partial<ContributionResponse> = {},
): ContributionResponse {
  return {
    id: 'contribution-one',
    space_id: 'space-one',
    branch_id: 'branch-one',
    kind: 'claim',
    title: 'Churn does not follow price',
    body: 'Two years of invoices say so.',
    author_id: 'owner-one',
    source: 'Notion page',
    tool_model: 'ChatGPT',
    transformation_history: null,
    status: 'confirmed',
    lang: 'en',
    created_at: '2026-09-17T09:00:00Z',
    updated_at: '2026-09-17T09:00:00Z',
    ...overrides,
  }
}

function byline(messages: typeof fr, name: string, date: string) {
  return messages.decisionSpaces.explore.branches.byline.replace('{name}', name).replace('{date}', date)
}

function dayLabel(locale: string, iso: string) {
  return new Intl.DateTimeFormat(locale, { day: 'numeric', month: 'long', year: 'numeric' }).format(new Date(iso))
}

for (const [locale, messages] of [['fr', fr], ['en', en]] as const) {
  test.describe(locale, () => {
    const prefix = locale === 'fr' ? '' : '/en'
    const explore = messages.decisionSpaces.explore

    test.beforeEach(async ({ page }) => {
      await page.route('**/api/session', route => route.fulfill({ json: { signedIn: true, subject: 'member-two' } }))
      await page.route('**/api/workspaces', route => route.fulfill({ json: workspaces }))
      await page.route('**/api/workspaces/workspace-one/members', route => route.fulfill({ json: members }))
      await page.route('**/api/workspaces/workspace-one/decision-spaces/*', route => route.fulfill({ json: makeDetail() }))
    })

    async function openExplore(page: import('@playwright/test').Page) {
      await page.goto(`${prefix}/workspace/decision-spaces/space-one/explore`)
      await expect(page.getByRole('heading', { name: explore.branches.title })).toBeVisible()
    }

    test('EXPLORE-01 frames the section and says what is empty', async ({ page }) => {
      await page.route(branchesPath, route => route.fulfill({ json: { items: [] } }))
      await page.route(contributionsPath, route => route.fulfill({ json: { items: [] } }))

      await openExplore(page)

      await expect(page.getByRole('heading', { name: messages.decisionSpaces.section.explore.title })).toBeVisible()
      await expect(page.getByText(messages.decisionSpaces.section.explore.body)).toBeVisible()
      await expect(page.getByText(explore.branches.empty)).toBeVisible()
      await expect(page.getByText(explore.contributions.pendingEmpty)).toBeVisible()
      await expect(page.getByText(explore.contributions.confirmedEmpty)).toBeVisible()
    })

    test('EXPLORE-02 creates a Branch with its raw material and its visibility', async ({ page }) => {
      const branches: BranchResponse[] = []
      const posted: Record<string, unknown>[] = []
      await page.route(branchesPath, async route => {
        if (route.request().method() === 'POST') {
          posted.push(route.request().postDataJSON() as Record<string, unknown>)
          const created = makeBranch({ visibility: 'shared' })
          branches.push(created)
          await route.fulfill({ status: 201, json: created })
          return
        }
        await route.fulfill({ json: { items: branches } })
      })
      await page.route(contributionsPath, route => route.fulfill({ json: { items: [] } }))

      await openExplore(page)
      await page.getByRole('button', { name: explore.branches.create }).click()
      await page.getByLabel(explore.branch.form.name).fill(makeBranch().title)
      await page.getByLabel(explore.branch.form.summary).fill(makeBranch().summary as string)
      await page.getByRole('radio', { name: explore.visibility.shared, exact: true }).check()
      await page.getByRole('button', { name: explore.branch.form.submit }).click()

      await expect(page.getByRole('heading', { name: makeBranch().title })).toBeVisible()
      await expect(page.getByText(makeBranch().summary as string)).toBeVisible()
      await expect(page.locator('.branch-visibility')).toHaveText(explore.visibility.shared)
      expect(posted).toEqual([
        { title: makeBranch().title, summary: makeBranch().summary, visibility: 'shared' },
      ])
    })

    test('EXPLORE-03 states the visibility of each Branch it was given', async ({ page }) => {
      await page.route(branchesPath, route => route.fulfill({
        json: {
          items: [
            makeBranch({ id: 'branch-private', title: 'My own notes', visibility: 'private' }),
            makeBranch({ id: 'branch-shared', title: 'The shared read', visibility: 'shared' }),
          ],
        },
      }))
      await page.route(contributionsPath, route => route.fulfill({ json: { items: [] } }))

      await openExplore(page)

      await expect(page.locator('.branch', { hasText: 'My own notes' }).locator('.branch-visibility'))
        .toHaveText(explore.visibility.private)
      await expect(page.locator('.branch', { hasText: 'The shared read' }).locator('.branch-visibility'))
        .toHaveText(explore.visibility.shared)
    })

    test('EXPLORE-04 labels Branch material as material, not as shared reasoning', async ({ page }) => {
      await page.route(branchesPath, route => route.fulfill({ json: { items: [makeBranch()] } }))
      await page.route(contributionsPath, route => route.fulfill({ json: { items: [] } }))

      await openExplore(page)

      const branch = page.locator('.branch', { hasText: makeBranch().title })
      await expect(branch.locator('.branch-raw-label')).toHaveText(explore.branch.form.summary)
      await expect(branch.locator('.branch-raw')).toHaveText(makeBranch().summary as string)
      await expect(branch).toContainText(byline(messages, 'Camille', dayLabel(locale, makeBranch().created_at)))
      await expect(page.getByText(explore.contributions.confirmedEmpty)).toBeVisible()
    })

    test('EXPLORE-05 refuses a Branch without a name', async ({ page }) => {
      const posted: string[] = []
      page.on('request', request => {
        if (request.method() === 'POST') posted.push(request.url())
      })
      await page.route(branchesPath, route => route.fulfill({ json: { items: [] } }))
      await page.route(contributionsPath, route => route.fulfill({ json: { items: [] } }))

      await openExplore(page)
      await page.getByRole('button', { name: explore.branches.create }).click()
      await page.getByRole('button', { name: explore.branch.form.submit }).click()

      await expect(page.getByRole('alert')).toHaveText(explore.branch.form.nameRequired)
      expect(posted).toEqual([])
    })

    test('EXPLORE-06 proposes a Contribution from a Branch', async ({ page }) => {
      const contributions: ContributionResponse[] = []
      const posted: Record<string, unknown>[] = []
      await page.route(branchesPath, route => route.fulfill({ json: { items: [makeBranch()] } }))
      await page.route(contributionsPath, async route => {
        if (route.request().method() === 'POST') {
          posted.push(route.request().postDataJSON() as Record<string, unknown>)
          const created = makeContribution({ branch_id: 'branch-one', kind: 'evidence' })
          contributions.push(created)
          await route.fulfill({ status: 201, json: created })
          return
        }
        await route.fulfill({ json: { items: contributions } })
      })

      await openExplore(page)
      await page.locator('.branch', { hasText: makeBranch().title })
        .getByRole('button', { name: explore.contributions.propose }).click()
      await expect(page.getByText(explore.contributions.forBranch.replace('{name}', makeBranch().title)))
        .toBeVisible()
      await page.getByLabel(explore.contributions.kind).selectOption('evidence')
      await page.getByLabel(explore.contributions.titleLabel).fill(makeContribution().title)
      await page.getByLabel(explore.contributions.source).fill(makeContribution().source as string)
      await page.getByRole('button', { name: explore.contributions.submit, exact: true }).click()

      await expect(page.getByText(explore.contributions.forBranch.replace('{name}', makeBranch().title)))
        .toBeHidden()
      await expect(page.locator('.contribution-status')).toHaveText(explore.contributions.status.confirmed)
      expect(posted).toEqual([
        {
          branch_id: 'branch-one',
          kind: 'evidence',
          title: makeContribution().title,
          body: null,
          source: makeContribution().source,
          tool_model: null,
        },
      ])
    })

    test('EXPLORE-07 refuses a proposal without a title', async ({ page }) => {
      const posted: string[] = []
      page.on('request', request => {
        if (request.method() === 'POST') posted.push(request.url())
      })
      await page.route(branchesPath, route => route.fulfill({ json: { items: [makeBranch()] } }))
      await page.route(contributionsPath, route => route.fulfill({ json: { items: [] } }))

      await openExplore(page)
      await page.locator('.branch', { hasText: makeBranch().title })
        .getByRole('button', { name: explore.contributions.propose }).click()
      await page.getByRole('button', { name: explore.contributions.submit, exact: true }).click()

      await expect(page.getByRole('alert')).toHaveText(explore.contributions.titleRequired)
      expect(posted).toEqual([])
    })

    test('EXPLORE-08 lists what waits for a human apart from what is confirmed', async ({ page }) => {
      await page.route(branchesPath, route => route.fulfill({ json: { items: [makeBranch()] } }))
      await page.route(contributionsPath, route => route.fulfill({
        json: {
          items: [
            makeContribution({ id: 'contribution-waiting', status: 'suggested', title: 'A waiting claim' }),
            makeContribution({ id: 'contribution-confirmed', title: 'A settled claim' }),
          ],
        },
      }))

      await openExplore(page)

      const waiting = page.locator('.contribution', { hasText: 'A waiting claim' })
      const confirmed = page.locator('.contribution', { hasText: 'A settled claim' })
      await expect(waiting.locator('.contribution-status')).toHaveText(explore.contributions.status.suggested)
      await expect(confirmed.locator('.contribution-status')).toHaveText(explore.contributions.status.confirmed)
      await expect(waiting.getByRole('button', { name: explore.contributions.confirm })).toBeVisible()
      await expect(confirmed.getByRole('button', { name: explore.contributions.confirm })).toHaveCount(0)
      await expect(page.getByText(explore.contributions.pendingEmpty)).toBeHidden()
    })

    test('EXPLORE-09 confirms what waited for a human', async ({ page }) => {
      const contributions: ContributionResponse[] = [
        makeContribution({ id: 'contribution-waiting', status: 'suggested', title: 'A waiting claim' }),
      ]
      const confirmed: string[] = []
      await page.route(branchesPath, route => route.fulfill({ json: { items: [makeBranch()] } }))
      await page.route(contributionsPath, route => route.fulfill({ json: { items: contributions } }))
      await page.route(confirmationPath, async route => {
        confirmed.push(route.request().url())
        contributions[0] = makeContribution({ id: 'contribution-waiting', title: 'A waiting claim' })
        await route.fulfill({ json: contributions[0] })
      })

      await openExplore(page)
      await page.getByRole('button', { name: explore.contributions.confirm }).click()

      await expect(page.getByText(explore.contributions.pendingEmpty)).toBeVisible()
      await expect(page.locator('.contribution', { hasText: 'A waiting claim' }).locator('.contribution-status'))
        .toHaveText(explore.contributions.status.confirmed)
      expect(confirmed).toHaveLength(1)
    })

    test('EXPLORE-10 shows the whole provenance of a Contribution', async ({ page }) => {
      await page.route(branchesPath, route => route.fulfill({
        json: { items: [makeBranch({ visibility: 'shared' })] },
      }))
      await page.route(contributionsPath, route => route.fulfill({ json: { items: [makeContribution()] } }))

      await openExplore(page)

      const provenance = page.locator('.contribution', { hasText: makeContribution().title })
        .locator('.contribution-provenance')
      await expect(provenance).toContainText(explore.provenance.author)
      await expect(provenance).toContainText('Camille')
      await expect(provenance).toContainText(explore.provenance.branch)
      await expect(provenance).toContainText(makeBranch().title)
      await expect(provenance).toContainText(makeContribution().source as string)
      await expect(provenance).toContainText(makeContribution().tool_model as string)
      await expect(provenance).toContainText(explore.provenance.added)
      await expect(provenance).toContainText('2026')
    })

    test('EXPLORE-11 says an absent source or tool is absent', async ({ page }) => {
      await page.route(branchesPath, route => route.fulfill({ json: { items: [makeBranch()] } }))
      await page.route(contributionsPath, route => route.fulfill({
        json: { items: [makeContribution({ source: null, tool_model: null })] },
      }))

      await openExplore(page)

      const provenance = page.locator('.contribution', { hasText: makeContribution().title })
        .locator('.contribution-provenance')
      await expect(provenance.getByText(explore.provenance.none)).toHaveCount(2)
    })

    test('EXPLORE-12 says so when the Branches could not be loaded', async ({ page }) => {
      await page.route(branchesPath, route => route.fulfill({ status: 500, json: {} }))
      await page.route(contributionsPath, route => route.fulfill({ json: { items: [] } }))

      await page.goto(`${prefix}/workspace/decision-spaces/space-one/explore`)

      await expect(page.getByRole('alert')).toHaveText(explore.loadFailed)
    })
  })
}
