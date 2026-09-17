import { deleteScenarioVariable } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  const spaceId = getRouterParam(event, 'spaceId')
  const variableId = getRouterParam(event, 'variableId')
  if (!workspaceId || !spaceId || !variableId) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Workspace, decision space and variable identifiers required',
    })
  }

  const client = await createKollioApiClient(event)
  const result = await deleteScenarioVariable({
    client,
    path: { workspace_id: workspaceId as never, space_id: spaceId as never, variable_id: variableId as never },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return null
})
