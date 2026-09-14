import { createCompanyObjective } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../utils/kollio-api'
import { requiredTitle } from '../../../../../utils/validation'

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  if (!workspaceId) {
    throw createError({ statusCode: 400, statusMessage: 'Workspace identifier required' })
  }

  const title = requiredTitle(await readBody(event))
  const client = await createKollioApiClient(event)
  const result = await createCompanyObjective({
    client,
    path: { workspace_id: workspaceId },
    body: { title },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
