# -*- coding: utf-8 -*-
"""
Build a standard US duplex receptacle (15A/125V) WITH a single-gang cover plate
and a device box stub.

Local frame (component convention):  X = width, Z = height, Y = depth with the
FRONT face toward +Y; origin at the back-left-bottom corner, bottom on Z=0.
Y=0 is the back of the device box; the finished WALL SURFACE is at Y=BOX_D
(the plate back), so to mount, seat local Y=BOX_D on the wall face.

Loose Part::Features wrapped in an App::Part named "Part" so it links like the
other library components.

Run headless:  freecadcmd build_outlet.py      Units: millimetres.
"""
import os
import FreeCAD as App
import Part
import Mesh

IN = 25.4
PLATE_W = 2.75 * IN     # 69.85  single-gang plate width
PLATE_H = 4.50 * IN     # 114.30 single-gang plate height
PLATE_T = 5.0           # plate thickness (proud of wall)
BOX_W = 2.0 * IN        # 50.8   device box
BOX_H = 3.0 * IN        # 76.2
BOX_D = 2.5 * IN        # 63.5   box depth (into wall)

WALL_Y = BOX_D                 # finished wall surface (plate back)
PLATE_FRONT = WALL_Y + PLATE_T # 68.5

DOC = "Outlet-Duplex"
doc = App.newDocument(DOC)
V = App.Vector


def box(l, w, h, x, y, z):
    return Part.makeBox(l, w, h, V(x, y, z))


def add(name, shp):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shp
    return o


# ---- device box (recessed into wall, -Y side) ----
bx0 = (PLATE_W - BOX_W) / 2.0
bz0 = (PLATE_H - BOX_H) / 2.0
add("Box", box(BOX_W, BOX_D, BOX_H, bx0, 0, bz0))

# ---- cover plate ----
add("Plate", box(PLATE_W, PLATE_T, PLATE_H, 0, WALL_Y, 0))

# ---- duplex device face (visible through the plate opening) ----
DEV_W = 1.31 * IN       # 33.3
DEV_H = 3.28 * IN       # 83.3
dx0 = (PLATE_W - DEV_W) / 2.0
dz0 = (PLATE_H - DEV_H) / 2.0
face = box(DEV_W, 1.6, DEV_H, dx0, PLATE_FRONT, dz0)   # proud 1.6mm of plate

cx = PLATE_W / 2.0
cuts = []
# two receptacles (lower + upper third of the device face)
for cz in (dz0 + DEV_H * 0.27, dz0 + DEV_H * 0.73):
    # two parallel vertical blade slots, above centre
    cuts.append(box(1.8, 8.0, 9.0, cx - 6.5 - 0.9, PLATE_FRONT - 2, cz + 1.5))
    cuts.append(box(1.8, 8.0, 9.0, cx + 6.5 - 0.9, PLATE_FRONT - 2, cz + 1.5))
    # ground hole, below centre
    cuts.append(box(5.0, 8.0, 4.0, cx - 2.5, PLATE_FRONT - 2, cz - 8.0))
recept = face.cut(Part.makeCompound(cuts))
add("Recept", recept)

# ---- two mounting screws (plate centre + device strap), simple discs ----
for cz in (PLATE_H * 0.5,):
    add("PlateScrew", Part.makeCylinder(2.6, 1.2, V(cx, PLATE_FRONT, cz), V(0, 1, 0)))

part = doc.addObject("App::Part", "Part")
part.Label = "Outlet_Duplex"
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
print("Saved Outlet  W x H x D (mm) = %.1f x %.1f x %.1f  (wall surface Y=%.1f)"
      % (bb.XLength, bb.ZLength, bb.YLength, WALL_Y))
print("OUTLET_DONE")
