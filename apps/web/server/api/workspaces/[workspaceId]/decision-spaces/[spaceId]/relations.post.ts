import { createRelation } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../utils/kollio-api'

const TYPES = new Set([
  'SUPPORTS',
  'CONTRADICTS',
  'DUPLICATES',
  'ALTERNATIVE_TO',
  'DERIVED_FROM',
  'SUPERSEDES',
  'EVIDENCE_FOR',
  'EVIDENCE_AGAINST',
])

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  const spaceId = getRouterParam(event, 'spaceId')
  if (!workspaceId || !spaceId) {
    throw createError({ statusCode: 400, statusMessage: 'Workspace and decision space identifiers required' })
  }

  const body = await readBody<{
    from_contribution_id?: string
    to_contribution_id?: string
    relation_type?: string
  }>(event)
  const fromId = body?.from_contribution_id ?? ''
  const toId = body?.to_contribution_id ?? ''
  if (!fromId || !toId) {
    throw createError({ statusCode: 422, statusMessage: 'A relation needs two contributions' })
  }
  if (fromId === toId) {
    throw createError({ statusCode: 422, statusMessage: 'A relation links two different contributions' })
  }
  const relationType = body?.relation_type ?? ''
  if (!TYPES.has(relationType)) {
    throw createError({ statusCode: 422, statusMessage: 'A relation has a known kind' })
  }

  const client = await createKollioApiClient(event)
  const result = await createRelation({
    client,
    path: { workspace_id: workspaceId as never, space_id: spaceId as never },
    body: {
      from_contribution_id: fromId as never,
      to_contribution_id: toId as never,
      relation_type: relationType as never,
    },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
