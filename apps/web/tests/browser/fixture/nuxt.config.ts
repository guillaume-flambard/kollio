import { fileURLToPath } from 'node:url'

export default defineNuxtConfig({
  extends: ['../../../'],
  srcDir: fileURLToPath(new URL('../../../app/', import.meta.url)),
  ssr: false,
  devtools: { enabled: false },
  runtimeConfig: { public: { authEnabled: false } },
})
