# -*- coding: utf-8 -*-
"""Link the Chimney into House at a chosen world placement.  Run OFFSCREEN GUI
(colours + GuiDocument survive).  Do NOT recompute() House -- the nested assembly
solver stalls; just save() (see link_deck.py / memory house-recompute-stall).

Placement (per chimney-location.png): the chimney backs onto the H_p11 wall
(world Y~4255) in the great room, main firebox facing EAST, basement WEST, with
the chimney's NORTH face 21" from that wall's north/low-X end (world X~9321.8).
Model->world mapping is a 180 deg Z rotation + translation so:
  model -Y (main-firebox side)     -> world +Y (EAST, into the great room)
  model +Y (basement-firebox side) -> world -Y (WEST, against the wall)
  model +X (width, 71")            -> world -X   (runs N-S)
  model +Z (height)                -> world +Z, local Z0 -> world 101.6 (slab)
North face at world X = 9321.8 + 21" = 9855.2  ->  base Tx = 9855.2 + 1803.4.
Chimney world footprint (mass) X[9855,11659] Y[4293,5080], base Z101.6, top Z7468.
"""
import os
import FreeCAD as App
try:
    import FreeCADGui as Gui  # noqa: F401
except Exception:
    pass

V = App.Vector
R = "/home/joee/github/alieniron/home-cad"
log = open(os.path.join(R, "Chimney/_linkchimney.txt"), "w", buffering=1)

cd = App.openDocument(os.path.join(R, "Chimney/Chimney.FCStd"))
cd.recompute()
part = cd.getObject("Part")

PLACE = App.Placement(V(11658.6, 5080.0, 101.6),
                      App.Rotation(V(0, 0, 1), 180.0))

h = App.openDocument(os.path.join(R, "House/House.FCStd"))
lnk = h.getObject("Chimney")
if lnk is None:
    lnk = h.addObject("App::Link", "Chimney")
    lnk.Label = "Chimney"
    lnk.LinkedObject = part
lnk.Placement = PLACE
lnk.Visibility = True
if getattr(lnk, "ViewObject", None):
    lnk.ViewObject.Visibility = True
asm = h.getObject("Assembly")
if asm is not None and lnk not in asm.Group:
    asm.addObject(lnk)
h.save()

try:
    b = lnk.Shape.BoundBox
    log.write("House link Chimney world X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]\n"
              % (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))
except Exception as e:
    log.write("bbox via link failed (%s); compounding part shapes...\n" % e)
    import Part
    shp = Part.makeCompound([o.Shape for o in part.Group
                             if getattr(o, "Shape", None) is not None])
    shp.transformShape(PLACE.Matrix)
    b = shp.BoundBox
    log.write("House link Chimney world X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]\n"
              % (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))
log.write("DONE\n")
log.close()
print("LINK_CHIMNEY_DONE")
