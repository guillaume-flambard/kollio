import { getExperiment } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const experimentId = getRouterParam(event, 'experimentId')
  if (!experimentId) {
    throw createError({ statusCode: 400, statusMessage: 'Experiment identifier required' })
  }

  const client = await createKollioApiClient(event)
  const result = await getExperiment({
    client,
    path: { experiment_id: experimentId },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
