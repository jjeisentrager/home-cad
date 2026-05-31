# -*- coding: utf-8 -*-
"""
Build the AddOn wall framing.

Each wall is an independent object built along its own local +X axis, then
positioned and rotated about Z into place. Complex / cornered layouts are just
more entries in WALLS -- there is no shared path and no Boolean masking.

Two modes via the global FINISHED toggle:
  - FINISHED = False : stud wall (2x4 studs at 16" O.C. + single top & bottom
                       plate, plus a flush end stud at each end).
  - FINISHED = True  : a single solid 4.5" drywall block per wall; studs omitted.

Run headless:  freecadcmd build_framing.py

Units: millimetres.  Orientation (local, before placement):
X = wall length, Y = wall thickness (depth), Z = up.  Wall starts at the local
origin; the stud wall and the finished block share the same centerline.
"""

import os
import FreeCAD as App
import Part

IN = 25.4  # mm per inch

# --- Framing parameters -----------------------------------------------------
STUD_W         = 1.5  * IN   # 2x4 face width, runs along wall length (X)
WALL_THICKNESS = 3.5  * IN   # stud depth -> stud-wall thickness (Y)
PLATE_T        = 1.5  * IN   # plate thickness in Z (laid flat)
WALL_HEIGHT    = 96.0 * IN   # 8'
STUD_SPACING   = 16.0 * IN   # on-center
FINISHED_THICK = 4.5  * IN   # solid drywall block (3.5 stud + 0.5 each side)

FINISHED = False             # GLOBAL toggle: False = stud wall, True = block

# --- Wall layout ------------------------------------------------------------
# (name, x, y, z, length_in, angle_deg)   x/y/z and length in inches,
# angle measured about +Z.  Each wall is built along its local +X axis with
# its 3.5" thickness in local +Y, then positioned/rotated by this entry.
#
# Addition footprint: 312" x 240" (26' x 20'), 96" tall, laid out in the same
# negative quadrant (X -312..0, Y -240..0) as the original model so it lines
# up in AddOn_Assembly.  Three walls: the 312" front (Y=0 edge) and the two
# 240" sides.  The 312" far wall (Y=-240) is intentionally omitted -- this is
# the wall the old model had to mask out, now simply not built.  Each wall's
# thickness falls inward, so outer faces sit on the footprint rectangle.
WALLS = [
    ("Wall_Front", 0,    0, 0, 312, 180),   # front, outer face at Y=0
    ("Wall_Right", 0, -240, 0, 240,  90),   # right side, outer face at X=0
    ("Wall_Left", -312,  0, 0, 240, 270),   # left side,  outer face at X=-312
]

OUT = os.path.dirname(os.path.abspath(__file__))
DOCNAME = "AddOn_Framing"


def box(l, w, h, x, y, z):
    return Part.makeBox(l, w, h, App.Vector(x, y, z))


def add(name, shape):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shape
    return o


def build_wall(length, finished):
    """Return a Part.Compound for one wall in local coordinates.

    Stud mode spans Y 0..3.5 (center 1.75); finished mode spans Y -0.5..4.0,
    sharing the same 1.75 centerline so the two modes overlay cleanly.
    """
    if finished:
        block = box(length, FINISHED_THICK, WALL_HEIGHT, 0, -0.5 * IN, 0)
        return Part.makeCompound([block])

    solids = []
    # Bottom and top plates run the full length.
    solids.append(box(length, WALL_THICKNESS, PLATE_T, 0, 0, 0))
    solids.append(box(length, WALL_THICKNESS, PLATE_T, 0, 0, WALL_HEIGHT - PLATE_T))

    # Studs seat on the bottom plate, up to the top plate.
    stud_h = WALL_HEIGHT - 2 * PLATE_T
    end_pos = length - STUD_W   # left edge of the flush end stud

    positions = []
    pos = 0.0
    while pos <= end_pos + 1e-6:
        positions.append(pos)
        pos += STUD_SPACING
    # Guarantee a flush end stud regardless of where the spacing grid landed.
    if not positions or abs(positions[-1] - end_pos) > 1e-6:
        positions.append(end_pos)

    for p in positions:
        solids.append(box(STUD_W, WALL_THICKNESS, stud_h, p, 0, PLATE_T))

    return Part.makeCompound(solids)


# --- build ------------------------------------------------------------------
doc = App.newDocument(DOCNAME)

objs = []
for name, x, y, z, length_in, angle_deg in WALLS:
    shape = build_wall(length_in * IN, FINISHED)
    o = add(name, shape)
    o.Placement = App.Placement(
        App.Vector(x * IN, y * IN, z * IN),
        App.Rotation(App.Vector(0, 0, 1), angle_deg),
    )
    objs.append(o)

# Group the walls under a single App::Part so the assembly can link to one
# stable target ("Framing") while each wall stays an individual object.
framing = doc.addObject("App::Part", "Framing")
framing.Label = "Framing"
for o in objs:
    framing.addObject(o)

doc.recompute()

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
print("Saved: %s" % fcstd)
print("Saved: %s" % step)
print("Saved: %s" % stl)
print("Mode: %s" % ("FINISHED (solid block)" if FINISHED else "STUD WALL"))
print("Walls: %d" % len(objs))
print("Overall (mm)  X x Y x Z = %.1f x %.1f x %.1f"
      % (bb.XLength, bb.YLength, bb.ZLength))
print("Overall (in)  X x Y x Z = %.2f x %.2f x %.2f"
      % (bb.XLength / IN, bb.YLength / IN, bb.ZLength / IN))
