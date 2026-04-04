import type { SeriesDef } from '@/types/library'
import sch40pvc from '@/data/series/sch40-pvc.json'
import floorplan from '@/data/series/floorplan.json'
import electrical from '@/data/series/electrical.json'

export function loadAllSeriesData(): SeriesDef[] {
  return [sch40pvc, floorplan, electrical] as SeriesDef[]
}
