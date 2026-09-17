import { listContributions } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  const spaceId = getRouterParam(event, 'spaceId')
  if (!workspaceId || !spaceId) {
    throw createError({ statusCode: 400, statusMessage: 'Workspace and decision space identifiers required' })
  }

  const client = await createKollioApiClient(event)
  const result = await listContributions({
    client,
    path: { workspace_id: workspaceId as never, space_id: spaceId as never },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
