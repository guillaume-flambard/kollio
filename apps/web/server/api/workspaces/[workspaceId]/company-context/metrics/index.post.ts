import { createCompanyMetric } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../utils/kollio-api'
import { optionalText } from '../../../../../utils/validation'

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  if (!workspaceId) {
    throw createError({ statusCode: 400, statusMessage: 'Workspace identifier required' })
  }

  const body = (await readBody(event)) as Record<string, unknown>
  const name = body?.name
  if (typeof name !== 'string' || name.trim() === '') {
    throw createError({ statusCode: 422, statusMessage: 'A metric name is required' })
  }

  const client = await createKollioApiClient(event)
  const result = await createCompanyMetric({
    client,
    path: { workspace_id: workspaceId },
    body: {
      name: name.trim(),
      value: optionalText(body?.value),
      unit: optionalText(body?.unit),
      observed_at: optionalText(body?.observed_at),
      source: optionalText(body?.source),
    },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
