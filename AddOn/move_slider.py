# -*- coding: utf-8 -*-
"""todo#4: move the AddOn slider a little closer to the kitchen counter.
Slider was placed (place_livingroom) at native V(-3692,0,0) ROT180 on the front
wall, leaving a ~263mm gap west of the counter (counter west edge native X=-3353).
Shift +200mm toward the counter (native +X) -> gap ~63mm, clear of WindowSink.
Run OFFSCREEN GUI (GuiDocument + colors survive)."""
import os, FreeCAD as App
try: import FreeCADGui as Gui  # noqa
except Exception: pass
V=App.Vector; R=App.Rotation; P=App.Placement
ROOT="/home/joee/github/alieniron/home-cad"
d=App.openDocument(os.path.join(ROOT,"AddOn/AddOn_Assembly.FCStd"))
A1=d.getObject("Assembly001").Placement; A1i=A1.inverse()
sl=d.getObject("Slider")
old=sl.Placement
sl.Placement=A1.multiply(P(V(-3492.0,0.0,0.0), R(V(0,0,1),180)))
if getattr(sl,'ViewObject',None) is not None: sl.ViewObject.Visibility=True
sl.Visibility=True
d.recompute(); d.save()
nb=sl.Shape.copy(); nb.transformShape(A1i.Matrix); b=nb.BoundBox
open(os.path.join(ROOT,"AddOn/_slidermove.txt"),"w").write(
    "Slider new native X[%.0f,%.0f] Y[%.0f,%.0f] (counter west edge ~-3353, gap=%.0f)\n"
    %(b.XMin,b.XMax,b.YMin,b.YMax,-3353-b.XMax))
print("DONE")
