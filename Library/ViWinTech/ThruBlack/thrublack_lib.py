# -*- coding: utf-8 -*-
"""
Parametric builder for ViWinTech **ThruBlack** series vinyl windows.

ThruBlack is ViWinTech's advanced through-color technology: an all-black vinyl
window, black inside and out, that keeps its colour over time. Per the 2026
catalog the ThruBlack window features:
  - a brick-mould exterior profile
  - block-and-tackle balance system
  - a fully welded 2 7/8" frame
  - double-strength glass standard
  - a 3/4" J pocket with a 1 1/4" integral nailing flange
Available styles: single hung, single glider (XO), 3-lite glider (XOX),
picture (fixed), and geometric (half-round here).

Source: ViWinTech 2026 product catalog, "New Construction Windows / ThruBlack"
(2026-ALL-Product-WEB-1.pdf). Callout sizes are inches and equal the rough
opening; the modelled unit is the rough opening less 1/4" of install clearance
per side.

This module is imported by each Library/ThruBlack-*/build_window.py:

    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import thrublack_lib as tb
    tb.build("single_hung", 32, 52, OUT, "ThruBlack_SH3252")

Run headless:  freecadcmd build_window.py

Units: millimetres.
"""
import os
import math
import FreeCAD as App
import Part
import Mesh

IN = 25.4  # mm per inch

# --- ThruBlack profile constants (mm) --------------------------------------
INSTALL_CLR = 0.25 * IN    # unit = rough opening less 1/4" per side
FRAME_DEPTH = 2.875 * IN   # fully welded 2 7/8" frame
FRAME_FACE = 1.75 * IN     # visible main-frame border width
SASH_FACE = 1.0 * IN       # sash rail / stile width
SASH_DEPTH = 1.25 * IN     # sash thickness (Y)
GLASS_T = 0.75 * IN        # double-strength insulated glass unit
FLANGE_W = 1.25 * IN       # 1 1/4" integral nailing flange
FLANGE_T = 1.6             # nailing-fin sheet thickness
BRICK_W = 1.75 * IN        # brick-mould exterior trim width
BRICK_T = 1.0 * IN         # brick-mould proud of the exterior face
SASH_OFFSET = 8.0          # operable/fixed sash stagger in Y

# Exterior face sits at Y = 0; the wall/interior is toward +Y.

STYLES = ("single_hung", "glider", "glider3", "picture", "geometric")


def _box(lx, ly, lz, x, y, z):
    return Part.makeBox(lx, ly, lz, App.Vector(x, y, z))


def _ring(ow, oh, face, depth, x0, z0, y0):
    """A rectangular picture-frame ring: outer ow(x) x oh(z), border `face`,
    extruded `depth` along Y starting at y0, lower-left corner at (x0, z0)."""
    outer = _box(ow, depth, oh, x0, y0, z0)
    inner = _box(ow - 2 * face, depth + 2, oh - 2 * face, x0 + face, y0 - 1, z0 + face)
    return outer.cut(inner)


def _half(shape, zcut):
    """Keep only the part of `shape` with Z >= zcut (flat-bottom half-round)."""
    bb = shape.BoundBox
    keep = _box(bb.XLength + 4, bb.YLength + 4, bb.ZMax - zcut + 2,
                bb.XMin - 2, bb.YMin - 2, zcut)
    return shape.common(keep)


class _Doc:
    """Collects black (vinyl) and glass solids as named Part::Features."""

    def __init__(self, name):
        self.doc = App.newDocument(name)
        self.objs = []

    def black(self, name, shp):
        return self._add(name, shp)

    def glass(self, name, shp):
        return self._add(name if "glass" in name.lower() else name + "_Glass", shp)

    def _add(self, name, shp):
        o = self.doc.addObject("Part::Feature", name)
        o.Shape = shp
        self.objs.append(o)
        return o


def _exterior_trim(D, UW, UH):
    """Brick-mould trim (proud, exterior) + integral nailing fin, rectangular."""
    # Brick mould stands proud of the exterior face (toward -Y).
    brick = _ring(UW + 2 * BRICK_W, UH + 2 * BRICK_W, BRICK_W, BRICK_T,
                  -BRICK_W, -BRICK_W, -BRICK_T)
    D.black("BrickMould", brick)
    # Nailing fin: thin sheet in the wall plane, extends past the brick mould.
    fin_face = BRICK_W + FLANGE_W
    fin = _ring(UW + 2 * fin_face, UH + 2 * fin_face, fin_face, FLANGE_T,
                -fin_face, -fin_face, 0.0)
    D.black("NailingFlange", fin)


def _sash(D, name, x0, z0, w, h, y0):
    """A glazed sash: black ring + recessed glass lite."""
    D.black(name, _ring(w, h, SASH_FACE, SASH_DEPTH, x0, z0, y0))
    gw, gh = w - 2 * SASH_FACE, h - 2 * SASH_FACE
    D.glass(name, _box(gw, GLASS_T, gh,
                       x0 + SASH_FACE, y0 + (SASH_DEPTH - GLASS_T) / 2.0,
                       z0 + SASH_FACE))


def _build_rect_frame(D, UW, UH):
    """Main welded frame + exterior trim. Returns interior opening rect."""
    D.black("Frame", _ring(UW, UH, FRAME_FACE, FRAME_DEPTH, 0, 0, 0))
    _exterior_trim(D, UW, UH)
    iw = UW - 2 * FRAME_FACE
    ih = UH - 2 * FRAME_FACE
    return FRAME_FACE, FRAME_FACE, iw, ih  # x0, z0, width, height


def build(style, ro_w_in, ro_h_in, out_dir, docname):
    if style not in STYLES:
        raise ValueError("unknown style %r (choose from %s)" % (style, STYLES))

    UW = ro_w_in * IN - 2 * INSTALL_CLR
    UH = ro_h_in * IN - 2 * INSTALL_CLR
    D = _Doc(docname)

    if style == "geometric":
        _build_geometric(D, UW)
    else:
        ix, iz, iw, ih = _build_rect_frame(D, UW, UH)
        # interior sash depth window (centred in the frame depth)
        ys = (FRAME_DEPTH - SASH_DEPTH) / 2.0

        if style == "single_hung":
            half = (ih + SASH_FACE) / 2.0
            # top sash fixed, shifted toward exterior; bottom operable, interior
            _sash(D, "Sash_Top", ix, iz + ih - half, iw, half, ys - SASH_OFFSET)
            _sash(D, "Sash_Bottom", ix, iz, iw, half, ys + SASH_OFFSET)

        elif style == "glider":  # XO, viewed from outside (left operable)
            half = (iw + SASH_FACE) / 2.0
            _sash(D, "Sash_Left", ix, iz, half, ih, ys + SASH_OFFSET)
            _sash(D, "Sash_Right", ix + iw - half, iz, half, ih, ys - SASH_OFFSET)

        elif style == "glider3":  # XOX, 25-50-25, centre fixed
            side = iw * 0.25
            cen = iw * 0.50
            _sash(D, "Sash_Left", ix, iz, side + SASH_FACE, ih, ys + SASH_OFFSET)
            _sash(D, "Sash_Center", ix + side - SASH_FACE / 2.0, iz,
                  cen + SASH_FACE, ih, ys - SASH_OFFSET)
            _sash(D, "Sash_Right", ix + iw - side - SASH_FACE, iz,
                  side + SASH_FACE, ih, ys + SASH_OFFSET)

        elif style == "picture":  # fixed, direct-glaze with glazing bead
            D.black("GlazingBead",
                    _ring(iw, ih, SASH_FACE * 0.6, SASH_DEPTH * 0.5,
                          ix, iz, FRAME_DEPTH - SASH_DEPTH * 0.5))
            D.glass("Picture",
                    _box(iw, GLASS_T, ih, ix,
                         (FRAME_DEPTH - GLASS_T) / 2.0, iz))

    D.doc.recompute()
    return _save(D, out_dir, docname)


def _build_geometric(D, UW):
    """Half-round (semicircle) fixed window: flat bottom, round top."""
    R = UW / 2.0
    axis = App.Vector(0, 1, 0)
    base = App.Vector(R, 0, 0)

    outer = Part.makeCylinder(R, FRAME_DEPTH, base, axis)
    inner = Part.makeCylinder(R - FRAME_FACE, FRAME_DEPTH + 2,
                              App.Vector(R, -1, 0), axis)
    D.black("Frame", _half(outer.cut(inner), 0.0))

    # brick-mould half-round, proud of the exterior face
    bm_o = Part.makeCylinder(R + BRICK_W, BRICK_T, App.Vector(R, -BRICK_T, 0), axis)
    bm_i = Part.makeCylinder(R, BRICK_T + 2, App.Vector(R, -BRICK_T - 1, 0), axis)
    D.black("BrickMould", _half(bm_o.cut(bm_i), 0.0))

    glass = Part.makeCylinder(R - FRAME_FACE, GLASS_T,
                              App.Vector(R, (FRAME_DEPTH - GLASS_T) / 2.0, 0), axis)
    D.glass("Geometric", _half(glass, 0.0))


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
    print("Saved: %s" % step)
    print("Saved: %s" % stl)
    print("Overall (in)  W x H x D = %.2f x %.2f x %.2f"
          % (bb.XLength / IN, bb.ZLength / IN, bb.YLength / IN))
    return D
