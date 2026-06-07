# ViWinTech ThruBlack Patio Door Library

Parametric CAD models of the ViWinTech **Grand Vista** vinyl patio doors in the
**ThruBlack** finish — ViWinTech's through-color technology, an all-black vinyl
door (black inside and out) that holds its color over time.

**Source:** ViWinTech 2026 product catalog, *Vinyl Doors / Patio Doors* and
*ThruBlack* (`../../_reference/ViWinTech-2026-ALL-Product-WEB-1.pdf`,
<https://www.viwintech.com/wp-content/uploads/2019/05/2026-ALL-Product-WEB-1.pdf>).
These are the two patio-door products in the catalog; both are sliding (ViWinTech
does not list a hinged/swing patio door).

## Modeled profile (from the catalog)

- Fully-welded, multi-chambered frame; 3/4" Emax double-strength insulated glass
- Brick-mould exterior profile with a 1 1/4" integral nailing flange (head + jambs)
- Low-rise sill; positive interlock at the meeting stiles
- Bypass operation: operable panels ride the interior track, fixed panels the
  exterior track (so panels slide past one another)

Constants live in `thrublack_door_lib.py` (it reuses the shared helpers /
brick-mould constants in `thrublack_lib.py`). Callout sizes are inches and equal
the **rough opening**; the modeled unit is the rough opening less 1/4" of install
clearance per side. The model number encodes style + callout (+ panel count for
multi-panel): `GVTS7280` = Grand Vista Traditional Sliding, 72"×80";
`GVFS14496_4P` = Grand Vista French Sliding, 144"×96", 4 panels.

Frame orientation: **X = width, Z = height (sill/floor at Z = 0), Y = depth with
the exterior face at Y = 0 and the interior toward +Y** — the same convention as
the window library, so a door drops into an assembly the same way (wrap the loose
`Part::Feature`s in an `App::Part`, then link + place).

## Layout

One folder per style; inside each, one sub-folder per callout holding that unit's
`.FCStd` / `.step` / `.stl` / `preview_iso.png` (e.g.
`ThruBlack-TraditionalSliding/GVTS7280/ThruBlack_GVTS7280.FCStd`).

| Style | Folder | Common sizes shipped (W×H in, panels) | Operation |
|-------|--------|----------------------------------------|-----------|
| Grand Vista Traditional Sliding | `ThruBlack-TraditionalSliding` | GVTS6080, GVTS7280, GVTS9680 (×80), GVTS7296, GVTS9696 (×96) — all 2-panel | XO bypass (left operable from outside) |
| Grand Vista French Sliding      | `ThruBlack-FrenchSliding`      | GVFS7280 (2P), GVFS9696 (2P), GVFS10896_3P (3P), GVFS14496_4P (4P), GVFS19296_4P (4P) | bypass slider, wide "French" stiles |

The French Sliding door can be made **up to 8 ft tall and up to 4 panels wide**;
panel patterns are 2 = XO, 3 = XOX, 4 = OXXO (X = operable / interior track).
These are a representative shipped set, not the full grid — add a tuple to the
`SIZES` list in a style's `build_door.py` and rebuild to generate any other
callout or panel count; the geometry is fully parametric.

## Workflow (per style folder)

```sh
freecadcmd build_door.py    # builds every SIZES entry -> <MODEL>/*.FCStd/.step/.stl
freecad   color_save.py     # GUI: bake ThruBlack/glass colors into each .FCStd
freecadcmd render_sw.py     # software-renders each variant -> <MODEL>/preview_iso.png
```

`build_door.py` imports the shared `thrublack_door_lib.py` builder (one level up,
in `Library/ViWinTech/ThruBlack/`). `render_sw.py` colors by object name (glass
vs. vinyl) and needs no GUI; `color_save.py` is the GUI step that bakes colors —
run it via the offscreen Qt platform so it doesn't drop `GuiDocument`:

```sh
flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD color_save.py
```
