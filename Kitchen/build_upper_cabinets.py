# -*- coding: utf-8 -*-
"""
Build the kitchen UPPER (wall) cabinets as standard-sized boxes plus one
DIAGONAL corner wall cabinet, in the kitchen-native frame (same frame as the
counter/appliances: X=0 = counter/east wall, Y=0 = front/sink wall, Z=0 floor,
room is toward -X / -Y).  Saves Kitchen_UpperCabinets.FCStd with an App::Part
"Part" (label Kitchen_UpperCabinets) so it can be linked into the assembly.

Standard cabinetry dims (mm):
  depth 305 (12"), regular height 914 (36"), bottom 1397 (18" over the 940 top),
  top 2311 (ceiling 2438 -> 5" reveal).  Widths in 3" increments.
  Diagonal corner cabinet: 24"x24" legs (610 along each wall), 12" (305) sides.
  Over-fridge cabinet: 24" deep (610), bottom 1800 (over the 1772 fridge), to
  the ceiling (2438).

Run OFFSCREEN GUI (GuiDocument + colours survive):
  flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD Kitchen/build_upper_cabinets.py
"""
import os
import FreeCAD as App
import Part
try:
    import FreeCADGui as Gui  # noqa: F401
except Exception:
    pass

V = App.Vector
ROOT = "/home/joee/github/alieniron/home-cad"
OUT = os.path.join(ROOT, "Kitchen")
log = open(os.path.join(OUT, "upper_cabinets_report.txt"), "w", buffering=1)
def L(*a): log.write(" ".join(str(x) for x in a) + "\n")

D = 305.0            # upper depth (12")
ZB = 1397.0          # bottom AFF (18" over the 940 counter)
HC = 914.0           # regular height (36")
ZT = ZB + HC         # 2311
CEIL = 2438.0

# regular box cabinets: (name, x0, y0, dx, dy, z0, dz)  -- corner is special
BOXES = [
    # --- FRONT wall (Y=0), depth in -Y (y0=-D..0), width in X ---
    ("Cab_Front12",  -915.0,   -D, 305.0, D, ZB, HC),   # 12" corner-adjacent
    ("Cab_Front36",  -3250.5,  -D, 914.0, D, ZB, HC),   # 36" west of sink window
    # --- EAST wall (X=0), depth in -X (x0=-D..0), width in Y ---
    ("Cab_East36",   -D, -4134.0, D, 914.0, ZB, HC),    # 36" range->fridge run
    ("Cab_East30",   -D, -4896.0, D, 762.0, ZB, HC),    # 30" range->fridge run
    # --- over-fridge: 24" deep, bottom over the fridge, to ceiling ---
    ("Cab_OverFridge", -610.0, -5809.0, 610.0, 908.0, 1800.0, CEIL - 1800.0),
]


def show(o, vis=True):
    o.Visibility = vis
    if getattr(o, "ViewObject", None) is not None:
        o.ViewObject.Visibility = vis


doc = App.newDocument("Kitchen_UpperCabinets")
feats = []
for name, x0, y0, dx, dy, z0, dz in BOXES:
    o = doc.addObject("Part::Feature", name)
    o.Shape = Part.makeBox(dx, dy, dz, V(x0, y0, z0))
    o.Label = name
    feats.append(o)

# --- diagonal corner wall cabinet (pentagon prism) ---
# corner at (0,0); 610 legs along each wall; 305 side panels; 45 diagonal face.
pts = [V(0, 0, ZB), V(0, -610, ZB), V(-305, -610, ZB),
       V(-610, -305, ZB), V(-610, 0, ZB)]
wire = Part.makePolygon(pts + [pts[0]])
corner = Part.Face(wire).extrude(V(0, 0, HC))
oc = doc.addObject("Part::Feature", "Cab_CornerDiagonal")
oc.Shape = corner
oc.Label = "Cab_CornerDiagonal"
feats.append(oc)

# --- wrap in an App::Part named "Part" for linking ---
part = doc.addObject("App::Part", "Part")
part.Label = "Kitchen_UpperCabinets"
for o in feats:
    part.addObject(o)
    show(o, True)
    # white cabinetry (match the base cabinets)
    if getattr(o, "ViewObject", None) is not None:
        o.ViewObject.ShapeColor = (0.95, 0.95, 0.95)
show(part, True)
doc.recompute()

fcstd = os.path.join(OUT, "Kitchen_UpperCabinets.FCStd")
doc.saveAs(fcstd)
comp = Part.makeCompound([o.Shape for o in feats])
bb = comp.BoundBox
L("Kitchen_UpperCabinets saved with %d cabinets" % len(feats))
for o in feats:
    b = o.Shape.BoundBox
    L("  %-18s X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]" %
      (o.Name, b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))
L("overall X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]" %
  (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))
Part.export(feats, os.path.join(OUT, "Kitchen_UpperCabinets.step"))
doc.save()
log.close()
print("UPPER_CABINETS_DONE")
