import { useLayoutStore } from '@/store/layoutStore'
import { useUiStore } from '@/store/uiStore'
import { exportLayoutToJson, importLayoutFromJson, downloadJson } from '@/lib/persistence'
import { UNITS_LABEL, type ProjectUnits } from '@/lib/dimensions'
import './Header.css'

const UNIT_OPTIONS: ProjectUnits[] = ['in', 'ft', 'mm', 'cm']

export default function Header() {
  const exportLayout = useLayoutStore(s => s.exportLayout)
  const loadLayout = useLayoutStore(s => s.loadLayout)
  const setViewport = useUiStore(s => s.setViewport)
  const projectUnits = useUiStore(s => s.projectUnits)
  const setProjectUnits = useUiStore(s => s.setProjectUnits)

  function handleSave() {
    const layout = exportLayout()
    downloadJson('layout.json', exportLayoutToJson(layout))
  }

  function handleLoad() {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.json'
    input.onchange = () => {
      const file = input.files?.[0]
      if (!file) return
      const reader = new FileReader()
      reader.onload = () => {
        try {
          const layout = importLayoutFromJson(reader.result as string)
          loadLayout(layout)
          if (layout.viewport) {
            const v = layout.viewport
            setViewport(v.panX, v.panY, v.zoom)
          }
        } catch {
          alert('Failed to load layout file.')
        }
      }
      reader.readAsText(file)
    }
    input.click()
  }

  return (
    <header className="header">
      <span className="header-title">Home Layout CAD</span>
      <div className="header-actions">
        <label className="header-units-label">Units</label>
        <select
          className="header-units-select"
          value={projectUnits}
          onChange={e => setProjectUnits(e.target.value as ProjectUnits)}
        >
          {UNIT_OPTIONS.map(u => (
            <option key={u} value={u}>{UNITS_LABEL[u]}</option>
          ))}
        </select>
        <button onClick={handleLoad}>Load</button>
        <button onClick={handleSave}>Save</button>
      </div>
    </header>
  )
}
