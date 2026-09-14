export const INITIATIVE_TYPES = [
  'idea',
  'hypothesis',
  'campaign',
  'opportunity',
  'decision',
  'experiment',
  'pricing',
  'market',
  'partnership',
  'internal_improvement',
] as const

export type InitiativeType = (typeof INITIATIVE_TYPES)[number]

export function requiredInitiativeType(value: unknown): InitiativeType {
  const found = typeof value === 'string' ? INITIATIVE_TYPES.find(candidate => candidate === value) : undefined
  if (!found) {
    throw createError({ statusCode: 422, statusMessage: 'Unknown initiative type' })
  }
  return found
}

export function optionalInitiativeType(value: unknown): InitiativeType | undefined {
  return value === undefined ? undefined : requiredInitiativeType(value)
}
