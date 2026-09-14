import { removeIdeaMember } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const ideaId = getRouterParam(event, 'ideaId')
  const memberId = getRouterParam(event, 'memberId')
  if (!ideaId || !memberId) {
    throw createError({ statusCode: 400, statusMessage: 'Identifiers required' })
  }

  const client = await createKollioApiClient(event)
  const result = await removeIdeaMember({
    client,
    path: { idea_id: ideaId as never, member_id: memberId as never },
    body: null,
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
