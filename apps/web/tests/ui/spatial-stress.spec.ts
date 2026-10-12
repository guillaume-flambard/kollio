import { describe, expect, it } from 'vitest'
import { spatialV3StressFixture } from '../../app/utils/spatialV3Stress.generated'
import { spatialV3Bounds } from '../../app/utils/spatialV3Camera'

describe('Spatial Ink — 100 objects and 200 routed relations', () => {
  it('uses the exact same 100 unique objects and 200 real relations', () => {
    expect(spatialV3StressFixture.nodes).toHaveLength(100)
    expect(spatialV3StressFixture.edges).toHaveLength(200)
    const ids = new Set(spatialV3StressFixture.nodes.map(node => node.id))
    expect(ids.size).toBe(100)
    for (const edge of spatialV3StressFixture.edges) {
      expect(ids.has(edge.source)).toBe(true)
      expect(ids.has(edge.target)).toBe(true)
      expect(edge.points.length).toBeGreaterThanOrEqual(2)
      expect(edge.blocked).toBe(false)
    }
  })
  it('provides a positive camera bounding box for the complete graph', () => {
    const bounds = spatialV3Bounds(spatialV3StressFixture.nodes)
    expect(bounds.width).toBeGreaterThan(1000)
    expect(bounds.height).toBeGreaterThan(640)
    expect(Number.isFinite(bounds.x)).toBe(true)
  })
})
