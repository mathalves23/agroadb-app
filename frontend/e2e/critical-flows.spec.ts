import { test, expect } from '@playwright/test'
import { mockAuthenticatedApi } from './api-mock'

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
