/** Camera presentation math, not part of the persisted Kollio document. */
export interface SpatialV3Camera {
  zoom: number
  x: number
  y: number
}
export const SPATIAL_V3_WORLD = { width: 1000, height: 640 } as const
export const SPATIAL_V3_ZOOM = { min: 0.08, max: 2.4 } as const
export function clampSpatialV3Zoom(value: number): number {
  if (!Number.isFinite(value))
    return 1
  return Math.max(SPATIAL_V3_ZOOM.min, Math.min(SPATIAL_V3_ZOOM.max, value))
}
export interface SpatialV3Bounds {
  x: number
  y: number
  width: number
  height: number
}
export interface SpatialV3SceneNode {
  kind: string
  x: number
  y: number
}
export function spatialV3Bounds(nodes: SpatialV3SceneNode[], padding = 30): SpatialV3Bounds {
  if (!nodes.length) return { x: 0, y: 0, width: 1000, height: 640 }
  const sizes = nodes.map(node => {
    const w = node.kind === 'mission' ? 247 : node.kind === 'question' ? 170 : 210
    const h = node.kind === 'mission' ? 115 : node.kind === 'question' ? 60 : 96
    const x = node.x * 1000
    const y = node.y * 640
    return { left: x - w / 2, top: y - h / 2, right: x + w / 2, bottom: y + h / 2 }
  })
  const x = Math.min(...sizes.map(s => s.left)) - padding
  const y = Math.min(...sizes.map(s => s.top)) - padding
  const right = Math.max(...sizes.map(s => s.right)) + padding
  const bottom = Math.max(...sizes.map(s => s.bottom)) + padding
  return { x, y, width: right - x, height: bottom - y }
}
export function fitSpatialV3(width: number, height: number, bounds: SpatialV3Bounds = {
  x: 0, y: 0, width: 1000, height: 640,
}): SpatialV3Camera {
  if (width <= 0 || height <= 0)
    return { zoom: 1, x: 0, y: 0 }
  const zoom = clampSpatialV3Zoom(Math.min(width / bounds.width, height / bounds.height))
  return {
    zoom,
    x: (width - bounds.width * zoom) / 2 - bounds.x * zoom,
    y: (height - bounds.height * zoom) / 2 - bounds.y * zoom,
  }
}
export function zoomSpatialV3(camera: SpatialV3Camera, factor: number, cx: number, cy: number): SpatialV3Camera {
  const zoom = clampSpatialV3Zoom(camera.zoom * factor)
  const ratio = zoom / camera.zoom
  return { zoom, x: cx - (cx - camera.x) * ratio, y: cy - (cy - camera.y) * ratio }
}
export function panSpatialV3(camera: SpatialV3Camera, dx: number, dy: number): SpatialV3Camera {
  return { ...camera, x: camera.x + dx, y: camera.y + dy }
}
export interface SpatialV3LayoutNode {
  id: string
  kind: string
  depth: number
  x: number
  y: number
}
/** Detect real card collisions in the canonical 1000×640 semantic world. */
export function spatialV3Overlaps(nodes: SpatialV3LayoutNode[]): string[] {
  const width = (n: SpatialV3LayoutNode) => n.kind === 'mission' ? 247 : n.kind === 'question' ? 170 : 210
  const height = (n: SpatialV3LayoutNode) => n.kind === 'mission' ? 115 : n.kind === 'question' ? 60 : 96
  const failures: string[] = []
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const a = nodes[i]!
      const b = nodes[j]!
      if (Math.abs((a.x - b.x) * 1000) < (width(a) + width(b)) / 2 + 8
        && Math.abs((a.y - b.y) * 640) < (height(a) + height(b)) / 2 + 8)
        failures.push(`${a.id} / ${b.id}`)
    }
  }
  return failures
}
