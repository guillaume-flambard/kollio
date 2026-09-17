import { updateOption } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../../utils/kollio-api'

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
  const optionId = getRouterParam(event, 'optionId')
  if (!workspaceId || !spaceId || !optionId) {
    throw createError({ statusCode: 400, statusMessage: 'Workspace, decision space and option identifiers required' })
  }

  const payload = await readBody<Record<string, unknown>>(event)
  const body: Record<string, string | null> = {}
  for (const field of ['title', 'proposal'] as const) {
    if (!(field in (payload ?? {}))) continue
    const value = typeof payload?.[field] === 'string' ? payload[field].trim() : ''
    if (!value) {
      throw createError({ statusCode: 422, statusMessage: `An option needs a ${field}` })
    }
    body[field] = value
  }
  for (const field of TEXT_FIELDS) {
    if (!(field in (payload ?? {}))) continue
    const value = payload?.[field]
    body[field] = typeof value === 'string' && value.trim() ? value.trim() : null
  }
  if (!Object.keys(body).length) {
    throw createError({ statusCode: 422, statusMessage: 'An option update carries at least one field' })
  }

  const client = await createKollioApiClient(event)
  const result = await updateOption({
    client,
    path: { workspace_id: workspaceId as never, space_id: spaceId as never, option_id: optionId as never },
    body: body as never,
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
