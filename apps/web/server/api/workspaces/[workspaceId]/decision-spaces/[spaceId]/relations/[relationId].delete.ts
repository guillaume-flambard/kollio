import { deleteRelation } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  const spaceId = getRouterParam(event, 'spaceId')
  const relationId = getRouterParam(event, 'relationId')
  if (!workspaceId || !spaceId || !relationId) {
    throw createError({ statusCode: 400, statusMessage: 'Workspace, decision space and relation identifiers required' })
  }

  const client = await createKollioApiClient(event)
  const result = await deleteRelation({
    client,
    path: {
      workspace_id: workspaceId as never,
      space_id: spaceId as never,
      relation_id: relationId as never,
    },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return null
})
