export default defineI18nConfig(() => ({
  legacy: false,
  datetimeFormats: {
    fr: { long: { year: 'numeric', month: 'long', day: 'numeric' } },
    en: { long: { year: 'numeric', month: 'long', day: 'numeric' } },
  },
}))
