import { useLayoutStore } from '@/store/layoutStore'
import { useLibraryStore } from '@/store/libraryStore'
import type { PlacedComponent } from '@/types/layout'
import type { ComponentTypeDef } from '@/types/library'
import './PropertiesPanel.css'

export default function PropertiesPanel() {
  const selectedId = useLayoutStore(s => s.selectedComponentId)
  const components = useLayoutStore(s => s.components)
  const comp = components.find(c => c.id === selectedId)

  const getComponentType = useLibraryStore(s => s.getComponentType)
  const typeDef = comp ? getComponentType(comp.seriesId, comp.typeId) : undefined

  if (!comp || !typeDef) {
    return <p className="props-empty">Select a component to view its properties.</p>
  }

  return <PropertiesEditor comp={comp} typeDef={typeDef} />
}

function PropertiesEditor({ comp, typeDef }: { comp: PlacedComponent; typeDef: ComponentTypeDef }) {
  const updateLabel = useLayoutStore(s => s.updateComponentLabel)
  const updateProperty = useLayoutStore(s => s.updateComponentProperty)
  const updateLayer = useLayoutStore(s => s.updateComponentLayer)
  const rotateComponent = useLayoutStore(s => s.rotateComponent)
  const setPositionAssignment = useLayoutStore(s => s.setPositionAssignment)
  const layers = useLayoutStore(s => s.layers)
  const components = useLayoutStore(s => s.components)
  const getComponentType = useLibraryStore(s => s.getComponentType)
  function getPropValue(key: string): string | number {
    const p = comp.properties.find(p => p.key === key)
    return p?.value ?? typeDef.properties.find(d => d.key === key)?.defaultValue ?? ''
  }

  const assign = comp.positionAssignment
  const destComp = components.find(c => c.id === assign?.destinationComponentId)
  const destTypeDef = destComp ? getComponentType(destComp.seriesId, destComp.typeId) : undefined

  return (
    <div className="props-panel">
      <div className="props-section">
        <div className="props-row">
          <label>Label</label>
          <input
            value={comp.label ?? ''}
            onChange={e => updateLabel(comp.id, e.target.value)}
            placeholder={typeDef.label}
          />
        </div>
        <div className="props-row">
          <label>Layer</label>
          <select
            value={comp.layerId}
            onChange={e => updateLayer(comp.id, e.target.value)}
          >
            {layers.map(l => <option key={l.id} value={l.id}>{l.name}</option>)}
          </select>
        </div>
        <div className="props-row">
          <label>Rotation</label>
          <input
            type="number"
            value={comp.manualRotation}
            onChange={e => rotateComponent(comp.id, Number(e.target.value))}
            step={15}
          />
        </div>
      </div>

      {typeDef.properties.length > 0 && (
        <div className="props-section">
          <div className="props-section-title">Properties</div>
          {typeDef.properties.map(def => (
            <div key={def.key} className="props-row">
              <label>{def.label}{def.unit ? ` (${def.unit})` : ''}</label>
              {def.type === 'enum' ? (
                <select
                  value={String(getPropValue(def.key))}
                  onChange={e => updateProperty(comp.id, def.key, e.target.value)}
                >
                  {def.enumValues?.map(v => <option key={v} value={v}>{v}</option>)}
                </select>
              ) : (
                <input
                  type={def.type === 'number' ? 'number' : 'text'}
                  value={getPropValue(def.key)}
                  onChange={e =>
                    updateProperty(comp.id, def.key,
                      def.type === 'number' ? Number(e.target.value) : e.target.value
                    )
                  }
                />
              )}
            </div>
          ))}
        </div>
      )}

      {typeDef.ports.length > 0 && (
        <div className="props-section">
          <div className="props-section-title">Position Assignment</div>
          <div className="props-row">
            <label>Source port</label>
            <select
              value={assign?.sourcePortId ?? ''}
              onChange={e => {
                if (!e.target.value) {
                  setPositionAssignment(comp.id, undefined)
                  return
                }
                setPositionAssignment(comp.id, {
                  sourcePortId: e.target.value,
                  destinationComponentId: assign?.destinationComponentId ?? '',
                  destinationPortId: assign?.destinationPortId ?? '',
                  offsetX: assign?.offsetX ?? 0,
                  offsetY: assign?.offsetY ?? 0,
                  orientationOffset: assign?.orientationOffset ?? 0,
                })
              }}
            >
              <option value="">(none)</option>
              {typeDef.ports.map(p => <option key={p.id} value={p.id}>{p.label}</option>)}
            </select>
          </div>
          {assign?.sourcePortId && (
            <>
              <div className="props-row">
                <label>Dest. component</label>
                <select
                  value={assign.destinationComponentId}
                  onChange={e => setPositionAssignment(comp.id, { ...assign, destinationComponentId: e.target.value, destinationPortId: '' })}
                >
                  <option value="">(select)</option>
                  {components.filter(c => c.id !== comp.id).map(c => (
                    <option key={c.id} value={c.id}>{c.label ?? getComponentType(c.seriesId, c.typeId)?.label ?? c.id}</option>
                  ))}
                </select>
              </div>
              {assign.destinationComponentId && destTypeDef && (
                <div className="props-row">
                  <label>Dest. port</label>
                  <select
                    value={assign.destinationPortId}
                    onChange={e => setPositionAssignment(comp.id, { ...assign, destinationPortId: e.target.value })}
                  >
                    <option value="">(select)</option>
                    {destTypeDef.ports.map(p => <option key={p.id} value={p.id}>{p.label}</option>)}
                  </select>
                </div>
              )}
              <div className="props-row">
                <label>Offset X</label>
                <input type="number" value={assign.offsetX} onChange={e => setPositionAssignment(comp.id, { ...assign, offsetX: Number(e.target.value) })} />
              </div>
              <div className="props-row">
                <label>Offset Y</label>
                <input type="number" value={assign.offsetY} onChange={e => setPositionAssignment(comp.id, { ...assign, offsetY: Number(e.target.value) })} />
              </div>
              <div className="props-row">
                <label>Orient. offset°</label>
                <input type="number" value={assign.orientationOffset} step={15} onChange={e => setPositionAssignment(comp.id, { ...assign, orientationOffset: Number(e.target.value) })} />
              </div>
              <button className="props-clear-btn" onClick={() => setPositionAssignment(comp.id, undefined)}>
                Clear assignment
              </button>
            </>
          )}
        </div>
      )}
    </div>
  )
}
