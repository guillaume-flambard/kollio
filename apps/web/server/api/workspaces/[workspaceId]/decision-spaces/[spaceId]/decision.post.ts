import { commitDecision } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../../utils/kollio-api'

const SIDES = new Set(['for', 'against'])

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  const spaceId = getRouterParam(event, 'spaceId')
  if (!workspaceId || !spaceId) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Workspace and decision space identifiers required',
    })
  }

  const body = await readBody<Record<string, unknown>>(event)
  const selectedOptionId =
    typeof body?.selected_option_id === 'string' ? body.selected_option_id.trim() : ''
  if (!selectedOptionId) {
    throw createError({
      statusCode: 422,
      statusMessage: 'A decision selects an option',
    })
  }
  const rationale = typeof body?.rationale === 'string' ? body.rationale.trim() : ''
  if (!rationale) {
    throw createError({
      statusCode: 422,
      statusMessage: 'A decision needs a rationale',
    })
  }
  const rejected = Array.isArray(body?.rejected_option_ids)
    ? (body.rejected_option_ids as unknown[]).filter(
        (value): value is string => typeof value === 'string' && value.length > 0,
      )
    : []
  const argumentPayload = Array.isArray(body?.arguments)
    ? (body.arguments as { contribution_id?: unknown, side?: unknown }[])
        .filter(
          (entry): entry is { contribution_id: string, side: string } =>
            typeof entry?.contribution_id === 'string' &&
            typeof entry?.side === 'string' &&
            SIDES.has(entry.side),
        )
        .map(entry => ({ contribution_id: entry.contribution_id, side: entry.side }))
    : []
  const triggers = Array.isArray(body?.revisit_triggers)
    ? (body.revisit_triggers as Record<string, unknown>[])
        .filter(
          entry => typeof entry?.metric === 'string' && (entry.metric as string).trim().length > 0,
        )
        .map((entry) => {
          const direction = entry.direction
          const threshold = typeof entry.threshold === 'string' ? entry.threshold.trim() : ''
          const note = typeof entry.note === 'string' ? entry.note.trim() : ''
          return {
            metric: (entry.metric as string).trim(),
            direction: direction === 'above' || direction === 'below' ? direction : null,
            threshold: threshold || null,
            note: note || null,
          }
        })
    : []

  const client = await createKollioApiClient(event)
  const result = await commitDecision({
    client,
    path: { workspace_id: workspaceId as never, space_id: spaceId as never },
    body: {
      selected_option_id: selectedOptionId,
      rationale,
      critical_assumptions: typeof body?.critical_assumptions === 'string' ? body.critical_assumptions : null,
      uncertainty: typeof body?.uncertainty === 'string' ? body.uncertainty : null,
      success_criteria: typeof body?.success_criteria === 'string' ? body.success_criteria : null,
      rejected_option_ids: rejected,
      arguments: argumentPayload,
      revisit_triggers: triggers,
    } as never,
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
