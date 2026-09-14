import { expect, test } from '@playwright/test'
import type { WorkspaceResponse } from '@kollio/api-client'
import fr from '../../i18n/locales/fr.json' with { type: 'json' }
import en from '../../i18n/locales/en.json' with { type: 'json' }

const workspaces: WorkspaceResponse[] = [{ id: 'workspace-one', name: 'Faktus', role: 'member' }]

interface SettingsMessages {
  title: string
  state: Record<string, string>
  profile: Record<string, string>
  objectives: Record<string, string>
  constraints: Record<string, string>
}

type Context = {
  profile: Record<string, string | null>
  objectives: Array<Record<string, unknown>>
  constraints: Array<Record<string, unknown>>
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
  return { profile: emptyProfile(), objectives: [], constraints: [] }
}

function populatedContext(): Context {
  return {
    profile: { ...emptyProfile(), name: 'Faktus', markets: 'France' },
    objectives: [{ id: 'obj-1', title: 'Grow pipeline', state: 'active', priority: true }],
    constraints: [{ id: 'con-1', title: 'Two-person team', detail: 'No hires', state: 'active' }],
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
    return route.fulfill({ status: 404, json: { detail: 'not found' } })
  })

  return { calls, context }
}

for (const [locale, messages] of [['fr', fr], ['en', en]] as const) {
  test.describe(locale, () => {
    const prefix = locale === 'fr' ? '' : '/en'
    const s = (messages.workspace as unknown as { settings: SettingsMessages }).settings

    test('SETTINGS-01 opens the screen with the saved context', async ({ page }) => {
      await mockContext(page, populatedContext())
      const loaded = page.waitForResponse(response => response.url().includes('/company-context'))
      await page.goto(`${prefix}/workspace/settings`)
      await loaded
      await expect(page.getByRole('heading', { name: s.title })).toBeVisible()
      await expect(page.getByLabel(s.profile.name, { exact: true })).toHaveValue('Faktus')
      await expect(page.getByLabel('Grow pipeline')).toHaveValue('Grow pipeline')
      await expect(page.getByLabel('Two-person team', { exact: true })).toHaveValue('Two-person team')
    })

    test('SETTINGS-02 shows the empty state when nothing is saved', async ({ page }) => {
      await mockContext(page, emptyContext())
      await page.goto(`${prefix}/workspace/settings`)
      await expect(page.getByLabel(s.profile.name, { exact: true })).toHaveValue('')
      await expect(page.getByText(s.objectives.empty)).toBeVisible()
      await expect(page.getByText(s.constraints.empty)).toBeVisible()
    })

    test('SETTINGS-03 saves the profile through the API', async ({ page }) => {
      const { calls } = await mockContext(page, emptyContext())
      await page.goto(`${prefix}/workspace/settings`)
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
      await page.getByLabel(s.constraints.placeholder).fill('Two-person team')
      await page.getByRole('button', { name: s.constraints.create }).click()
      await expect(page.getByLabel('Two-person team', { exact: true })).toHaveValue('Two-person team')

      const detail = page.getByLabel(`${s.constraints.detailPlaceholder} — Two-person team`)
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
      await page.getByLabel(s.profile.name, { exact: true }).fill('Faktus')
      await page.getByRole('button', { name: s.profile.save }).click()
      await expect(page.getByRole('alert')).toBeVisible()
      await expect(page.getByLabel(s.profile.name, { exact: true })).toHaveValue('Faktus')
    })
  })
}
