# -*- coding: utf-8 -*-
"""todo#7: add a vent to the AddOn kitchen-sink drain.

Per Michigan Plumbing / IPC: an individual vent for a kitchen sink (2 DFU) is
min 1-1/2".  The vent takes off above the trap on the sink stack, runs to the
back wall by the sink, and rises in the wall up into the attic (above the
ceiling ~Z5041).  Built in House-world (DrainAddOn M3 frame) and baked as
Part::Features.  Run OFFSCREEN GUI.  SAVE=1 to persist.
"""
import os, FreeCAD as App, Part
R = "/home/joee/github/alieniron/home-cad"
SAVE = os.environ.get("SAVE", "0") == "1"
M3 = App.Matrix(0, -1, 0, 13722.4, 0, 0, 1, 7187.0, -1, 0, 0, 2984.9, 0, 0, 0, 1)
M3i = M3.inverse()
V = App.Vector
rep = open(os.path.join(R, "Drain/_vent_rep.txt"), "w")
def w(s): rep.write(s + "\n")

d = App.openDocument(os.path.join(R, "Drain/DrainAddOn.FCStd"))
asm = d.getObject("Assembly")

RV = 24.13          # 1.5" vent OD/2 (~48.26 OD)
SINK_X = 13570.0
STACK_Y = 13688.0   # sink drain stack
WALL_Y = 13735.0    # back wall by the sink
Z_TAKEOFF = 3280.0  # above trap top (~3050), on the tailpiece
Z_ATTIC = 5400.0    # ceiling ~5041 -> ~359mm into the attic

# vent polyline (House-world): into stack -> to wall -> up to attic
H = [
    V(SINK_X, STACK_Y - 30, Z_TAKEOFF),   # overlap into the sink stack (tee)
    V(SINK_X, WALL_Y,       Z_TAKEOFF),   # run to the back wall
    V(SINK_X, WALL_Y,       Z_ATTIC),     # rise in the wall into the attic
]

parts = []
for i in range(len(H) - 1):
    a, b = H[i], H[i + 1]
    dv = b.sub(a); L = dv.Length
    dvn = V(dv); dvn.normalize()
    parts.append(Part.makeCylinder(RV, L, a, dvn))
    parts.append(Part.makeSphere(RV, b))     # elbow ball at each vertex
# a little tee saddle where it meets the stack
parts.append(Part.makeSphere(RV + 4, H[0]))
vent_world = Part.makeCompound(parts)

b = vent_world.BoundBox
w("vent WORLD bbox X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]" %
  (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))
w("takeoff Z=%.0f (trap top ~3050)  riser top Z=%.0f (ceiling ~5041)" % (Z_TAKEOFF, Z_ATTIC))

vent_local = vent_world.copy(); vent_local.transformShape(M3i)
old = d.getObject("KitchenVent")
if old is not None:
    d.removeObject("KitchenVent")
f = d.addObject("Part::Feature", "KitchenVent")
f.Shape = vent_local
if asm is not None:
    asm.addObject(f)
f.Visibility = True
if App.GuiUp and f.ViewObject is not None:
    f.ViewObject.Visibility = True
    f.ViewObject.ShapeColor = (0.80, 0.85, 0.90)

# verify readback world
chk = f.Shape.copy(); chk.transformShape(M3); b = chk.BoundBox
w("KitchenVent readback M3*Shape WORLD X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]" %
  (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))

if SAVE:
    d.save(); w("SAVED GuiUp=%s" % App.GuiUp); print("SAVED")
else:
    print("DRYRUN")
rep.close()
