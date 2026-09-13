export function useSourceDisplayName() {
  const { t, te } = useI18n()
  return (source?: string) => {
    if (!source) return source
    const key = `ideas.detail.sources.${source}`
    return te(key) ? t(key) : source
  }
}
