# -*- coding: utf-8 -*-
"""Colour AddOn_RoofConnector and link it into House as its OWN assembly piece.

It shares the roof-local frame with AddOn_RoofFrame, so its world placement is
AP * RP -- the AddOn assembly placement times the existing RoofFrame link's
placement.

Run OFFSCREEN GUI.  Do NOT recompute() House -- the assembly solver stalls.
"""
import os
import FreeCAD as App
try:
    import FreeCADGui as Gui  # noqa
except Exception:
    pass

R = "/home/joee/github/alieniron/home-cad"
WOOD = (0.72, 0.62, 0.47)          # stick framing, like the rest of the roof

log = open(os.path.join(R, "AddOn/_linkconnector.txt"), "w", buffering=1)

c = App.openDocument(os.path.join(R, "AddOn/AddOn_RoofConnector.FCStd"))
for o in c.Objects:
    o.Visibility = True
    vo = getattr(o, "ViewObject", None)
    if vo is None:
        continue
    vo.Visibility = True
    if o.TypeId != "Part::Feature":
        continue
    try:
        vo.ShapeColor = WOOD
    except Exception:
        pass
    try:
        m = vo.ShapeAppearance[0]
        m.DiffuseColor = WOOD + (1.0,)
        vo.ShapeAppearance = [m]
    except Exception:
        pass
c.save()
log.write("coloured RoofConnector\n")

h = App.openDocument(os.path.join(R, "House/House.FCStd"))
AP = h.getObject("AddOn").Placement
RP = h.getObject("RoofFrame").Placement          # same roof-local frame

lnk = h.getObject("RoofConnector")
if lnk is None:
    lnk = h.addObject("App::Link", "RoofConnector")
    lnk.Label = "AddOn_RoofConnector"
    lnk.LinkedObject = c.getObject("Part")
lnk.Placement = AP.multiply(RP)
lnk.Visibility = True
if getattr(lnk, "ViewObject", None):
    lnk.ViewObject.Visibility = True
h.save()
b = lnk.Shape.BoundBox
log.write("House link RoofConnector world X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]\n"
          % (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))
log.write("DONE\n")
log.close()
print("LINK_CONNECTOR_DONE")
