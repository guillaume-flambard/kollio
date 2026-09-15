import assert from 'node:assert/strict'
import { readFile, readdir } from 'node:fs/promises'
import { extname, join } from 'node:path'

function keys(value, prefix = '') {
  return Object.entries(value).flatMap(([key, item]) => {
    const path = prefix ? `${prefix}.${key}` : key
    return typeof item === 'object' && item !== null ? keys(item, path) : [path]
  }).sort()
}

async function catalogue(directory) {
  const [french, english] = await Promise.all(['fr', 'en'].map(async locale =>
    JSON.parse(await readFile(`${directory}/${locale}.json`, 'utf8'))))
  assert.deepEqual(keys(french), keys(english), `Translation keys differ in ${directory}`)
  return keys(french)
}

const webKeys = await catalogue('apps/web/i18n/locales')
await catalogue('apps/api/src/locales')
const known = new Set(webKeys)

const call = /(?<![\w.])(?:\$)?t[e]?\(\s*(['"`])((?:\\.|(?!\1)[\s\S])*?)\1(\s*\+)?/g

const missing = new Map()
function report(key, file) {
  if (!missing.has(key)) missing.set(key, new Set())
  missing.get(key).add(file)
}

for (const file of (await readdir('apps/web/app', { recursive: true }))
  .filter(name => ['.js', '.ts', '.vue'].includes(extname(name)))) {
  const path = join('apps/web/app', file)
  for (const [, quote, literal, concatenation] of (await readFile(path, 'utf8')).matchAll(call)) {
    const cut = quote === '`' ? literal.indexOf('${') : -1
    const key = cut === -1 ? literal.replace(/\\(['"\\])/g, '$1') : literal.slice(0, cut)
    if (cut === -1 && !concatenation) {
      if (!known.has(key)) report(key, path)
      continue
    }
    if (key.includes('.') && !webKeys.some(candidate => candidate.startsWith(key))) {
      report(`${key}*`, path)
    }
  }
}

if (missing.size > 0) {
  for (const [key, files] of missing) {
    console.error(`missing ${key} (used in ${[...files].sort().join(', ')})`)
  }
  throw new Error(`${missing.size} translation key(s) used in apps/web/app are absent from the FR and EN catalogs`)
}

console.log(`FR/EN translation keys match, and all ${known.size} catalog keys cover their usages.`)
