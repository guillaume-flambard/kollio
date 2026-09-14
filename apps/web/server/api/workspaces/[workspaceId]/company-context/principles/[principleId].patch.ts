import type { PrincipleUpdate } from '@kollio/api-client'
import { updateCompanyPrinciple } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  const principleId = getRouterParam(event, 'principleId')
  if (!workspaceId || !principleId) {
    throw createError({ statusCode: 400, statusMessage: 'Identifiers required' })
  }

  const body = (await readBody(event)) as Record<string, unknown>
  const patch: PrincipleUpdate = {}
  if (typeof body?.title === 'string' && body.title.trim() !== '') patch.title = body.title.trim()
  if (typeof body?.detail === 'string') patch.detail = body.detail.trim() === '' ? null : body.detail.trim()
  if (body?.state === 'active' || body?.state === 'archived') patch.state = body.state

  const client = await createKollioApiClient(event)
  const result = await updateCompanyPrinciple({
    client,
    path: { workspace_id: workspaceId, principle_id: principleId },
    body: patch,
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
