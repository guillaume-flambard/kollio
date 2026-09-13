import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/browser',
  timeout: 30_000,
  forbidOnly: Boolean(process.env.CI),
  retries: 0,
  workers: 1,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: 'http://127.0.0.1:3197',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: {
    command: 'pnpm exec nuxt dev tests/browser/fixture --host 127.0.0.1 --port 3197',
    url: 'http://127.0.0.1:3197',
    reuseExistingServer: false,
    timeout: 120_000,
    env: { NUXT_PUBLIC_AUTH_ENABLED: 'false' },
  },
})
