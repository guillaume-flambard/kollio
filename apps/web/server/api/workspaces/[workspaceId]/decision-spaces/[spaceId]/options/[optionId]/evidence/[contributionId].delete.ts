import { unlinkOptionEvidence } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../../../../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  const spaceId = getRouterParam(event, 'spaceId')
  const optionId = getRouterParam(event, 'optionId')
  const contributionId = getRouterParam(event, 'contributionId')
  if (!workspaceId || !spaceId || !optionId || !contributionId) {
    throw createError({ statusCode: 400, statusMessage: 'Workspace, decision space, option and contribution identifiers required' })
  }

  const client = await createKollioApiClient(event)
  const result = await unlinkOptionEvidence({
    client,
    path: {
      workspace_id: workspaceId as never,
      space_id: spaceId as never,
      option_id: optionId as never,
      contribution_id: contributionId as never,
    },
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data ?? null
})
