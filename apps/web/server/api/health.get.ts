import { healthReady } from '@kollio/api-client'

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig(event)
  const { data } = await healthReady({
    baseUrl: config.apiBase,
    headers: { 'Accept-Language': getHeader(event, 'accept-language') || 'fr' },
    throwOnError: true,
  })
  return data
})
