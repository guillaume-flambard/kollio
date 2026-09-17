import { deleteCluster } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  const spaceId = getRouterParam(event, 'spaceId')
  const clusterId = getRouterParam(event, 'clusterId')
  if (!workspaceId || !spaceId || !clusterId) {
    throw createError({ statusCode: 400, statusMessage: 'Workspace, decision space and cluster identifiers required' })
  }

  const client = await createKollioApiClient(event)
  const result = await deleteCluster({
    client,
    path: {
      workspace_id: workspaceId as never,
      space_id: spaceId as never,
      cluster_id: clusterId as never,
    },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return null
})
