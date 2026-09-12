export default defineNuxtRouteMiddleware(async () => {
  const { data: session } = await useFetch('/api/session', { key: 'auth-session' })
  if (!session.value?.signedIn) {
    return navigateTo('/sign-in', { external: true })
  }
})
