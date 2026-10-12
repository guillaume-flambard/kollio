import { describe, expect, it } from 'vitest'
import { spatialV3Fixture } from '../../app/utils/spatialV3.generated'
import { fitSpatialV3, spatialV3Bounds, panSpatialV3, spatialV3Overlaps, zoomSpatialV3 } from '../../app/utils/spatialV3Camera'

describe('Spatial Ink viewport navigation', () => {
  it('centers the 1000×640 world at fit without deforming it', () => {
    expect(fitSpatialV3(1200, 640)).toEqual({ zoom: 1, x: 100, y: 0 })
    expect(fitSpatialV3(500, 320)).toEqual({ zoom: 0.5, x: 0, y: 0 })
  })
  it('zoom preserves the world point below the pointer', () => {
    const initial = fitSpatialV3(1200, 640)
    const target = { x: 333, y: 171 }
    const zoomed = zoomSpatialV3(initial, 1.7, target.x, target.y)
    const xBefore = (target.x - initial.x) / initial.zoom
    const xAfter = (target.x - zoomed.x) / zoomed.zoom
    const yBefore = (target.y - initial.y) / initial.zoom
    const yAfter = (target.y - zoomed.y) / zoomed.zoom
    expect(xAfter).toBeCloseTo(xBefore)
    expect(yAfter).toBeCloseTo(yBefore)
  })
  it('clamps zoom and treats pan as presentation-only', () => {
    const original = fitSpatialV3(1000, 640)
    expect(zoomSpatialV3(original, 100, 500, 320).zoom).toBe(2.4)
    expect(zoomSpatialV3(original, 0.01, 500, 320).zoom).toBe(0.08)
    expect(panSpatialV3(original, -34, 48)).toEqual({ zoom: 1, x: -34, y: 48 })
    expect(original).toEqual({ zoom: 1, x: 0, y: 0 })
  })
  it('fits objects outside the original 1000×640 reference world', () => {
    const bounds = spatialV3Bounds([
      { kind: 'mission', x: -1.2, y: -0.5 },
      { kind: 'source', x: 3, y: 2 },
    ])
    const camera = fitSpatialV3(1280, 800, bounds)
    expect(bounds.x).toBeLessThan(0)
    expect(bounds.x + bounds.width).toBeGreaterThan(1000)
    expect(camera.zoom).toBeLessThan(0.35)
    expect(bounds.x * camera.zoom + camera.x).toBeGreaterThanOrEqual(-0.00001)
    expect((bounds.x + bounds.width) * camera.zoom + camera.x).toBeLessThanOrEqual(1280.00001)
  })
  it('detects overlaps before displaying an expanded fixture', () => {
    expect(spatialV3Overlaps(spatialV3Fixture.nodes)).toEqual([])
    const colliding = [
      { id: 'a', kind: 'mission', x: 0.5, y: 0.5, depth: 1 },
      { id: 'b', kind: 'source', x: 0.5, y: 0.5, depth: 2 },
    ]
    expect(spatialV3Overlaps(colliding)).toEqual(['a / b'])
  })
})
