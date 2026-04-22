type PwaUpdateState = {
  needRefresh: boolean
}

const UPDATE_EVENT = 'agroadb:pwa-update'
const updateState: PwaUpdateState = {
  needRefresh: false,
}
let registrationRef: ServiceWorkerRegistration | null = null
let lifecycleListenersRegistered = false

function emitUpdate() {
  window.dispatchEvent(new CustomEvent(UPDATE_EVENT, { detail: updateState }))
}

function setNeedRefresh(nextValue: boolean) {
  updateState.needRefresh = nextValue
  emitUpdate()
}

function watchRegistration(registration: ServiceWorkerRegistration) {
  registrationRef = registration

  if (registration.waiting && navigator.serviceWorker.controller) {
    setNeedRefresh(true)
  }

  registration.addEventListener('updatefound', () => {
    const installing = registration.installing
    if (!installing) return

    installing.addEventListener('statechange', () => {
      if (installing.state === 'installed' && navigator.serviceWorker.controller) {
        setNeedRefresh(true)
      }
    })
  })
}

async function refreshRegistration() {
  if (!registrationRef) return

  try {
    await registrationRef.update()
    if (registrationRef.waiting && navigator.serviceWorker.controller) {
      setNeedRefresh(true)
    }
  } catch {
    // Falha silenciosa para nao interferir na navegacao.
  }
}

function registerLifecycleListeners() {
  if (lifecycleListenersRegistered) return
  lifecycleListenersRegistered = true

  const handleVisibility = () => {
    if (document.visibilityState === 'visible') {
      void refreshRegistration()
    }
  }

  const handleOnline = () => {
    void refreshRegistration()
  }

  document.addEventListener('visibilitychange', handleVisibility)
  window.addEventListener('online', handleOnline)
}

export function getPwaUpdateState() {
  return updateState
}

export function subscribePwaUpdates(listener: (state: PwaUpdateState) => void) {
  const handler = (event: Event) => {
    listener((event as CustomEvent<PwaUpdateState>).detail)
  }

  window.addEventListener(UPDATE_EVENT, handler)
  listener(updateState)

  return () => window.removeEventListener(UPDATE_EVENT, handler)
}

export async function activateWaitingServiceWorker() {
  if (!registrationRef?.waiting) return

  await new Promise<void>((resolve) => {
    const onControllerChange = () => {
      navigator.serviceWorker.removeEventListener('controllerchange', onControllerChange)
      resolve()
    }
    navigator.serviceWorker.addEventListener('controllerchange', onControllerChange)
    registrationRef?.waiting?.postMessage({ type: 'SKIP_WAITING' })
  })

  setNeedRefresh(false)
  window.location.reload()
}

export async function registerServiceWorker() {
  if (!('serviceWorker' in navigator) || import.meta.env.DEV) {
    return
  }

  const register = async () => {
    try {
      const registration = await navigator.serviceWorker.register(`${import.meta.env.BASE_URL}sw.js`)
      watchRegistration(registration)
      registerLifecycleListeners()
      void refreshRegistration()
      window.setInterval(() => {
        void refreshRegistration()
      }, 60 * 60 * 1000)
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
