# ViWinTech ThruBlack Window Library

Parametric CAD models of the ViWinTech **ThruBlack** series new-construction
vinyl windows. ThruBlack is ViWinTech's through-color technology — an all-black
vinyl window, black inside and out, that holds its color over time.

> **Patio doors:** the matching ThruBlack **Grand Vista** sliding patio doors
> (Traditional Sliding + French Sliding) live in `ThruBlack-TraditionalSliding/`
> and `ThruBlack-FrenchSliding/` — see [`ThruBlack-Doors-README.md`](ThruBlack-Doors-README.md).

**Source:** ViWinTech 2026 product catalog, *New Construction Windows / ThruBlack*
(`../../_reference/ViWinTech-2026-ALL-Product-WEB-1.pdf`,
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

## Layout

One folder per style; inside each, one sub-folder per callout size holding that
unit's `.FCStd` / `.step` / `.stl` / `preview_iso.png` (e.g.
`ThruBlack-SingleHung/SH3252/ThruBlack_SH3252.FCStd`). The model number encodes
the style and the callout: `SH3252` = single hung 32"×52".

A representative set of **common sizes** is shipped per style (below). These are
not the full catalog grid — each style also offers the other standard callouts
and custom sizing. Add a tuple to the `SIZES` list in a style's
`build_window.py` and rebuild to generate any additional callout; the geometry
is fully parametric.

| Style | Folder | Common sizes shipped (W×H, in) | Operation |
|-------|--------|--------------------------------|-----------|
| Single hung        | `ThruBlack-SingleHung`  | SH2436, SH2852, SH3048, SH3252, SH3660 | top fixed, bottom operable |
| Single glider (XO) | `ThruBlack-Glider`      | SG3624, SG4836, SG6036, SG6048, SG7248 | left operable, right fixed (from outside) |
| 3-lite glider (XOX)| `ThruBlack-3LiteGlider` | 3LG7248, 3LG8448, 3LG9648, 3LG9660, 3LG10848 | 25-50-25, ends operable, center fixed |
| Picture (fixed)    | `ThruBlack-Picture`     | PW2424, PW3636, PW4848, PW6048, PW6060 | direct-glazed fixed |
| Geometric          | `ThruBlack-Geometric`   | HR24, HR36, HR48, HR60, HR72 | half-round (flat bottom, round top), H = W/2, fixed |

### Full standard grids (from the catalog)

- **Single hung** (brick-mould): widths 19/20, 24, 28, 30, 32, 36, 40, 44, 48 ×
  heights 36, 44, 48, 52, 60.
- **Single glider**: widths 24, 36, 48, 52, 60, 72 × heights 24, 36, 42, 48.
- **Picture / 3-lite glider / geometric**: broad ranges plus made-to-order
  shapes; see the catalog size pages.

## Workflow (per style folder)

```sh
freecadcmd build_window.py   # builds every SIZES entry -> <MODEL>/*.FCStd/.step/.stl
freecadcmd render_sw.py      # software-renders each variant -> <MODEL>/preview_iso.png
freecad   color_save.py      # GUI: apply ThruBlack/glass colors to each, resave .FCStd
```

`build_window.py` imports the shared `thrublack_lib.py` builder (one level up, in
`Library/ViWinTech/ThruBlack/`). `render_sw.py` colors by object name
(glass vs. vinyl) and needs no GUI; `color_save.py` is the GUI step that bakes
colors into each `.FCStd`.
