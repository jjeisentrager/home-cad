import { useUiStore } from '@/store/uiStore'
import { useLayoutStore } from '@/store/layoutStore'
import LayersPanel from './LayersPanel'
import SeriesPanel from './SeriesPanel'
import PropertiesPanel from './PropertiesPanel'
import './Sidebar.css'

export default function Sidebar() {
  const sidebarTab = useUiStore(s => s.sidebarTab)
  const setSidebarTab = useUiStore(s => s.setSidebarTab)
  const selectedId = useLayoutStore(s => s.selectedComponentId)

  return (
    <aside className="sidebar">
      <div className="sidebar-tabs">
        <button
          className={sidebarTab === 'layers' ? 'active' : ''}
          onClick={() => setSidebarTab('layers')}
        >Layers</button>
        <button
          className={sidebarTab === 'components' ? 'active' : ''}
          onClick={() => setSidebarTab('components')}
        >Components</button>
        <button
          className={sidebarTab === 'properties' ? 'active' : ''}
          onClick={() => setSidebarTab('properties')}
          disabled={!selectedId}
        >Properties</button>
      </div>
      <div className="sidebar-content">
        {sidebarTab === 'layers' && <LayersPanel />}
        {sidebarTab === 'components' && <SeriesPanel />}
        {sidebarTab === 'properties' && <PropertiesPanel />}
      </div>
    </aside>
  )
}
