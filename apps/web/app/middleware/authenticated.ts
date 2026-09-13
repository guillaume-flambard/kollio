export default defineNuxtRouteMiddleware(async () => {
  const config = useRuntimeConfig()
  const authEnabled = config.public.authEnabled === true || String(config.public.authEnabled) === 'true'

  if (!authEnabled) return

  const { data: session } = await useFetch('/api/session', { key: 'auth-session' })
  if (!session.value?.signedIn) {
    return navigateTo('/sign-in', { external: true })
  }
})
