import { rejectIdeaIteration } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const ideaId = getRouterParam(event, 'ideaId')
  const iterationId = getRouterParam(event, 'iterationId')
  if (!ideaId || !iterationId) {
    throw createError({ statusCode: 400, statusMessage: 'Identifiers required' })
  }

  const body = await readBody(event)
  const rationale = typeof body?.rationale === 'string' ? body.rationale.trim() : ''
  if (rationale === '') {
    throw createError({ statusCode: 422, statusMessage: 'A short rationale is required' })
  }

  const client = await createKollioApiClient(event)
  const result = await rejectIdeaIteration({
    client,
    path: { idea_id: ideaId as never, iteration_id: iterationId as never },
    body: { rationale },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
