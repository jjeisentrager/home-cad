# -*- coding: utf-8 -*-
"""Task2: lower the AddOn drain WEST run so its centerline sits at the joist
mid-height (~world Z 2476.3), keeping it under the subfloor.

Chain: STrap(outlet Z2821) -> Straight001 vertical drop -> Sweep90 (down->west)
-> Straight002 (WEST run) -> Elbow001 (turn down).

World->local (M3): world_z = 2984.9 - local_x  => lowering world Z by d means
adding +d to local x. So shift Sweep90/Straight002/Elbow001 local Base.x by
-DZ (DZ negative). Lengthen the trap drop Pad032 by -DZ to reach the lowered
sweep (drop top stays at the trap outlet).

Joints are suppressed so manual placements hold (no solver). Run OFFSCREEN GUI.
SAVE=1 to persist.
"""
import os, FreeCAD as App, Part
R="/home/joee/github/alieniron/home-cad"
SAVE=os.environ.get("SAVE","0")=="1"
M3=App.Matrix(0,-1,0,13722.4,0,0,1,7187.0,-1,0,0,2984.9,0,0,0,1)
V=App.Vector
rep=open(os.path.join(R,"Drain/_lower_rep.txt"),"w")
def w(s): rep.write(s+"\n")
d=App.openDocument(os.path.join(R,"Drain/DrainAddOn.FCStd"))

TARGET_Z=2476.3

def world_bbox(name):
    o=d.getObject(name)
    s=o.LinkedObject.Shape.copy() if (o.TypeId=="App::Link") else o.Shape.copy()
    s.transformShape(o.Placement.Matrix); s.transformShape(M3); return s.BoundBox

b=world_bbox("Straight002")
cur=(b.ZMin+b.ZMax)/2.0
DZ=TARGET_Z-cur                 # negative (lowering)
dlx=-DZ                          # local-x shift
w("Straight002 current centerline Z=%.1f  target=%.1f  DZ=%.2f  local dx=%.2f"%(cur,TARGET_Z,DZ,dlx))

# suppress all joints
nsupp=0
for o in d.Objects:
    if 'Joint' in o.TypeId or getattr(o,'Label','').startswith(('Fixed','Grounded')):
        try:
            if getattr(o,'Suppressed',False) is False: o.Suppressed=True; nsupp+=1
        except Exception: pass
w("joints suppressed this run: %d"%nsupp)

# LINKS: world = M3 * link.Placement * body.Shape -> shift placement base local +x
for nm in ("Straight002","Elbow001"):
    o=d.getObject(nm)
    p=o.Placement; nb=V(p.Base.x+dlx, p.Base.y, p.Base.z)
    o.Placement=App.Placement(nb, p.Rotation)
    w("shifted link %s base.x %.1f -> %.1f"%(nm, p.Base.x, nb.x))

# BAKED Part::Feature Sweep90: world = M3 * Shape (placement inert) -> translate the
# shape itself by local (dlx,0,0) and zero the stale placement.
sw=d.getObject("Sweep90")
sh=sw.Shape.copy(); sh.translate(V(dlx,0,0)); sw.Shape=sh
sw.Placement=App.Placement(V(0,0,0), App.Rotation())
w("translated Sweep90 SHAPE by local dx=%.1f, placement reset to identity"%dlx)

# lengthen trap drop Pad032 by -DZ (= |DZ|)
pad=d.getObject("Pad032")
body=next((o for o in pad.InList if o.TypeId=="PartDesign::Body"), pad.InList[0])
oldL=pad.Length.Value
pad.setExpression('Length', None); pad.Length=oldL+(-DZ)
pad.touch(); body.touch(); d.recompute([pad,body], True, True)
w("Pad032 length %.1f -> %.1f (body=%s)"%(oldL, pad.Length.Value, body.Name))

# ---- verify ----
def wb(name):
    b=world_bbox(name); return b
for nm in ("STrap","Straight001","Sweep90","Straight002","Elbow001"):
    b=wb(nm)
    w("  %-12s X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.1f,%.1f]"%(nm,b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax))
b=wb("Straight002"); w("NEW west centerline Z=%.1f  top=%.1f (subfloor bottom ~2590.8)"%((b.ZMin+b.ZMax)/2.0,b.ZMax))

if SAVE:
    d.save(); w("SAVED GuiUp=%s"%App.GuiUp); print("SAVED")
else:
    print("DRYRUN")
rep.close()
