export interface PropertyDef {
  key: string
  label: string
  type: 'string' | 'number' | 'enum'
  unit?: string
  enumValues?: string[]
  defaultValue: string | number
}

// Port position expressed as fractions of the component bounding box (0–1).
// normalAngle is the outward direction in degrees: 0=right, 90=down, 180=left, 270=up.
export interface PortDef {
  id: string
  label: string
  xFraction: number
  yFraction: number
  normalAngle: number
}

export interface ComponentTypeDef {
  id: string
  label: string
  description?: string
  // SVG path data drawn in a [0, 0, defaultWidth, defaultHeight] local space
  svgPath: string
  defaultWidth: number
  defaultHeight: number
  ports: PortDef[]
  properties: PropertyDef[]
}

export interface SeriesDef {
  id: string
  label: string
  description?: string
  components: ComponentTypeDef[]
}
