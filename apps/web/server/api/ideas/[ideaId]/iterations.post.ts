import { createIdeaIteration } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const ideaId = getRouterParam(event, 'ideaId')
  if (!ideaId) {
    throw createError({ statusCode: 400, statusMessage: 'Idea identifier required' })
  }

  const body = await readBody(event)
  if (
    typeof body?.message !== 'string'
    || body.message.trim() === ''
    || typeof body?.snapshot?.title !== 'string'
    || body.snapshot.title.trim() === ''
    || typeof body?.snapshot?.pitch !== 'string'
    || body.snapshot.pitch.trim() === ''
  ) {
    throw createError({ statusCode: 422, statusMessage: 'Message and snapshot are required' })
  }
  const branch = typeof body.branch === 'string' && /^proposal\/[a-z0-9][a-z0-9._-]{0,47}$/.test(body.branch)
    ? body.branch
    : undefined
  const expectedParentId = typeof body.expected_parent_id === 'string' ? body.expected_parent_id : null

  const client = await createKollioApiClient(event)
  const result = await createIdeaIteration({
    client,
    path: { idea_id: ideaId },
    body: {
      message: body.message,
      lang: body.lang === 'fr' ? 'fr' : 'en',
      snapshot: {
        title: body.snapshot.title,
        pitch: body.snapshot.pitch,
        stage: ['seed', 'iterating', 'team_formed'].includes(body.snapshot.stage)
          ? body.snapshot.stage
          : 'seed',
      },
      branch,
      expected_parent_id: expectedParentId,
    },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
