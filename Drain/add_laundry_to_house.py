# -*- coding: utf-8 -*-
"""TASK 6: add the laundry drain (existing DrainLaundry assembly) into the House,
repositioned so its P-trap inlet sits under the new basement laundry sink drain
(world ~14977,7474) and the long run heads NORTH (-X) along the east wall, just
clearing it, sloping downhill north, landing at ~X8450 (no tie-in -> 'leave it
where it lands').

Placement maps DrainLaundry-local -> world: x'=lz, y'=ly, z'=-lx  + t, so the
P-trap inlet (local -215.1,152.4,6501) -> world (14977.3, 7305, 535) just below
the sink stub, inlet pointing up; long run (local Z) -> world north.

Run OFFSCREEN so GuiDocument.xml survives.
"""
import os, FreeCAD as App
R = "/home/joee/github/alieniron/home-cad"
tx, ty, tz = 8476.3, 7152.6, 319.9
M = App.Matrix(0,0,1,tx,  0,1,0,ty,  -1,0,0,tz,  0,0,0,1)

lan = App.openDocument(os.path.join(R, "Drain/DrainLaundry.FCStd"))
lan_asm = lan.getObject("Assembly")
house = App.openDocument(os.path.join(R, "House/House.FCStd"))
asm = house.getObject("Assembly")

old = house.getObject("DrainLaundry")
if old is not None:
    house.removeObject("DrainLaundry")
lnk = house.addObject("App::Link", "DrainLaundry")
lnk.LinkedObject = lan_asm
lnk.Label = "DrainLaundry"
lnk.Placement = App.Placement(M)
if asm is not None:
    asm.addObject(lnk)
if App.GuiUp and lnk.ViewObject is not None:
    lnk.ViewObject.Visibility = True
lnk.Visibility = True

house.recompute()
house.save()

rep = open(os.path.join(R, "Drain/laundry_house_report.txt"), "w")
o = house.getObject("DrainLaundry")
rep.write("DrainLaundry link added: %s linked=%s GuiUp=%s\n" % (
    o is not None, o.LinkedObject is not None, App.GuiUp))
try:
    bb = o.Shape.BoundBox
    rep.write("world bbox X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]\n" % (
        bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax))
except Exception as e:
    rep.write("bbox err %s\n" % e)
rep.close()
print("ADD_LAUNDRY_DONE")
