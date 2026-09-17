import { createBranch } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../utils/kollio-api'

const VISIBILITIES = new Set(['private', 'shared'])

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  const spaceId = getRouterParam(event, 'spaceId')
  if (!workspaceId || !spaceId) {
    throw createError({ statusCode: 400, statusMessage: 'Workspace and decision space identifiers required' })
  }

  const body = await readBody<{ title?: string, summary?: string | null, visibility?: string }>(event)
  const title = body?.title?.trim() ?? ''
  if (!title) {
    throw createError({ statusCode: 422, statusMessage: 'A branch needs a title' })
  }
  const visibility = body?.visibility ?? ''
  if (!VISIBILITIES.has(visibility)) {
    throw createError({ statusCode: 422, statusMessage: 'A branch is private or shared' })
  }

  const client = await createKollioApiClient(event)
  const result = await createBranch({
    client,
    path: { workspace_id: workspaceId as never, space_id: spaceId as never },
    body: { title, summary: body?.summary?.trim() || null, visibility: visibility as never },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
