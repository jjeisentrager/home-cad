# -*- coding: utf-8 -*-
"""
Parametric builder for ViWinTech **ThruBlack** patio DOORS (Grand Vista line).

The 2026 catalog ships ViWinTech's patio doors in two styles, both available in
ThruBlack through-color black vinyl (black inside and out):

  - traditional_sliding : Grand Vista Traditional Sliding Door -- 2-panel XO
        bypass slider; multi-chambered welded frame, double weatherstrip,
        no-jump rolling screen, low-rise sill, reversible.
  - french_sliding      : Grand Vista French Sliding Door -- wide-stile "French"
        aesthetic on a bypass slider; up to 8 ft tall and up to 4 panels wide,
        multi-point latch/lock.

Both: fully-welded frame + sash, 3/4" Emax double-strength insulated glass,
brick-mould exterior profile with an integral nailing flange (new construction),
and a positive interlock at the meeting stiles.  Callout sizes are inches and
equal the rough opening; the modelled unit is the rough opening less 1/4" of
install clearance per side (matches the window library).

Frame: X = width, Z = height (sill/floor at Z=0), Y = depth with the EXTERIOR
face at Y=0 and the interior toward +Y.  Operable panels ride the interior
track, fixed panels the exterior track, so adjacent panels bypass.

Imported by each ThruBlack-*Sliding/build_door.py:

    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import thrublack_door_lib as td
    td.build("traditional_sliding", 72, 80, 2, OUT, "ThruBlack_GVTS7280")

Run headless:  freecadcmd build_door.py
Units: millimetres.
"""
import os
import FreeCAD as App
import Part
import Mesh
import thrublack_lib as tb   # shared helpers (_box, _ring, _Doc) + profile consts

IN = 25.4

# --- patio-door profile constants (mm) -------------------------------------
INSTALL_CLR = 0.25 * IN      # unit = rough opening less 1/4" per side
FRAME_DEPTH = 4.5 * IN       # multi-chambered patio-door frame depth = 114.3
FRAME_FACE = 2.0 * IN        # frame head / jamb / sill visible face = 50.8
PANEL_DEPTH = 1.75 * IN      # sliding panel (sash) thickness in Y = 44.45
GLASS_T = 0.75 * IN          # 3/4" Emax insulated glass
STILE_TRAD = 2.5 * IN        # traditional sliding stile / rail = 63.5
STILE_FRENCH = 3.75 * IN     # wider "French" stile / rail = 95.25
BOTTOM_RAIL = 4.0 * IN       # taller bottom rail (kick) = 101.6
HANDLE_H = 250.0             # pull-handle length
HANDLE_Z = 1000.0            # pull-handle centre height (mm above floor)
HANDLE_PROUD = 32.0          # pull-handle projection into the room

STYLES = ("traditional_sliding", "french_sliding")

# operable (X) / fixed (O) per panel count; X rides interior track, O exterior
PATTERNS = {2: "XO", 3: "XOX", 4: "OXXO"}


def _door_trim(D, UW, UH):
    """Brick-mould + integral nailing flange around the head and jambs only
    (a patio door has a sill at the floor, not brick mould)."""
    bw, bt = tb.BRICK_W, tb.BRICK_T
    D.black("BrickMould_Top", tb._box(UW + 2 * bw, bt, bw, -bw, -bt, UH))
    D.black("BrickMould_L", tb._box(bw, bt, UH + bw, -bw, -bt, 0.0))
    D.black("BrickMould_R", tb._box(bw, bt, UH + bw, UW, -bt, 0.0))
    fw, ft = bw + tb.FLANGE_W, tb.FLANGE_T
    D.black("NailingFlange_Top", tb._box(UW + 2 * fw, ft, fw, -fw, 0.0, UH))
    D.black("NailingFlange_L", tb._box(fw, ft, UH + fw, -fw, 0.0, 0.0))
    D.black("NailingFlange_R", tb._box(fw, ft, UH + fw, UW, 0.0, 0.0))


def _panel(D, idx, x0, z0, w, h, y0, stile, operable, door_cx):
    """One glazed sliding panel: black stiles + rails (wider bottom kick rail)
    around a recessed glass lite, plus a pull handle if operable."""
    name = "Panel%d" % idx
    d = PANEL_DEPTH
    D.black(name + "_StileL", tb._box(stile, d, h, x0, y0, z0))
    D.black(name + "_StileR", tb._box(stile, d, h, x0 + w - stile, y0, z0))
    iw = w - 2 * stile
    D.black(name + "_RailTop", tb._box(iw, d, stile, x0 + stile, y0, z0 + h - stile))
    D.black(name + "_RailBot", tb._box(iw, d, BOTTOM_RAIL, x0 + stile, y0, z0))
    gz = z0 + BOTTOM_RAIL
    gh = h - BOTTOM_RAIL - stile
    D.glass(name, tb._box(iw, GLASS_T, gh, x0 + stile, y0 + (d - GLASS_T) / 2.0, gz))
    if operable:
        lead_x = (x0 + w - stile) if (x0 + w / 2.0) < door_cx else x0
        hw = stile * 0.55
        hx = lead_x + (stile - hw) / 2.0
        hz = max(z0 + BOTTOM_RAIL, HANDLE_Z - HANDLE_H / 2.0)
        D.black(name + "_Handle", tb._box(hw, HANDLE_PROUD, HANDLE_H, hx, y0 + d, hz))


def build(style, ro_w_in, ro_h_in, panels, out_dir, docname):
    if style not in STYLES:
        raise ValueError("unknown style %r (choose from %s)" % (style, STYLES))
    pattern = PATTERNS.get(panels)
    if pattern is None:
        raise ValueError("no panel pattern for %d panels" % panels)

    UW = ro_w_in * IN - 2 * INSTALL_CLR
    UH = ro_h_in * IN - 2 * INSTALL_CLR
    D = tb._Doc(docname)

    D.black("Frame", tb._ring(UW, UH, FRAME_FACE, FRAME_DEPTH, 0, 0, 0))
    _door_trim(D, UW, UH)

    ix, iz = FRAME_FACE, FRAME_FACE
    iw, ih = UW - 2 * FRAME_FACE, UH - 2 * FRAME_FACE
    stile = STILE_FRENCH if style == "french_sliding" else STILE_TRAD
    s = iw / panels
    gap = (FRAME_DEPTH - 2 * PANEL_DEPTH) / 3.0    # two bypass tracks
    y_ext, y_int = gap, 2 * gap + PANEL_DEPTH
    door_cx = ix + iw / 2.0
    for k, ch in enumerate(pattern):
        x0 = ix + k * s
        y0 = y_int if ch == "X" else y_ext          # operable interior, fixed exterior
        _panel(D, k + 1, x0, iz, s, ih, y0, stile, ch == "X", door_cx)

    D.doc.recompute()
    return _save(D, out_dir, docname)


def _save(D, out_dir, docname):
    fcstd = os.path.join(out_dir, docname + ".FCStd")
    step = os.path.join(out_dir, docname + ".step")
    stl = os.path.join(out_dir, docname + ".stl")
    D.doc.saveAs(fcstd)
    Part.export(D.objs, step)
    compound = Part.makeCompound([o.Shape for o in D.objs])
    Mesh.Mesh(compound.tessellate(0.8)).write(stl)
    bb = compound.BoundBox
    print("Saved: %s" % fcstd)
    print("Overall (in)  W x H x D = %.2f x %.2f x %.2f"
          % (bb.XLength / IN, bb.ZLength / IN, bb.YLength / IN))
    return D
