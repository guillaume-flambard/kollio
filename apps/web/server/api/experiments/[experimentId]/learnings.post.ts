import { writeExperimentLearning } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const experimentId = getRouterParam(event, 'experimentId')
  if (!experimentId) {
    throw createError({ statusCode: 400, statusMessage: 'Experiment identifier required' })
  }

  const body = await readBody(event)
  const client = await createKollioApiClient(event)
  const result = await writeExperimentLearning({
    client,
    path: { experiment_id: experimentId },
    body: {
      text: body?.text ?? null,
      confirm: body?.confirm === true,
    },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
