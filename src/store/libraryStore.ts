import { create } from 'zustand'
import type { SeriesDef, ComponentTypeDef } from '@/types/library'
import { loadAllSeriesData } from '@/lib/libraryLoader'

interface LibraryState {
  series: SeriesDef[]
  loading: boolean
  error: string | null
}

interface LibraryActions {
  loadAllSeries: () => Promise<void>
  getSeriesById: (id: string) => SeriesDef | undefined
  getComponentType: (seriesId: string, typeId: string) => ComponentTypeDef | undefined
}

export const useLibraryStore = create<LibraryState & LibraryActions>()((set, get) => ({
  series: [],
  loading: false,
  error: null,

  loadAllSeries: async () => {
    set({ loading: true, error: null })
    try {
      const series = loadAllSeriesData()
      set({ series, loading: false })
    } catch (e) {
      set({ error: String(e), loading: false })
    }
  },

  getSeriesById: (id) => get().series.find(s => s.id === id),

  getComponentType: (seriesId, typeId) =>
    get().series.find(s => s.id === seriesId)?.components.find(c => c.id === typeId),
}))
