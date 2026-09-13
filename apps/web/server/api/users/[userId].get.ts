import { getProfile } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const userId = getRouterParam(event, 'userId')
  if (!userId) {
    throw createError({ statusCode: 400, statusMessage: 'User identifier required' })
  }

  const client = await createKollioApiClient(event)
  const result = await getProfile({
    client,
    path: { user_id: userId as never },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
