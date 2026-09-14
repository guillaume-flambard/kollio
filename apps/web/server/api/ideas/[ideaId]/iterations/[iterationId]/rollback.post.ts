import { rollbackIdeaIteration } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const ideaId = getRouterParam(event, 'ideaId')
  const iterationId = getRouterParam(event, 'iterationId')
  if (!ideaId || !iterationId) {
    throw createError({ statusCode: 400, statusMessage: 'Identifiers required' })
  }

  const body = await readBody(event)
  if (typeof body?.message !== 'string' || body.message.trim() === '') {
    throw createError({ statusCode: 422, statusMessage: 'A message is required' })
  }
  const expectedMainParentId = typeof body.expected_parent_id === 'string' ? body.expected_parent_id : null

  const client = await createKollioApiClient(event)
  const result = await rollbackIdeaIteration({
    client,
    path: { idea_id: ideaId as never, iteration_id: iterationId as never },
    body: {
      message: body.message,
      lang: body.lang === 'fr' ? 'fr' : 'en',
      expected_main_parent_id: expectedMainParentId,
    },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
