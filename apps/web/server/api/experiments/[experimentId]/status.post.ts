import { changeExperimentStatus } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const experimentId = getRouterParam(event, 'experimentId')
  if (!experimentId) {
    throw createError({ statusCode: 400, statusMessage: 'Experiment identifier required' })
  }

  const body = await readBody(event)
  if (typeof body?.status !== 'string' || body.status === '') {
    throw createError({ statusCode: 422, statusMessage: 'Target status is required' })
  }

  const client = await createKollioApiClient(event)
  const result = await changeExperimentStatus({
    client,
    path: { experiment_id: experimentId },
    body: { status: body.status },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
