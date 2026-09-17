import { proposeContribution } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../utils/kollio-api'

const KINDS = new Set(['idea', 'claim', 'evidence', 'objection', 'constraint'])

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  const spaceId = getRouterParam(event, 'spaceId')
  if (!workspaceId || !spaceId) {
    throw createError({ statusCode: 400, statusMessage: 'Workspace and decision space identifiers required' })
  }

  const body = await readBody<{
    branch_id?: string
    kind?: string
    title?: string
    body?: string | null
    source?: string | null
    tool_model?: string | null
  }>(event)
  const branchId = body?.branch_id ?? ''
  if (!branchId) {
    throw createError({ statusCode: 422, statusMessage: 'A contribution is proposed from a branch' })
  }
  const kind = body?.kind ?? ''
  if (!KINDS.has(kind)) {
    throw createError({ statusCode: 422, statusMessage: 'A contribution has a known kind' })
  }
  const title = body?.title?.trim() ?? ''
  if (!title) {
    throw createError({ statusCode: 422, statusMessage: 'A contribution proposal needs a title' })
  }

  const client = await createKollioApiClient(event)
  const result = await proposeContribution({
    client,
    path: { workspace_id: workspaceId as never, space_id: spaceId as never },
    body: {
      branch_id: branchId as never,
      kind: kind as never,
      title,
      body: body?.body?.trim() || null,
      source: body?.source?.trim() || null,
      tool_model: body?.tool_model?.trim() || null,
      transformation_history: null,
    },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
