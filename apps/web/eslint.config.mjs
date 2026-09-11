import withNuxt from './.nuxt/eslint.config.mjs'
import vueI18n from '@intlify/eslint-plugin-vue-i18n'

export default withNuxt({
  plugins: { '@intlify/vue-i18n': vueI18n },
  files: ['app/**/*.vue'],
  rules: {
    '@intlify/vue-i18n/no-raw-text': ['error', { ignorePattern: '^[\\s.]+$' }],
  },
})
