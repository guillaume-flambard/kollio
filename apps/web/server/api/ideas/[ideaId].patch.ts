import { updateIdeaInitiativeType } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../utils/kollio-api'
import { requiredInitiativeType } from '../../utils/initiative'

export default defineEventHandler(async (event) => {
  const ideaId = getRouterParam(event, 'ideaId')
  if (!ideaId) {
    throw createError({ statusCode: 400, statusMessage: 'Idea identifier required' })
  }

  const body = await readBody(event)
  const initiativeType = requiredInitiativeType(body?.initiative_type)

  const client = await createKollioApiClient(event)
  const result = await updateIdeaInitiativeType({
    client,
    path: { idea_id: ideaId },
    body: { initiative_type: initiativeType },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
