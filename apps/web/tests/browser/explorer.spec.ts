import { expect, test } from '@playwright/test'
import type { IdeaPageResponse, WorkspaceResponse } from '@kollio/api-client'
import fr from '../../i18n/locales/fr.json' with { type: 'json' }
import en from '../../i18n/locales/en.json' with { type: 'json' }

const workspaces: WorkspaceResponse[] = [{ id: 'workspace-one', name: 'Team', role: 'member' }]

for (const [locale, messages] of [['fr', fr], ['en', en]] as const) {
  test.describe(locale, () => {
    const prefix = locale === 'fr' ? '' : '/en'

    test.beforeEach(async ({ page }) => {
      await page.route('**/api/session', route => route.fulfill({ json: { signedIn: true, subject: 'member-two' } }))
      await page.route('**/api/workspaces', route => route.fulfill({ json: workspaces }))
    })

    test('EXPLORER-02 filters by sought role through the API', async ({ page }) => {
      const requested: string[] = []
      page.on('request', request => {
        if (request.url().includes('/api/workspaces/workspace-one/ideas')) requested.push(request.url())
      })
      await page.route('**/api/workspaces/workspace-one/ideas?*', route => route.fulfill({
        json: { items: [], total: 0, limit: 5, offset: 0 } satisfies IdeaPageResponse,
      }))
      await page.goto(`${prefix}/workspace/ideas`)
      await page.getByLabel(messages.ideas.detail.team.soughtTitle).selectOption('marketing')
      await expect.poll(() => requested.some(url => url.includes('sought_role=marketing')), { timeout: 15_000 }).toBe(true)
    })

    test('EXPLORER-04 keeps the domain chips out of the rail', async ({ page }) => {
      await page.route('**/api/workspaces/workspace-one/ideas?*', route => route.fulfill({
        json: { items: [], total: 0, limit: 5, offset: 0 } satisfies IdeaPageResponse,
      }))
      const listResponse = page.waitForResponse(r => r.url().includes('/api/workspaces/workspace-one/ideas'))
      await page.goto(`${prefix}/workspace/ideas`)
      await listResponse
      await expect(page.getByLabel(messages.ideas.detail.team.soughtTitle)).toBeVisible()
      await expect(page.getByText('IA et société')).toHaveCount(0)
    })

    test('EXPLORER-06 keeps a single reset control with no duplicate recent toggle', async ({ page }) => {
      await page.route('**/api/workspaces/workspace-one/ideas?*', route => route.fulfill({
        json: { items: [], total: 0, limit: 5, offset: 0 } satisfies IdeaPageResponse,
      }))
      await page.goto(`${prefix}/workspace/ideas`)
      const rail = page.locator('.ideas-filter-rail')
      await expect(rail.getByRole('button', { name: new RegExp(messages.ideas.explorer.forYou) })).toHaveCount(1)
      await expect(rail.getByRole('button', { name: new RegExp(messages.ideas.explorer.recent) })).toHaveCount(0)
    })

    test('EXPLORER-08 names the search field and keeps a single main landmark', async ({ page }) => {
      await page.route('**/api/workspaces/workspace-one/ideas?*', route => route.fulfill({
        json: { items: [], total: 0, limit: 5, offset: 0 } satisfies IdeaPageResponse,
      }))
      await page.goto(`${prefix}/workspace/ideas`)
      await expect(page.getByRole('searchbox', { name: messages.ideas.explorer.searchLabel })).toBeVisible()
      await expect(page.locator('main')).toHaveCount(1)
    })
  })
}
