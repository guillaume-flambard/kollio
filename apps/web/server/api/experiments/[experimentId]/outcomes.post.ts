import { recordExperimentOutcome } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const experimentId = getRouterParam(event, 'experimentId')
  if (!experimentId) {
    throw createError({ statusCode: 400, statusMessage: 'Experiment identifier required' })
  }

  const body = await readBody(event)
  const hasMetric = typeof body?.metric === 'string' && body.metric.trim() !== ''
  const hasValue = typeof body?.value === 'string' && body.value.trim() !== ''
  if (!hasMetric || !hasValue) {
    throw createError({ statusCode: 422, statusMessage: 'Metric and value are required' })
  }

  const client = await createKollioApiClient(event)
  const result = await recordExperimentOutcome({
    client,
    path: { experiment_id: experimentId },
    body: {
      metric: body.metric,
      value: body.value,
      unit: body.unit ?? null,
      observed_at: body.observed_at ?? null,
      comment: body.comment ?? null,
      qualitative: body.qualitative ?? null,
    },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
