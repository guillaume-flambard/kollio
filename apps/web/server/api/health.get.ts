import { healthLive } from '@kollio/api-client'

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig(event)
  const { data } = await healthLive({
    baseUrl: config.apiBase,
    headers: { 'Accept-Language': getHeader(event, 'accept-language') || 'fr' },
    throwOnError: true,
  })
  return data
})
