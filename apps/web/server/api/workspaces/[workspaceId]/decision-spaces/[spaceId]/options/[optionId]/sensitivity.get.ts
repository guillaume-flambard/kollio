import { readSensitivity } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../../../utils/kollio-api'

const DIRECTIONS = new Set(['above', 'below'])

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  const spaceId = getRouterParam(event, 'spaceId')
  const optionId = getRouterParam(event, 'optionId')
  if (!workspaceId || !spaceId || !optionId) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Workspace, decision space and option identifiers required',
    })
  }

  const query = getQuery(event)
  const metricVariableId =
    typeof query.metric_variable_id === 'string' ? query.metric_variable_id.trim() : ''
  const direction = typeof query.direction === 'string' ? query.direction : ''
  const rawThreshold = typeof query.threshold === 'string' ? query.threshold.trim() : ''

  if (metricVariableId === '') {
    throw createError({ statusCode: 422, statusMessage: 'A sensitivity read names a result variable' })
  }
  if (!DIRECTIONS.has(direction)) {
    throw createError({ statusCode: 422, statusMessage: 'A sensitivity read states above or below' })
  }
  if (rawThreshold === '' || !Number.isFinite(Number(rawThreshold))) {
    throw createError({ statusCode: 422, statusMessage: 'A sensitivity read states a threshold' })
  }

  const client = await createKollioApiClient(event)
  const result = await readSensitivity({
    client,
    path: {
      workspace_id: workspaceId as never,
      space_id: spaceId as never,
      option_id: optionId as never,
    },
    query: {
      metric_variable_id: metricVariableId,
      direction: direction as never,
      threshold: rawThreshold as never,
    },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
