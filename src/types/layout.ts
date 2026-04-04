export interface PortPositionAssignment {
  sourcePortId: string
  destinationComponentId: string
  destinationPortId: string
  offsetX: number
  offsetY: number
  orientationOffset: number // degrees added on top of anti-parallel alignment
}

export interface PropertyValue {
  key: string
  value: string | number
}

export interface PlacedComponent {
  id: string
  typeId: string
  seriesId: string
  layerId: string
  label?: string
  // Used when no positionAssignment, or as the root anchor
  manualX: number
  manualY: number
  manualRotation: number // degrees
  // When set, world position is derived from another component's port
  positionAssignment?: PortPositionAssignment
  properties: PropertyValue[]
}

export interface Layer {
  id: string
  name: string
  visible: boolean
  locked: boolean
  order: number // lower renders first (bottom)
}

// Computed world transform — never stored, always derived by positionResolver
export interface WorldTransform {
  x: number       // top-left of bounding box in canvas units
  y: number
  rotation: number // degrees
  hasCycleError?: boolean
}

export interface CanvasLayout {
  version: number
  name: string
  createdAt: string
  updatedAt: string
  layers: Layer[]
  components: PlacedComponent[]
  viewport?: {
    panX: number
    panY: number
    zoom: number
  }
}
