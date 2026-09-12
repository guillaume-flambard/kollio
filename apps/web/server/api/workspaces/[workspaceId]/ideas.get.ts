import { listWorkspaceIdeas } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  if (!workspaceId) {
    throw createError({ statusCode: 400, statusMessage: 'Workspace identifier required' })
  }

  const query = getQuery(event)
  const limit = Number(query.limit ?? 24)
  const offset = Number(query.offset ?? 0)
  const client = await createKollioApiClient(event)
  const result = await listWorkspaceIdeas({
    client,
    path: { workspace_id: workspaceId },
    query: { limit, offset },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
