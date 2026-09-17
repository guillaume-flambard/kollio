import { expect, test } from '@playwright/test'
import type { Page } from '@playwright/test'

import fr from '../../i18n/locales/fr.json' with { type: 'json' }
import en from '../../i18n/locales/en.json' with { type: 'json' }

const workspaces = [{ id: 'workspace-one', name: 'Team', role: 'member' }]

type Entry = {
  kind: string
  workspace_id: string
  space_id: string
  space_question: string
  space_status: string
  subject_id: string | null
  detail: string | null
  created_at: string
}

type Section = { entries: Entry[], total: number }

type Inbox = {
  needs_convergence: Section
  needs_my_input: Section
  ready_to_decide: Section
  needs_learning: Section
}

function makeEntry(overrides: Partial<Entry> = {}): Entry {
  return {
    kind: 'space_needs_convergence',
    workspace_id: 'workspace-one',
    space_id: 'space-one',
    space_question: 'Which pricing should we pick?',
    space_status: 'CONVERGING',
    subject_id: null,
    detail: null,
    created_at: '2026-09-17T09:00:00Z',
    ...overrides,
  }
}

function makeSection(entries: Entry[] = [], total?: number): Section {
  return { entries, total: total ?? entries.length }
}

function emptyInbox(overrides: Partial<Inbox> = {}): Inbox {
  return {
    needs_convergence: makeSection(),
    needs_my_input: makeSection(),
    ready_to_decide: makeSection(),
    needs_learning: makeSection(),
    ...overrides,
  }
}

async function serveInbox(page: Page, inbox: Inbox, options: { fail?: boolean } = {}) {
  await page.route('**/api/inbox', route =>
    options.fail
      ? route.fulfill({ status: 500, json: { statusCode: 500, message: 'Boom' } })
      : route.fulfill({ json: inbox }))
}

for (const [locale, messages] of [['fr', fr], ['en', en]] as const) {
  test.describe(locale, () => {
    const prefix = locale === 'fr' ? '' : '/en'
    const copy = messages.inbox
    const section = messages.inbox.sections

    async function openInbox(page: Page) {
      await page.goto(`${prefix}/workspace`)
      await expect(page.locator('.inbox-header h1')).toHaveText(copy.title)
    }

    function blocks(page: Page) {
      return page.locator('.inbox-section')
    }

    function entries(page: Page) {
      return page.locator('.inbox-entry')
    }

    function pluralLabel(template: string, count: number) {
      const forms = template.split(' | ')
      const form = count === 1 ? forms[0] : forms[forms.length - 1]
      return form.replace('{count}', String(count))
    }

    test.beforeEach(async ({ page }) => {
      await page.route('**/api/session', route => route.fulfill({ json: { signedIn: true, subject: 'member-two' } }))
      await page.route('**/api/workspaces', route => route.fulfill({ json: workspaces }))
    })

    test('INBOX-01 frames the inbox and lists what waits, section by section', async ({ page }) => {
      await serveInbox(page, emptyInbox({
        needs_convergence: makeSection([makeEntry()]),
        needs_my_input: makeSection([makeEntry({
          kind: 'contribution_awaits_confirmation',
          subject_id: 'contribution-one',
          detail: 'Churn does not follow price',
        })]),
        ready_to_decide: makeSection([makeEntry({
          kind: 'decision_awaits_commitment',
          space_status: 'READY_TO_DECIDE',
        })]),
        needs_learning: makeSection([makeEntry({
          kind: 'experiment_awaits_outcome',
          subject_id: 'experiment-one',
          detail: 'Test the 20% raise',
        })]),
      }))

      await openInbox(page)

      await expect(page.locator('.inbox-header p')).toHaveText(copy.description)
      await expect(page.getByRole('heading', { name: section.needsConvergence.title })).toBeVisible()
      await expect(page.getByRole('heading', { name: section.needsMyInput.title })).toBeVisible()
      await expect(page.getByRole('heading', { name: section.readyToDecide.title })).toBeVisible()
      await expect(page.getByRole('heading', { name: section.needsLearning.title })).toBeVisible()
      await expect(entries(page)).toHaveCount(4)
      await expect(entries(page).first().locator('.inbox-entry-kind')).toHaveText(copy.kinds.space_needs_convergence)
      await expect(entries(page).first().locator('.inbox-entry-question')).toHaveText('Which pricing should we pick?')
      await expect(entries(page).nth(1).locator('.inbox-entry-kind')).toHaveText(copy.kinds.contribution_awaits_confirmation)
    })

    test('INBOX-02 sends every entry to the section where it can be acted on', async ({ page }) => {
      await serveInbox(page, emptyInbox({
        needs_convergence: makeSection([makeEntry()]),
        needs_my_input: makeSection([makeEntry({
          kind: 'contribution_awaits_confirmation',
          subject_id: 'contribution-one',
          detail: 'Churn does not follow price',
        })]),
        ready_to_decide: makeSection([makeEntry({
          kind: 'finding_awaits_resolution',
          subject_id: 'finding-one',
          detail: 'Nothing supports the claim',
        })]),
        needs_learning: makeSection([makeEntry({
          kind: 'learning_awaits_confirmation',
          subject_id: 'learning-one',
          detail: 'Churn did not follow the price.',
        })]),
      }))

      await openInbox(page)

      const links = entries(page).locator('.inbox-entry-link')
      await expect(links.nth(0)).toHaveAttribute(
        'href',
        `${prefix}/workspace/decision-spaces/space-one/converge?workspace=workspace-one`,
      )
      await expect(links.nth(1)).toHaveAttribute(
        'href',
        `${prefix}/workspace/decision-spaces/space-one/explore?workspace=workspace-one`,
      )
      await expect(links.nth(2)).toHaveAttribute(
        'href',
        `${prefix}/workspace/decision-spaces/space-one/decision?workspace=workspace-one`,
      )
      await expect(links.nth(3)).toHaveAttribute(
        'href',
        `${prefix}/workspace/decision-spaces/space-one/learning?workspace=workspace-one`,
      )
    })

    test('INBOX-03 says how many entries a section holds beyond the ones it shows', async ({ page }) => {
      await serveInbox(page, emptyInbox({
        needs_convergence: makeSection([makeEntry()], 4),
      }))

      await openInbox(page)

      await expect(blocks(page).first().locator('.inbox-more')).toHaveText(pluralLabel(copy.more, 3))
    })

    test('INBOX-04 tells apart the work that waits on the reader', async ({ page }) => {
      await serveInbox(page, emptyInbox({
        needs_my_input: makeSection([
          makeEntry({
            kind: 'contribution_awaits_confirmation',
            subject_id: 'contribution-one',
            detail: 'Churn does not follow price',
          }),
          makeEntry({
            kind: 'finding_awaits_resolution',
            subject_id: 'finding-one',
            detail: 'Nothing supports the claim',
            created_at: '2026-09-16T09:00:00Z',
          }),
        ]),
      }))

      await openInbox(page)

      await expect(entries(page).nth(0).locator('.inbox-entry-kind')).toHaveText(copy.kinds.contribution_awaits_confirmation)
      await expect(entries(page).nth(1).locator('.inbox-entry-kind')).toHaveText(copy.kinds.finding_awaits_resolution)
      await expect(entries(page).nth(0).locator('.inbox-entry-detail')).toHaveText('Churn does not follow price')
    })

    test('INBOX-05 shows an honest empty state when nothing waits', async ({ page }) => {
      await serveInbox(page, emptyInbox())

      await openInbox(page)

      await expect(page.locator('.inbox-empty-state h2')).toHaveText(copy.empty.title)
      await expect(page.locator('.inbox-empty-state p')).toHaveText(copy.empty.body)
      await expect(entries(page)).toHaveCount(0)
    })

    test('INBOX-06 says an empty section is empty', async ({ page }) => {
      await serveInbox(page, emptyInbox({
        needs_convergence: makeSection([makeEntry()]),
      }))

      await openInbox(page)

      await expect(blocks(page).nth(1).locator('.inbox-empty')).toHaveText(section.needsMyInput.empty)
      await expect(blocks(page).nth(2).locator('.inbox-empty')).toHaveText(section.readyToDecide.empty)
      await expect(blocks(page).nth(3).locator('.inbox-empty')).toHaveText(section.needsLearning.empty)
    })

    test('INBOX-07 explains the section it cannot answer instead of showing an empty one', async ({ page }) => {
      await serveInbox(page, emptyInbox({
        needs_convergence: makeSection([makeEntry()]),
      }))

      await openInbox(page)

      const memory = page.locator('.inbox-memory')
      await expect(memory.locator('h2')).toHaveText(copy.memory.title)
      await expect(memory.locator('.inbox-intro')).toHaveText(copy.memory.body)
      await expect(memory.locator('.inbox-list')).toHaveCount(0)
      await expect(memory.locator('.inbox-empty')).toHaveCount(0)
    })

    test('INBOX-08 says so when the inbox could not be read', async ({ page }) => {
      await serveInbox(page, emptyInbox(), { fail: true })

      await openInbox(page)

      await expect(page.getByRole('alert')).toHaveText(copy.loadFailed)
      await expect(page.locator('.inbox-header h1')).toHaveText(copy.title)
    })

    test('INBOX-09 leads to the decision spaces list', async ({ page }) => {
      await serveInbox(page, emptyInbox())

      await openInbox(page)

      await expect(page.locator('.inbox-spaces-link')).toHaveAttribute('href', `${prefix}/workspace/decision-spaces`)
      await expect(page.locator('.inbox-spaces-link')).toHaveText(copy.spacesLink)
    })
  })
}
