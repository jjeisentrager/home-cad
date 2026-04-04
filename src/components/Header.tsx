import { useLayoutStore } from '@/store/layoutStore'
import { useUiStore } from '@/store/uiStore'
import { exportLayoutToJson, importLayoutFromJson, downloadJson } from '@/lib/persistence'
import './Header.css'

export default function Header() {
  const exportLayout = useLayoutStore(s => s.exportLayout)
  const loadLayout = useLayoutStore(s => s.loadLayout)
  const setViewport = useUiStore(s => s.setViewport)

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
        <button onClick={handleLoad}>Load</button>
        <button onClick={handleSave}>Save</button>
      </div>
    </header>
  )
}
