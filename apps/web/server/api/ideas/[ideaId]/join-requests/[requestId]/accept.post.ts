import { acceptIdeaMembershipRequest } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const ideaId = getRouterParam(event, 'ideaId')
  const requestId = getRouterParam(event, 'requestId')
  if (!ideaId || !requestId) {
    throw createError({ statusCode: 400, statusMessage: 'Identifiers required' })
  }

  const client = await createKollioApiClient(event)
  const result = await acceptIdeaMembershipRequest({
    client,
    path: { idea_id: ideaId as never, request_id: requestId as never },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
