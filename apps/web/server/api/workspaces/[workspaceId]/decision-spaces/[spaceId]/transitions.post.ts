import { transitionDecisionSpace } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  const spaceId = getRouterParam(event, 'spaceId')
  if (!workspaceId || !spaceId) {
    throw createError({ statusCode: 400, statusMessage: 'Workspace and decision space identifiers required' })
  }

  const body = await readBody<{ to_status?: string, reason?: string | null }>(event)
  const toStatus = body?.to_status ?? ''
  if (!toStatus) {
    throw createError({ statusCode: 422, statusMessage: 'A transition needs its target status' })
  }

  const client = await createKollioApiClient(event)
  const result = await transitionDecisionSpace({
    client,
    path: { workspace_id: workspaceId as never, space_id: spaceId as never },
    body: { to_status: toStatus, reason: body?.reason?.trim() || null } as never,
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
