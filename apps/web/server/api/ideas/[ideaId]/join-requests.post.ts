import { requestIdeaMembership } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const ideaId = getRouterParam(event, 'ideaId')
  if (!ideaId) {
    throw createError({ statusCode: 400, statusMessage: 'Idea identifier required' })
  }

  const body = await readBody(event)
  if (typeof body?.role !== 'string' || body.role === '' || typeof body?.note !== 'string' || body.note.trim() === '') {
    throw createError({ statusCode: 422, statusMessage: 'Role and note are required' })
  }

  const client = await createKollioApiClient(event)
  const result = await requestIdeaMembership({
    client,
    path: { idea_id: ideaId as never },
    body: { role: body.role, note: body.note },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
