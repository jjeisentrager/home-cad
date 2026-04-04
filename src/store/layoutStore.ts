import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import { v4 as uuidv4 } from 'uuid'
import type { Layer, PlacedComponent, PortPositionAssignment, CanvasLayout } from '@/types/layout'

interface LayoutState {
  layers: Layer[]
  components: PlacedComponent[]
  selectedComponentId: string | null
}

interface LayoutActions {
  // Layer actions
  addLayer: (name: string) => void
  removeLayer: (id: string) => void
  toggleLayerVisible: (id: string) => void
  toggleLayerLocked: (id: string) => void
  renameLayer: (id: string, name: string) => void
  reorderLayers: (orderedIds: string[]) => void

  // Component actions
  addComponent: (comp: Omit<PlacedComponent, 'id'>) => string
  removeComponent: (id: string) => void
  moveComponent: (id: string, x: number, y: number) => void
  rotateComponent: (id: string, rotation: number) => void
  updateComponentProperty: (id: string, key: string, value: string | number) => void
  updateComponentLabel: (id: string, label: string) => void
  updateComponentLayer: (id: string, layerId: string) => void
  setPositionAssignment: (id: string, assignment: PortPositionAssignment | undefined) => void
  selectComponent: (id: string | null) => void

  // Persistence
  loadLayout: (layout: CanvasLayout) => void
  exportLayout: () => CanvasLayout
}

export const useLayoutStore = create<LayoutState & LayoutActions>()(
  immer((set, get) => ({
    layers: [],
    components: [],
    selectedComponentId: null,

    addLayer: (name) =>
      set(state => {
        const maxOrder = state.layers.reduce((m, l) => Math.max(m, l.order), -1)
        state.layers.push({
          id: uuidv4(),
          name,
          visible: true,
          locked: false,
          order: maxOrder + 1,
        })
      }),

    removeLayer: (id) =>
      set(state => {
        state.layers = state.layers.filter(l => l.id !== id)
        state.components = state.components.filter(c => c.layerId !== id)
      }),

    toggleLayerVisible: (id) =>
      set(state => {
        const l = state.layers.find(l => l.id === id)
        if (l) l.visible = !l.visible
      }),

    toggleLayerLocked: (id) =>
      set(state => {
        const l = state.layers.find(l => l.id === id)
        if (l) l.locked = !l.locked
      }),

    renameLayer: (id, name) =>
      set(state => {
        const l = state.layers.find(l => l.id === id)
        if (l) l.name = name
      }),

    reorderLayers: (orderedIds) =>
      set(state => {
        orderedIds.forEach((id, idx) => {
          const l = state.layers.find(l => l.id === id)
          if (l) l.order = idx
        })
      }),

    addComponent: (comp) => {
      const id = uuidv4()
      set(state => { state.components.push({ ...comp, id }) })
      return id
    },

    removeComponent: (id) =>
      set(state => {
        state.components = state.components.filter(c => c.id !== id)
        // Clear position assignments pointing to the removed component
        state.components.forEach(c => {
          if (c.positionAssignment?.destinationComponentId === id) {
            c.positionAssignment = undefined
          }
        })
        if (state.selectedComponentId === id) state.selectedComponentId = null
      }),

    moveComponent: (id, x, y) =>
      set(state => {
        const c = state.components.find(c => c.id === id)
        if (c) { c.manualX = x; c.manualY = y }
      }),

    rotateComponent: (id, rotation) =>
      set(state => {
        const c = state.components.find(c => c.id === id)
        if (c) c.manualRotation = rotation
      }),

    updateComponentProperty: (id, key, value) =>
      set(state => {
        const c = state.components.find(c => c.id === id)
        if (!c) return
        const prop = c.properties.find(p => p.key === key)
        if (prop) prop.value = value
        else c.properties.push({ key, value })
      }),

    updateComponentLabel: (id, label) =>
      set(state => {
        const c = state.components.find(c => c.id === id)
        if (c) c.label = label
      }),

    updateComponentLayer: (id, layerId) =>
      set(state => {
        const c = state.components.find(c => c.id === id)
        if (c) c.layerId = layerId
      }),

    setPositionAssignment: (id, assignment) =>
      set(state => {
        const c = state.components.find(c => c.id === id)
        if (c) c.positionAssignment = assignment
      }),

    selectComponent: (id) =>
      set(state => { state.selectedComponentId = id }),

    loadLayout: (layout) =>
      set(state => {
        state.layers = layout.layers
        state.components = layout.components
        state.selectedComponentId = null
      }),

    exportLayout: () => {
      const { layers, components } = get()
      return {
        version: 1,
        name: 'My Layout',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        layers,
        components,
      }
    },
  })),
)
