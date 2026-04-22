export async function registerServiceWorker() {
  if (!('serviceWorker' in navigator) || import.meta.env.DEV) {
    return
  }

  const register = async () => {
    try {
      await navigator.serviceWorker.register(`${import.meta.env.BASE_URL}sw.js`)
    } catch {
      // Falha silenciosa para nao bloquear bootstrap da UI.
    }
  }

  if (document.readyState === 'complete') {
    await register()
    return
  }

  window.addEventListener('load', () => {
    void register()
  })
}
