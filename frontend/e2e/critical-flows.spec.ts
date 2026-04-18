import { test, expect, type Page } from '@playwright/test'

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

async function mockAuthenticatedApi(page: Page) {
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

test.describe('Fluxos críticos', () => {
  test('login e dashboard', async ({ page }) => {
    await mockAuthenticatedApi(page)
    await page.goto('/login')
    await page.getByLabel('Usuário ou Email').fill('e2euser')
    await page.getByLabel('Senha', { exact: true }).fill('password12')
    await page.getByRole('button', { name: 'Entrar' }).click()
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible({ timeout: 20_000 })
  })

  test('registo e redirecionamento para login', async ({ page }) => {
    await page.route('**/api/v1/auth/register', async (route) => {
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 2,
          email: 'novo@test.local',
          username: 'novouser',
          full_name: 'Novo Utilizador',
          is_active: true,
          is_superuser: false,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        }),
      })
    })
    await page.goto('/register')
    await page.locator('#full_name').fill('Novo Utilizador')
    await page.locator('#email').fill('novo@test.local')
    await page.locator('#username').fill('novouser')
    await page.locator('#password').fill('password12')
    await page.getByRole('button', { name: 'Criar Conta' }).click()
    await expect(page).toHaveURL(/\/login$/)
    await expect(page.getByRole('heading', { name: 'Entrar' })).toBeVisible()
  })
})
