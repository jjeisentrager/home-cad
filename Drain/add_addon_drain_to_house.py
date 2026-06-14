# -*- coding: utf-8 -*-
"""TASKS 7+8: add the AddOn kitchen drain (DrainAddOn, a copy of DrainLaundry, so
'same PVC-SCH40 parts and assembly methods') into the House, repositioned so its
P-trap inlet sits under the kitchen sink drain (world ~13570,13688,3315), the long
run heads WEST (-Y) past the main-house wall over the basement, then the (lengthened)
end segment turns 90 deg DOWN into the basement toward the main drain. Leave where
it lands (no tie-in). Run OFFSCREEN.

Placement M3 maps DrainAddOn-local -> world: x'=-ly, y'=lz, z'=-lx + t3
(inlet up, run west)."""
import os, FreeCAD as App
R = "/home/joee/github/alieniron/home-cad"
M = App.Matrix(0,-1,0,13722.4,  0,0,1,7187.0,  -1,0,0,2984.9,  0,0,0,1)
addon = App.openDocument(os.path.join(R, "Drain/DrainAddOn.FCStd"))
addon_asm = addon.getObject("Assembly")
house = App.openDocument(os.path.join(R, "House/House.FCStd"))
asm = house.getObject("Assembly")
old = house.getObject("DrainAddOn")
if old is not None:
    house.removeObject("DrainAddOn")
lnk = house.addObject("App::Link", "DrainAddOn")
lnk.LinkedObject = addon_asm
lnk.Label = "DrainAddOn"
lnk.Placement = App.Placement(M)
if asm is not None:
    asm.addObject(lnk)
if App.GuiUp and lnk.ViewObject is not None:
    lnk.ViewObject.Visibility = True
lnk.Visibility = True
house.recompute()
house.save()
rep = open(os.path.join(R, "Drain/addon_house_report.txt"), "w")
o = house.getObject("DrainAddOn")
rep.write("DrainAddOn link added=%s linked=%s GuiUp=%s\n" % (
    o is not None, o.LinkedObject is not None, App.GuiUp))
try:
    b = o.Shape.BoundBox
    rep.write("world bbox X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]\n" % (
        b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax))
except Exception as e:
    rep.write("bbox err %s\n" % e)
rep.close()
print("ADD_ADDON_DONE")
