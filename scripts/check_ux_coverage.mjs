import { existsSync, statSync, readFileSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const registry = resolve(root, '.agents/skills/ux-flow-auditor/COVERAGE.md')

const lines = readFileSync(registry, 'utf8').split('\n')
const failures = []

for (const line of lines) {
  if (!line.startsWith('|')) continue
  const cells = line.split('|').map(cell => cell.trim())
  if (cells[1] === 'Identifier' || cells[1].startsWith('-')) continue
  const [_, identifier, , , evidence, status] = cells
  if (status !== 'AUDITED') continue
  const target = resolve(root, evidence)
  if (!existsSync(target) || statSync(target).size === 0) {
    failures.push(`${identifier}: missing or empty evidence at ${evidence}`)
  }
}

if (failures.length > 0) {
  for (const failure of failures) console.error(`coverage: ${failure}`)
  process.exit(1)
}
console.log('coverage: ok')
