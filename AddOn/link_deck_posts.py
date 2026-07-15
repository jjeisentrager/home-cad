# -*- coding: utf-8 -*-
"""Colour the AddOn_DeckPosts (6x6 wood) and link them into House at identity
placement (they are built in world coords).  Run OFFSCREEN GUI.  Do NOT
recompute() House -- the assembly solver stalls.
"""
import os
import FreeCAD as App
try:
    import FreeCADGui as Gui  # noqa
except Exception:
    pass

R = "/home/joee/github/alieniron/home-cad"
BROWN = (0.55, 0.40, 0.24)          # wood, matching the framing/roof posts

log = open(os.path.join(R, "AddOn/_linkdeckposts.txt"), "w", buffering=1)

d = App.openDocument(os.path.join(R, "AddOn/AddOn_DeckPosts.FCStd"))
for o in d.Objects:
    o.Visibility = True
    vo = getattr(o, "ViewObject", None)
    if vo is None:
        continue
    vo.Visibility = True
    if not o.TypeId.startswith("Part::"):
        continue
    try:
        vo.ShapeColor = BROWN
    except Exception:
        pass
    try:
        m = vo.ShapeAppearance[0]
        m.DiffuseColor = BROWN + (1.0,)
        vo.ShapeAppearance = [m]
    except Exception:
        pass
d.save()
log.write("coloured AddOn_DeckPosts\n")

h = App.openDocument(os.path.join(R, "House/House.FCStd"))
lnk = h.getObject("DeckPosts")
if lnk is None:
    lnk = h.addObject("App::Link", "DeckPosts")
    lnk.Label = "AddOn_DeckPosts"
    lnk.LinkedObject = d.getObject("Part")
lnk.Placement = App.Placement()
lnk.Visibility = True
if getattr(lnk, "ViewObject", None):
    lnk.ViewObject.Visibility = True
h.save()
b = lnk.Shape.BoundBox
log.write("House link DeckPosts world X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]\n"
          % (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))
log.write("DONE\n")
log.close()
print("LINK_DECK_POSTS_DONE")
