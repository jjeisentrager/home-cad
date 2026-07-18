# -*- coding: utf-8 -*-
"""
Two-flue masonry chimney, traced from chimney.PNG.

A single tall brick mass, 31" deep x 71" wide x 290" tall, with TWO fireboxes
that open in OPPOSITE directions on the two floors (as in the sketch):
  * BASEMENT firebox  -> opens out the +Y face (basement rec-room side)
  * MAIN-FLOOR firebox -> opens out the -Y face (main living side)
Each firebox gets a projecting CEMENT hearth slab at its floor level.

Local frame (component convention): origin at the back-left-bottom corner,
+X = width (71"), +Y = depth (31"), +Z = height (290").  Local Z=0 is meant to
sit on the BASEMENT floor slab (world Z = 101.6), so:
  * basement floor  -> local Z 0
  * main floor      -> local Z 2501.9  (world 2603.5 - 101.6)

Appearance: brick-red masonry, light-grey cement hearths (ShapeAppearance).

Run OFFSCREEN GUI so colours + GuiDocument survive:
  flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD Chimney/build_chimney.py
Units: mm.
"""
import os
import FreeCAD as App
import Part
try:
    import FreeCADGui as Gui  # noqa: F401
except Exception:
    pass

V = App.Vector
IN = 25.4

# --- overall mass -----------------------------------------------------------
W = 71.0 * IN        # 1803.4  width  (X)
D = 31.0 * IN        # 787.4   depth  (Y)
H = 290.0 * IN       # 7366.0  height (Z)

# --- floor levels in LOCAL Z (local 0 = basement slab top, world 101.6) ------
WORLD_BASE_Z   = 101.6                       # info: where local Z0 lands in world
MAIN_FLOOR_LOC = 2603.5 - WORLD_BASE_Z       # 2501.9  main finished floor, local

# --- firebox geometry -------------------------------------------------------
FB_W = 42.0 * IN     # 1066.8  opening width (centered in W)
FB_H = 30.0 * IN     # 762.0   opening height
FB_D = 18.0 * IN     # 457.2   firebox depth into the mass
HEARTH_T    = 4.0  * IN       # 101.6  hearth slab thickness
HEARTH_PROJ = 18.0 * IN       # 457.2  hearth projection into the room
HEARTH_SIDE = 8.0  * IN       # 203.2  hearth overhang each side of the firebox
HEARTH_W = FB_W + 2 * HEARTH_SIDE            # 1473.2

FB_X0 = (W - FB_W) / 2.0      # firebox left edge
FB_X1 = (W + FB_W) / 2.0
H_X0 = (W - HEARTH_W) / 2.0   # hearth left edge
H_X1 = (W + HEARTH_W) / 2.0

BASE_FB_FLOOR = HEARTH_T                      # 101.6   basement firebox floor (on hearth)
MAIN_FB_FLOOR = MAIN_FLOOR_LOC + HEARTH_T     # 2603.5  main firebox floor (on hearth)

DOC = "Chimney"
doc = App.newDocument(DOC)
OUT = os.path.dirname(os.path.abspath(__file__))
doc.saveAs(os.path.join(OUT, DOC + ".FCStd"))   # on disk first


def box(l, w, h, x, y, z):
    return Part.makeBox(l, w, h, V(x, y, z))


# --- brick mass with the two firebox cavities cut out -----------------------
mass = box(W, D, H, 0, 0, 0)
# basement firebox: opens the +Y face
cav_base = box(FB_W, FB_D + 1.0, FB_H, FB_X0, D - FB_D, BASE_FB_FLOOR)
# main firebox: opens the -Y face
cav_main = box(FB_W, FB_D + 1.0, FB_H, FB_X0, -1.0, MAIN_FB_FLOOR)
mass = mass.cut(Part.makeCompound([cav_base, cav_main]))

# --- cement hearths (slab = firebox floor + apron projecting into the room) --
# basement hearth projects +Y; sits on the slab (Z 0 -> HEARTH_T)
hearth_base = box(HEARTH_W, (D - (D - FB_D)) + HEARTH_PROJ, HEARTH_T,
                  H_X0, D - FB_D, BASE_FB_FLOOR - HEARTH_T)
# main hearth projects -Y; at main-floor level
hearth_main = box(HEARTH_W, FB_D + HEARTH_PROJ, HEARTH_T,
                  H_X0, -HEARTH_PROJ, MAIN_FB_FLOOR - HEARTH_T)

objs = []


def add(name, shp):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shp
    objs.append(o)
    return o


add("ChimneyMass", mass)
add("HearthBasement", hearth_base)
add("HearthMain", hearth_main)

part = doc.addObject("App::Part", "Part")
part.Label = "Chimney"
for o in objs:
    part.addObject(o)
doc.recompute()

# --- appearance: brick-red mass, grey cement hearths ------------------------
BRICK  = (0.60, 0.27, 0.20)     # weathered red brick
CEMENT = (0.74, 0.74, 0.71)     # light grey concrete
COLS = {"ChimneyMass": BRICK, "HearthBasement": CEMENT, "HearthMain": CEMENT}


def paint(o, rgb):
    vo = getattr(o, "ViewObject", None)
    if vo is None:
        return
    vo.Visibility = True
    try:
        vo.ShapeColor = rgb
    except Exception:
        pass
    try:
        m = vo.ShapeAppearance[0]
        m.DiffuseColor = rgb + (1.0,)
        m.AmbientColor = tuple(c * 0.4 for c in rgb) + (1.0,)
        vo.ShapeAppearance = [m]
    except Exception:
        pass


for o in objs:
    o.Visibility = True
    paint(o, COLS[o.Name])
part.Visibility = True
if getattr(part, "ViewObject", None):
    part.ViewObject.Visibility = True

doc.recompute()
doc.save()

# --- exports + report -------------------------------------------------------
Part.export(objs, os.path.join(OUT, DOC + ".step"))
rep = open(os.path.join(OUT, "chimney_report.txt"), "w")
rep.write("Chimney %.1f W x %.1f D x %.1f H mm (71 x 31 x 290 in)\n" % (W, D, H))
rep.write("local Z0 = world %.1f (basement slab); main floor local Z=%.1f\n"
          % (WORLD_BASE_Z, MAIN_FLOOR_LOC))
rep.write("basement firebox opens +Y, floor local Z=%.1f, opening %.1f x %.1f\n"
          % (BASE_FB_FLOOR, FB_W, FB_H))
rep.write("main firebox opens -Y, floor local Z=%.1f, opening %.1f x %.1f\n"
          % (MAIN_FB_FLOOR, FB_W, FB_H))
for o in objs:
    b = o.Shape.BoundBox
    rep.write("%-15s n=%d  X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]\n"
              % (o.Name, len(o.Shape.Solids), b.XMin, b.XMax, b.YMin, b.YMax,
                 b.ZMin, b.ZMax))
rep.close()
print("CHIMNEY_DONE")
