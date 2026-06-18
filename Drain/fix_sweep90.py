# -*- coding: utf-8 -*-
"""Rebuild the AddOn drain Sweep90 (down->west long-radius elbow) at the lowered
run height. The previous shape-translate corrupted its frame; recreate it fresh
in WORLD coords then M3i->local and bake (same method as the other fittings, which
read world = M3*Shape). Connects drop bottom (13367,13688,2616.3) to west-run
start (13367,13548,2476.3), R=140, pipe radius 30.48. OFFSCREEN, SAVE=1.
"""
import os, math, FreeCAD as App, Part
R="/home/joee/github/alieniron/home-cad"
SAVE=os.environ.get("SAVE","0")=="1"
M3=App.Matrix(0,-1,0,13722.4,0,0,1,7187.0,-1,0,0,2984.9,0,0,0,1); M3i=M3.inverse()
V=App.Vector
d=App.openDocument(os.path.join(R,"Drain/DrainAddOn.FCStd"))
asm=d.getObject("Assembly")
rep=open(os.path.join(R,"Drain/_fixsweep.txt"),"w")
def w(s): rep.write(s+"\n")

ROD=30.48; RSW=140.0
SINK_X=13366.5
E1=V(SINK_X, 13688.0, 2616.3)   # drop bottom (top of sweep), tangent -Z
E2=V(SINK_X, 13548.0, 2476.3)   # west-run start, tangent -Y
C =V(SINK_X, 13548.0, 2616.3)   # arc center
Mid=V(SINK_X, 13548.0+RSW*math.sin(math.radians(45)), 2616.3-RSW*math.cos(math.radians(45)))
arc=Part.Arc(E1,Mid,E2); spine=Part.Wire(arc.toShape())
prof=Part.Wire(Part.makeCircle(ROD, E1, V(0,0,1)))
sweep=spine.makePipeShell([prof], True, True)
# verify world bbox before M3i
b=sweep.BoundBox; w("sweep WORLD bbox X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]"%(b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax))
local=sweep.copy(); local.transformShape(M3i)

old=d.getObject("Sweep90")
col=None
if old is not None:
    if App.GuiUp and old.ViewObject is not None: col=old.ViewObject.ShapeColor
    d.removeObject("Sweep90")
f=d.addObject("Part::Feature","Sweep90"); f.Shape=local
if asm is not None: asm.addObject(f)
f.Visibility=True
if App.GuiUp and f.ViewObject is not None:
    f.ViewObject.Visibility=True
    f.ViewObject.ShapeColor=col if col else (0.82,0.82,0.85)

# verify round-trip: world = M3*Shape
chk=f.Shape.copy(); chk.transformShape(M3); b=chk.BoundBox
w("Sweep90 readback M3*Shape WORLD X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]"%(b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax))

if SAVE:
    d.save(); w("SAVED GuiUp=%s"%App.GuiUp); print("SAVED")
else:
    print("DRYRUN")
rep.close()
