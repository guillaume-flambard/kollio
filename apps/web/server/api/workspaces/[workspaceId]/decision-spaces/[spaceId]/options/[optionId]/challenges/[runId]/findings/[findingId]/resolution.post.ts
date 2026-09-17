import { resolveChallengeFinding } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../../../../../../../utils/kollio-api'

const RESOLUTIONS = new Set(['confirmed', 'dismissed'])

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  const spaceId = getRouterParam(event, 'spaceId')
  const optionId = getRouterParam(event, 'optionId')
  const runId = getRouterParam(event, 'runId')
  const findingId = getRouterParam(event, 'findingId')
  if (!workspaceId || !spaceId || !optionId || !runId || !findingId) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Workspace, decision space, option, run and finding identifiers required',
    })
  }

  const body = await readBody<{ resolution?: string }>(event)
  const resolution = typeof body?.resolution === 'string' ? body.resolution : ''
  if (!RESOLUTIONS.has(resolution)) {
    throw createError({
      statusCode: 422,
      statusMessage: 'A finding is confirmed or dismissed',
    })
  }

  const client = await createKollioApiClient(event)
  const result = await resolveChallengeFinding({
    client,
    path: {
      workspace_id: workspaceId as never,
      space_id: spaceId as never,
      option_id: optionId as never,
      run_id: runId as never,
      finding_id: findingId as never,
    },
    body: { resolution: resolution as never },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
