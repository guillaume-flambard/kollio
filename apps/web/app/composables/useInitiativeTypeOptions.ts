export function useInitiativeTypeOptions() {
  const { tm, rt } = useI18n()
  return computed(() => {
    const catalog = tm('ideas.initiativeType') as Record<string, unknown>
    return Object.fromEntries(
      Object.entries(catalog).map(([key, value]) => [key, rt(value as never)]),
    )
  })
}
