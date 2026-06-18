# -*- coding: utf-8 -*-
"""todo#3 (centering): shift the A1-frame openings so their depth is centered in
the 3.5" stud wall instead of sitting proud of the exterior face.
Front wall studs native Y 0..-88.9 (center -44.45); West wall studs native
X -7924.8..-7836 (center -7880.4). Shifts applied in world via A1 rotation.
Run OFFSCREEN GUI."""
import os, FreeCAD as App
try: import FreeCADGui as Gui  # noqa
except Exception: pass
V=App.Vector
R="/home/joee/github/alieniron/home-cad"
d=App.openDocument(os.path.join(R,"AddOn/AddOn_Assembly.FCStd"))
A1=d.getObject("Assembly001").Placement; A1i=A1.inverse()
rep=open(os.path.join(R,"AddOn/_center.txt"),"w")
def nbb(o):
    s=o.Shape.copy(); s.transformShape(A1i.Matrix); return s.BoundBox
WALL_C_Y=-44.45; WALL_C_X=-7880.4
# (name, axis)  axis: 'Y' front-wall normal, 'X' west-wall normal
JOBS=[("WindowFrontLeft","Y"),("Slider","Y"),("WindowWest","X")]
for nm,ax in JOBS:
    o=d.getObject(nm)
    if o is None: rep.write("%s MISSING\n"%nm); continue
    b=nbb(o)
    if ax=="Y":
        cur=(b.YMin+b.YMax)/2.0; delta=WALL_C_Y-cur; nd=V(0,delta,0)
    else:
        cur=(b.XMin+b.XMax)/2.0; delta=WALL_C_X-cur; nd=V(delta,0,0)
    ws=A1.Rotation.multVec(nd)
    o.Placement=App.Placement(o.Placement.Base.add(ws), o.Placement.Rotation)
    rep.write("%-16s axis=%s curC=%.1f delta=%.1f\n"%(nm,ax,cur,delta))
d.recompute(); d.save()
for nm,ax in JOBS:
    b=nbb(d.getObject(nm)); rep.write("  %-16s NATIVE X[%.0f,%.0f] Y[%.0f,%.0f]\n"%(nm,b.XMin,b.XMax,b.YMin,b.YMax))
rep.close(); print("DONE")
