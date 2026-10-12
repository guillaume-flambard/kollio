import { describe, expect, it } from 'vitest'
import { spatialV3Fixture } from '../../app/utils/spatialV3.generated'

describe('Spatial Ink V3 shared fixture', () => {
  it('has stable unique identities and no dangling relationships', () => {
    const ids = new Set(spatialV3Fixture.nodes.map(node => node.id))
    expect(ids.size).toBe(spatialV3Fixture.nodes.length)
    for (const edge of spatialV3Fixture.edges) {
      expect(ids.has(edge.source)).toBe(true)
      expect(ids.has(edge.target)).toBe(true)
      expect(edge.source).not.toBe(edge.target)
    }
  })

  it('reveals more information without deleting the initial context', () => {
    const initial = spatialV3Fixture.nodes.filter(node => node.depth <= 1)
    const expanded = spatialV3Fixture.nodes.filter(node => node.depth <= 2)
    expect(initial).toHaveLength(3)
    expect(expanded).toHaveLength(6)
    for (const node of initial)
      expect(expanded.map(value => value.id)).toContain(node.id)
  })

  it('marks sources as unverified and proposals as pending', () => {
    expect(spatialV3Fixture.nodes.find(node => node.kind === 'source')?.status).toBe('unverified')
    expect(spatialV3Fixture.nodes.find(node => node.kind === 'proposal')?.status).toBe('pending')
  })

  it('uses normalized coordinates inside the stage', () => {
    for (const node of spatialV3Fixture.nodes) {
      expect(node.x).toBeGreaterThanOrEqual(0)
      expect(node.x).toBeLessThanOrEqual(1)
      expect(node.y).toBeGreaterThanOrEqual(0)
      expect(node.y).toBeLessThanOrEqual(1)
    }
  })
})
