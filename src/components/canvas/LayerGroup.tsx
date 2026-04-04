import type { Layer, WorldTransform } from '@/types/layout'
import { useLayoutStore } from '@/store/layoutStore'
import PlacedComponentSVG from './PlacedComponentSVG'

interface Props {
  layer: Layer
  transforms: Map<string, WorldTransform>
  zoom: number
}

export default function LayerGroup({ layer, transforms, zoom }: Props) {
  // Select the full array (stable reference when unchanged), then filter in render
  // to avoid creating a new array in the Zustand selector (which causes infinite loops)
  const allComponents = useLayoutStore(s => s.components)
  const components = allComponents.filter(c => c.layerId === layer.id)

  return (
    <g id={`layer-${layer.id}`} opacity={layer.visible ? 1 : 0} pointerEvents={layer.visible ? 'auto' : 'none'}>
      {components.map(comp => {
        const transform = transforms.get(comp.id)
        if (!transform) return null
        return (
          <PlacedComponentSVG
            key={comp.id}
            comp={comp}
            transform={transform}
            zoom={zoom}
          />
        )
      })}
    </g>
  )
}
