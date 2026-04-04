import type { PortDef } from '@/types/library'
import type { WorldTransform } from '@/types/layout'
import { getPortWorldPosition } from '@/lib/geometry'
import type { ComponentTypeDef } from '@/types/library'

interface Props {
  portDef: PortDef
  typeDef: ComponentTypeDef
  transform: WorldTransform
  isConnected: boolean
  isConnecting: boolean // this port is the source of an active connection
  onPointerDown: (portId: string, e: React.PointerEvent) => void
}

export default function PortDot({ portDef, typeDef, transform, isConnected, isConnecting, onPointerDown }: Props) {
  const pos = getPortWorldPosition(transform, portDef, typeDef)

  const color = isConnecting ? '#ffcc00'
    : isConnected ? '#44dd88'
    : '#4a9eff'

  return (
    <circle
      cx={pos.x}
      cy={pos.y}
      r={5}
      fill={color}
      fillOpacity={0.9}
      stroke="#1a1a2e"
      strokeWidth={1}
      style={{ cursor: 'crosshair' }}
      onPointerDown={e => { e.stopPropagation(); onPointerDown(portDef.id, e) }}
    >
      <title>{portDef.label}</title>
    </circle>
  )
}
