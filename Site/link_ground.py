# -*- coding: utf-8 -*-
"""Colour the Ground and link it into House at identity placement (world coords).
Run OFFSCREEN GUI.  Do NOT recompute() House -- the assembly solver stalls.
"""
import os
import FreeCAD as App
try:
    import FreeCADGui as Gui  # noqa
except Exception:
    pass

R = "/home/joee/github/alieniron/home-cad"
GRASS = (0.42, 0.55, 0.31)

log = open(os.path.join(R, "Site/_linkground.txt"), "w", buffering=1)

g = App.openDocument(os.path.join(R, "Site/Ground.FCStd"))
for o in g.Objects:
    o.Visibility = True
    vo = getattr(o, "ViewObject", None)
    if vo is None:
        continue
    vo.Visibility = True
    if o.TypeId == "Part::Feature":
        try:
            vo.ShapeColor = GRASS
        except Exception:
            pass
        try:
            m = vo.ShapeAppearance[0]
            m.DiffuseColor = GRASS + (1.0,)
            vo.ShapeAppearance = [m]
        except Exception:
            pass
g.save()
log.write("coloured Ground\n")

h = App.openDocument(os.path.join(R, "House/House.FCStd"))
lnk = h.getObject("Ground")
if lnk is None:
    lnk = h.addObject("App::Link", "Ground")
    lnk.Label = "Ground"
    lnk.LinkedObject = g.getObject("Part")
lnk.Placement = App.Placement()
lnk.Visibility = True
if getattr(lnk, "ViewObject", None):
    lnk.ViewObject.Visibility = True
h.save()
b = lnk.Shape.BoundBox
log.write("House link Ground bb X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.1f,%.1f]\n"
          % (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))
log.write("DONE\n")
log.close()
print("LINK_GROUND_DONE")
