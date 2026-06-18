# -*- coding: utf-8 -*-
"""
Build a standard US single-pole TOGGLE switch WITH a single-gang cover plate
and a device box stub.

Local frame (component convention):  X = width, Z = height, Y = depth with the
FRONT face toward +Y; origin at the back-left-bottom corner, bottom on Z=0.
Y=0 is the back of the device box; the finished WALL SURFACE is at Y=BOX_D
(plate back).  Seat local Y=BOX_D on the wall face to mount.

Loose Part::Features wrapped in an App::Part named "Part" (linkable).

Run headless:  freecadcmd build_switch.py     Units: millimetres.
"""
import os, math
import FreeCAD as App
import Part
import Mesh

IN = 25.4
PLATE_W = 2.75 * IN     # 69.85
PLATE_H = 4.50 * IN     # 114.30
PLATE_T = 5.0
BOX_W = 2.0 * IN        # 50.8
BOX_H = 3.0 * IN        # 76.2
BOX_D = 2.5 * IN        # 63.5

WALL_Y = BOX_D
PLATE_FRONT = WALL_Y + PLATE_T

DOC = "Switch-Toggle"
doc = App.newDocument(DOC)
V = App.Vector


def box(l, w, h, x, y, z):
    return Part.makeBox(l, w, h, V(x, y, z))


def add(name, shp):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shp
    return o


# ---- device box ----
bx0 = (PLATE_W - BOX_W) / 2.0
bz0 = (PLATE_H - BOX_H) / 2.0
add("Box", box(BOX_W, BOX_D, BOX_H, bx0, 0, bz0))

# ---- cover plate ----
add("Plate", box(PLATE_W, PLATE_T, PLATE_H, 0, WALL_Y, 0))

# ---- switch body strap face (visible through the plate opening) ----
DEV_W = 0.93 * IN       # 23.6  toggle device face width
DEV_H = 2.62 * IN       # 66.5
dx0 = (PLATE_W - DEV_W) / 2.0
dz0 = (PLATE_H - DEV_H) / 2.0
add("StrapFace", box(DEV_W, 1.2, DEV_H, dx0, PLATE_FRONT, dz0))   # proud 1.2mm

# ---- toggle lever: small paddle protruding +Y through the plate, tilted UP ----
cx = PLATE_W / 2.0
cz = PLATE_H / 2.0
TW, TT, TL = 6.0, 5.0, 16.0     # lever width(X), thickness(Z at base), length(+Y)
lever = box(TW, TL, TT, -TW / 2.0, 0, -TT / 2.0)   # build at origin, +Y = length
# round the protruding tip
lever = lever.fuse(Part.makeCylinder(TT / 2.0, TW, V(-TW / 2.0, TL, 0), V(1, 0, 0)))
# tilt up ~18deg about X, then move to plate centre, base at plate front
pl = App.Placement(V(cx, PLATE_FRONT - 2.0, cz),
                   App.Rotation(V(1, 0, 0), -18))
lever.Placement = pl
add("Toggle", lever)

# ---- plate centre screw ----
add("PlateScrew", Part.makeCylinder(2.6, 1.2, V(cx, PLATE_FRONT, PLATE_H * 0.5),
                                    V(0, 1, 0)))

part = doc.addObject("App::Part", "Part")
part.Label = "Switch_Toggle"
for o in [o for o in doc.Objects if o.TypeId.startswith("Part::")]:
    part.addObject(o)
doc.recompute()

OUT = os.path.dirname(os.path.abspath(__file__))
doc.saveAs(os.path.join(OUT, DOC + ".FCStd"))
feats = [o for o in doc.Objects if o.TypeId.startswith("Part::")]
Part.export(feats, os.path.join(OUT, DOC + ".step"))
Mesh.Mesh(Part.makeCompound([o.Shape for o in feats]).tessellate(0.3)).write(
    os.path.join(OUT, DOC + ".stl"))
bb = Part.makeCompound([o.Shape for o in feats]).BoundBox
print("Saved Switch  W x H x D (mm) = %.1f x %.1f x %.1f  (wall surface Y=%.1f)"
      % (bb.XLength, bb.ZLength, bb.YLength, WALL_Y))
print("SWITCH_DONE")
