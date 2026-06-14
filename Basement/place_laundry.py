# -*- coding: utf-8 -*-
"""TASKS 3-5: add the dryer, washer and laundry sink to the Basement assembly,
along the EAST wall (inner face Y=7772.4), facing WEST (180 deg about Z), on the
slab (top Z=101.6).  Order south->north: dryer (SE corner, offset 200mm off the
south wall X=16891 to leave door-swing clearance), washer, laundry sink.

Basement is grounded at the House origin, so basement-local == world coords.
Links are added directly to the Basement 'Assembly' (un-jointed -> the solver
leaves them where placed).  Run OFFSCREEN so GuiDocument.xml survives.
"""
import os, FreeCAD as App
R = "/home/joee/github/alieniron/home-cad"
V = App.Vector
def Z(d): return App.Rotation(V(0, 0, 1), d)
rep = open(os.path.join(R, "Basement/place_laundry_report.txt"), "w", buffering=1)
def P(*a): rep.write(" ".join(str(x) for x in a) + "\n"); rep.flush()

FLOOR = 101.6
WALL_Y = 7772.4          # inner face of east wall (back of appliances)
SOUTH_X = 16891.0        # inner face of south wall
DOOR_GAP = 200.0         # clearance south of dryer for the door
GAP = 25.0               # gap between appliances

# widths (local X) of each unit
W_DRY, W_WASH, W_SINK = 685.8, 685.8, 584.2
x_dry = SOUTH_X - DOOR_GAP                 # dryer south(=max world X) face
x_wash = (x_dry - W_DRY) - GAP             # washer south face
x_sink = (x_wash - W_WASH) - GAP           # sink south face

dry_doc = App.openDocument(os.path.join(R, "Library/DLGX3701W/DLGX3701W.FCStd"))
wash_doc = App.openDocument(os.path.join(R, "Library/WM3700HWA/WM3700HWA.FCStd"))
sink_doc = App.openDocument(os.path.join(R, "Library/Mustee-19/Mustee-19.FCStd"))

bas = App.openDocument(os.path.join(R, "Basement/Basement.FCStd"))
asm = bas.getObject("Assembly")

JOBS = [
    ("Dryer",       dry_doc.getObject("Part"),  V(x_dry,  WALL_Y, FLOOR), Z(180)),
    ("Washer",      wash_doc.getObject("Part"), V(x_wash, WALL_Y, FLOOR), Z(180)),
    ("LaundrySink", sink_doc.getObject("Part"), V(x_sink, WALL_Y, FLOOR), Z(180)),
]
for name, part, base, rot in JOBS:
    old = bas.getObject(name)
    if old is not None:
        bas.removeObject(name)
    lnk = bas.addObject("App::Link", name)
    lnk.LinkedObject = part
    lnk.Label = name
    lnk.Placement = App.Placement(base, rot)
    if asm is not None:
        asm.addObject(lnk)
    if App.GuiUp and lnk.ViewObject is not None:
        lnk.ViewObject.Visibility = True
    lnk.Visibility = True

bas.recompute()
bas.save()

# report world bboxes + the laundry-sink drain stub world position (for task 6)
for name, part, base, rot in JOBS:
    o = bas.getObject(name)
    s = o.LinkedObject.Shape.copy(); s.transformShape(o.Placement.Matrix)
    bb = s.BoundBox
    P("%-12s base=(%.1f,%.1f,%.1f) ang180  world X[%.1f,%.1f] Y[%.1f,%.1f] Z[%.1f,%.1f]" % (
        name, base.x, base.y, base.z, bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))
# laundry sink drain stub
o = bas.getObject("LaundrySink")
for ch in o.LinkedObject.Group:
    if ch.Name == "DrainStub" or ch.Label == "DrainStub":
        sh = ch.Shape.copy(); sh.transformShape(o.Placement.Matrix)
        c = sh.BoundBox.Center
        P("LaundrySink DrainStub world center=(%.1f,%.1f,%.1f) bbox X[%.1f,%.1f] Y[%.1f,%.1f] Z[%.1f,%.1f]" % (
            c.x, c.y, c.z, sh.BoundBox.XMin, sh.BoundBox.XMax, sh.BoundBox.YMin,
            sh.BoundBox.YMax, sh.BoundBox.ZMin, sh.BoundBox.ZMax))
P("recompute errors:", bas.recompute())
P("DONE"); rep.close(); print("PLACE_LAUNDRY_DONE")
