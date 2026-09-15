import { describe, expect, it } from 'vitest'
import en from '../../i18n/locales/en.json' with { type: 'json' }
import fr from '../../i18n/locales/fr.json' with { type: 'json' }

function flatten(node: unknown): string[] {
  if (typeof node === 'string') return [node]
  if (Array.isArray(node)) return node.flatMap(flatten)
  if (node && typeof node === 'object') {
    const record = node as Record<string, unknown>
    // The i18n plugin compiles each catalog entry to a vue-i18n message AST; the
    // raw copy is kept on `source` (directly, or inside `loc`), so only that
    // string counts as visible wording.
    if (typeof record.source === 'string') return [record.source]
    const loc = record.loc
    if (loc && typeof loc === 'object' && typeof (loc as Record<string, unknown>).source === 'string') {
      return [(loc as Record<string, unknown>).source as string]
    }
    return Object.values(record).flatMap(flatten)
  }
  return []
}

const NAMESPACES = ['ideas', 'workspace'] as const

function b2bValues(catalog: typeof fr) {
  return [
    ...NAMESPACES.flatMap(namespace => flatten(catalog[namespace])),
    ...flatten(catalog.navigation.ideas),
    ...flatten(catalog.navigation.promise),
  ]
}

// Interpolation placeholders are parameters, not visible copy: `{idea}` names a
// slot while the wording around it stays free of the word.
const visibleCopy = (value: unknown) => String(value).replace(/\{[^}]*\}/g, '')

describe('B2B copy says Initiative', () => {
  it('names no idée in the French workspace namespaces', () => {
    const forbidden = b2bValues(fr).filter(value => /\bidées?\b/i.test(visibleCopy(value)))
    expect(forbidden).toEqual([])
  })

  it('names no idea in the English workspace namespaces', () => {
    const forbidden = b2bValues(en).filter(value => /\bideas?\b/i.test(visibleCopy(value)))
    expect(forbidden).toEqual([])
  })

  it('offers the ten initiative kinds in both locales', () => {
    const keys = (catalog: typeof fr) => Object.keys(catalog.ideas.initiativeType).sort()
    expect(keys(fr)).toHaveLength(10)
    expect(keys(en)).toEqual(keys(fr))
  })
})
