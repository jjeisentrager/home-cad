# -*- coding: utf-8 -*-
"""Colour the Deck and link it into House at identity placement (world coords).
Run OFFSCREEN GUI.  Do NOT recompute() House -- the assembly solver stalls.
"""
import os
import FreeCAD as App
try:
    import FreeCADGui as Gui  # noqa
except Exception:
    pass

R = "/home/joee/github/alieniron/home-cad"
COLS = {
    "Decking": (0.62, 0.44, 0.29),        # warm deck boards
    "Joists": (0.55, 0.40, 0.24),         # PT framing
    "RimAndLedger": (0.50, 0.36, 0.22),
    "Beams": (0.50, 0.36, 0.22),
    "Piers": (0.72, 0.72, 0.70),          # concrete
    "Footings": (0.72, 0.72, 0.70),
    "BearingPlates": (0.45, 0.47, 0.50),  # galvanised
    "StairEast": (0.62, 0.44, 0.29),      # deck-board / PT wood
    "StairSouth": (0.62, 0.44, 0.29),
    "StairPads": (0.72, 0.72, 0.70),      # concrete landing pads
}

log = open(os.path.join(R, "Deck/_linkdeck.txt"), "w", buffering=1)

d = App.openDocument(os.path.join(R, "Deck/Deck.FCStd"))
for o in d.Objects:
    o.Visibility = True
    vo = getattr(o, "ViewObject", None)
    if vo is None:
        continue
    vo.Visibility = True
    col = COLS.get(o.Name)
    if col is None:
        continue
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
d.save()
log.write("coloured Deck\n")

h = App.openDocument(os.path.join(R, "House/House.FCStd"))
lnk = h.getObject("Deck")
if lnk is None:
    lnk = h.addObject("App::Link", "Deck")
    lnk.Label = "Deck"
    lnk.LinkedObject = d.getObject("Part")
lnk.Placement = App.Placement()
lnk.Visibility = True
if getattr(lnk, "ViewObject", None):
    lnk.ViewObject.Visibility = True
h.save()
b = lnk.Shape.BoundBox
log.write("House link Deck bb X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]\n"
          % (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))
log.write("DONE\n")
log.close()
print("LINK_DECK_DONE")
