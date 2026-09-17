import { createExperiment } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  const spaceId = getRouterParam(event, 'spaceId')
  if (!workspaceId || !spaceId) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Workspace and decision space identifiers required',
    })
  }

  const body = await readBody(event)
  const ideaId = typeof body?.idea_id === 'string' ? body.idea_id.trim() : ''
  if (ideaId === '') {
    throw createError({
      statusCode: 422,
      statusMessage: 'An experiment is created against an initiative',
    })
  }

  const title = typeof body?.title === 'string' ? body.title.trim() : ''
  const hypothesis = typeof body?.hypothesis === 'string' ? body.hypothesis.trim() : ''
  const successMetric = typeof body?.success_metric === 'string' ? body.success_metric.trim() : ''
  if (title === '') {
    throw createError({ statusCode: 422, statusMessage: 'An experiment needs a title' })
  }
  if (hypothesis === '') {
    throw createError({ statusCode: 422, statusMessage: 'An experiment states its hypothesis' })
  }
  if (successMetric === '') {
    throw createError({ statusCode: 422, statusMessage: 'An experiment names its success metric' })
  }

  const optionId = typeof body?.option_id === 'string' ? body.option_id.trim() : ''

  const client = await createKollioApiClient(event)
  const result = await createExperiment({
    client,
    path: { idea_id: ideaId as never },
    body: {
      title,
      hypothesis,
      success_metric: successMetric,
      baseline: typeof body?.baseline === 'string' ? body.baseline.trim() || null : null,
      target: typeof body?.target === 'string' ? body.target.trim() || null : null,
      decision_space_id: spaceId as never,
      option_id: (optionId === '' ? null : optionId) as never,
    },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
