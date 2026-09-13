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
  const q = typeof query.q === 'string' ? query.q : undefined
  const stage = typeof query.stage === 'string' && ['seed', 'iterating', 'team_formed'].includes(query.stage)
    ? query.stage as 'seed' | 'iterating' | 'team_formed'
    : undefined
  const soughtRole = typeof query.sought_role === 'string' ? query.sought_role : undefined
  const requestedRealism = Number(query.realism_min)
  const realismMin = Number.isInteger(requestedRealism) && requestedRealism >= 1 && requestedRealism <= 99
    ? requestedRealism
    : undefined
  const client = await createKollioApiClient(event)
  const result = await listWorkspaceIdeas({
    client,
    path: { workspace_id: workspaceId },
    query: { limit, offset, q, stage, sought_role: soughtRole, realism_min: realismMin },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
