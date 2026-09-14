import type { CompanyConstraintUpdate } from '@kollio/api-client'
import { updateCompanyConstraint } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  const constraintId = getRouterParam(event, 'constraintId')
  if (!workspaceId || !constraintId) {
    throw createError({ statusCode: 400, statusMessage: 'Identifiers required' })
  }

  const body = (await readBody(event)) as Record<string, unknown>
  const patch: CompanyConstraintUpdate = {}
  if (typeof body?.title === 'string' && body.title.trim() !== '') patch.title = body.title.trim()
  if (typeof body?.detail === 'string') patch.detail = body.detail.trim() === '' ? null : body.detail.trim()
  if (body?.state === 'active' || body?.state === 'archived') patch.state = body.state

  const client = await createKollioApiClient(event)
  const result = await updateCompanyConstraint({
    client,
    path: { workspace_id: workspaceId, constraint_id: constraintId },
    body: patch,
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
