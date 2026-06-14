# -*- coding: utf-8 -*-
"""Extend the laundry drain so its north vertical drop lands in the single large
floor-slab penetration at world (7315,7112) Ø508, while KEEPING the P-trap under
the laundry tub.

Two coordinated edits (length alone only grows the P-trap end, the grounded base
is the north drop):
  1) DrainLaundry Pad035 length 250" -> 295.72" (7511.3mm) via expression.
  2) House DrainLaundry link X-translation 8476.3 -> 7315.0.
The +1161.3mm pipe and -1161.3mm placement shift cancel at the P-trap.

Run OFFSCREEN so GuiDocument.xml survives in both files.
"""
import FreeCAD as App, Part
R="/home/joee/github/alieniron/home-cad"
rep=open(R+"/Drain/extend_floordrain_report.txt","w",buffering=1)
def L(*a): rep.write(" ".join(str(x) for x in a)+"\n")
L("GuiUp=%s"%App.GuiUp)

# --- 1) lengthen the run --------------------------------------------------
d=App.openDocument(R+"/Drain/DrainLaundry.FCStd")
p=d.getObject("Pad035")
L("Pad035 before: len=%.2f expr=%s"%(p.Length.Value,p.ExpressionEngine))
p.setExpression('Length','295.72 "')
d.recompute()
L("Pad035 after : len=%.2f"%p.Length.Value)
if App.GuiUp:
    d.save(); L("DrainLaundry SAVED")
else:
    L("NO GUI - DrainLaundry NOT saved")

# --- 2) shift the House link so the P-trap stays put ----------------------
h=App.openDocument(R+"/House/House.FCStd")
lnk=h.getObject("DrainLaundry")
pl=lnk.Placement
L("link tx before: %.1f"%pl.Base.x)
b=pl.Base; b.x=7315.0; pl.Base=b
lnk.Placement=pl
h.recompute()
L("link tx after : %.1f"%lnk.Placement.Base.x)

# --- verify in world (compound component shapes x link matrix) ------------
m=lnk.LinkPlacement.Matrix
def world_bb(objname):
    o=d.getObject(objname); s=o.Shape.copy(); s.transformShape(m); bb=s.BoundBox
    return bb
pt=world_bb("PTrap")
gs=world_bb("Straight")  # grounded north vertical drop
L("PTrap world  X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]"%(pt.XMin,pt.XMax,pt.YMin,pt.YMax,pt.ZMin,pt.ZMax))
L("NorthDrop wld X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]"%(gs.XMin,gs.XMax,gs.YMin,gs.YMax,gs.ZMin,gs.ZMax))
L("FLOOR HOLE   center(7315,7112) r=254 -> X[7061,7569] Y[6858,7366] slab Z[0,102]")
cx=0.5*(gs.XMin+gs.XMax); cy=0.5*(gs.YMin+gs.YMax)
import math
dist=math.hypot(cx-7315, cy-7112)
L("drop center=(%.0f,%.0f)  offset from hole center=%.0f mm  (must be < %d)"%(cx,cy,dist,254-30))
L("DROP INSIDE HOLE: %s"%(dist < (254-30)))
L("PTrap tub target world X~14977 (was ~15016)")

if App.GuiUp:
    h.save(); L("House SAVED")
else:
    L("NO GUI - House NOT saved")
rep.close()
