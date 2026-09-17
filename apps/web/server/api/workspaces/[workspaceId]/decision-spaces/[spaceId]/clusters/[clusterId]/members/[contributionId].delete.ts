import { removeClusterMember } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../../../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  const spaceId = getRouterParam(event, 'spaceId')
  const clusterId = getRouterParam(event, 'clusterId')
  const contributionId = getRouterParam(event, 'contributionId')
  if (!workspaceId || !spaceId || !clusterId || !contributionId) {
    throw createError({ statusCode: 400, statusMessage: 'Workspace, decision space, cluster and contribution identifiers required' })
  }

  const client = await createKollioApiClient(event)
  const result = await removeClusterMember({
    client,
    path: {
      workspace_id: workspaceId as never,
      space_id: spaceId as never,
      cluster_id: clusterId as never,
      contribution_id: contributionId as never,
    },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data ?? null
})
