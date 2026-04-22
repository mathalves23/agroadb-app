import { expect, test } from '@playwright/test'
import { mockAuthenticatedApi } from './api-mock'

test.describe('Resiliência offline e sessão persistida', () => {
  test('permite reload offline exibindo feedback de conectividade', async ({ page, context }) => {
    const apiState: { mode: 'online' | 'degraded' } = { mode: 'online' }
    await mockAuthenticatedApi(context, { state: apiState })

    await page.goto('/login')
    await page.getByLabel('Usuário ou Email').fill('e2euser')
    await page.getByLabel('Senha', { exact: true }).fill('password12')
    await page.getByRole('button', { name: 'Entrar' }).click()
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible({ timeout: 20_000 })

    await context.addInitScript(() => {
      Object.defineProperty(window.navigator, 'onLine', {
        configurable: true,
        get: () => false,
      })
    })
    await page.reload()

    await expect(page.getByText(/você está offline/i)).toBeVisible()
  })

  test('sinaliza retorno da conexão após estado offline', async ({ page, context }) => {
    const apiState: { mode: 'online' | 'degraded' } = { mode: 'online' }
    await mockAuthenticatedApi(context, { state: apiState })

    await page.goto('/login')
    await page.getByLabel('Usuário ou Email').fill('e2euser')
    await page.getByLabel('Senha', { exact: true }).fill('password12')
    await page.getByRole('button', { name: 'Entrar' }).click()
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible({ timeout: 20_000 })

    await context.setOffline(true)
    await expect(page.getByText(/você está offline/i)).toBeVisible()

    await context.setOffline(false)

    await expect(page.getByText(/conexão restabelecida|backend restabelecido/i)).toBeVisible({
      timeout: 15_000,
    })
  })

  test('mantém a sessão após reload e reabertura da app shell', async ({ page, context }) => {
    const apiState: { mode: 'online' | 'degraded' } = { mode: 'online' }
    await mockAuthenticatedApi(context, { state: apiState })

    await page.goto('/login')
    await page.getByLabel('Usuário ou Email').fill('e2euser')
    await page.getByLabel('Senha', { exact: true }).fill('password12')
    await page.getByRole('button', { name: 'Entrar' }).click()
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible({ timeout: 20_000 })

    await page.reload()
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible()

    await page.close()

    const reopened = await context.newPage()
    await reopened.goto('/dashboard')
    await expect(reopened.getByRole('heading', { name: 'Dashboard' })).toBeVisible()
  })

  test('usa snapshots locais quando a API cai após uma carga bem-sucedida', async ({
    page,
    context,
  }) => {
    const apiState: { mode: 'online' | 'degraded' } = { mode: 'online' }
    await mockAuthenticatedApi(context, { state: apiState })

    await page.goto('/login')
    await page.getByLabel('Usuário ou Email').fill('e2euser')
    await page.getByLabel('Senha', { exact: true }).fill('password12')
    await page.getByRole('button', { name: 'Entrar' }).click()
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible({ timeout: 20_000 })

    await expect
      .poll(async () =>
        page.evaluate(() =>
          Object.keys(window.localStorage).some((key) =>
            key.includes('agroadb:offline-snapshot:/investigations/dashboard-statistics')
          )
        )
      )
      .toBe(true)

    apiState.mode = 'degraded'

    await page.reload()
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible()
    await expect(
      page.getByText(/backend indisponível|backend ainda não respondeu|offline/i)
    ).toBeVisible()
  })

  test('exibe prompt quando uma atualização do service worker fica disponível', async ({
    page,
    context,
  }) => {
    const apiState: { mode: 'online' | 'degraded' } = { mode: 'online' }
    await mockAuthenticatedApi(context, { state: apiState })

    await page.goto('/login')
    await page.getByLabel('Usuário ou Email').fill('e2euser')
    await page.getByLabel('Senha', { exact: true }).fill('password12')
    await page.getByRole('button', { name: 'Entrar' }).click()
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible({ timeout: 20_000 })

    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent('agroadb:pwa-update', {
          detail: { needRefresh: true },
        })
      )
    })

    await expect(page.getByText(/atualização pronta/i)).toBeVisible()
    await expect(page.getByRole('button', { name: /atualizar app/i })).toBeVisible()
  })
})
