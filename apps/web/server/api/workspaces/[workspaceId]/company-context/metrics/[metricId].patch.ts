import type { MetricUpdate } from '@kollio/api-client'
import { updateCompanyMetric } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  const metricId = getRouterParam(event, 'metricId')
  if (!workspaceId || !metricId) {
    throw createError({ statusCode: 400, statusMessage: 'Identifiers required' })
  }

  const body = (await readBody(event)) as Record<string, unknown>
  const patch: MetricUpdate = {}
  if (typeof body?.name === 'string' && body.name.trim() !== '') patch.name = body.name.trim()
  if (typeof body?.value === 'string') patch.value = body.value.trim() === '' ? null : body.value.trim()
  if (typeof body?.unit === 'string') patch.unit = body.unit.trim() === '' ? null : body.unit.trim()
  if (typeof body?.observed_at === 'string') patch.observed_at = body.observed_at.trim() === '' ? null : body.observed_at.trim()
  if (typeof body?.source === 'string') patch.source = body.source.trim() === '' ? null : body.source.trim()
  if (body?.state === 'active' || body?.state === 'archived') patch.state = body.state

  const client = await createKollioApiClient(event)
  const result = await updateCompanyMetric({
    client,
    path: { workspace_id: workspaceId, metric_id: metricId },
    body: patch,
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
