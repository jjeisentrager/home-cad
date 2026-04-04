import type { PlacedComponent, WorldTransform } from '@/types/layout'
import type { SeriesDef } from '@/types/library'
import { getPortWorldPosition, normalizeAngle, degreesToRadians } from './geometry'

function findTypeDef(series: SeriesDef[], seriesId: string, typeId: string) {
  return series.find(s => s.id === seriesId)?.components.find(c => c.id === typeId)
}

function findPortDef(series: SeriesDef[], seriesId: string, typeId: string, portId: string) {
  return findTypeDef(series, seriesId, typeId)?.ports.find(p => p.id === portId)
}

// Build a topological order. Returns component ids in dependency order (roots first).
// Also returns the set of ids involved in a cycle.
function topoSort(components: PlacedComponent[]): {
  order: string[]
  cycleIds: Set<string>
} {
  const idMap = new Map(components.map(c => [c.id, c]))
  const visited = new Set<string>()
  const inStack = new Set<string>()
  const cycleIds = new Set<string>()
  const order: string[] = []

  function visit(id: string) {
    if (inStack.has(id)) {
      cycleIds.add(id)
      return
    }
    if (visited.has(id)) return
    inStack.add(id)
    const comp = idMap.get(id)
    if (comp?.positionAssignment) {
      visit(comp.positionAssignment.destinationComponentId)
    }
    inStack.delete(id)
    visited.add(id)
    order.push(id)
  }

  for (const c of components) visit(c.id)

  return { order, cycleIds }
}

export function resolveAllPositions(
  components: PlacedComponent[],
  series: SeriesDef[]
): Map<string, WorldTransform> {
  const result = new Map<string, WorldTransform>()
  const { order, cycleIds } = topoSort(components)
  const compMap = new Map(components.map(c => [c.id, c]))

  for (const id of order) {
    const comp = compMap.get(id)
    if (!comp) continue
    const typeDef = findTypeDef(series, comp.seriesId, comp.typeId)

    // Nodes in a cycle or with no type def fall back to manual position
    if (!comp.positionAssignment || cycleIds.has(id) || !typeDef) {
      result.set(id, {
        x: comp.manualX,
        y: comp.manualY,
        rotation: comp.manualRotation,
        hasCycleError: cycleIds.has(id),
      })
      continue
    }

    const { sourcePortId, destinationComponentId, destinationPortId, offsetX, offsetY, orientationOffset } =
      comp.positionAssignment

    const destTransform = result.get(destinationComponentId)
    const destComp = compMap.get(destinationComponentId)
    if (!destTransform || !destComp) {
      // Destination not yet resolved; fall back
      result.set(id, { x: comp.manualX, y: comp.manualY, rotation: comp.manualRotation })
      continue
    }

    const destTypeDef = findTypeDef(series, destComp.seriesId, destComp.typeId)
    const destPortDef = findPortDef(series, destComp.seriesId, destComp.typeId, destinationPortId)
    const srcPortDef = findPortDef(series, comp.seriesId, comp.typeId, sourcePortId)

    if (!destTypeDef || !destPortDef || !srcPortDef) {
      result.set(id, { x: comp.manualX, y: comp.manualY, rotation: comp.manualRotation })
      continue
    }

    // World position of the destination port
    const destPortWorld = getPortWorldPosition(destTransform, destPortDef, destTypeDef)

    // Target point where our source port must land
    const targetX = destPortWorld.x + offsetX
    const targetY = destPortWorld.y + offsetY

    // Rotation: source port normal must point anti-parallel to dest port normal
    // Anti-parallel means dest normal + 180, plus any orientationOffset
    const desiredNormal = normalizeAngle(destPortWorld.angle + 180 + orientationOffset)
    // Our source port's natural normal angle is srcPortDef.normalAngle (at rotation=0)
    // We need: srcPortDef.normalAngle + rotation = desiredNormal
    const rotation = normalizeAngle(desiredNormal - srcPortDef.normalAngle)

    // Now compute the bbox top-left so that the source port lands at targetX/Y.
    // At the computed rotation, the source port's local position relative to bbox:
    const w = typeDef.defaultWidth
    const h = typeDef.defaultHeight
    // Assume bbox top-left at (0,0) temporarily to find port offset from center
    const portLocalX = srcPortDef.xFraction * w
    const portLocalY = srcPortDef.yFraction * h
    const centerOffsetX = portLocalX - w / 2
    const centerOffsetY = portLocalY - h / 2

    // Rotate that offset by the computed rotation
    const rad = degreesToRadians(rotation)
    const rotatedOffsetX = centerOffsetX * Math.cos(rad) - centerOffsetY * Math.sin(rad)
    const rotatedOffsetY = centerOffsetX * Math.sin(rad) + centerOffsetY * Math.cos(rad)

    // The source port world position = bbox_center + rotatedOffset
    // bbox_center = (x + w/2, y + h/2)
    // So: x + w/2 + rotatedOffsetX = targetX  →  x = targetX - w/2 - rotatedOffsetX
    const x = targetX - w / 2 - rotatedOffsetX
    const y = targetY - h / 2 - rotatedOffsetY

    result.set(id, { x, y, rotation })
  }

  return result
}
