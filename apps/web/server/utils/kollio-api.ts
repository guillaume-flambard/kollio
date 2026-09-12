import { createClient } from '@kollio/api-client/client'
import type { H3Event } from 'h3'

const API_AUDIENCE = 'https://kollio.memolabs.dev/api'

export async function createKollioApiClient(event: H3Event) {
  if (!event.context.logtoUser) {
    throw createError({ statusCode: 401, statusMessage: 'Authentication required' })
  }

  const accessToken = await event.context.logtoClient.getAccessToken(API_AUDIENCE)
  const config = useRuntimeConfig(event)
  return createClient({
    baseUrl: config.apiBase,
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'Accept-Language': getHeader(event, 'accept-language') ?? 'fr',
    },
  })
}

export function forwardApiError(status: number, error: unknown): never {
  const detail =
    typeof error === 'object' && error !== null && 'detail' in error
      ? String(error.detail)
      : 'Kollio API request failed'
  throw createError({ statusCode: status, statusMessage: detail })
}
