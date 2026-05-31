# ViWinTech ThruBlack Window Library

Parametric CAD models of the ViWinTech **ThruBlack** series new-construction
vinyl windows. ThruBlack is ViWinTech's through-color technology — an all-black
vinyl window, black inside and out, that holds its color over time.

**Source:** ViWinTech 2026 product catalog, *New Construction Windows / ThruBlack*
(`_reference/ViWinTech-2026-ALL-Product-WEB-1.pdf`,
<https://www.viwintech.com/wp-content/uploads/2019/05/2026-ALL-Product-WEB-1.pdf>).

## Modeled profile (from the catalog)

- Brick-mould exterior profile
- Block-and-tackle balance system
- Fully welded 2 7/8" frame
- Double-strength glass standard
- 3/4" J pocket with a 1 1/4" integral nailing flange

All constants live in `thrublack_lib.py`. Callout sizes are inches and equal the
**rough opening**; the modeled unit is the rough opening less 1/4" of install
clearance per side.

## Styles (one folder each)

| Folder | Style | Default callout | Operation |
|--------|-------|-----------------|-----------|
| `ThruBlack-SingleHung`  | Single hung        | SH3252 — 32×52  | top fixed, bottom operable |
| `ThruBlack-Glider`      | Single glider (XO) | SG4836 — 48×36  | left operable, right fixed (viewed from outside) |
| `ThruBlack-3LiteGlider` | 3-lite glider (XOX)| 3LG9648 — 96×48 | 25-50-25, ends operable, center fixed |
| `ThruBlack-Picture`     | Picture (fixed)    | PW4848 — 48×48  | direct-glazed fixed |
| `ThruBlack-Geometric`   | Geometric          | HR48 — 48×24    | half-round (flat bottom, round top), fixed |

The 1150 brick-mould size grid (single hung shown in the catalog) gives the
standard callouts; e.g. single-hung widths 20/24/28/30/32/36/40/44/48" ×
heights 36/44/48/52/60". Change `RO_W` / `RO_H` in any `build_window.py` to
generate a different callout — the geometry is fully parametric.

## Workflow (per folder)

```sh
freecadcmd build_window.py   # geometry -> .FCStd / .step / .stl
freecadcmd render_sw.py      # software render -> preview_iso.png
freecad   color_save.py      # GUI: apply ThruBlack/glass colors, resave .FCStd
```

`build_window.py` imports the shared `Library/thrublack_lib.py` builder.
`render_sw.py` colors by object name (glass vs. vinyl) and needs no GUI;
`color_save.py` is the GUI step that bakes colors into the `.FCStd`.
