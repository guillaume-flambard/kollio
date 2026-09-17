import { linkOptionEvidence } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../../../utils/kollio-api'

const SIDES = new Set(['for', 'against'])

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  const spaceId = getRouterParam(event, 'spaceId')
  const optionId = getRouterParam(event, 'optionId')
  if (!workspaceId || !spaceId || !optionId) {
    throw createError({ statusCode: 400, statusMessage: 'Workspace, decision space and option identifiers required' })
  }

  const payload = await readBody<{ contribution_id?: string, side?: string }>(event)
  const contributionId = typeof payload?.contribution_id === 'string' ? payload.contribution_id : ''
  const side = typeof payload?.side === 'string' ? payload.side : ''
  if (!contributionId) {
    throw createError({ statusCode: 422, statusMessage: 'An evidence link carries a contribution' })
  }
  if (!SIDES.has(side)) {
    throw createError({ statusCode: 422, statusMessage: 'Evidence is for or against an option' })
  }

  const client = await createKollioApiClient(event)
  const result = await linkOptionEvidence({
    client,
    path: { workspace_id: workspaceId as never, space_id: spaceId as never, option_id: optionId as never },
    body: { contribution_id: contributionId, side } as never,
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
