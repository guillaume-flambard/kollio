import { depositWorkspaceIdea } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  if (!workspaceId) {
    throw createError({ statusCode: 400, statusMessage: 'Workspace identifier required' })
  }

  const body = await readBody(event)
  const title = typeof body?.title === 'string' ? body.title.trim() : ''
  const pitch = typeof body?.pitch === 'string' ? body.pitch.trim() : ''
  const lang = body?.lang === 'en' || body?.lang === 'fr' ? body.lang : undefined
  if (!title || !pitch) {
    throw createError({ statusCode: 422, statusMessage: 'Title and pitch are required' })
  }

  const client = await createKollioApiClient(event)
  const result = await depositWorkspaceIdea({
    client,
    path: { workspace_id: workspaceId },
    body: { title, pitch, lang },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
