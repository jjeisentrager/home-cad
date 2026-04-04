import type { PortDef, ComponentTypeDef } from '@/types/library'
import type { WorldTransform } from '@/types/layout'

export function degreesToRadians(deg: number): number {
  return (deg * Math.PI) / 180
}

export function normalizeAngle(deg: number): number {
  return ((deg % 360) + 360) % 360
}

export function rotatePoint(
  px: number, py: number,
  cx: number, cy: number,
  angleDeg: number
): { x: number; y: number } {
  const rad = degreesToRadians(angleDeg)
  const cos = Math.cos(rad)
  const sin = Math.sin(rad)
  const dx = px - cx
  const dy = py - cy
  return {
    x: cx + dx * cos - dy * sin,
    y: cy + dx * sin + dy * cos,
  }
}

// Returns the world-space position and outward normal angle of a port,
// given the component's resolved world transform.
// Pass `dims` to override defaultWidth/defaultHeight (for dimensionally-driven components).
export function getPortWorldPosition(
  transform: WorldTransform,
  portDef: PortDef,
  typeDef: ComponentTypeDef,
  dims?: { width: number; height: number }
): { x: number; y: number; angle: number } {
  const { x, y, rotation } = transform
  const w = dims?.width ?? typeDef.defaultWidth
  const h = dims?.height ?? typeDef.defaultHeight

  // Port position in local (unrotated) space
  const lx = x + portDef.xFraction * w
  const ly = y + portDef.yFraction * h

  // Center of bounding box
  const cx = x + w / 2
  const cy = y + h / 2

  const rotated = rotatePoint(lx, ly, cx, cy, rotation)

  return {
    x: rotated.x,
    y: rotated.y,
    angle: normalizeAngle(portDef.normalAngle + rotation),
  }
}
