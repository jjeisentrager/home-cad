# -*- coding: utf-8 -*-
"""Link AddOn_Beams (the steel I-beam across the AddOn's open side + its 3 posts)
into House.  The file existed but was linked nowhere, so the I-beam was not in the
House model at all -- yet the roof's bottom chords are spaced to it.

AddOn_Beams is built in the KITCHEN-NATIVE frame, so the link placement is
AP * A1 (AddOn assembly placement * Assembly001 placement), which lands it at
world X[7348,15185] Y[7893,8109] Z[4686,5042].

Steel gets a steel colour; the posts stay wood.
Run OFFSCREEN GUI.  Do NOT recompute() House (assembly solver stalls).
"""
import os
import FreeCAD as App
try:
    import FreeCADGui as Gui  # noqa
except Exception:
    pass

R = "/home/joee/github/alieniron/home-cad"
STEEL = (0.55, 0.57, 0.60)
BROWN = (0.55, 0.40, 0.24)

log = open(os.path.join(R, "AddOn/_linkbeams.txt"), "w", buffering=1)


def paint(o, col):
    o.Visibility = True
    vo = getattr(o, "ViewObject", None)
    if vo is None:
        return
    vo.Visibility = True
    try:
        vo.ShapeColor = col
    except Exception:
        pass
    try:
        m = vo.ShapeAppearance[0]
        m.DiffuseColor = col + (1.0,)
        vo.ShapeAppearance = [m]
    except Exception:
        pass


bm = App.openDocument(os.path.join(R, "AddOn/AddOn_Beams.FCStd"))
for o in bm.Objects:
    if o.Name == "IBeam":
        paint(o, STEEL)
    elif o.Name.startswith("Post"):
        paint(o, BROWN)
    elif o.TypeId == "App::Part":
        paint(o, BROWN)
bm.save()
log.write("coloured AddOn_Beams (I-beam steel, posts wood)\n")

a = App.openDocument(os.path.join(R, "AddOn/AddOn_Assembly.FCStd"))
A1 = a.getObject("Assembly001").Placement
h = App.openDocument(os.path.join(R, "House/House.FCStd"))
AP = h.getObject("AddOn").Placement

src = bm.getObject("Beams")            # the App::Part
lnk = h.getObject("AddOnBeams")
if lnk is None:
    lnk = h.addObject("App::Link", "AddOnBeams")
    lnk.Label = "AddOn_IBeam"
    lnk.LinkedObject = src
lnk.Placement = AP.multiply(A1)
lnk.Visibility = True
if getattr(lnk, "ViewObject", None):
    lnk.ViewObject.Visibility = True
h.save()
b = lnk.Shape.BoundBox
log.write("House link AddOnBeams world X[%.1f,%.1f] Y[%.1f,%.1f] Z[%.1f,%.1f]\n"
          % (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))
log.write("DONE\n")
log.close()
print("LINK_BEAMS_DONE")
