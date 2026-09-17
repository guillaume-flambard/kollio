import { createScenarioRun } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../../../utils/kollio-api'

const LEVELS = new Set(['optimistic', 'base', 'pessimistic', 'failure'])

type RunBody = {
  level?: unknown
  assumptions?: unknown
  values?: unknown
}

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  const spaceId = getRouterParam(event, 'spaceId')
  const optionId = getRouterParam(event, 'optionId')
  if (!workspaceId || !spaceId || !optionId) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Workspace, decision space and option identifiers required',
    })
  }

  const body = await readBody<RunBody>(event)
  const level = typeof body?.level === 'string' ? body.level : ''
  if (!LEVELS.has(level)) {
    throw createError({ statusCode: 422, statusMessage: 'A run has a known level' })
  }
  const assumptions = typeof body?.assumptions === 'string' ? body.assumptions.trim() : ''
  if (!assumptions) {
    throw createError({ statusCode: 422, statusMessage: 'A scenario run states its assumptions' })
  }

  const raw = Array.isArray(body?.values) ? body.values : []
  const values = raw
    .filter((entry): entry is { variable_id?: unknown; value?: unknown } => typeof entry === 'object' && entry !== null)
    .filter(entry => typeof entry.variable_id === 'string' && Number.isFinite(Number(entry.value)))
    .map(entry => ({ variable_id: String(entry.variable_id), value: Number(entry.value) }))

  const client = await createKollioApiClient(event)
  const result = await createScenarioRun({
    client,
    path: { workspace_id: workspaceId as never, space_id: spaceId as never, option_id: optionId as never },
    body: { level, assumptions, values } as never,
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
