# -*- coding: utf-8 -*-
"""
Build the main-floor wall framing.

Same philosophy as AddOn/build_framing.py: walls are plain data, each built as
loose Part::Feature solids (studs + top/bottom plates), then grouped under a
single App::Part so assemblies can link to one stable target. No Spreadsheet,
no Draft PathArray, no Boolean masking -- the whole floor plan lives in the
WALLS table below and the geometry is reproducible from this script alone.

This replaces the previous GUI/Spreadsheet/PathArray construction. The wall
centerlines were extracted from that model's bottom-plate footprint, so the
plan matches; studs here are placed at true 16" O.C. (the old model used Draft
even-spacing with hand-set counts, so individual stud positions differ).

Run headless:  freecadcmd build_mainframing.py

Units: millimetres. World frame matches the old model (origin at floor center;
footprint X -335.5..335.5 in, Y -156..156 in, Z up). Z=0 is the subfloor top:
bottom plate 0..1.5", studs 1.5..96", top plate 96..97.5".
"""

import os
import FreeCAD as App
import Part

IN = 25.4

# --- Framing parameters -----------------------------------------------------
STUD_W       = 1.5  * IN    # 2x face width, runs along the wall length
EXT_THICK    = 4.0  * IN    # exterior wall depth (2x4 + sheathing nominal here)
INT_THICK    = 3.0  * IN    # interior partition depth
PLATE_T      = 1.5  * IN    # plate thickness in Z (laid flat)
WALL_HEIGHT  = 97.5 * IN    # floor to top of top plate
STUD_SPACING = 16.0 * IN    # on-center

FINISHED = False            # GLOBAL toggle: False = stud wall, True = solid block

# --- Wall layout (centerlines, inches) --------------------------------------
# Each wall is axis-aligned:
#   ("name", orient, center, lo, hi, thick_in)
#   orient "V": vertical wall, centerline at x=center, spans y in [lo, hi]
#   orient "H": horizontal wall, centerline at y=center, spans x in [lo, hi]
# thickness straddles the centerline (center +/- thick/2). Collinear segments
# split by a gap are separate entries -- the gaps are door/passage openings.
WALLS = [
    # Exterior perimeter (4" walls; centerlines inset 2" from the outer face)
    ("Ext_West",  "V", -333.5, -154.0, 154.0, 4.0),
    ("Ext_East",  "V",  333.5, -154.0, 154.0, 4.0),
    ("Ext_South", "H", -154.0, -333.5, 333.5, 4.0),
    # North wall is split by the AddOn opening: the studs are removed across the
    # AddOn's open side (world X 7348..15313 -> local x -46.2..267.4 in), where
    # the AddOn's I-beam carries the load. Two segments flank the opening.
    ("Ext_North_W", "H", 154.0, -333.5, -46.2, 4.0),
    ("Ext_North_E", "H", 154.0,  267.4, 333.5, 4.0),

    # Interior partitions (3"), vertical runs
    ("V_n176_a", "V", -176.0, -29.0,  10.0, 3.0),
    ("V_n176_b", "V", -176.0,  13.0,  94.0, 3.0),
    ("V_n176_c", "V", -176.0,  97.0, 152.0, 3.0),
    ("V_n140",   "V", -140.0,  13.0,  94.0, 3.0),
    ("V_n76",    "V",  -76.0,  63.0,  94.0, 3.0),
    ("V_n66",    "V",  -66.0, -152.0,-32.0, 3.0),
    ("V_n39_a",  "V",  -39.0,  13.0,  94.0, 3.0),
    ("V_n39_b",  "V",  -39.0,  97.0, 152.0, 3.0),
    ("V_p30",    "V",   30.0, -152.0, 10.0, 3.0),
    ("V_p267",   "V",  267.0,  80.0, 152.0, 3.0),

    # Interior partitions (3"), horizontal runs
    ("H_n30_a", "H", -30.5, -331.5,-177.5, 3.0),
    ("H_n30_b", "H", -30.5, -174.5, -67.5, 3.0),
    ("H_p11_a", "H",  11.5, -174.5,-141.5, 3.0),
    ("H_p11_b", "H",  11.5, -138.5, -40.5, 3.0),
    ("H_p11_c", "H",  11.5,   31.5, 228.5, 3.0),
    ("H_p95_a", "H",  95.5, -174.5,-141.5, 3.0),
    ("H_p95_b", "H",  95.5, -138.5, -77.5, 3.0),
    ("H_p95_c", "H",  95.5,  -74.5, -40.5, 3.0),
]

OUT = os.path.dirname(os.path.abspath(__file__))
DOCNAME = "MainFraming"


def box(l, w, h, x, y, z):
    return Part.makeBox(l, w, h, App.Vector(x, y, z))


def stud_positions(length):
    """Stud left-edge offsets along a wall of the given length, 16" O.C. with a
    flush stud at each end."""
    pos = []
    p = 0.0
    end = length - STUD_W
    while p <= end + 1e-6:
        pos.append(p)
        p += STUD_SPACING
    if not pos or abs(pos[-1] - end) > 1e-6:
        pos.append(end)
    return pos


def build_wall(orient, lo, hi, thick):
    """Return a Part.Compound for one wall, in WORLD coordinates, given its
    centerline. Vertical: extends along +y; horizontal: along +x."""
    length = (hi - lo) * IN
    t = thick * IN
    solids = []

    if FINISHED:
        if orient == "V":
            solids.append(box(t, length, WALL_HEIGHT, -t / 2, lo * IN, 0))
        else:
            solids.append(box(length, t, WALL_HEIGHT, lo * IN, -t / 2, 0))
        # caller offsets to the centerline; here lo/center handled below
        return Part.makeCompound(solids), length

    stud_h = WALL_HEIGHT - 2 * PLATE_T
    # plates (full length)
    if orient == "V":
        solids.append(box(t, length, PLATE_T, -t / 2, lo * IN, 0))
        solids.append(box(t, length, PLATE_T, -t / 2, lo * IN, WALL_HEIGHT - PLATE_T))
        for s in stud_positions(length):
            solids.append(box(t, STUD_W, stud_h, -t / 2, lo * IN + s, PLATE_T))
    else:
        solids.append(box(length, t, PLATE_T, lo * IN, -t / 2, 0))
        solids.append(box(length, t, PLATE_T, lo * IN, -t / 2, WALL_HEIGHT - PLATE_T))
        for s in stud_positions(length):
            solids.append(box(STUD_W, t, stud_h, lo * IN + s, -t / 2, PLATE_T))
    return Part.makeCompound(solids), length


# --- build ------------------------------------------------------------------
doc = App.newDocument(DOCNAME)

objs = []
for name, orient, center, lo, hi, thick in WALLS:
    comp, _ = build_wall(orient, lo, hi, thick)
    # translate compound onto its centerline (build_wall put the span on the
    # axis; shift the perpendicular axis to `center`)
    if orient == "V":
        comp.translate(App.Vector(center * IN, 0, 0))
    else:
        comp.translate(App.Vector(0, center * IN, 0))
    o = doc.addObject("Part::Feature", name)
    o.Shape = comp
    o.Label = name
    objs.append(o)

# Group under an App::Part whose internal Name is "Part" -- House.FCStd and
# Basement.FCStd link to this file by object name "Part" (label MainFraming).
part = doc.addObject("App::Part", "Part")
part.Label = "MainFraming"
for o in objs:
    part.addObject(o)

doc.recompute()

# Make every wall (and the App::Part) visible. Saving with the GUI layer up
# (offscreen) then writes a GuiDocument.xml so the framing shows by default
# wherever it's linked (Main / House assemblies). Run this build with:
#   flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD build_mainframing.py
if App.GuiUp:
    for o in objs + [part]:
        if o.ViewObject is not None:
            o.ViewObject.Visibility = True

# --- save / export ----------------------------------------------------------
fcstd = os.path.join(OUT, DOCNAME + ".FCStd")
step = os.path.join(OUT, DOCNAME + ".step")
stl = os.path.join(OUT, DOCNAME + ".stl")

doc.saveAs(fcstd)
Part.export(objs, step)

import Mesh
compound = Part.makeCompound([o.Shape for o in objs])
Mesh.Mesh(compound.tessellate(1.0)).write(stl)

bb = compound.BoundBox
nstuds = sum(len(stud_positions((hi - lo) * IN)) for _, o2, _, lo, hi, _ in WALLS) if not FINISHED else 0
print("Saved: %s" % fcstd)
print("Mode: %s" % ("FINISHED (blocks)" if FINISHED else "STUD WALL"))
print("Walls: %d   Studs: %d" % (len(objs), nstuds))
print("Overall (in) X x Y x Z = %.1f x %.1f x %.1f"
      % (bb.XLength / IN, bb.YLength / IN, bb.ZLength / IN))
