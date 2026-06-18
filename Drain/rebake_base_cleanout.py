# -*- coding: utf-8 -*-
"""Task1: after restoring the FLAT HEAD DrainAssembly, re-seat the user's
sanitary-tee + cleanout (added in the sloped batch) at the FLAT stack base.

We move them rigidly by R = HEAD_Straight019_pl * sloped_Straight019_pl^-1,
the same transform that maps the sloped/extended building-drain main back to
its flat HEAD position+orientation. So the fittings stay attached to the main's
base end and become un-sloped automatically. Baked as Part::Features (no joints,
no solver) so they hold and the flat assembly is untouched.

Run OFFSCREEN GUI so GuiDocument survives.  SAVE=1 to persist.
"""
import os, FreeCAD as App, Part
R="/home/joee/github/alieniron/home-cad"
SAVE=os.environ.get("SAVE","0")=="1"
rep=open(os.path.join(R,"Drain/_rebake_rep.txt"),"w")
def w(s): rep.write(s+"\n")

# --- read shapes + sloped main placement from the preserved sloped file ---
sl=App.openDocument(os.path.join(R,"Drain/_sloped_DrainAssembly.FCStd"))
def gshape(name):
    o=sl.getObject(name)
    s=o.LinkedObject.Shape.copy(); s.transformShape(o.Placement.Matrix)
    return s
tee_sh=gshape("SanitaryTee010")
cap_sh=gshape("CleanoutCap002")
sloped_main=App.Placement(sl.getObject("Straight019").Placement)
b=tee_sh.BoundBox; w("sloped tee  bbox X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]"%(b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax))
b=cap_sh.BoundBox; w("sloped cap  bbox X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]"%(b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax))

# --- open the restored FLAT assembly, get HEAD main placement ---
d=App.openDocument(os.path.join(R,"Drain/DrainAssembly.FCStd"))
head_main=App.Placement(d.getObject("Straight019").Placement)
w("HEAD main base=(%.1f,%.1f,%.1f)"%(head_main.Base.x,head_main.Base.y,head_main.Base.z))
w("sloped main base=(%.1f,%.1f,%.1f)"%(sloped_main.Base.x,sloped_main.Base.y,sloped_main.Base.z))

# R maps sloped-main frame -> HEAD-main frame (global), applied to fitting shapes
Rm = head_main.Matrix.multiply(sloped_main.Matrix.inverse())

asm=d.getObject("Assembly")
def bake(name,world_shape,color):
    s=world_shape.copy(); s.transformShape(Rm)
    old=d.getObject(name)
    if old is not None: d.removeObject(name)
    f=d.addObject("Part::Feature",name); f.Shape=s
    if asm is not None: asm.addObject(f)
    f.Visibility=True
    if App.GuiUp and f.ViewObject is not None:
        f.ViewObject.Visibility=True; f.ViewObject.ShapeColor=color
    bb=s.BoundBox
    w("baked %-16s X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]"%(name,bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax))
    return f

bake("BaseSanTee", tee_sh, (0.78,0.78,0.80))
bake("BaseCleanout", cap_sh, (0.55,0.85,0.55))

# verify the new HEAD main bottom (where fittings should meet)
ms=d.getObject("Straight019").LinkedObject.Shape.copy()
ms.transformShape(d.getObject("Straight019").Placement.Matrix)
mb=ms.BoundBox; w("HEAD main bbox X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]"%(mb.XMin,mb.XMax,mb.YMin,mb.YMax,mb.ZMin,mb.ZMax))

if SAVE:
    d.save(); w("SAVED GuiUp=%s"%App.GuiUp); print("SAVED")
else:
    print("DRYRUN")
rep.close()
