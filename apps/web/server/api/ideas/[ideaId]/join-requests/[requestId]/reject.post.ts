import { rejectIdeaMembershipRequest } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const ideaId = getRouterParam(event, 'ideaId')
  const requestId = getRouterParam(event, 'requestId')
  if (!ideaId || !requestId) {
    throw createError({ statusCode: 400, statusMessage: 'Identifiers required' })
  }

  const body = await readBody(event)
  if (typeof body?.rationale !== 'string' || body.rationale.trim() === '') {
    throw createError({ statusCode: 422, statusMessage: 'A short rationale is required' })
  }

  const client = await createKollioApiClient(event)
  const result = await rejectIdeaMembershipRequest({
    client,
    path: { idea_id: ideaId as never, request_id: requestId as never },
    body: { rationale: body.rationale },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
