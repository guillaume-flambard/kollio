export function requiredTitle(body: unknown): string {
  const title = (body as { title?: unknown } | null)?.title
  if (typeof title !== 'string' || title.trim() === '') {
    throw createError({ statusCode: 422, statusMessage: 'A title is required' })
  }
  return title.trim()
}

export function optionalText(value: unknown): string | undefined {
  return typeof value === 'string' && value.trim() !== '' ? value.trim() : undefined
}
