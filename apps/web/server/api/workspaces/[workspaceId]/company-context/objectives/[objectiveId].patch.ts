import type { ObjectiveUpdate } from '@kollio/api-client'
import { updateCompanyObjective } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  const objectiveId = getRouterParam(event, 'objectiveId')
  if (!workspaceId || !objectiveId) {
    throw createError({ statusCode: 400, statusMessage: 'Identifiers required' })
  }

  const body = (await readBody(event)) as Record<string, unknown>
  const patch: ObjectiveUpdate = {}
  if (typeof body?.title === 'string' && body.title.trim() !== '') patch.title = body.title.trim()
  if (body?.state === 'active' || body?.state === 'archived') patch.state = body.state
  if (typeof body?.priority === 'boolean') patch.priority = body.priority

  const client = await createKollioApiClient(event)
  const result = await updateCompanyObjective({
    client,
    path: { workspace_id: workspaceId, objective_id: objectiveId },
    body: patch,
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
