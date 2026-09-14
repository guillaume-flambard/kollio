import { describe, expect, it } from 'vitest'
import en from '../../i18n/locales/en.json' with { type: 'json' }
import fr from '../../i18n/locales/fr.json' with { type: 'json' }

function flatten(node: unknown): string[] {
  if (typeof node === 'string') return [node]
  if (node && typeof node === 'object') {
    return Object.values(node as Record<string, unknown>).flatMap(flatten)
  }
  return []
}

const NAMESPACES = ['ideas', 'workspace'] as const

function b2bValues(catalog: typeof fr) {
  return [
    ...NAMESPACES.flatMap(namespace => flatten(catalog[namespace])),
    catalog.navigation.ideas,
    catalog.navigation.promise,
  ]
}

describe('B2B copy says Initiative', () => {
  it('names no idée in the French workspace namespaces', () => {
    const forbidden = b2bValues(fr).filter(value => /\bidées?\b/i.test(value))
    expect(forbidden).toEqual([])
  })

  it('names no idea in the English workspace namespaces', () => {
    const forbidden = b2bValues(en).filter(value => /\bideas?\b/i.test(value))
    expect(forbidden).toEqual([])
  })

  it('offers the ten initiative kinds in both locales', () => {
    const keys = (catalog: typeof fr) => Object.keys(catalog.ideas.initiativeType).sort()
    expect(keys(fr)).toHaveLength(10)
    expect(keys(en)).toEqual(keys(fr))
  })
})
