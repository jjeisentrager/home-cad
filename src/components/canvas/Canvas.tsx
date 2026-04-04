import { useEffect, useMemo, useRef } from 'react'
import { useLayoutStore } from '@/store/layoutStore'
import { useLibraryStore } from '@/store/libraryStore'
import { useUiStore } from '@/store/uiStore'
import { resolveAllPositions } from '@/lib/positionResolver'
import LayerGroup from './LayerGroup'
import './Canvas.css'

export default function Canvas() {
  const layers = useLayoutStore(s => s.layers)
  const components = useLayoutStore(s => s.components)
  const selectComponent = useLayoutStore(s => s.selectComponent)
  const addComponent = useLayoutStore(s => s.addComponent)
  const series = useLibraryStore(s => s.series)

  const panX = useUiStore(s => s.panX)
  const panY = useUiStore(s => s.panY)
  const zoom = useUiStore(s => s.zoom)
  const setPan = useUiStore(s => s.setPan)
  const setZoom = useUiStore(s => s.setZoom)
  const screenToCanvas = useUiStore(s => s.screenToCanvas)
  const activeLayerId = useUiStore(s => s.activeLayerId)
  const draggingTypeId = useUiStore(s => s.draggingTypeId)
  const draggingSeriesId = useUiStore(s => s.draggingSeriesId)
  const endDragType = useUiStore(s => s.endDragType)
  const cancelPortConnect = useUiStore(s => s.cancelPortConnect)
  const setSvgOffset = useUiStore(s => s.setSvgOffset)

  const removeComponent = useLayoutStore(s => s.removeComponent)
  const selectedId = useLayoutStore(s => s.selectedComponentId)

  const svgRef = useRef<SVGSVGElement>(null)
  const isPanning = useRef(false)
  const panStart = useRef({ x: 0, y: 0, px: 0, py: 0 })

  // Keep SVG offset in sync for coordinate conversion
  useEffect(() => {
    function updateOffset() {
      if (!svgRef.current) return
      const rect = svgRef.current.getBoundingClientRect()
      setSvgOffset(rect.left, rect.top)
    }
    updateOffset()
    window.addEventListener('resize', updateOffset)
    return () => window.removeEventListener('resize', updateOffset)
  }, [setSvgOffset])

  // Keyboard shortcuts
  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      const tag = (e.target as HTMLElement).tagName
      if (tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA') return
      if (e.key === 'Delete' || e.key === 'Backspace') {
        if (selectedId) removeComponent(selectedId)
      }
      if (e.key === 'Escape') {
        selectComponent(null)
        cancelPortConnect()
      }
      if (e.key === 'f' || e.key === 'F') {
        fitToView()
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [selectedId]) // eslint-disable-line react-hooks/exhaustive-deps

  function fitToView() {
    if (components.length === 0 || !svgRef.current) return
    const allTransforms = resolveAllPositions(components, series)
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity
    for (const comp of components) {
      const t = allTransforms.get(comp.id)
      const typeDef = series.find(s => s.id === comp.seriesId)?.components.find(c => c.id === comp.typeId)
      if (!t || !typeDef) continue
      minX = Math.min(minX, t.x)
      minY = Math.min(minY, t.y)
      maxX = Math.max(maxX, t.x + typeDef.defaultWidth)
      maxY = Math.max(maxY, t.y + typeDef.defaultHeight)
    }
    if (!isFinite(minX)) return
    const rect = svgRef.current.getBoundingClientRect()
    const margin = 60
    const scaleX = (rect.width - margin * 2) / (maxX - minX)
    const scaleY = (rect.height - margin * 2) / (maxY - minY)
    const newZoom = Math.min(scaleX, scaleY, 5)
    const newPanX = margin - minX * newZoom
    const newPanY = margin - minY * newZoom
    setPan(newPanX, newPanY)
    setZoom(newZoom)
  }

  const transforms = useMemo(
    () => resolveAllPositions(components, series),
    [components, series]
  )

  const sortedLayers = [...layers].sort((a, b) => a.order - b.order)

  // ── Pan via middle mouse or background pointer drag ──────────────────
  function handlePointerDown(e: React.PointerEvent<SVGSVGElement>) {
    if (e.button === 1 || e.button === 0) {
      // Only pan on background (target is svg or viewport g)
      if ((e.target as Element).id === 'canvas-bg' || (e.target as Element).id === 'canvas-root') {
        isPanning.current = true
        panStart.current = { x: e.clientX, y: e.clientY, px: panX, py: panY }
        e.currentTarget.setPointerCapture(e.pointerId)
        selectComponent(null)
        cancelPortConnect()
      }
    }
  }

  function handlePointerMove(e: React.PointerEvent<SVGSVGElement>) {
    if (!isPanning.current) return
    setPan(
      panStart.current.px + (e.clientX - panStart.current.x),
      panStart.current.py + (e.clientY - panStart.current.y)
    )
  }

  function handlePointerUp() {
    isPanning.current = false
  }

  // ── Zoom via wheel ────────────────────────────────────────────────────
  function handleWheel(e: React.WheelEvent<SVGSVGElement>) {
    e.preventDefault()
    const factor = e.deltaY < 0 ? 1.1 : 1 / 1.1
    const newZoom = Math.min(10, Math.max(0.1, zoom * factor))

    // Pivot around pointer position
    const rect = svgRef.current!.getBoundingClientRect()
    const sx = e.clientX - rect.left
    const sy = e.clientY - rect.top
    const newPanX = sx - (sx - panX) * (newZoom / zoom)
    const newPanY = sy - (sy - panY) * (newZoom / zoom)

    setPan(newPanX, newPanY)
    setZoom(newZoom)
  }

  // ── Drop from component palette ───────────────────────────────────────
  function handleDragOver(e: React.DragEvent) {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'copy'
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault()
    if (!draggingTypeId || !draggingSeriesId) return

    const canvasPos = screenToCanvas(e.clientX, e.clientY)

    // Determine target layer
    const targetLayer = activeLayerId
      ? layers.find(l => l.id === activeLayerId && !l.locked)
      : layers.filter(l => !l.locked)[0]

    if (!targetLayer) {
      alert('Please select or create an unlocked layer first.')
      endDragType()
      return
    }

    const typeDef = series
      .find(s => s.id === draggingSeriesId)
      ?.components.find(c => c.id === draggingTypeId)

    if (!typeDef) { endDragType(); return }

    // Center on drop point
    addComponent({
      typeId: draggingTypeId,
      seriesId: draggingSeriesId,
      layerId: targetLayer.id,
      manualX: canvasPos.x - typeDef.defaultWidth / 2,
      manualY: canvasPos.y - typeDef.defaultHeight / 2,
      manualRotation: 0,
      properties: [],
    })

    endDragType()
  }

  return (
    <div className="canvas-container">
      <div className="canvas-toolbar">
        <button onClick={fitToView} title="Fit view (F)">⊡ Fit</button>
        <button onClick={() => { const z = Math.min(10, zoom * 1.25); const r = svgRef.current?.getBoundingClientRect(); setPan(panX - (r ? r.width/2 : 400) * 0.25 * zoom, panY - (r ? r.height/2 : 300) * 0.25 * zoom); setZoom(z) }} title="Zoom in">+</button>
        <button onClick={() => { const z = Math.max(0.1, zoom / 1.25); setZoom(z) }} title="Zoom out">−</button>
        {selectedId && (
          <button onClick={() => removeComponent(selectedId)} title="Delete selected (Del)" className="canvas-toolbar-del">✕ Delete</button>
        )}
      </div>
      <svg
        id="canvas-root"
        ref={svgRef}
        className="canvas-svg"
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onWheel={handleWheel}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <defs>
          <pattern
            id="grid-minor"
            width={20 * zoom}
            height={20 * zoom}
            x={panX % (20 * zoom)}
            y={panY % (20 * zoom)}
            patternUnits="userSpaceOnUse"
          >
            <path d={`M ${20 * zoom} 0 L 0 0 0 ${20 * zoom}`} fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="0.5" />
          </pattern>
          <pattern
            id="grid-major"
            width={100 * zoom}
            height={100 * zoom}
            x={panX % (100 * zoom)}
            y={panY % (100 * zoom)}
            patternUnits="userSpaceOnUse"
          >
            <path d={`M ${100 * zoom} 0 L 0 0 0 ${100 * zoom}`} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="1" />
          </pattern>
        </defs>
        {/* Background click target */}
        <rect id="canvas-bg" x="0" y="0" width="100%" height="100%" fill="url(#grid-minor)" />
        <rect x="0" y="0" width="100%" height="100%" fill="url(#grid-major)" pointerEvents="none" />
        <g id="viewport" transform={`translate(${panX}, ${panY}) scale(${zoom})`}>
          {sortedLayers.map(layer => (
            <LayerGroup key={layer.id} layer={layer} transforms={transforms} zoom={zoom} />
          ))}
        </g>
      </svg>
      <ZoomIndicator zoom={zoom} />
    </div>
  )
}

function ZoomIndicator({ zoom }: { zoom: number }) {
  return (
    <div className="canvas-zoom-indicator">
      {Math.round(zoom * 100)}%
    </div>
  )
}
