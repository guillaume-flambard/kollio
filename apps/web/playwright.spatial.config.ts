import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/browser',
  testMatch: 'spatial-v3.spec.ts',
  timeout: 45_000,
  expect: { timeout: 15_000 },
  retries: 0,
  workers: 1,
  reporter: 'list',
  use: {
    baseURL: 'http://127.0.0.1:3198',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    ...devices['Desktop Chrome'],
  },
  webServer: {
    command: 'pnpm exec nuxt dev --host 127.0.0.1 --port 3198',
    url: 'http://127.0.0.1:3198/spatial-v3?stress=100',
    reuseExistingServer: !process.env.CI,
    timeout: 180_000,
    env: { NUXT_PUBLIC_AUTH_ENABLED: 'false' },
  },
})
