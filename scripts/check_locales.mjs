import assert from 'node:assert/strict'
import { readFile, readdir, writeFile, mkdir, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { extname, join } from 'node:path'
import process from 'node:process'

const WEB_CATALOG = 'apps/web/i18n/locales'
const API_CATALOG = 'apps/api/src/locales'
const ROOTS = ['apps/web', 'packages/ui/src']
const SKIP = new Set([
  'node_modules', '.output', '.nuxt', 'playwright-report', 'test-results', 'dist', '.git', '.agents',
])
const SOURCE = /\.(js|ts|vue|mjs|cjs)$/
const CALL = /(?<![\w.])((?:\$)?(?:t|te|tm|rt))\(\s*(['"`])((?:\\.|(?!\2)[\s\S])*?)\2(\s*\+)?/g
const MESSAGES = /\bmessages((?:\.[A-Za-z0-9_$]+)+)/g

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

async function sources(directory) {
  const found = []
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if (entry.isDirectory()) {
      if (SKIP.has(entry.name)) continue
      found.push(...(await sources(join(directory, entry.name))))
    } else if (SOURCE.test(entry.name)) {
      found.push(join(directory, entry.name))
    }
  }
  return found
}

function covers(prefix, key) {
  return key === prefix || key.startsWith(prefix.endsWith('.') ? prefix : `${prefix}.`)
}

function unescape(literal) {
  return literal.replace(/\\(['"\\`])/g, '$1')
}

// Both directions: every key the code uses must exist, and every catalog key
// must be reachable from the code, a template family or a browser test.
export function audit(files, webKeys) {
  const known = new Set(webKeys)
  const exact = new Set()
  const families = new Set()
  const missing = new Map()
  const report = (key, path) => {
    if (!missing.has(key)) missing.set(key, new Set())
    missing.get(key).add(path)
  }

  for (const { path, text } of files) {
    for (const [, call, quote, literal, concatenation] of text.matchAll(CALL)) {
      const cut = quote === '`' ? literal.indexOf('${') : -1
      if (cut === -1 && !concatenation) {
        const key = unescape(literal)
        if (call.endsWith('tm')) {
          families.add(key)
          continue
        }
        exact.add(key)
        if (!known.has(key)) report(key, path)
        continue
      }
      const key = cut === -1 ? unescape(literal) : literal.slice(0, cut)
      if (!key) continue
      families.add(key)
      if (!webKeys.some(candidate => covers(key, candidate))) report(`${key}*`, path)
    }
    for (const [, reference] of text.matchAll(MESSAGES)) {
      families.add(reference.slice(1))
    }
  }

  const reachable = key =>
    exact.has(key) || [...families].some(family => covers(family, key))
  return { missing, dead: webKeys.filter(key => !reachable(key)) }
}

async function selfTest() {
  const workspace = join(tmpdir(), `kollio-locales-${process.pid}`)
  await mkdir(workspace, { recursive: true })
  const cases = {
    'used.vue': "<template>{{ t('ideas.title') }}</template>",
    'family.vue': '<script>const label = (role: string) => t(`ideas.detail.roles.${role}`)</script>',
    'absent.vue': "<template>{{ t('ideas.absent') }}</template>",
    'namespace.vue': "<script>const catalog = tm('ideas.initiativeType')</script>",
    'reference.spec.ts': 'const title = messages.ideas.profile.ownedTitle',
  }
  const files = []
  for (const [name, body] of Object.entries(cases)) {
    const path = join(workspace, name)
    await writeFile(path, body)
    files.push({ path, text: body })
  }
  const webKeys = [
    'ideas.title',
    'ideas.detail.roles.dev',
    'ideas.initiativeType.software',
    'ideas.profile.ownedTitle',
    'ideas.orphan',
  ]
  const { missing, dead } = audit(files, webKeys)
  await rm(workspace, { recursive: true, force: true })
  assert.ok(missing.has('ideas.absent'), 'a key absent from the catalog must be reported')
  assert.ok(!missing.has('ideas.title'), 'a key present in the catalog must pass')
  assert.ok(!missing.has('ideas.detail.roles.*'), 'a template family that exists must pass')
  assert.ok(dead.includes('ideas.orphan'), 'a catalog key no source reaches must be reported')
  assert.ok(!dead.includes('ideas.detail.roles.dev'), 'a key reached through a family must pass')
  assert.ok(!dead.includes('ideas.initiativeType.software'), 'a key reached through tm() must pass')
  assert.ok(!dead.includes('ideas.profile.ownedTitle'), 'a key reached through a test must pass')
  console.log('Locale guard self-test passed.')
}

if (process.argv.includes('--self-test')) {
  await selfTest()
  process.exit(0)
}

const webKeys = await catalogue(WEB_CATALOG)
await catalogue(API_CATALOG)

const files = []
for (const root of ROOTS) {
  for (const path of await sources(root)) {
    files.push({ path, text: await readFile(path, 'utf8') })
  }
}

const { missing, dead } = audit(files, webKeys)

if (missing.size > 0 || dead.length > 0) {
  for (const [key, paths] of missing) {
    console.error(`missing ${key} (used in ${[...paths].sort().join(', ')})`)
  }
  for (const key of dead) {
    console.error(`unreachable ${key} (in ${WEB_CATALOG}, no source reaches it)`)
  }
  console.error(`\n${missing.size + dead.length} locale problem(s). See docs/07-i18n.md.`)
  process.exit(1)
}

console.log(
  `FR/EN catalogs match (${webKeys.length} web keys): every key the code uses exists, ` +
    `and every catalog key is reachable from ${ROOTS.join(' or ')}.`,
)
