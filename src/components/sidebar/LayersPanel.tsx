import { useState } from 'react'
import { useLayoutStore } from '@/store/layoutStore'
import { useUiStore } from '@/store/uiStore'
import './LayersPanel.css'

export default function LayersPanel() {
  const layers = useLayoutStore(s => s.layers)
  const addLayer = useLayoutStore(s => s.addLayer)
  const removeLayer = useLayoutStore(s => s.removeLayer)
  const toggleLayerVisible = useLayoutStore(s => s.toggleLayerVisible)
  const toggleLayerLocked = useLayoutStore(s => s.toggleLayerLocked)
  const renameLayer = useLayoutStore(s => s.renameLayer)
  const activeLayerId = useUiStore(s => s.activeLayerId)
  const setActiveLayer = useUiStore(s => s.setActiveLayer)

  const [newLayerName, setNewLayerName] = useState('')
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editingName, setEditingName] = useState('')

  const sorted = [...layers].sort((a, b) => b.order - a.order)

  function handleAdd() {
    const name = newLayerName.trim() || `Layer ${layers.length + 1}`
    addLayer(name)
    setNewLayerName('')
  }

  function startEdit(id: string, name: string) {
    setEditingId(id)
    setEditingName(name)
  }

  function commitEdit() {
    if (editingId && editingName.trim()) {
      renameLayer(editingId, editingName.trim())
    }
    setEditingId(null)
  }

  return (
    <div className="layers-panel">
      <div className="layers-add">
        <input
          value={newLayerName}
          onChange={e => setNewLayerName(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleAdd()}
          placeholder="New layer name…"
        />
        <button onClick={handleAdd}>+</button>
      </div>
      <ul className="layers-list">
        {sorted.map(layer => (
          <li
            key={layer.id}
            className={`layer-item ${layer.id === activeLayerId ? 'active' : ''}`}
            onClick={() => setActiveLayer(layer.id)}
          >
            <button
              className="layer-btn vis"
              title={layer.visible ? 'Hide layer' : 'Show layer'}
              onClick={e => { e.stopPropagation(); toggleLayerVisible(layer.id) }}
            >
              {layer.visible ? '👁' : '○'}
            </button>
            <button
              className="layer-btn lock"
              title={layer.locked ? 'Unlock layer' : 'Lock layer'}
              onClick={e => { e.stopPropagation(); toggleLayerLocked(layer.id) }}
            >
              {layer.locked ? '🔒' : '○'}
            </button>
            {editingId === layer.id ? (
              <input
                className="layer-name-input"
                value={editingName}
                onChange={e => setEditingName(e.target.value)}
                onBlur={commitEdit}
                onKeyDown={e => e.key === 'Enter' && commitEdit()}
                autoFocus
                onClick={e => e.stopPropagation()}
              />
            ) : (
              <span
                className="layer-name"
                onDoubleClick={e => { e.stopPropagation(); startEdit(layer.id, layer.name) }}
              >
                {layer.name}
              </span>
            )}
            <button
              className="layer-btn del"
              title="Delete layer"
              onClick={e => { e.stopPropagation(); removeLayer(layer.id) }}
            >✕</button>
          </li>
        ))}
      </ul>
      {layers.length === 0 && (
        <p className="layers-empty">No layers yet. Add one above.</p>
      )}
    </div>
  )
}
