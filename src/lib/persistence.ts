import type { CanvasLayout } from '@/types/layout'

export function exportLayoutToJson(layout: CanvasLayout): string {
  return JSON.stringify({ ...layout, updatedAt: new Date().toISOString() }, null, 2)
}

export function importLayoutFromJson(json: string): CanvasLayout {
  const data = JSON.parse(json) as CanvasLayout
  if (!data.version || !Array.isArray(data.layers) || !Array.isArray(data.components)) {
    throw new Error('Invalid layout file')
  }
  return data
}

export function downloadJson(filename: string, content: string): void {
  const blob = new Blob([content], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}
