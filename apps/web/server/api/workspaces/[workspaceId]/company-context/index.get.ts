import { getCompanyContext } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  if (!workspaceId) {
    throw createError({ statusCode: 400, statusMessage: 'Workspace identifier required' })
  }

  const client = await createKollioApiClient(event)
  const result = await getCompanyContext({ client, path: { workspace_id: workspaceId } })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
