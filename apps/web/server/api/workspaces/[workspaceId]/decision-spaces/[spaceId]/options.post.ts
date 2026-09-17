import { createOption } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../utils/kollio-api'

const TEXT_FIELDS = [
  'mechanism',
  'upside',
  'cost',
  'risks',
  'critical_assumptions',
  'success_metrics',
] as const

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  const spaceId = getRouterParam(event, 'spaceId')
  if (!workspaceId || !spaceId) {
    throw createError({ statusCode: 400, statusMessage: 'Workspace and decision space identifiers required' })
  }

  const payload = await readBody<Record<string, unknown>>(event)
  const title = typeof payload?.title === 'string' ? payload.title.trim() : ''
  const proposal = typeof payload?.proposal === 'string' ? payload.proposal.trim() : ''
  if (!title) {
    throw createError({ statusCode: 422, statusMessage: 'An option needs a title' })
  }
  if (!proposal) {
    throw createError({ statusCode: 422, statusMessage: 'An option needs a proposal' })
  }

  const body: Record<string, string | null> = { title, proposal }
  for (const field of TEXT_FIELDS) {
    const value = payload?.[field]
    body[field] = typeof value === 'string' && value.trim() ? value.trim() : null
  }

  const client = await createKollioApiClient(event)
  const result = await createOption({
    client,
    path: { workspace_id: workspaceId as never, space_id: spaceId as never },
    body: body as never,
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
