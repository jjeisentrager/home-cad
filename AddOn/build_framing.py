# -*- coding: utf-8 -*-
"""
Build the AddOn wall framing -- now with proper ROUGH OPENINGS for the windows
and the patio slider (todo#3: real cutouts in the wall, not just a window pasted
on the surface).

Each wall is built along its own local +X axis (X = wall length, Y = 3.5" stud
depth, Z = up), then positioned/rotated about Z into place. Openings are given
per wall in wall-local X with their sill/head heights; each gets king studs,
jack (trimmer) studs, a doubled header, a sill (windows), and cripple studs
above the header and below the sill. Regular studs that would fall inside an
opening are dropped.

Run headless:  freecadcmd build_framing.py
(then AddOn/color_save-equivalent / recolor_brown.py to restore wood colour, since
 a headless save drops GuiDocument)

Units: millimetres.
"""

import os
import FreeCAD as App
import Part

IN = 25.4

STUD_W         = 1.5  * IN   # 38.1  2x face width (along wall length X)
WALL_THICKNESS = 3.5  * IN   # 88.9  stud depth (Y)
PLATE_T        = 1.5  * IN   # 38.1  plate thickness (Z)
WALL_HEIGHT    = 96.0 * IN   # 2438.4
STUD_SPACING   = 16.0 * IN   # 406.4 on-center
HEADER_H       = 7.25 * IN   # 184.2  (2x8 doubled header depth in Z)

# Wall layout: (name, x, y, z, length_in, angle_deg)  -- x/y/z/length in inches
WALLS = [
    ("Wall_Front", 0,    0, 0, 312, 180),
    ("Wall_Right", 0, -240, 0, 240,  90),
    ("Wall_Left", -312,  0, 0, 240, 270),
]

# Rough openings per wall, positions in WALL-LOCAL millimetres:
#   (center_x, width, sill_z, head_z, is_door)
OPENINGS = {
    "Wall_Front": [
        (1651.0, 1371.0, 1018.0, 2084.0, False),   # WindowSink
        (4520.5, 1980.0,    0.0, 2110.0, True),    # Slider (patio door) -- was
        # 4400.0; nudged 120.5 mm toward the window so the slider clears the
        # counter.  Wall-local x runs OPPOSITE world X, so +120.5 here = -120.5
        # world X.  This centres the slider in the window..counter run, giving
        # 89.5 mm (3.5") each side -- the run only has 179 mm of slack total, so
        # a full 4" on both sides does not fit.
        (6273.8, 1371.0, 1018.0, 2084.0, False),   # WindowFrontLeft
    ],
    "Wall_Right": [
        (4572.0, 1371.0, 1018.0, 2084.0, False),   # WindowWall
    ],
    "Wall_Left": [
        (1350.0, 1371.0, 1018.0, 2084.0, False),   # WindowWest
    ],
}

OUT = os.path.dirname(os.path.abspath(__file__))
DOCNAME = "AddOn_Framing"


def box(l, w, h, x, y, z):
    return Part.makeBox(l, w, h, App.Vector(x, y, z))


def build_wall(length, openings):
    """Return a list of solids for one wall (local coords) with rough openings."""
    T = WALL_THICKNESS
    solids = []
    stud_top = WALL_HEIGHT - PLATE_T          # underside of top plate
    stud_h = WALL_HEIGHT - 2 * PLATE_T

    # --- plates (full length); cut the bottom plate under doors ---
    solids.append(box(length, T, PLATE_T, 0, 0, WALL_HEIGHT - PLATE_T))   # top plate
    door_spans = [(xc - w / 2.0, xc + w / 2.0) for (xc, w, s, h, door) in openings if door]
    if not door_spans:
        solids.append(box(length, T, PLATE_T, 0, 0, 0))
    else:
        # bottom plate in segments between door openings
        xs = 0.0
        for a, b in sorted(door_spans):
            if a > xs:
                solids.append(box(a - xs, T, PLATE_T, xs, 0, 0))
            xs = b
        if xs < length:
            solids.append(box(length - xs, T, PLATE_T, xs, 0, 0))

    # --- opening framing ---
    forbidden = []   # x-ranges where common studs are dropped
    for (xc, w, sill, head, door) in openings:
        ro_l = xc - w / 2.0
        ro_r = xc + w / 2.0
        jl = ro_l - STUD_W            # jack left start
        jr = ro_r                     # jack right start
        kl = jl - STUD_W              # king left start
        kr = jr + STUD_W              # king right start
        forbidden.append((kl - 1.0, kr + STUD_W + 1.0))

        # king studs (full height)
        solids.append(box(STUD_W, T, stud_h, kl, 0, PLATE_T))
        solids.append(box(STUD_W, T, stud_h, kr, 0, PLATE_T))
        # jack/trimmer studs (bottom plate top -> header bottom)
        jack_h = head - PLATE_T
        solids.append(box(STUD_W, T, jack_h, jl, 0, PLATE_T))
        solids.append(box(STUD_W, T, jack_h, jr, 0, PLATE_T))
        # doubled header over the opening (between jacks, on the jacks)
        solids.append(box(w + 2 * STUD_W, T, HEADER_H, jl, 0, head))
        # sill (windows only) + cripples below
        if not door:
            solids.append(box(w, T, STUD_W, ro_l, 0, sill - STUD_W))
            # cripples below sill at ~16" o.c.
            p = ro_l
            while p < ro_r - 1e-6:
                wseg = min(STUD_W, ro_r - p)
                solids.append(box(wseg, T, sill - STUD_W - PLATE_T, p, 0, PLATE_T))
                p += STUD_SPACING
        # cripples above header
        crip_z0 = head + HEADER_H
        crip_h = stud_top - crip_z0
        if crip_h > 1.0:
            p = ro_l
            while p < ro_r - 1e-6:
                wseg = min(STUD_W, ro_r - p)
                solids.append(box(wseg, T, crip_h, p, 0, crip_z0))
                p += STUD_SPACING

    # --- common studs at 16" o.c. (skip those inside an opening span) ---
    def blocked(x):
        return any(a <= x <= b or a <= x + STUD_W <= b for (a, b) in forbidden)

    positions = []
    pos = 0.0
    end_pos = length - STUD_W
    while pos <= end_pos + 1e-6:
        positions.append(pos)
        pos += STUD_SPACING
    if not positions or abs(positions[-1] - end_pos) > 1e-6:
        positions.append(end_pos)
    for p in positions:
        if not blocked(p):
            solids.append(box(STUD_W, T, stud_h, p, 0, PLATE_T))

    return solids


doc = App.newDocument(DOCNAME)
objs = []
for name, x, y, z, length_in, angle_deg in WALLS:
    solids = build_wall(length_in * IN, OPENINGS.get(name, []))
    o = doc.addObject("Part::Feature", name)
    o.Shape = Part.makeCompound(solids)
    o.Placement = App.Placement(
        App.Vector(x * IN, y * IN, z * IN),
        App.Rotation(App.Vector(0, 0, 1), angle_deg),
    )
    objs.append(o)

framing = doc.addObject("App::Part", "Framing")
framing.Label = "Framing"
for o in objs:
    framing.addObject(o)
doc.recompute()

fcstd = os.path.join(OUT, DOCNAME + ".FCStd")
doc.saveAs(fcstd)
Part.export(objs, os.path.join(OUT, DOCNAME + ".step"))
import Mesh
compound = Part.makeCompound([o.Shape for o in objs])
Mesh.Mesh(compound.tessellate(1.0)).write(os.path.join(OUT, DOCNAME + ".stl"))
bb = compound.BoundBox
print("Saved framing with rough openings.  Overall (mm) X x Y x Z = %.1f x %.1f x %.1f"
      % (bb.XLength, bb.YLength, bb.ZLength))
print("FRAMING_DONE")
