import type { CompanyProfileWrite } from '@kollio/api-client'
import { saveCompanyProfile } from '@kollio/api-client'
import { createKollioApiClient, forwardApiError } from '../../../../utils/kollio-api'
import { optionalText } from '../../../../utils/validation'

export default defineEventHandler(async (event) => {
  const workspaceId = getRouterParam(event, 'workspaceId')
  if (!workspaceId) {
    throw createError({ statusCode: 400, statusMessage: 'Workspace identifier required' })
  }

  const body = (await readBody(event)) as Record<string, unknown>
  const profile: CompanyProfileWrite = {
    name: optionalText(body?.name),
    description: optionalText(body?.description),
    business_model: optionalText(body?.business_model),
    products_services: optionalText(body?.products_services),
    customer_segments: optionalText(body?.customer_segments),
    markets: optionalText(body?.markets),
    structure: optionalText(body?.structure),
  }

  const client = await createKollioApiClient(event)
  const result = await saveCompanyProfile({
    client,
    path: { workspace_id: workspaceId },
    body: profile,
  })
  if (result.error) {
    forwardApiError(result.response?.status ?? 502, result.error)
  }
  return result.data
})
