import type { Page } from '@playwright/test'

const tokens = {
  access_token: 'e2e-access-token',
  refresh_token: 'e2e-refresh-token',
  token_type: 'bearer',
}

const mockUser = {
  id: 1,
  email: 'e2e@test.local',
  username: 'e2euser',
  full_name: 'Utilizador E2E',
  is_active: true,
  is_superuser: false,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
}

/** Respostas mínimas para sessão autenticada (login, /me, dashboard, barra). */
export async function mockAuthenticatedApi(page: Page) {
  await page.route('**/api/v1/auth/login', async (route) => {
    if (route.request().method() !== 'POST') {
      await route.continue()
      return
    }
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(tokens),
    })
  })
  await page.route('**/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockUser),
    })
  })
  await page.route('**/api/v1/investigations?**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: [],
        total: 0,
        page: 1,
        page_size: 20,
        total_pages: 0,
      }),
    })
  })
  await page.route('**/api/v1/legal/queries/summary', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ summary: {}, updated_at: '2024-01-01T00:00:00Z' }),
    })
  })
  await page.route('**/api/v1/investigations/dashboard-statistics', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        investigations_by_month: [],
        scrapers_performance: [],
        properties_by_state: [],
        status_distribution: [],
      }),
    })
  })
  await page.route('**/api/v1/notifications/unread/count', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ count: 0 }),
    })
  })
}
