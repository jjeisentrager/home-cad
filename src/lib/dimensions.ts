import type { PlacedComponent } from '@/types/layout'
import type { ComponentTypeDef } from '@/types/library'

export type ProjectUnits = 'in' | 'ft' | 'mm' | 'cm'

export const UNITS_LABEL: Record<ProjectUnits, string> = {
  in: 'Inches',
  ft: 'Feet',
  mm: 'Millimeters',
  cm: 'Centimeters',
}

export const UNITS_SHORT: Record<ProjectUnits, string> = {
  in: 'in',
  ft: 'ft',
  mm: 'mm',
  cm: 'cm',
}

// How many inches equal one of this unit
const INCHES_PER_UNIT: Record<ProjectUnits, number> = {
  in: 1,
  ft: 12,
  mm: 1 / 25.4,
  cm: 1 / 2.54,
}

// Extract a leading number from strings like "2\"", "1.5\"", "3\""
export function parseEnumNumber(value: string | number): number | null {
  const m = String(value).match(/^[\d.]+/)
  return m ? parseFloat(m[0]) : null
}

// Compute the effective canvas pixel dimensions for a placed component
// based on its current property values and the active project unit.
// Components whose JSON has widthProperty/heightProperty set will scale;
// all others return their defaultWidth/defaultHeight unchanged.
export function getEffectiveDimensions(
  comp: PlacedComponent,
  typeDef: ComponentTypeDef,
  projectUnits: ProjectUnits,
): { width: number; height: number } {
  function resolveAxis(propertyKey: string, defaultPx: number): number {
    const def = typeDef.properties.find(p => p.key === propertyKey)
    if (!def) return defaultPx

    const stored = comp.properties.find(p => p.key === propertyKey)
    const rawValue = stored?.value ?? def.defaultValue

    if (def.type === 'number') {
      const val = Number(rawValue)
      const defaultVal = Number(def.defaultValue)
      if (!isFinite(val) || !isFinite(defaultVal) || defaultVal === 0 || val <= 0) return defaultPx
      // defaultValue is always in inches (the base unit encoded in the JSON).
      // Multiply the stored value by inches-per-unit to get inches, then scale.
      const valueInInches = val * INCHES_PER_UNIT[projectUnits]
      return (valueInInches / defaultVal) * defaultPx
    }

    if (def.type === 'enum') {
      // Enum values encode absolute inch sizes, e.g. "2\"", "3\"".
      // No project unit conversion needed — they are always inches.
      const val = parseEnumNumber(rawValue)
      const defaultVal = parseEnumNumber(def.defaultValue)
      if (val == null || defaultVal == null || defaultVal === 0 || val <= 0) return defaultPx
      return (val / defaultVal) * defaultPx
    }

    return defaultPx
  }

  return {
    width: typeDef.widthProperty
      ? resolveAxis(typeDef.widthProperty, typeDef.defaultWidth)
      : typeDef.defaultWidth,
    height: typeDef.heightProperty
      ? resolveAxis(typeDef.heightProperty, typeDef.defaultHeight)
      : typeDef.defaultHeight,
  }
}
