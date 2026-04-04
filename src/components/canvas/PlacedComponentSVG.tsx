import { useLayoutStore } from '@/store/layoutStore'
import { useUiStore } from '@/store/uiStore'
import { useLibraryStore } from '@/store/libraryStore'
import type { PlacedComponent, WorldTransform } from '@/types/layout'
import PortDot from './PortDot'
import SelectionBox from './SelectionBox'

interface Props {
  comp: PlacedComponent
  transform: WorldTransform
  zoom: number
}

export default function PlacedComponentSVG({ comp, transform, zoom }: Props) {
  const selectedId = useLayoutStore(s => s.selectedComponentId)
  const selectComponent = useLayoutStore(s => s.selectComponent)
  const moveComponent = useLayoutStore(s => s.moveComponent)
  const setPositionAssignment = useLayoutStore(s => s.setPositionAssignment)
  const setSidebarTab = useUiStore(s => s.setSidebarTab)
  const beginDragPlaced = useUiStore(s => s.beginDragPlaced)
  const endDragPlaced = useUiStore(s => s.endDragPlaced)
  const screenToCanvas = useUiStore(s => s.screenToCanvas)
  const connectingFromComponentId = useUiStore(s => s.connectingFromComponentId)
  const connectingFromPortId = useUiStore(s => s.connectingFromPortId)
  const beginPortConnect = useUiStore(s => s.beginPortConnect)
  const cancelPortConnect = useUiStore(s => s.cancelPortConnect)
  const layers = useLayoutStore(s => s.layers)

  const getComponentType = useLibraryStore(s => s.getComponentType)
  // Select all components for connection detection (stable reference)
  const allComponents = useLayoutStore(s => s.components)
  const typeDef = getComponentType(comp.seriesId, comp.typeId)
  if (!typeDef) return null

  const layer = layers.find(l => l.id === comp.layerId)
  const isLocked = layer?.locked ?? false

  const isSelected = selectedId === comp.id
  const { x, y, rotation, hasCycleError } = transform
  const cx = x + typeDef.defaultWidth / 2
  const cy = y + typeDef.defaultHeight / 2

  // Show ports when selected or zoomed in
  const showPorts = isSelected || zoom >= 0.7

  // Check if any port on this component is connected (another component points to us)
  const connectedPortIds = new Set(
    allComponents
      .filter(c => c.positionAssignment?.destinationComponentId === comp.id)
      .map(c => c.positionAssignment!.destinationPortId)
  )

  function handlePointerDown(e: React.PointerEvent) {
    e.stopPropagation()

    // If we're in port-connect mode and clicking background of this component, cancel
    if (connectingFromComponentId && connectingFromComponentId !== comp.id) {
      cancelPortConnect()
      return
    }

    selectComponent(comp.id)
    setSidebarTab('properties')

    if (isLocked) return

    // Begin dragging placed component
    const canvasPos = screenToCanvas(e.clientX, e.clientY)
    beginDragPlaced(comp.id, canvasPos.x - x, canvasPos.y - y)

    const onMove = (me: PointerEvent) => {
      const p = screenToCanvas(me.clientX, me.clientY)
      moveComponent(comp.id, p.x - (canvasPos.x - x), p.y - (canvasPos.y - y))
    }
    const onUp = () => {
      endDragPlaced()
      window.removeEventListener('pointermove', onMove)
      window.removeEventListener('pointerup', onUp)
    }
    window.addEventListener('pointermove', onMove)
    window.addEventListener('pointerup', onUp)
  }

  function handlePortPointerDown(portId: string, e: React.PointerEvent) {
    e.stopPropagation()

    if (connectingFromComponentId === null) {
      // Start connection
      beginPortConnect(comp.id, portId)
    } else if (connectingFromComponentId === comp.id) {
      // Clicking same component's port — cancel
      cancelPortConnect()
    } else {
      // Complete connection: the previously started port connects to this port
      const sourceCompId = connectingFromComponentId
      const sourcePortId = connectingFromPortId!
      setPositionAssignment(sourceCompId, {
        sourcePortId,
        destinationComponentId: comp.id,
        destinationPortId: portId,
        offsetX: 0,
        offsetY: 0,
        orientationOffset: 0,
      })
      cancelPortConnect()
    }
  }

  return (
    <g
      transform={`rotate(${rotation}, ${cx}, ${cy})`}
      onPointerDown={handlePointerDown}
      style={{ cursor: isLocked ? 'not-allowed' : 'move' }}
    >
      <rect x={x} y={y} width={typeDef.defaultWidth} height={typeDef.defaultHeight} fill="transparent" />
      <g transform={`translate(${x}, ${y})`}>
        <path
          d={typeDef.svgPath}
          stroke="#4a9eff"
          strokeWidth={2}
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {comp.label && (
          <text
            x={typeDef.defaultWidth / 2}
            y={-6}
            textAnchor="middle"
            fontSize={10}
            fill="#c0c0d0"
            pointerEvents="none"
          >
            {comp.label}
          </text>
        )}
        {isSelected && (
          <SelectionBox
            width={typeDef.defaultWidth}
            height={typeDef.defaultHeight}
            hasCycleError={hasCycleError}
          />
        )}
      </g>
      {showPorts && typeDef.ports.map(port => (
        <PortDot
          key={port.id}
          portDef={port}
          typeDef={typeDef}
          transform={transform}
          isConnected={connectedPortIds.has(port.id)}
          isConnecting={connectingFromComponentId === comp.id && connectingFromPortId === port.id}
          onPointerDown={handlePortPointerDown}
        />
      ))}
    </g>
  )
}
