# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
npm run dev       # Start dev server (Vite)
npm run build     # Type-check + production build (tsc -b && vite build)
npm run preview   # Serve the dist/ build locally
```

No test suite is configured. TypeScript errors surface via `npm run build`.

The `@/` path alias maps to `src/` (configured in Vite).

## Architecture

This is a browser-based CAD/diagramming tool built with React, Zustand, and SVG rendering. There are no tests and no backend — everything is client-side.

### Three Zustand stores

- **`layoutStore`** — the source of truth for the canvas: `layers[]` and `components[]` (both persisted as JSON), plus `selectedComponentId`. Uses `immer` middleware for immutable updates.
- **`libraryStore`** — read-only component type definitions loaded from JSON files in `src/data/series/`. Provides lookup helpers (`getComponentType`, `getSeriesById`).
- **`uiStore`** — ephemeral view state: pan/zoom, drag-in-progress flags, port-connection mode, active layer/series, sidebar tab.

### Library vs. Layout

The library (`src/types/library.ts`) defines *types* of components via `SeriesDef → ComponentTypeDef`. Each `ComponentTypeDef` has an `svgPath`, default dimensions, `PortDef[]` (connection points expressed as fractions of the bounding box), and `PropertyDef[]`.

The layout (`src/types/layout.ts`) stores *instances* (`PlacedComponent`) which reference a `(seriesId, typeId)` pair and hold a manual position/rotation plus optional `positionAssignment`.

### Port-based positioning (`positionResolver.ts`)

When a `PlacedComponent` has a `positionAssignment`, its world position is *derived* rather than manual. The resolver:
1. Topologically sorts components by their assignment dependency chain (detects cycles).
2. For each dependent component, computes the world position of the destination port, then solves for the bbox top-left so the source port aligns anti-parallel to the destination port.

`WorldTransform` (x, y, rotation, hasCycleError) is never stored — it is recomputed via `resolveAllPositions()` inside a `useMemo` in `Canvas.tsx` on every render.

### Dimension-driven rendering

`ComponentTypeDef` has optional `widthProperty` and `heightProperty` fields — property keys whose values drive the visual pixel size on canvas. `src/lib/dimensions.ts` provides:

- `getEffectiveDimensions(comp, typeDef, projectUnits)` — returns `{width, height}` in canvas pixels. For `number` properties the stored value is converted from project units to inches (the JSON base unit), then scaled proportionally from `defaultWidth/Height`. For `enum` properties (e.g., diameter like `"2\""`) the number is parsed directly and scaled proportionally.
- `ProjectUnits` type (`'in' | 'ft' | 'mm' | 'cm'`) and associated constants.

Effective dimensions flow into: `PlacedComponentSVG` (SVG `scale()` transform + port dot positions), `positionResolver.resolveAllPositions` (port world positions + bbox math), `Canvas.fitToView` (bounds calculation), and `PortDot` (circle center via `getPortWorldPosition`).

The `getPortWorldPosition` in `geometry.ts` accepts an optional `dims` override to use instead of `typeDef.defaultWidth/Height`.

`projectUnits` lives in `uiStore` (default `'in'`). The Header exposes a unit selector. PropertiesPanel displays the active unit label next to spatial-unit inputs.

### Adding a new component series

1. Create `src/data/series/<id>.json` matching the `SeriesDef` type.
2. Import and add it to the array in `src/lib/libraryLoader.ts`.
3. Add `widthProperty` / `heightProperty` to any components whose visual size should track property values.

### Canvas interaction

- SVG-based rendering in `Canvas.tsx`; each layer is a `<LayerGroup>` which renders `<PlacedComponentSVG>` per component.
- Drag-to-place: set `draggingTypeId/draggingSeriesId` via `beginDragType`, handled by `onDrop` on the SVG.
- Port connection: two-click workflow — `beginPortConnect` on the first port, `setPositionAssignment` on the second.
- Keyboard shortcuts (when no input is focused): `Delete`/`Backspace` deletes selected, `Escape` deselects/cancels, `F` fits to view.

### Persistence

`src/lib/persistence.ts` provides `exportLayoutToJson` / `importLayoutFromJson` / `downloadJson`. The `Header` component calls `layoutStore.exportLayout()` and `loadLayout()` for save/open. There is no autosave.
