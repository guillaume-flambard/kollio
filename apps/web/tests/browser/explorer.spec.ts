import { expect, test } from '@playwright/test'
import type { IdeaPageResponse, WorkspaceResponse } from '@kollio/api-client'
import fr from '../../i18n/locales/fr.json' with { type: 'json' }
import en from '../../i18n/locales/en.json' with { type: 'json' }

const workspaces: WorkspaceResponse[] = [{ id: 'workspace-one', name: 'Team', role: 'member' }]

function idea(id: string, title: string, overrides: Partial<IdeaPageResponse['items'][number]> = {}): IdeaPageResponse['items'][number] {
  return {
    id, slug: id, title,
    pitch: 'Une flotte coopérative.',
    stage: 'seed', lang: 'fr', created_at: '2026-09-01T10:00:00Z',
    sought_roles: [], realism_score: null, last_activity_at: null,
    collaborators: [],
    ...overrides,
  }
}

for (const [locale, messages] of [['fr', fr], ['en', en]] as const) {
  test.describe(locale, () => {
    const prefix = locale === 'fr' ? '' : '/en'

    test.beforeEach(async ({ page }) => {
      await page.route('**/api/session', route => route.fulfill({ json: { signedIn: true, subject: 'member-two' } }))
      await page.route('**/api/workspaces', route => route.fulfill({ json: workspaces }))
    })

    test('EXPLORER-01 renders realism badges on rows', async ({ page }) => {
      await page.route('**/api/workspaces/workspace-one/ideas?*', route => route.fulfill({
        json: {
          items: [
            idea('idea-one', 'Ancrée', { realism_score: 72, sought_roles: ['dev'] }),
            idea('idea-two', 'En attente'),
          ],
          total: 2, limit: 5, offset: 0,
        } satisfies IdeaPageResponse,
      }))
      const listResponse = page.waitForResponse(r => r.url().includes('/api/workspaces/workspace-one/ideas'))
      await page.goto(`${prefix}/workspace`)
      await listResponse
      await expect(page.getByRole('button', { name: new RegExp('Ancrée') })).toBeVisible()
      await expect(page.getByText(/Score 72/)).toBeVisible()
    })

    test('EXPLORER-02 filters by sought role through the API', async ({ page }) => {
      const requested: string[] = []
      page.on('request', request => {
        if (request.url().includes('/api/workspaces/workspace-one/ideas')) requested.push(request.url())
      })
      await page.route('**/api/workspaces/workspace-one/ideas?*', route => route.fulfill({
        json: { items: [], total: 0, limit: 5, offset: 0 } satisfies IdeaPageResponse,
      }))
      await page.goto(`${prefix}/workspace`)
      await page.getByLabel(messages.ideas.detail.team.soughtTitle).selectOption('growth')
      await expect.poll(() => requested.some(url => url.includes('sought_role=growth')), { timeout: 15_000 }).toBe(true)
    })

    test('EXPLORER-03 filters by realism band through the API', async ({ page }) => {
      const requested: string[] = []
      page.on('request', request => {
        if (request.url().includes('/api/workspaces/workspace-one/ideas')) requested.push(request.url())
      })
      await page.route('**/api/workspaces/workspace-one/ideas?*', route => route.fulfill({
        json: { items: [], total: 0, limit: 5, offset: 0 } satisfies IdeaPageResponse,
      }))
      await page.goto(`${prefix}/workspace`)
      await page.getByRole('button', { name: new RegExp(messages.ideas.explorer.realism.grounded) }).click()
      await expect.poll(() => requested.some(url => url.includes('realism_min=60')), { timeout: 15_000 }).toBe(true)
    })

    test('EXPLORER-04 keeps the domain chips out of the rail', async ({ page }) => {
      await page.route('**/api/workspaces/workspace-one/ideas?*', route => route.fulfill({
        json: { items: [], total: 0, limit: 5, offset: 0 } satisfies IdeaPageResponse,
      }))
      const listResponse = page.waitForResponse(r => r.url().includes('/api/workspaces/workspace-one/ideas'))
      await page.goto(`${prefix}/workspace`)
      await listResponse
      await expect(page.getByLabel(messages.ideas.detail.team.soughtTitle)).toBeVisible()
      await expect(page.getByRole('button', { name: new RegExp(messages.ideas.explorer.realism.grounded) })).toBeVisible()
      await expect(page.getByText('IA et société')).toHaveCount(0)
    })
  })
}
