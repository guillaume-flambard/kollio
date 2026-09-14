import { addIdeaParticipant } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const ideaId = getRouterParam(event, 'ideaId')
  if (!ideaId) {
    throw createError({ statusCode: 400, statusMessage: 'Idea identifier required' })
  }

  const body = await readBody(event)
  const hasMember = typeof body?.user_id === 'string' && body.user_id !== ''
  const hasParticipation = typeof body?.participation === 'string' && body.participation !== ''
  const hasFunction = typeof body?.function === 'string' && body.function !== ''
  if (!hasMember || !hasParticipation || !hasFunction) {
    throw createError({
      statusCode: 422,
      statusMessage: 'Colleague, participation and function are required',
    })
  }

  const client = await createKollioApiClient(event)
  const result = await addIdeaParticipant({
    client,
    path: { idea_id: ideaId as never },
    body: {
      user_id: body.user_id,
      participation: body.participation,
      function: body.function,
    },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
