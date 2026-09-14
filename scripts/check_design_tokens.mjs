import assert from 'node:assert/strict'
import { readFile, readdir, writeFile, mkdir, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join, relative } from 'node:path'
import process from 'node:process'

const APP = 'apps/web/app'
const TOKENS = 'packages/ui/src/tokens.css'
const HEX = /#[0-9a-fA-F]{3,8}\b/
const TOKEN_USE = /var\(\s*(--[a-z0-9-]+)/g

async function sources(directory) {
  const found = []
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const path = join(directory, entry.name)
    if (entry.isDirectory()) found.push(...(await sources(path)))
    else if (/\.(vue|css)$/.test(entry.name)) found.push(path)
  }
  return found
}

// Locally declared in the same file, or provided by Nuxt UI at runtime.
function isLocal(name, text) {
  return new RegExp(`^\\s*${name}\\s*:`, 'm').test(text)
}

export async function scan(files, defined) {
  const problems = []
  for (const path of files) {
    const text = await readFile(path, 'utf8')
    text.split('\n').forEach((line, index) => {
      const hex = line.match(HEX)
      if (hex) {
        problems.push(
          `${path}:${index + 1} literal colour ${hex[0]}. Use a token from ${TOKENS}.`,
        )
      }
      for (const [, name] of line.matchAll(TOKEN_USE)) {
        if (name.startsWith('--ui-')) continue
        if (defined.has(name) || isLocal(name, text)) continue
        problems.push(
          `${path}:${index + 1} token ${name} is absent from ${TOKENS}. ` +
            'It is a typo or a legacy name, and its fallback would silently win.',
        )
      }
    })
  }
  return problems
}

async function selfTest() {
  const workspace = join(tmpdir(), `kollio-design-tokens-${process.pid}`)
  await mkdir(workspace, { recursive: true })
  const cases = {
    'undefined-token.vue': '<style>.a { color: var(--kollio-nope, #ffffff); }</style>',
    'literal-colour.vue': '<style>.a { color: #123456; }</style>',
    'clean.vue': '<style>.a { color: var(--ui-text); padding: var(--kollio-space-sm); }</style>',
  }
  for (const [name, body] of Object.entries(cases)) {
    await writeFile(join(workspace, name), body)
  }
  const defined = new Set(['--ui-text', '--kollio-space-sm'])
  const files = Object.keys(cases).map(name => join(workspace, name))
  const problems = await scan(files, defined)
  await rm(workspace, { recursive: true, force: true })
  const hit = name => problems.some(problem => problem.includes(name))
  assert.ok(hit('undefined-token.vue'), 'an undefined token must be reported')
  assert.ok(hit('literal-colour.vue'), 'a literal colour must be reported')
  assert.ok(!hit('clean.vue'), 'a token-only file must pass')
  console.log('Design token guard self-test passed.')
}

if (process.argv.includes('--self-test')) {
  await selfTest()
  process.exit(0)
}

const defined = new Set(
  (await readFile(TOKENS, 'utf8')).match(/--[a-z0-9-]+/g) ?? [],
)
const problems = await scan(await sources(APP), defined)
if (problems.length) {
  console.error(problems.join('\n'))
  console.error(`\n${problems.length} design token problem(s). See docs/06-design-system.md.`)
  process.exit(1)
}
console.log(`Design tokens: ${relative(process.cwd(), APP)} uses only canonical tokens.`)
