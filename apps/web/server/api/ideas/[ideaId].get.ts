import { getIdea } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const ideaId = getRouterParam(event, 'ideaId')
  if (!ideaId) {
    throw createError({ statusCode: 400, statusMessage: 'Idea identifier required' })
  }

  const client = await createKollioApiClient(event)
  const result = await getIdea({ client, path: { idea_id: ideaId } })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
