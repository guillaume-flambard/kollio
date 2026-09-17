import { readDecisionInbox } from '@kollio/api-client'

import { createKollioApiClient, forwardApiError } from '../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const client = await createKollioApiClient(event)
  const requested = typeof query.limit === 'string' && query.limit !== '' ? Number(query.limit) : undefined

  const result = await readDecisionInbox(
    requested && Number.isFinite(requested)
      ? { client, query: { limit: requested as never } }
      : { client },
  )

  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }

  return result.data
})
