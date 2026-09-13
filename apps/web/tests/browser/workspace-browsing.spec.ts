import { expect, test } from '@playwright/test'
import type { IdeaPageResponse, IdeaResponse, WorkspaceResponse } from '@kollio/api-client'
import fr from '../../i18n/locales/fr.json' with { type: 'json' }
import en from '../../i18n/locales/en.json' with { type: 'json' }

const idea: IdeaResponse = {
  id: 'idea-one', slug: 'une-idee', title: 'Une idée à explorer',
  pitch: 'Un contenu original français conservé dans les deux langues.',
  stage: 'seed', lang: 'fr', created_at: '2026-09-01T10:00:00Z',
  owner_id: 'member-one', workspace_id: 'workspace-one', visibility: 'workspace',
  collaborators: [],
}
const workspaces: WorkspaceResponse[] = [{ id: 'workspace-one', name: 'Team', role: 'member' }]

for (const [locale, messages] of [['fr', fr], ['en', en]] as const) {
  test.describe(locale, () => {
    const prefix = locale === 'fr' ? '' : '/en'
    test.beforeEach(async ({ page }) => {
      await page.route(/^http:\/\/127\.0\.0\.1:3197\/api\//, async (route) => {
        const url = new URL(route.request().url())
        if (url.pathname === '/api/session') return route.fulfill({ json: { signedIn: true } })
        if (url.pathname === '/api/workspaces') return route.fulfill({ json: workspaces })
        if (url.pathname === '/api/workspaces/workspace-one/ideas') {
          const offset = Number(url.searchParams.get('offset') ?? 0)
          const items = offset === 0 ? [idea] : [{ ...idea, id: 'idea-two', title: 'Deuxième idée' }]
          const result: IdeaPageResponse = { items, total: 6, limit: 5, offset }
          return route.fulfill({ json: result })
        }
        if (url.pathname === '/api/ideas/idea-one') return route.fulfill({ json: idea })
        return route.fulfill({ status: 404, json: { statusCode: 404, message: 'Not found' } })
      })
    })

    test('BROWSE-01 opens an idea and preserves its original content', async ({ page }) => {
      await page.goto(`${prefix}/workspace`)
      await expect(page.getByRole('heading', { name: messages.ideas.title, exact: true })).toBeVisible()
      await page.getByRole('button', { name: new RegExp(idea.title) }).click()
      await page.getByRole('link', { name: messages.ideas.explorer.open, exact: true }).click()
      await expect(page).toHaveURL(new RegExp(`${prefix}/workspace/ideas/idea-one$`))
      await expect(page.getByRole('heading', { name: idea.title, exact: true })).toBeVisible()
      await expect(page.getByText(idea.pitch, { exact: true }).first()).toBeVisible()
    })

    test('BROWSE-02 changes pages and returns to the first page', async ({ page }) => {
      await page.goto(`${prefix}/workspace`)
      await page.getByRole('link', { name: messages.ideas.next, exact: true }).click()
      await expect(page.getByRole('button', { name: /Deuxième idée/ })).toBeVisible()
      await expect(page.getByRole('button', { name: new RegExp(idea.title) })).toHaveCount(0)
      await page.getByRole('link', { name: messages.ideas.previous, exact: true }).click()
      await expect(page.getByRole('button', { name: new RegExp(idea.title) })).toBeVisible()
    })

    test('BROWSE-03 explains an empty workspace', async ({ page }) => {
      await page.route('**/api/workspaces/workspace-one/ideas?*', route => route.fulfill({
        json: { items: [], total: 0, limit: 5, offset: 0 } satisfies IdeaPageResponse,
      }))
      await page.goto(`${prefix}/workspace`)
      await expect(page.getByRole('heading', { name: messages.ideas.empty.title })).toBeVisible()
      await expect(page.getByRole('link', { name: messages.ideas.next, exact: true })).toHaveCount(0)
    })

    test('BROWSE-04 shows an unavailable idea without content', async ({ page }) => {
      await page.goto(`${prefix}/workspace/ideas/inaccessible`)
      await expect(page.getByRole('heading', { name: messages.ideas.detail.notFound })).toBeVisible()
      await expect(page.getByText(idea.pitch, { exact: true })).toHaveCount(0)
    })
  })
}
