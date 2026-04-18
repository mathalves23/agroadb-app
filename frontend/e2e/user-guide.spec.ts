import { test, expect } from '@playwright/test'
import { mockAuthenticatedApi } from './api-mock'

test.describe('Manual do utilizador (/guide)', () => {
  test('após login, /guide mostra título ou conteúdo canónico do manual', async ({ page }) => {
    await mockAuthenticatedApi(page)
    await page.goto('/login')
    await page.getByLabel('Usuário ou Email').fill('e2euser')
    await page.getByLabel('Senha', { exact: true }).fill('password12')
    await page.getByRole('button', { name: 'Entrar' }).click()
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible({ timeout: 20_000 })

    await page.goto('/guide')
    await expect(page.getByRole('heading', { level: 1, name: /Manual do utilizador/ })).toBeVisible({
      timeout: 15_000,
    })
    await expect(page.getByText('Mapa de menus', { exact: false })).toBeVisible()
  })
})
