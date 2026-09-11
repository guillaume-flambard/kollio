import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'

function keys(value, prefix = '') {
  return Object.entries(value).flatMap(([key, item]) => {
    const path = prefix ? `${prefix}.${key}` : key
    return typeof item === 'object' && item !== null ? keys(item, path) : [path]
  }).sort()
}
for (const directory of ['apps/web/i18n/locales', 'apps/api/src/locales']) {
  const [french, english] = await Promise.all(['fr', 'en'].map(async locale =>
    JSON.parse(await readFile(`${directory}/${locale}.json`, 'utf8'))))
  assert.deepEqual(keys(french), keys(english), `Translation keys differ in ${directory}`)
}
console.log('FR/EN translation keys match.')
