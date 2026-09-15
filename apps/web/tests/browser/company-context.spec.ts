import { expect, test } from '@playwright/test'
import type { WorkspaceResponse } from '@kollio/api-client'
import fr from '../../i18n/locales/fr.json' with { type: 'json' }
import en from '../../i18n/locales/en.json' with { type: 'json' }

const workspaces: WorkspaceResponse[] = [{ id: 'workspace-one', name: 'Faktus', role: 'member' }]

interface SettingsMessages {
  title: string
  state: Record<string, string>
  profile: Record<string, string>
  detailed: Record<string, string>
  objectives: Record<string, string>
  constraints: Record<string, string>
  onboarding: {
    title: string
    intro: string
    pending: string
    submit: string
    saved: string
    steps: Record<string, string>
    facts: Record<string, string>
    model: Record<string, string>
    markets: Record<string, string>
    objectives: Record<string, string>
    constraints: Record<string, string>
    principles: Record<string, string>
    metrics: Record<string, string>
  }
  principles: Record<string, string>
  metrics: Record<string, string>
}

type Context = {
  profile: Record<string, string | null>
  objectives: Array<Record<string, unknown>>
  constraints: Array<Record<string, unknown>>
  principles: Array<Record<string, unknown>>
  metrics: Array<Record<string, unknown>>
}

function emptyProfile() {
  return {
    name: null,
    description: null,
    business_model: null,
    products_services: null,
    customer_segments: null,
    markets: null,
    structure: null,
  }
}

function emptyContext(): Context {
  return { profile: emptyProfile(), objectives: [], constraints: [], principles: [], metrics: [] }
}

function populatedContext(): Context {
  return {
    profile: { ...emptyProfile(), name: 'Faktus', markets: 'France' },
    objectives: [{ id: 'obj-1', title: 'Grow pipeline', state: 'active', priority: true }],
    constraints: [{ id: 'con-1', title: 'Two-person team', detail: 'No hires', state: 'active' }],
    principles: [{ id: 'pri-1', title: 'No discount-led growth', detail: null, state: 'active' }],
    metrics: [{ id: 'met-1', name: 'Active accounts', value: '128', unit: 'accounts', observed_at: null, source: null, state: 'active' }],
  }
}

async function mockContext(page: import('@playwright/test').Page, context: Context) {
  const calls: Array<{ method: string, url: string, body: unknown }> = []

  await page.route(/\/api\/session$/, route =>
    route.fulfill({ json: { signedIn: true, subject: 'member-one' } }))
  await page.route(/\/api\/workspaces$/, route => route.fulfill({ json: workspaces }))

  await page.route(/\/api\/workspaces\/workspace-one\/company-context.*$/, async (route) => {
    const request = route.request()
    const path = new URL(request.url()).pathname
    const method = request.method()
    const body = method === 'GET' ? undefined : request.postDataJSON() as Record<string, unknown>
    calls.push({ method, url: path, body })

    const objectiveMatch = path.match(/\/objectives\/([^/]+)$/)
    const constraintMatch = path.match(/\/constraints\/([^/]+)$/)
    const principleMatch = path.match(/\/principles\/([^/]+)$/)
    const metricMatch = path.match(/\/metrics\/([^/]+)$/)

    if (path.endsWith('/company-context') && method === 'GET') {
      return route.fulfill({ json: context })
    }
    if (path.endsWith('/profile') && method === 'PUT') {
      context.profile = { ...emptyProfile(), ...(body as Record<string, string | null>) }
      return route.fulfill({ json: context.profile })
    }
    if (path.endsWith('/objectives') && method === 'POST') {
      const created = { id: 'obj-new', title: body!.title, state: 'active', priority: false }
      context.objectives.push(created)
      return route.fulfill({ status: 201, json: created })
    }
    if (objectiveMatch && method === 'PATCH') {
      const target = context.objectives.find(item => item.id === objectiveMatch[1])
      if (!target) return route.fulfill({ status: 404, json: { detail: 'not found' } })
      Object.assign(target, body)
      return route.fulfill({ json: target })
    }
    if (path.endsWith('/constraints') && method === 'POST') {
      const created = { id: 'con-new', title: body!.title, detail: body!.detail ?? null, state: 'active' }
      context.constraints.push(created)
      return route.fulfill({ status: 201, json: created })
    }
    if (constraintMatch && method === 'PATCH') {
      const target = context.constraints.find(item => item.id === constraintMatch[1])
      if (!target) return route.fulfill({ status: 404, json: { detail: 'not found' } })
      Object.assign(target, body)
      return route.fulfill({ json: target })
    }
    if (path.endsWith('/principles') && method === 'POST') {
      const created = { id: `pri-${context.principles.length + 1}`, title: body!.title, detail: body!.detail ?? null, state: 'active' }
      context.principles.push(created)
      return route.fulfill({ status: 201, json: created })
    }
    if (principleMatch && method === 'PATCH') {
      const target = context.principles.find(item => item.id === principleMatch[1])
      if (!target) return route.fulfill({ status: 404, json: { detail: 'not found' } })
      Object.assign(target, body)
      return route.fulfill({ json: target })
    }
    if (path.endsWith('/metrics') && method === 'POST') {
      const created = { id: `met-${context.metrics.length + 1}`, name: body!.name, value: body!.value ?? null, unit: body!.unit ?? null, observed_at: body!.observed_at ?? null, source: body!.source ?? null, state: 'active' }
      context.metrics.push(created)
      return route.fulfill({ status: 201, json: created })
    }
    if (metricMatch && method === 'PATCH') {
      const target = context.metrics.find(item => item.id === metricMatch[1])
      if (!target) return route.fulfill({ status: 404, json: { detail: 'not found' } })
      Object.assign(target, body)
      return route.fulfill({ json: target })
    }
    return route.fulfill({ status: 404, json: { detail: 'not found' } })
  })

  return { calls, context }
}

for (const [locale, messages] of [['fr', fr], ['en', en]] as const) {
  test.describe(locale, () => {
    const prefix = locale === 'fr' ? '' : '/en'
    const s = (messages.workspace as unknown as { settings: SettingsMessages }).settings
    const rowLabel = (field: string, item: string) => `${field}: ${item}`
    // The structured editor is the collapsed advanced surface; open it before touching its fields.
    const openDetailedEditor = (page: import('@playwright/test').Page) =>
      page.getByRole('button', { name: s.detailed.title }).click()

    test('SETTINGS-01 opens the screen with the saved context', async ({ page }) => {
      await mockContext(page, populatedContext())
      const loaded = page.waitForResponse(response => response.url().includes('/company-context'))
      await page.goto(`${prefix}/workspace/settings`)
      await loaded
      await expect(page.getByRole('heading', { name: s.title, exact: true })).toBeVisible()
      await openDetailedEditor(page)
      await expect(page.getByLabel(s.profile.name, { exact: true })).toHaveValue('Faktus')
      await expect(page.getByLabel('Grow pipeline')).toHaveValue('Grow pipeline')
      await expect(page.getByLabel(rowLabel(s.constraints.titleLabel, 'Two-person team'))).toHaveValue('Two-person team')
    })

    test('SETTINGS-02 shows the empty state when nothing is saved', async ({ page }) => {
      await mockContext(page, emptyContext())
      await page.goto(`${prefix}/workspace/settings`)
      await openDetailedEditor(page)
      await expect(page.getByLabel(s.profile.name, { exact: true })).toHaveValue('')
      await expect(page.getByText(s.objectives.empty)).toBeVisible()
      await expect(page.getByText(s.constraints.empty)).toBeVisible()
    })

    test('SETTINGS-03 saves the profile through the API', async ({ page }) => {
      const { calls } = await mockContext(page, emptyContext())
      await page.goto(`${prefix}/workspace/settings`)
      await openDetailedEditor(page)
      await page.getByLabel(s.profile.name, { exact: true }).fill('Faktus')
      await page.getByLabel(s.profile.markets, { exact: true }).fill('France')
      await page.getByRole('button', { name: s.profile.save }).click()
      await expect.poll(() => calls.some(call => call.method === 'PUT' && call.url.endsWith('/profile'))).toBe(true)
      expect(calls.find(call => call.method === 'PUT')!.body).toMatchObject({ name: 'Faktus', markets: 'France' })
      await expect(page.getByText(s.profile.saved)).toBeVisible()
    })

    test('SETTINGS-04 creates, edits, prioritises, archives and restores an objective', async ({ page }) => {
      const { calls } = await mockContext(page, emptyContext())
      await page.goto(`${prefix}/workspace/settings`)
      await openDetailedEditor(page)
      await page.getByLabel(s.objectives.placeholder).fill('Grow pipeline')
      await page.getByRole('button', { name: s.objectives.create }).click()
      await expect(page.getByLabel('Grow pipeline')).toHaveValue('Grow pipeline')

      const objectiveTitleField = page.getByLabel('Grow pipeline')
      await objectiveTitleField.fill('Grow enterprise pipeline')
      await objectiveTitleField.press('Tab')
      await expect.poll(() => calls.some(call => call.method === 'PATCH' && call.body && (call.body as { title?: string }).title === 'Grow enterprise pipeline')).toBe(true)

      await page.getByRole('checkbox', { name: s.objectives.priority }).check()
      await expect.poll(() => calls.some(call => call.method === 'PATCH' && (call.body as { priority?: boolean }).priority === true)).toBe(true)

      await page.getByRole('button', { name: s.objectives.archive }).click()
      await expect(page.getByText(s.state.archived)).toBeVisible()

      await page.getByRole('button', { name: s.objectives.restore }).click()
      await expect(page.getByText(s.state.active)).toBeVisible()
      await expect.poll(() => calls.some(call => call.method === 'PATCH' && (call.body as { state?: string }).state === 'active')).toBe(true)
    })

    test('SETTINGS-05 creates, edits and archives-restores a constraint', async ({ page }) => {
      const { calls } = await mockContext(page, emptyContext())
      await page.goto(`${prefix}/workspace/settings`)
      await openDetailedEditor(page)
      await page.getByLabel(s.constraints.placeholder).fill('Two-person team')
      await page.getByRole('button', { name: s.constraints.create }).click()
      await expect(page.getByLabel(rowLabel(s.constraints.titleLabel, 'Two-person team'))).toHaveValue('Two-person team')

      const detail = page.getByLabel(rowLabel(s.constraints.detailLabel, 'Two-person team'))
      await detail.fill('No hires this year')
      await detail.press('Tab')
      await expect.poll(() => calls.some(call => call.method === 'PATCH' && call.url.includes('/constraints/') && (call.body as { detail?: string }).detail === 'No hires this year')).toBe(true)

      await page.getByRole('button', { name: s.constraints.archive }).click()
      await expect(page.getByText(s.state.archived)).toBeVisible()
      await page.getByRole('button', { name: s.constraints.restore }).click()
      await expect.poll(() => calls.some(call => call.method === 'PATCH' && call.url.includes('/constraints/') && (call.body as { state?: string }).state === 'active')).toBe(true)
    })

    test('SETTINGS-06 reports a failure and keeps the entered values', async ({ page }) => {
      await mockContext(page, emptyContext())
      await page.route(/\/api\/workspaces\/workspace-one\/company-context\/profile$/, route =>
        route.fulfill({ status: 500, json: { detail: 'boom' } }))
      await page.goto(`${prefix}/workspace/settings`)
      await openDetailedEditor(page)
      await page.getByLabel(s.profile.name, { exact: true }).fill('Faktus')
      await page.getByRole('button', { name: s.profile.save }).click()
      await expect(page.getByRole('alert')).toBeVisible()
      await expect(page.getByLabel(s.profile.name, { exact: true })).toHaveValue('Faktus')
    })

    test('SETTINGS-07 keeps the detailed editor collapsed until the advanced surface is opened', async ({ page }) => {
      await mockContext(page, populatedContext())
      await page.goto(`${prefix}/workspace/settings`)
      const toggle = page.getByRole('button', { name: s.detailed.title })
      await expect(toggle).toHaveAttribute('aria-expanded', 'false')
      const panelId = await toggle.getAttribute('aria-controls')
      expect(panelId).toBeTruthy()
      const panel = page.locator(`#${panelId}`)
      await expect(panel).toBeHidden()

      await toggle.focus()
      await page.keyboard.press('Enter')
      await expect(toggle).toHaveAttribute('aria-expanded', 'true')
      await expect(panel).toBeVisible()
      await expect(page.getByRole('button', { name: s.profile.save })).toBeVisible()

      await toggle.click()
      await expect(toggle).toHaveAttribute('aria-expanded', 'false')
      await expect(panel).toBeHidden()
    })

    test('ONBOARD-01 shows seven pending steps when nothing is filled', async ({ page }) => {
      await mockContext(page, emptyContext())
      await page.goto(`${prefix}/workspace/settings`)
      await expect(page.getByRole('heading', { name: s.onboarding.title })).toBeVisible()
      await expect(page.locator('.settings-pending')).toHaveCount(7)
    })

    test('ONBOARD-02 persists partial answers across all seven questions', async ({ page }) => {
      const { calls } = await mockContext(page, emptyContext())
      await page.goto(`${prefix}/workspace/settings`)
      await openDetailedEditor(page)
      await page.getByLabel(s.onboarding.facts.name, { exact: true }).fill('Faktus')
      await page.getByLabel(s.onboarding.objectives.first, { exact: true }).fill('Grow enterprise pipeline')
      await page.getByLabel(s.onboarding.objectives.second, { exact: true }).fill('Reduce churn')
      await page.getByLabel(s.onboarding.constraints.first, { exact: true }).fill('Two-person team')
      await page.getByLabel(s.onboarding.principles.first, { exact: true }).fill('No discount-led growth')
      await page.getByLabel(s.onboarding.metrics.first, { exact: true }).fill('Monthly active accounts')
      await page.getByRole('button', { name: s.onboarding.submit }).click()

      // The "saved" note appears only after the whole run (profile + all four lists) finishes.
      await expect(page.getByText(s.onboarding.saved)).toBeVisible()
      expect(calls.some(call => call.method === 'PUT' && call.url.endsWith('/profile'))).toBe(true)
      expect(calls.find(call => call.method === 'PUT')!.body).toMatchObject({ name: 'Faktus' })
      const postedTitles = calls.filter(call => call.method === 'POST' && call.url.endsWith('/objectives')).map(call => (call.body as { title: string }).title)
      expect(postedTitles).toEqual(['Grow enterprise pipeline', 'Reduce churn'])
      expect(calls.some(call => call.method === 'POST' && call.url.endsWith('/constraints') && (call.body as { title: string }).title === 'Two-person team')).toBe(true)
      expect(calls.some(call => call.method === 'POST' && call.url.endsWith('/principles') && (call.body as { title: string }).title === 'No discount-led growth')).toBe(true)
      expect(calls.some(call => call.method === 'POST' && call.url.endsWith('/metrics') && (call.body as { name: string }).name === 'Monthly active accounts')).toBe(true)
      // model and markets were skipped, so they stay pending; the other five are answered.
      await expect(page.locator('.settings-pending')).toHaveCount(2)
      await expect(page.getByLabel(rowLabel(s.principles.titleLabel, 'No discount-led growth'))).toHaveValue('No discount-led growth')
    })

    test('ONBOARD-03 keeps skipped questions visibly pending', async ({ page }) => {
      const { calls } = await mockContext(page, emptyContext())
      await page.goto(`${prefix}/workspace/settings`)
      await page.getByLabel(s.onboarding.facts.name, { exact: true }).fill('Faktus')
      await page.getByRole('button', { name: s.onboarding.submit }).click()
      await expect.poll(() => calls.some(call => call.method === 'PUT' && call.url.endsWith('/profile'))).toBe(true)
      await expect(page.locator('[data-step="facts"][data-answered="true"]')).toHaveCount(1)
      await expect(page.locator('[data-step="objectives"][data-answered="false"]')).toHaveCount(1)
      await expect(page.locator('.settings-pending')).toHaveCount(6)
    })

    test('ONBOARD-04 creates and archives a non-negotiable from enrichment', async ({ page }) => {
      const { calls } = await mockContext(page, emptyContext())
      await page.goto(`${prefix}/workspace/settings`)
      await openDetailedEditor(page)
      await page.getByLabel(s.principles.placeholder).fill('Support local first')
      await page.getByRole('button', { name: s.principles.create }).click()
      await expect(page.getByLabel(rowLabel(s.principles.titleLabel, 'Support local first'))).toHaveValue('Support local first')
      await page.getByRole('button', { name: s.principles.archive }).click()
      await expect(page.getByText(s.state.archived)).toBeVisible()
      await expect.poll(() => calls.some(call => call.method === 'PATCH' && call.url.includes('/principles/') && (call.body as { state?: string }).state === 'archived')).toBe(true)
    })

    test('ONBOARD-05 records and edits a key indicator from enrichment', async ({ page }) => {
      const { calls } = await mockContext(page, emptyContext())
      await page.goto(`${prefix}/workspace/settings`)
      await openDetailedEditor(page)
      await page.getByLabel(s.metrics.namePlaceholder).fill('Activation rate')
      await page.getByLabel(s.metrics.valuePlaceholder).fill('32')
      await page.getByRole('button', { name: s.metrics.create }).click()
      await expect(page.getByLabel(rowLabel(s.metrics.nameLabel, 'Activation rate'))).toHaveValue('Activation rate')
      const valueField = page.getByLabel(rowLabel(s.metrics.valueLabel, 'Activation rate'))
      await valueField.fill('41')
      await valueField.press('Tab')
      await expect.poll(() => calls.some(call => call.method === 'PATCH' && call.url.includes('/metrics/') && (call.body as { value?: string }).value === '41')).toBe(true)
    })

    test('ONBOARD-06 saving twice does not duplicate an answered question', async ({ page }) => {
      const { calls } = await mockContext(page, emptyContext())
      await page.goto(`${prefix}/workspace/settings`)
      await page.getByLabel(s.onboarding.facts.name, { exact: true }).fill('Faktus')
      await page.getByLabel(s.onboarding.objectives.first, { exact: true }).fill('Grow enterprise pipeline')
      await page.getByRole('button', { name: s.onboarding.submit }).click()
      await expect(page.getByText(s.onboarding.saved)).toBeVisible()
      await page.getByRole('button', { name: s.onboarding.submit }).click()
      await expect(page.getByText(s.onboarding.saved).last()).toBeVisible()
      const objectivePosts = calls.filter(call => call.method === 'POST' && call.url.endsWith('/objectives'))
      expect(objectivePosts).toHaveLength(1)
    })
  })
}
