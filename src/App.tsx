import { useEffect } from 'react'
import { useLibraryStore } from '@/store/libraryStore'
import { useLayoutStore } from '@/store/layoutStore'
import Sidebar from '@/components/sidebar/Sidebar'
import Canvas from '@/components/canvas/Canvas'
import Header from '@/components/Header'
import './App.css'

export default function App() {
  const loadAllSeries = useLibraryStore(s => s.loadAllSeries)
  const addLayer = useLayoutStore(s => s.addLayer)
  const layers = useLayoutStore(s => s.layers)

  useEffect(() => {
    loadAllSeries()
    // Seed a default layer if none exist
    if (layers.length === 0) {
      addLayer('Layer 1')
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="app">
      <Header />
      <div className="app-body">
        <Sidebar />
        <Canvas />
      </div>
    </div>
  )
}
