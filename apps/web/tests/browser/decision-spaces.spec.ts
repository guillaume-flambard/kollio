import { expect, test } from '@playwright/test'
import type {
  DecisionSpaceDetailResponse,
  DecisionSpaceResponse,
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
    participants: [
      { user_id: 'owner-one', created_at: '2026-09-17T09:00:00Z' },
      { user_id: 'participant-one', created_at: '2026-09-17T09:05:00Z' },
    ],
    history: [],
  }
}

function participantLabel(messages: typeof fr, count: number) {
  const forms = messages.decisionSpaces.list.participants.split(' | ')
  return (count === 1 ? forms[0] : forms[forms.length - 1]).replace('{count}', String(count))
}

for (const [locale, messages] of [['fr', fr], ['en', en]] as const) {
  test.describe(locale, () => {
    const prefix = locale === 'fr' ? '' : '/en'

    test.beforeEach(async ({ page }) => {
      await page.route('**/api/session', route => route.fulfill({ json: { signedIn: true, subject: 'member-two' } }))
      await page.route('**/api/workspaces', route => route.fulfill({ json: workspaces }))
      await page.route('**/api/workspaces/workspace-one/members', route => route.fulfill({ json: members }))
    })

    test('DECISION-SPACES-01 lists the decision spaces of the workspace', async ({ page }) => {
      await page.route('**/api/workspaces/workspace-one/decision-spaces', route => route.fulfill({
        json: { items: [makeSpace()] },
      }))
      await page.route('**/api/workspaces/workspace-one/decision-spaces/*', route => route.fulfill({ json: makeDetail() }))

      await page.goto(`${prefix}/workspace/decision-spaces`)

      await expect(page.getByRole('heading', { name: messages.decisionSpaces.title })).toBeVisible()
      await expect(page.getByText(makeSpace().question)).toBeVisible()
      await expect(page.getByText(messages.decisionSpaces.list.ownerLine.replace('{name}', 'Camille'))).toBeVisible()
      await expect(page.getByText(participantLabel(messages, 2))).toBeVisible()
      await expect(page.locator('.spaces-row-status')).toHaveText(messages.decisionSpaces.status.EXPLORING)
    })

    test('DECISION-SPACES-02 says the workspace has none yet', async ({ page }) => {
      await page.route('**/api/workspaces/workspace-one/decision-spaces', route => route.fulfill({ json: { items: [] } }))

      await page.goto(`${prefix}/workspace/decision-spaces`)

      await expect(page.getByRole('heading', { name: messages.decisionSpaces.empty.title })).toBeVisible()
      await expect(page.getByText(messages.decisionSpaces.empty.description)).toBeVisible()
    })

    test('DECISION-SPACES-03 opens a space from a question and lands on its screen', async ({ page }) => {
      const created = makeSpace({ id: 'space-new', question: 'Which channel do we try first?', status: 'OPEN' })
      await page.route('**/api/workspaces/workspace-one/decision-spaces', async route => {
        if (route.request().method() === 'POST') {
          await route.fulfill({ status: 201, json: created })
          return
        }
        await route.fulfill({ json: { items: [] } })
      })
      await page.route('**/api/workspaces/workspace-one/decision-spaces/*', route => route.fulfill({ json: makeDetail({ id: 'space-new', question: created.question, status: 'OPEN' }) }))

      await page.goto(`${prefix}/workspace/decision-spaces`)
      await page.getByRole('button', { name: messages.decisionSpaces.open }).first().click()
      await page.getByLabel(messages.decisionSpaces.form.question).fill(created.question)
      await page.getByRole('button', { name: messages.decisionSpaces.form.submit }).click()

      await expect(page.getByRole('heading', { name: created.question })).toBeVisible({ timeout: 15_000 })
      await expect(page.getByRole('heading', { name: messages.decisionSpaces.moments.title })).toBeVisible()
      await expect(page.locator('.space-orientation-moment')).toHaveCount(3)
    })

    test('DECISION-SPACES-04 refuses a blank question', async ({ page }) => {
      const posted: string[] = []
      page.on('request', request => {
        if (request.method() === 'POST' && request.url().includes('/decision-spaces')) posted.push(request.url())
      })
      await page.route('**/api/workspaces/workspace-one/decision-spaces', route => route.fulfill({ json: { items: [] } }))

      await page.goto(`${prefix}/workspace/decision-spaces`)
      await page.getByRole('button', { name: messages.decisionSpaces.open }).first().click()
      await page.getByLabel(messages.decisionSpaces.form.question).fill('   ')
      await page.getByRole('button', { name: messages.decisionSpaces.form.submit }).click()

      await expect(page.getByRole('alert')).toHaveText(messages.decisionSpaces.form.questionRequired)
      expect(posted).toHaveLength(0)
    })

    test('DECISION-SPACES-05 frames the space and reaches every section', async ({ page }) => {
      await page.route('**/api/workspaces/workspace-one/decision-spaces/*', route => route.fulfill({ json: makeDetail() }))

      await page.goto(`${prefix}/workspace/decision-spaces/space-one?workspace=workspace-one`)

      await expect(page.getByRole('heading', { name: makeSpace().question })).toBeVisible()
      await expect(page.locator('.space-status')).toHaveText(messages.decisionSpaces.status.EXPLORING)
      await expect(page.locator('.space-facts dd').first()).toHaveText('Camille')
      await expect(page.locator('.space-participants li')).toHaveCount(2)

      for (const section of ['explore', 'converge', 'options', 'decision', 'experiment', 'learning'] as const) {
        await page.locator('.space-sections a').filter({ hasText: messages.decisionSpaces.section[section].label }).click()
        await expect(page.getByRole('heading', { name: messages.decisionSpaces.section[section].title })).toBeVisible()
      }
    })

    test('DECISION-SPACES-07 applies a permitted transition and it survives a reload', async ({ page }) => {
      let status = 'EXPLORING'
      await page.route('**/api/workspaces/workspace-one/decision-spaces/*', route => route.fulfill({ json: makeDetail({ status }) }))
      await page.route('**/api/workspaces/workspace-one/decision-spaces/*/transitions', async route => {
        status = (route.request().postDataJSON() as { to_status: string }).to_status
        await route.fulfill({ json: makeSpace({ status }) })
      })

      await page.goto(`${prefix}/workspace/decision-spaces/space-one?workspace=workspace-one`)
      await page.getByLabel(messages.decisionSpaces.transition.choose).selectOption('CONVERGING')
      await page.getByRole('button', { name: messages.decisionSpaces.transition.submit }).click()

      await expect(page.locator('.space-status')).toHaveText(messages.decisionSpaces.status.CONVERGING)

      await page.reload()
      await expect(page.locator('.space-status')).toHaveText(messages.decisionSpaces.status.CONVERGING)
    })

    test('DECISION-SPACES-08 offers only the transitions the lifecycle declares', async ({ page }) => {
      await page.route('**/api/workspaces/workspace-one/decision-spaces/*', route => route.fulfill({ json: makeDetail({ status: 'OPEN' }) }))

      await page.goto(`${prefix}/workspace/decision-spaces/space-one?workspace=workspace-one`)

      const options = page.getByLabel(messages.decisionSpaces.transition.choose).locator('option')
      await expect(options).toHaveCount(1)
      await expect(options.first()).toHaveText(messages.decisionSpaces.status.EXPLORING)
    })

    test('DECISION-SPACES-09 marks the active area without confusing ideas with spaces', async ({ page }) => {
      await page.route('**/api/workspaces/workspace-one/decision-spaces', route => route.fulfill({ json: { items: [] } }))
      await page.route('**/api/workspaces/workspace-one/ideas?*', route => route.fulfill({
        json: { items: [], total: 0, limit: 5, offset: 0 },
      }))
      await page.route('**/api/inbox', route => route.fulfill({
        json: {
          needs_convergence: { entries: [], total: 0 },
          needs_my_input: { entries: [], total: 0 },
          ready_to_decide: { entries: [], total: 0 },
          needs_learning: { entries: [], total: 0 },
        },
      }))

      await page.goto(`${prefix}/workspace`)
      await expect(page.locator('.workspace-nav a:visible', { hasText: messages.navigation.inbox })).toHaveAttribute('data-active', 'true')
      await expect(page.locator('.workspace-nav a:visible', { hasText: messages.navigation.decisionSpaces })).toHaveAttribute('data-active', 'false')

      await page.goto(`${prefix}/workspace/decision-spaces`)
      await expect(page.locator('.workspace-nav a:visible', { hasText: messages.navigation.decisionSpaces })).toHaveAttribute('data-active', 'true')
      await expect(page.locator('.workspace-nav a:visible', { hasText: messages.navigation.inbox })).toHaveAttribute('data-active', 'false')

      await page.goto(`${prefix}/workspace/ideas`)
      await expect(page.locator('.workspace-nav a:visible', { hasText: messages.navigation.ideas })).toHaveAttribute('data-active', 'true')
      await expect(page.locator('.workspace-nav a:visible', { hasText: messages.navigation.decisionSpaces })).toHaveAttribute('data-active', 'false')
    })

    test('DECISION-SPACES-10 keeps the idea explorer at its own route', async ({ page }) => {      await page.route('**/api/workspaces/workspace-one/ideas?*', route => route.fulfill({
        json: { items: [], total: 0, limit: 5, offset: 0 },
      }))

      await page.goto(`${prefix}/workspace/ideas`)

      await expect(page.getByRole('heading', { name: messages.ideas.title })).toBeVisible()
      await expect(page.getByRole('heading', { name: messages.decisionSpaces.title })).toHaveCount(0)
    })

    test('DECISION-SPACES-11 says a space was not found instead of rendering nothing', async ({ page }) => {
      await page.route('**/api/workspaces/workspace-one/decision-spaces/*', route => route.fulfill({
        status: 404,
        json: { statusCode: 404, message: 'Not found' },
      }))

      await page.goto(`${prefix}/workspace/decision-spaces/space-elsewhere?workspace=workspace-one`)

      await expect(page.getByText(messages.decisionSpaces.notFound.title)).toBeVisible()
      await expect(page.getByText(messages.decisionSpaces.notFound.description)).toBeVisible()
    })

    test('DECISION-SPACES-12 reads the space as three moments', async ({ page }) => {
      await page.route('**/api/workspaces/workspace-one/decision-spaces/*', route => route.fulfill({ json: makeDetail() }))

      const moments = [
        { key: 'frame', first: 'explore', second: 'converge' },
        { key: 'choose', first: 'options', second: 'decision' },
        { key: 'happened', first: 'experiment', second: 'learning' },
      ] as const
      const copy = messages.decisionSpaces.moments

      await page.goto(`${prefix}/workspace/decision-spaces/space-one?workspace=workspace-one`)

      await expect(page.locator('.space-moment-label')).toHaveText(moments.map(moment => copy[moment.key].label))

      for (const moment of moments) {
        const group = page.locator('.space-moment').filter({ hasText: copy[moment.key].label })
        await expect(group.locator('a')).toHaveText([
          messages.decisionSpaces.section[moment.first].label,
          messages.decisionSpaces.section[moment.second].label,
        ])
      }

      const orientation = page.locator('.space-orientation')
      await expect(orientation.getByRole('heading', { name: copy.title })).toBeVisible()

      const blocks = orientation.locator('.space-orientation-moment')
      await expect(blocks).toHaveCount(3)
      await expect(blocks.first().getByText(copy.frame.description)).toBeVisible()
      await expect(blocks.first().getByText(copy.frame.empty)).toBeVisible()
      await expect(blocks.first().getByRole('link', { name: copy.frame.action }))
        .toHaveAttribute('href', /\/workspace\/decision-spaces\/space-one\/explore/)
      await expect(blocks.nth(2).getByRole('link', { name: copy.happened.action }))
        .toHaveAttribute('href', /\/workspace\/decision-spaces\/space-one\/experiment/)
    })
  })
}
