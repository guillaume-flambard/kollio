import { createExperiment } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const ideaId = getRouterParam(event, 'ideaId')
  if (!ideaId) {
    throw createError({ statusCode: 400, statusMessage: 'Idea identifier required' })
  }

  const body = await readBody(event)
  const hasTitle = typeof body?.title === 'string' && body.title.trim() !== ''
  const hasHypothesis = typeof body?.hypothesis === 'string' && body.hypothesis.trim() !== ''
  const hasMetric = typeof body?.success_metric === 'string' && body.success_metric.trim() !== ''
  if (!hasTitle || !hasHypothesis || !hasMetric) {
    throw createError({
      statusCode: 422,
      statusMessage: 'Title, hypothesis and success metric are required',
    })
  }

  const client = await createKollioApiClient(event)
  const result = await createExperiment({
    client,
    path: { idea_id: ideaId as never },
    body: {
      title: body.title,
      hypothesis: body.hypothesis,
      success_metric: body.success_metric,
      baseline: body.baseline ?? null,
      target: body.target ?? null,
    },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
