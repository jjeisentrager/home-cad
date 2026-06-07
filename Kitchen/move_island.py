# -*- coding: utf-8 -*-
"""
Move the Kitchen_Island link to a reasonable spot and make sure it is visible.

The island had been left at Z=-1153 (sunk below the floor) out in the far -X
open area.  Re-seat it on the floor (Z=0) in the open quadrant, long axis
parallel to the long counter run, across from the range with comfortable aisles:

  island base world  X[-3079.6,-1809.6]  Y[-4470,-1930]  Z[0,914.4]
    -> ~1200 mm aisle to the long-counter front (X=-609.6; ~1076 mm to the range
       front at X=-734) and ~1320 mm to the short-leg sink counter (Y=-609.6).

Island local base (Body002) is X[-3302,-2032] Y[-4572,-2032] Z[0,914.4], link
rotation identity, so world = local + base  ->  base = (222.4, 102.0, 0.0).

Run with the GUI layer up so visibility + GuiDocument persist:
  flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD \
    Kitchen/move_island.py
"""
import os
import FreeCAD as App
import FreeCADGui as Gui  # noqa: F401

V = App.Vector
ROOT = "/home/joee/github/alieniron/home-cad"
KIT = os.path.join(ROOT, "Kitchen")
log = open(os.path.join(ROOT, "island_report.txt"), "w")
def L(*a): log.write(" ".join(str(x) for x in a) + "\n")

def show(o, vis=True):
    o.Visibility = vis
    if o.ViewObject is not None:
        o.ViewObject.Visibility = vis

adoc = App.openDocument(os.path.join(KIT, "Kitchen_Assembly.FCStd"))
isl = adoc.getObject("Kitchen_Island")
pl = isl.Placement
pl.Base = V(222.4, 102.0, 0.0)        # rotation already identity
isl.Placement = pl
show(isl, True)
# keep the rest of the scene visible too
for o in adoc.Objects:
    if o.TypeId in ("App::Link", "App::Part") or o.TypeId.startswith("Assembly::"):
        show(o, True)
adoc.recompute()
adoc.save()

bb = isl.Shape.BoundBox
L("island moved. link base:", isl.Placement.Base)
L("island world bbox: X[%.1f,%.1f] Y[%.1f,%.1f] Z[%.1f,%.1f]" %
  (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))
L("link Visibility:", isl.Visibility,
  " VO.Visibility:", (isl.ViewObject.Visibility if isl.ViewObject else "n/a"))
log.close()
print("ISLAND_MOVED")
