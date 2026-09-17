import { createScenarioVariable } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../utils/kollio-api'

type VariableBody = {
  name?: unknown
  unit?: unknown
  low?: unknown
  base?: unknown
  high?: unknown
}

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  const spaceId = getRouterParam(event, 'spaceId')
  if (!workspaceId || !spaceId) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Workspace and decision space identifiers required',
    })
  }

  const body = await readBody<VariableBody>(event)
  const name = typeof body?.name === 'string' ? body.name.trim() : ''
  if (!name) {
    throw createError({ statusCode: 422, statusMessage: 'A scenario variable needs a name' })
  }

  const low = Number(body?.low)
  const base = Number(body?.base)
  const high = Number(body?.high)
  if (![low, base, high].every(Number.isFinite)) {
    throw createError({ statusCode: 422, statusMessage: 'A scenario variable needs numeric bounds' })
  }
  if (!(low <= base && base <= high)) {
    throw createError({ statusCode: 422, statusMessage: 'The range must stay ordered: low, base, high' })
  }

  const unit = typeof body?.unit === 'string' ? body.unit.trim() : ''

  const client = await createKollioApiClient(event)
  const result = await createScenarioVariable({
    client,
    path: { workspace_id: workspaceId as never, space_id: spaceId as never },
    body: { name, unit: unit || null, low, base, high } as never,
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
