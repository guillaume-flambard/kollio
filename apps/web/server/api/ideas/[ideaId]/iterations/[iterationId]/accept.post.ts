import { acceptIdeaIteration } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const ideaId = getRouterParam(event, 'ideaId')
  const iterationId = getRouterParam(event, 'iterationId')
  if (!ideaId || !iterationId) {
    throw createError({ statusCode: 400, statusMessage: 'Identifiers required' })
  }

  const body = await readBody(event).catch(() => ({}))
  const expectedMainParentId = typeof body?.expected_parent_id === 'string' ? body.expected_parent_id : null

  const client = await createKollioApiClient(event)
  const result = await acceptIdeaIteration({
    client,
    path: { idea_id: ideaId as never, iteration_id: iterationId as never },
    body: { expected_main_parent_id: expectedMainParentId },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
