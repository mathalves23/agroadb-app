import { defineConfig, devices } from '@playwright/test'

const sub =
  (process.env.VITE_BASE_PATH || '/').replace(/\/+/g, '/').replace(/\/$/, '') || ''
const origin = 'http://127.0.0.1:5173'
const baseURL = sub && sub !== '/' ? `${origin}/${sub}` : origin

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? 'line' : 'list',
  use: {
    baseURL,
    trace: 'on-first-retry',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: {
    command: 'npm run dev -- --host 127.0.0.1 --port 5173 --strictPort',
    url: `${baseURL}/`,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    cwd: __dirname,
    env: {
      ...process.env,
      VITE_BASE_PATH: process.env.VITE_BASE_PATH || '/',
    },
  },
})
