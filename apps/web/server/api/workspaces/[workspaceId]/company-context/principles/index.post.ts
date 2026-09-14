import { createCompanyPrinciple } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../utils/kollio-api'
import { optionalText, requiredTitle } from '../../../../../utils/validation'

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  if (!workspaceId) {
    throw createError({ statusCode: 400, statusMessage: 'Workspace identifier required' })
  }

  const body = await readBody(event)
  const title = requiredTitle(body)
  const client = await createKollioApiClient(event)
  const result = await createCompanyPrinciple({
    client,
    path: { workspace_id: workspaceId },
    body: { title, detail: optionalText((body as Record<string, unknown>)?.detail) },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
