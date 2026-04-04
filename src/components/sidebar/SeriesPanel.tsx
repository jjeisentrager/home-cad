import { useLibraryStore } from '@/store/libraryStore'
import { useUiStore } from '@/store/uiStore'
import { useLayoutStore } from '@/store/layoutStore'
import type { ComponentTypeDef } from '@/types/library'
import './SeriesPanel.css'

export default function SeriesPanel() {
  const series = useLibraryStore(s => s.series)
  const activeSeriesId = useUiStore(s => s.activeSeriesId)
  const setActiveSeries = useUiStore(s => s.setActiveSeries)
  const beginDragType = useUiStore(s => s.beginDragType)

  const activeSeries = series.find(s => s.id === activeSeriesId) ?? series[0]

  function handleDragStart(comp: ComponentTypeDef, e: React.DragEvent) {
    e.dataTransfer.effectAllowed = 'copy'
    e.dataTransfer.setData('text/plain', comp.id)
    beginDragType(comp.id, activeSeries?.id ?? '')
  }

  return (
    <div className="series-panel">
      <div className="series-select">
        <label>Series</label>
        <select
          value={activeSeries?.id ?? ''}
          onChange={e => setActiveSeries(e.target.value)}
        >
          {series.map(s => (
            <option key={s.id} value={s.id}>{s.label}</option>
          ))}
        </select>
      </div>
      <div className="series-components">
        {activeSeries?.components.map(comp => (
          <div
            key={comp.id}
            className="comp-tile"
            draggable
            onDragStart={e => handleDragStart(comp, e)}
            title={comp.description ?? comp.label}
          >
            <svg
              viewBox={`0 0 ${comp.defaultWidth} ${comp.defaultHeight}`}
              className="comp-tile-preview"
            >
              <path d={comp.svgPath} stroke="#4a9eff" strokeWidth="2" fill="none" />
            </svg>
            <span>{comp.label}</span>
          </div>
        ))}
        {!activeSeries && <p className="series-empty">No series loaded.</p>}
      </div>
      <p className="series-hint">Drag a component onto the canvas to place it.</p>
      <ActiveLayerNote />
    </div>
  )
}

function ActiveLayerNote() {
  const activeLayerId = useUiStore(s => s.activeLayerId)
  const layers = useLayoutStore(s => s.layers)
  const activeLayer = layers.find(l => l.id === activeLayerId)
  return (
    <p className="series-layer-note">
      Active layer: <strong>{activeLayer?.name ?? '(none — select a layer first)'}</strong>
    </p>
  )
}
