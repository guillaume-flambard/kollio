export default defineI18nConfig(() => ({
  legacy: false,
  datetimeFormats: {
    fr: { short: { year: 'numeric', month: 'short', day: 'numeric' } },
    en: { short: { year: 'numeric', month: 'short', day: 'numeric' } },
  },
  numberFormats: { fr: { decimal: { style: 'decimal' } }, en: { decimal: { style: 'decimal' } } },
}))
