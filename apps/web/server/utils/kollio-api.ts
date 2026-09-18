import { createClient } from '@kollio/api-client/client'
import type { H3Event } from 'h3'

export async function createKollioApiClient(event: H3Event) {
  if (!event.context.logtoUser) {
    throw createError({ statusCode: 401, statusMessage: 'Authentication required' })
  }

  const config = useRuntimeConfig(event)
  const [audience] = (config.logto.resources ?? []) as string[]
  if (!audience) {
    throw createError({ statusCode: 500, statusMessage: 'No API resource is configured' })
  }

  const accessToken = await event.context.logtoClient.getAccessToken(audience)
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
