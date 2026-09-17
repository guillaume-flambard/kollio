import { openDecisionSpace } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  if (!workspaceId) {
    throw createError({ statusCode: 400, statusMessage: 'Workspace identifier required' })
  }

  const body = await readBody<{ question?: string, description?: string | null, deadline?: string | null }>(event)
  const question = body?.question?.trim() ?? ''
  if (!question) {
    throw createError({ statusCode: 422, statusMessage: 'A decision space needs a question' })
  }

  const client = await createKollioApiClient(event)
  const result = await openDecisionSpace({
    client,
    path: { workspace_id: workspaceId as never },
    body: {
      question,
      description: body?.description?.trim() || null,
      deadline: body?.deadline || null,
    } as never,
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
