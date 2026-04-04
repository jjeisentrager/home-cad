import { create } from 'zustand'
import type { ProjectUnits } from '@/lib/dimensions'

export type SidebarTab = 'layers' | 'components' | 'properties'

interface UiState {
  activeSeriesId: string | null
  activeLayerId: string | null
  sidebarTab: SidebarTab
  projectUnits: ProjectUnits

  // Viewport
  panX: number
  panY: number
  zoom: number

  // SVG element offset in the page (updated by Canvas on mount/resize)
  svgOffsetX: number
  svgOffsetY: number

  // Drag: placing a new component from the palette
  draggingTypeId: string | null
  draggingSeriesId: string | null

  // Drag: moving an already-placed component
  draggingPlacedId: string | null
  dragOffsetX: number
  dragOffsetY: number

  // Port connection mode
  connectingFromComponentId: string | null
  connectingFromPortId: string | null
}

interface UiActions {
  setActiveSeries: (id: string) => void
  setActiveLayer: (id: string | null) => void
  setSidebarTab: (tab: SidebarTab) => void
  setProjectUnits: (units: ProjectUnits) => void
  setPan: (x: number, y: number) => void
  setZoom: (zoom: number) => void
  setViewport: (panX: number, panY: number, zoom: number) => void
  setSvgOffset: (x: number, y: number) => void
  // Convert absolute client coordinates to canvas world coordinates
  screenToCanvas: (clientX: number, clientY: number) => { x: number; y: number }

  beginDragType: (typeId: string, seriesId: string) => void
  endDragType: () => void

  beginDragPlaced: (id: string, offsetX: number, offsetY: number) => void
  endDragPlaced: () => void

  beginPortConnect: (componentId: string, portId: string) => void
  cancelPortConnect: () => void
}

export const useUiStore = create<UiState & UiActions>()((set, get) => ({
  activeSeriesId: null,
  activeLayerId: null,
  sidebarTab: 'layers',
  projectUnits: 'in',
  panX: 40,
  panY: 40,
  zoom: 1,
  svgOffsetX: 0,
  svgOffsetY: 0,
  draggingTypeId: null,
  draggingSeriesId: null,
  draggingPlacedId: null,
  dragOffsetX: 0,
  dragOffsetY: 0,
  connectingFromComponentId: null,
  connectingFromPortId: null,

  setActiveSeries: (id) => set({ activeSeriesId: id }),
  setActiveLayer: (id) => set({ activeLayerId: id }),
  setSidebarTab: (tab) => set({ sidebarTab: tab }),
  setProjectUnits: (units) => set({ projectUnits: units }),
  setPan: (x, y) => set({ panX: x, panY: y }),
  setZoom: (zoom) => set({ zoom }),
  setViewport: (panX, panY, zoom) => set({ panX, panY, zoom }),
  setSvgOffset: (x, y) => set({ svgOffsetX: x, svgOffsetY: y }),

  screenToCanvas: (clientX, clientY) => {
    const { panX, panY, zoom, svgOffsetX, svgOffsetY } = get()
    const svgLocalX = clientX - svgOffsetX
    const svgLocalY = clientY - svgOffsetY
    return { x: (svgLocalX - panX) / zoom, y: (svgLocalY - panY) / zoom }
  },

  beginDragType: (typeId, seriesId) =>
    set({ draggingTypeId: typeId, draggingSeriesId: seriesId }),
  endDragType: () =>
    set({ draggingTypeId: null, draggingSeriesId: null }),

  beginDragPlaced: (id, offsetX, offsetY) =>
    set({ draggingPlacedId: id, dragOffsetX: offsetX, dragOffsetY: offsetY }),
  endDragPlaced: () =>
    set({ draggingPlacedId: null, dragOffsetX: 0, dragOffsetY: 0 }),

  beginPortConnect: (componentId, portId) =>
    set({ connectingFromComponentId: componentId, connectingFromPortId: portId }),
  cancelPortConnect: () =>
    set({ connectingFromComponentId: null, connectingFromPortId: null }),
}))
