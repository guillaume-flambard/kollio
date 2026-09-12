import { listWorkspaces } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../utils/kollio-api'

export default defineEventHandler(async (event) => {
  const client = await createKollioApiClient(event)
  const result = await listWorkspaces({ client })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
