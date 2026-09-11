const API_AUDIENCE = 'https://kollio.memolabs.dev/api'

export default defineEventHandler(async (event) => {
  if (!event.context.logtoUser) {
    throw createError({ statusCode: 401, statusMessage: 'Authentication required' })
  }

  const ideaId = getRouterParam(event, 'ideaId')
  if (!ideaId) {
    throw createError({ statusCode: 400, statusMessage: 'Idea identifier required' })
  }

  const accessToken = await event.context.logtoClient.getAccessToken(API_AUDIENCE)
  const config = useRuntimeConfig(event)
  return await $fetch(`/ideas/${encodeURIComponent(ideaId)}`, {
    baseURL: config.apiBase,
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'Accept-Language': getHeader(event, 'accept-language') ?? 'fr',
    },
  })
})
