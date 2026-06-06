# -*- coding: utf-8 -*-
"""
Replace the solid CounterBase with a run of individual base cabinets fitted to
the L-counter, leaving gaps for the range (long leg) and dishwasher (short leg)
and a sink base under the sink.  The countertop (CounterTop_Cut, black) and the
island are left untouched.

Reference frame (counter-local == world): long leg runs -Y along wall X=0,
front faces -X; short leg runs -X along wall Y=0, front faces -Y; both 609.6 deep
(24"); cabinet box top Z=914.4 (36"); countertop slab 914.4..939.8.

Cabinets carry a recessed toe kick (4" tall, 3" set-back) on their exposed front.
Each cabinet is one fused Part::Feature, painted white, added into the linked
App::Part "Part" so it shows through the Kitchen_Counter link in the assembly.

Run with the GUI layer up so colors + GuiDocument persist:
  flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD \
    Kitchen/make_base_cabinets.py
"""
import os
import FreeCAD as App
import FreeCADGui as Gui  # noqa: F401
import Part

ROOT = "/home/joee/github/alieniron/home-cad"
KIT = os.path.join(ROOT, "Kitchen")
V = App.Vector
IN = 25.4
DEPTH = 609.6        # 24"
TOP_Z = 914.4        # 36" cabinet box top (countertop sits above)
TK_H = 101.6         # 4" toe kick height
TK_SET = 76.2        # 3" toe kick set-back
WHITE = (1.0, 1.0, 1.0, 1.0)

log = open(os.path.join(ROOT, "cab_report.txt"), "w")
def L(*a): log.write(" ".join(str(x) for x in a) + "\n")

def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))

def show(o, vis=True):
    o.Visibility = vis
    if o.ViewObject is not None:
        o.ViewObject.Visibility = vis

def paint(o, rgba=WHITE):
    vo = o.ViewObject
    vo.Transparency = 0
    vo.ShapeColor = rgba
    try:
        m = vo.ShapeAppearance[0]
        m.DiffuseColor = rgba
        vo.ShapeAppearance = [m]
    except Exception as e:
        L("paint err", o.Name, e)

cd = App.openDocument(os.path.join(KIT, "Kitchen_Counter.FCStd"))
part = cd.getObject("Part")

# --- remove any cabinets from a previous run -------------------------------
for o in list(cd.Objects):
    if o.Name.startswith("Cab_") or o.Name == "SinkBase":
        cd.removeObject(o.Name)

# --- cabinet builders ------------------------------------------------------
def long_cab(y0, y1):   # along -Y, front -X; y0 nearer corner (> y1)
    carc = box(-DEPTH, 0.0, y1, y0, TK_H, TOP_Z)
    plin = box(-DEPTH + TK_SET, 0.0, y1, y0, 0.0, TK_H)
    return carc.fuse(plin)

def short_cab(x0, x1):  # along -X, front -Y; x0 nearer corner (> x1)
    carc = box(x1, x0, -DEPTH, 0.0, TK_H, TOP_Z)
    plin = box(x1, x0, -DEPTH + TK_SET, 0.0, 0.0, TK_H)
    return carc.fuse(plin)

def corner_cab():
    carc = box(-DEPTH, 0.0, -DEPTH, 0.0, TK_H, TOP_Z)
    plin = box(-DEPTH + TK_SET, 0.0, -DEPTH + TK_SET, 0.0, 0.0, TK_H)
    return carc.fuse(plin)

cabs = []  # (name, shape)
cabs.append(("Cab_Corner", corner_cab()))

# LONG LEG -- segment A (corner side -> range), segment B (range -> fridge end)
# range gap kept at Y[-3090, -3870] (range occupies Y[-3100.4,-3859.2])
longA = [(-609.6, -1524.0), (-1524.0, -2438.4), (-2438.4, -3090.0)]
longB = [(-3870.0, -4784.4), (-4784.4, -5698.8),
         (-5698.8, -6613.2), (-6613.2, -6959.6)]
for i, (y0, y1) in enumerate(longA + longB, 1):
    cabs.append(("Cab_L%d" % i, long_cab(y0, y1)))

# SHORT LEG -- sink base centered on sink (center X=-1651), DW gap at the end
# S1: corner -> sink base; SinkBase 36"; S2: sink base -> DW; DW gap X[-2690,-3302]
short_plain = [("Cab_S1", -609.6, -1193.8), ("Cab_S2", -2108.2, -2690.0)]
for name, x0, x1 in short_plain:
    cabs.append((name, short_cab(x0, x1)))

# sink base: 36" cabinet, then cut the sink shaft so the bowl hangs inside it
sink_base = short_cab(-1193.8, -2108.2)
sink_shaft = box(-2060.7, -1241.3, -524.0, -85.6, 705.0, TOP_Z + 1)
sink_base = sink_base.cut(sink_shaft)
cabs.append(("SinkBase", sink_base))

# --- create the features, paint, and file them in the App::Part ------------
for name, shp in cabs:
    f = cd.addObject("Part::Feature", name)
    f.Label = name
    f.Shape = shp
    part.addObject(f)

cd.recompute()
for name, _ in cabs:
    o = cd.getObject(name)
    paint(o, WHITE)
    show(o, True)

# hide the old solid base representations (keep the black countertop)
for nm in ("Body", "Pad", "CounterBase_Cut"):
    o = cd.getObject(nm)
    if o:
        show(o, False)
# keep these visible
for nm in ("CounterTop_Cut", "Part", "Part001",
           "Body002", "Pad003", "Body003", "Pad004"):
    o = cd.getObject(nm)
    if o:
        show(o, True)
cd.recompute()
cd.save()
L("cabinets created:", [c[0] for c in cabs])
for name, _ in cabs:
    bb = cd.getObject(name).Shape.BoundBox
    L("  %-12s X[%8.1f,%8.1f] Y[%9.1f,%9.1f] Z[%6.1f,%6.1f]" %
      (name, bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))

# --- refresh the assembly so the link re-reads the rebuilt counter ----------
ad = App.openDocument(os.path.join(KIT, "Kitchen_Assembly.FCStd"))
for o in ad.Objects:
    if o.TypeId in ("App::Link", "App::Part") or o.TypeId.startswith("Assembly::"):
        show(o, True)
    if o.TypeId == "App::Link":
        o.touch()
ad.recompute()
ad.save()
log.close()
print("CABINETS_DONE")
