import type { BrowserContext, Page, Route } from '@playwright/test'

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
export async function mockAuthenticatedApi(
  target: Page | BrowserContext,
  options?: { state?: { mode: 'online' | 'degraded' } }
) {
  const state: { mode: 'online' | 'degraded' } = options?.state ?? { mode: 'online' }

  const fulfillJson = async (route: Route, body: unknown) => {
    if (state.mode === 'degraded') {
      await route.fulfill({
        status: 503,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'backend unavailable' }),
      })
      return
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(body),
    })
  }

  await target.route('**/health', async (route) => {
    if (state.mode === 'degraded') {
      await route.fulfill({
        status: 503,
        contentType: 'application/json',
        body: JSON.stringify({ status: 'degraded' }),
      })
      return
    }
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ status: 'healthy' }),
    })
  })

  await target.route('**/api/v1/auth/login', async (route) => {
    if (route.request().method() !== 'POST') {
      await route.continue()
      return
    }
    await fulfillJson(route, tokens)
  })
  await target.route('**/api/v1/auth/me', async (route) => {
    await fulfillJson(route, mockUser)
  })
  await target.route('**/api/v1/investigations?**', async (route) => {
    await fulfillJson(route, {
      items: [],
      total: 0,
      page: 1,
      page_size: 20,
      total_pages: 0,
    })
  })
  await target.route('**/api/v1/legal/queries/summary', async (route) => {
    await fulfillJson(route, { summary: {}, updated_at: '2024-01-01T00:00:00Z' })
  })
  await target.route('**/api/v1/investigations/dashboard-statistics', async (route) => {
    await fulfillJson(route, {
      investigations_by_month: [],
      scrapers_performance: [],
      properties_by_state: [],
      status_distribution: [],
    })
  })
  await target.route('**/api/v1/notifications/unread/count', async (route) => {
    await fulfillJson(route, { count: 0 })
  })
  await target.route('**/api/v1/notifications/**', async (route) => {
    await fulfillJson(route, [])
  })
}
