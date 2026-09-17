import { expect, test } from '@playwright/test'
import type { Page } from '@playwright/test'
import fr from '../../i18n/locales/fr.json' with { type: 'json' }
import en from '../../i18n/locales/en.json' with { type: 'json' }

const workspaces = [{ id: 'workspace-one', name: 'Team', role: 'member' }]

const roster = [
  { id: 'owner-one', display_name: 'Camille', role: 'admin' },
  { id: 'outsider-one', display_name: 'Nadia', role: 'member' },
]

const companyContext = {
  profile: {
    name: 'Team',
    description: null,
    business_model: null,
    products_services: null,
    customer_segments: null,
    markets: null,
    structure: null,
  },
  objectives: [],
  constraints: [],
  principles: [],
  metrics: [],
}

type Request = {
  id: string
  requester_id: string
  business_function: string
  note: string
  status: string
  rationale: string | null
  created_at: string
}

type Collaborator = {
  id: string
  display_name: string
  participation: string
  business_function: string
}

type State = {
  requests: Request[]
  team: Collaborator[]
  failMembers: boolean
}

function makeRequest(overrides: Partial<Request> = {}): Request {
  return {
    id: 'join-one',
    requester_id: 'outsider-one',
    business_function: 'product',
    note: 'I ran the September test and want to keep going.',
    status: 'pending',
    rationale: null,
    created_at: '2026-09-20T09:00:00Z',
    ...overrides,
  }
}

function makeCollaborator(overrides: Partial<Collaborator> = {}): Collaborator {
  return {
    id: 'participant-one',
    display_name: 'Sam',
    participation: 'contributor',
    business_function: 'product',
    ...overrides,
  }
}

function emptyState(overrides: Partial<State> = {}): State {
  return { requests: [makeRequest()], team: [makeCollaborator()], failMembers: false, ...overrides }
}

function makeIdeaPage(items: unknown[] = [makeIdea()]) {
  return { items, total: items.length, limit: 100, offset: 0 }
}

function makeIdea(overrides: Record<string, unknown> = {}) {
  return {
    id: 'idea-one',
    title: 'Pricing v2',
    pitch: 'Test a raise on the entry plan.',
    initiative_type: 'experiment',
    lang: 'en',
    created_at: '2026-09-17T09:00:00Z',
    ...overrides,
  }
}

async function serveMembers(page: Page, state: State, options: { initiatives?: boolean } = {}) {
  const withInitiatives = options.initiatives !== false

  await page.route('**/api/workspaces/workspace-one/company-context', route =>
    route.fulfill({ json: companyContext }),
  )

  await page.route('**/api/workspaces/workspace-one/members', route =>
    state.failMembers
      ? route.fulfill({ status: 500, json: { statusCode: 500, message: 'Boom' } })
      : route.fulfill({ json: roster }),
  )

  await page.route('**/api/workspaces/workspace-one/ideas*', route =>
    route.fulfill({ json: withInitiatives ? makeIdeaPage() : makeIdeaPage([]) }),
  )

  await page.route('**/api/ideas/idea-one/join-requests/*/accept', route => {
    const url = route.request().url()
    const request = state.requests.find(candidate => url.includes(`/${candidate.id}/accept`))
    if (request) {
      request.status = 'accepted'
      state.team.push({
        id: request.requester_id,
        display_name: 'Nadia',
        participation: 'observer',
        business_function: request.business_function,
      })
    }
    return route.fulfill({ json: request ?? {} })
  })

  await page.route('**/api/ideas/idea-one/join-requests/*/reject', route => {
    const body = route.request().postDataJSON() as { rationale: string }
    const url = route.request().url()
    const request = state.requests.find(candidate => url.includes(`/${candidate.id}/reject`))
    if (request) {
      request.status = 'rejected'
      request.rationale = body.rationale
    }
    return route.fulfill({ json: request ?? {} })
  })

  await page.route('**/api/ideas/idea-one/team/remove/*', route => {
    const memberId = route.request().url().split('/').pop() ?? ''
    state.team = state.team.filter(member => member.id !== memberId)
    return route.fulfill({ json: { removed: memberId } })
  })

  await page.route('**/api/ideas/idea-one/members', route => {
    const body = route.request().postDataJSON() as {
      user_id: string
      participation: string
      function: string
    }
    const known = roster.find(candidate => candidate.id === body.user_id)
    state.team.push({
      id: body.user_id,
      display_name: known?.display_name ?? body.user_id,
      participation: body.participation,
      business_function: body.function,
    })
    return route.fulfill({ json: { added: body.user_id } })
  })

  await page.route('**/api/ideas/idea-one', route =>
    route.fulfill({
      json: {
        ...makeIdea(),
        collaborators: state.team,
        join_requests: state.requests,
      },
    }),
  )
}

for (const [locale, messages] of [
  ['fr', fr],
  ['en', en],
] as const) {
  test.describe(locale, () => {
    const prefix = locale === 'fr' ? '' : '/en'
    const copy = messages.workspace.settings.members

    async function openSettings(page: Page) {
      await page.goto(`${prefix}/workspace/settings?workspace=workspace-one`)
      await expect(page.locator('.settings-members h2')).toHaveText(copy.title)
    }

    function alert(page: Page) {
      return page.locator('.settings-members [role="alert"]')
    }

    function section(page: Page) {
      return page.locator('.settings-members')
    }

    function blocks(page: Page) {
      return page.locator('.settings-members .settings-list')
    }

    function requests(page: Page) {
      return blocks(page).nth(1)
    }

    function team(page: Page) {
      return blocks(page).last()
    }

    test.beforeEach(async ({ page }) => {
      await page.route('**/api/session', route =>
        route.fulfill({ json: { signedIn: true, subject: 'member-two' } }),
      )
      await page.route('**/api/workspaces', route => route.fulfill({ json: workspaces }))
    })

    test('MEMBERS-01 lists the members of the workspace with their roles', async ({ page }) => {
      await serveMembers(page, emptyState())
      await openSettings(page)

      const members = blocks(page).first()
      await expect(members.locator('li')).toHaveCount(2)
      await expect(members).toContainText('Camille')
      await expect(members).toContainText('Nadia')
      await expect(members.locator('li').first().locator('.settings-state')).toHaveText(
        messages.workspace.role.admin,
      )
      await expect(members.locator('li').last().locator('.settings-state')).toHaveText(
        messages.workspace.role.member,
      )
    })

    test('MEMBERS-02 shows the waiting requests with who asked', async ({ page }) => {
      await serveMembers(page, emptyState())
      await openSettings(page)

      const waiting = requests(page)
      await expect(waiting.locator('li')).toHaveCount(1)
      await expect(waiting).toContainText(copy.requests.requester.replace('{name}', 'Nadia'))
      await expect(waiting).toContainText('I ran the September test and want to keep going.')
    })

    test('MEMBERS-03 accepting a request adds the person to the initiative team', async ({ page }) => {
      const posted: string[] = []
      await serveMembers(page, emptyState())
      await openSettings(page)

      page.on('request', request => {
        if (request.method() === 'POST') posted.push(request.url())
      })

      await requests(page).locator('li').first().locator('.settings-primary').click()

      await expect.poll(() => posted.some(url => url.endsWith('/accept'))).toBe(true)
      await expect(section(page)).toContainText(copy.requests.empty)
      await expect(section(page)).toContainText(copy.participation.observer)
    })

    test('MEMBERS-04 refuses a rejection without a reason', async ({ page }) => {
      const posted: string[] = []
      await serveMembers(page, emptyState())
      await openSettings(page)

      page.on('request', request => {
        if (request.method() === 'POST') posted.push(request.url())
      })

      await requests(page).locator('li').first().locator('.settings-link').click()

      await expect(alert(page)).toHaveText(copy.requests.rationaleRequired)
      expect(posted.filter(url => url.endsWith('/reject'))).toEqual([])
    })

    test('MEMBERS-05 rejects a request with the reason given', async ({ page }) => {
      const bodies: unknown[] = []
      await serveMembers(page, emptyState())
      await openSettings(page)

      page.on('request', request => {
        if (request.method() === 'POST' && request.url().endsWith('/reject')) {
          bodies.push(request.postDataJSON())
        }
      })

      await requests(page).locator('li').first().locator('.settings-members-reason input').fill(
        'We already cover pricing this quarter.',
      )
      await requests(page).locator('li').first().locator('.settings-link').click()

      await expect.poll(() => bodies.length).toBe(1)
      expect(bodies[0]).toEqual({ rationale: 'We already cover pricing this quarter.' })
      await expect(section(page)).toContainText(copy.requests.empty)
    })

    test('MEMBERS-06 removes a member from the initiative team', async ({ page }) => {
      const posted: string[] = []
      await serveMembers(page, emptyState())
      await openSettings(page)

      page.on('request', request => {
        if (request.method() === 'POST') posted.push(request.url())
      })

      await expect(team(page)).toContainText('Sam')
      await team(page).locator('li').first().locator('.settings-link').click()

      await expect.poll(() => posted.some(url => url.includes('/team/remove/participant-one'))).toBe(
        true,
      )
      await expect(section(page)).not.toContainText('Sam')
      await expect(section(page)).toContainText(copy.team.empty)
    })

    test('MEMBERS-07 adds a participant to the initiative', async ({ page }) => {
      const bodies: unknown[] = []
      await serveMembers(page, emptyState())
      await openSettings(page)

      page.on('request', request => {
        if (request.method() === 'POST' && request.url().endsWith('/members')) {
          bodies.push(request.postDataJSON())
        }
      })

      const form = page.locator('.settings-members-add')
      await form.locator('select').nth(0).selectOption({ label: 'Nadia' })
      await form.locator('select').nth(1).selectOption({ label: copy.participation.decision_maker })
      await form.locator('select').nth(2).selectOption({ label: messages.ideas.function.product })
      await form.getByRole('button', { name: copy.add.submit, exact: true }).click()

      await expect.poll(() => bodies.length).toBe(1)
      expect(bodies[0]).toEqual({
        user_id: 'outsider-one',
        participation: 'decision_maker',
        function: 'product',
      })
      await expect(section(page)).toContainText(copy.participation.decision_maker)
    })

    test('MEMBERS-08 refuses an add without choosing a member', async ({ page }) => {
      const posted: string[] = []
      await serveMembers(page, emptyState())
      await openSettings(page)

      page.on('request', request => {
        if (request.method() === 'POST') posted.push(request.url())
      })

      const form = page.locator('.settings-members-add')
      await form.getByRole('button', { name: copy.add.submit, exact: true }).click()

      await expect(alert(page)).toHaveText(copy.add.userRequired)
      expect(posted.filter(url => url.endsWith('/members'))).toEqual([])
    })

    test('MEMBERS-09 shows a failure instead of pretending it worked', async ({ page }) => {
      await serveMembers(page, emptyState({ failMembers: true }))
      await openSettings(page)

      await expect(alert(page)).toHaveText(copy.roster.failed)
      await expect(page.locator('.settings-members h2')).toHaveText(copy.title)
    })

    test('MEMBERS-10 says there is no initiative to manage', async ({ page }) => {
      await serveMembers(page, emptyState(), { initiatives: false })
      await openSettings(page)

      await expect(section(page)).toContainText(copy.initiative.empty)
    })
  })
}
