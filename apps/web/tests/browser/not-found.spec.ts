import { expect, test } from '@playwright/test'
import fr from '../../i18n/locales/fr.json' with { type: 'json' }
import en from '../../i18n/locales/en.json' with { type: 'json' }

for (const [locale, messages] of [['fr', fr], ['en', en]] as const) {
  test.describe(locale, () => {
    const prefix = locale === 'fr' ? '' : '/en'
    const copy = messages.errors.notFound
    const homeHref = locale === 'fr' ? '/' : '/en'

    test('NOT-FOUND-01 answers an unknown path in the reader locale', async ({ page }) => {
      await page.goto(`${prefix}/no-such-page`)

      await expect(page.locator('html')).toHaveAttribute('lang', locale === 'fr' ? 'fr-FR' : 'en-GB')
      await expect(page.getByRole('heading', { level: 1 })).toHaveText(copy.title)
      await expect(page.getByText(copy.description)).toBeVisible()
      await expect(page.getByRole('link', { name: copy.action })).toHaveAttribute('href', homeHref)
      await expect(page.locator('body')).not.toContainText('errors.')
    })
  })
}
