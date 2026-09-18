export function useFormatters() {
  const { d, locale } = useI18n()

  const relativeFormatter = computed(() => new Intl.RelativeTimeFormat(locale.value, { numeric: 'auto' }))

  function formatDate(value: string | Date) {
    return d(value instanceof Date ? value : new Date(value), 'long')
  }

  function formatRelative(value: string | Date) {
    const date = value instanceof Date ? value : new Date(value)
    const days = Math.round((date.getTime() - Date.now()) / 86_400_000)
    if (Math.abs(days) < 1) {
      return relativeFormatter.value.format(Math.round((date.getTime() - Date.now()) / 3_600_000), 'hour')
    }
    return relativeFormatter.value.format(days, 'day')
  }

  return { formatDate, formatRelative }
}
