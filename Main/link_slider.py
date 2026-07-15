# -*- coding: utf-8 -*-
"""Add a patio SLIDER (ViWinTech ThruBlack GVTS7280) to the main-floor east wall
(world Y=7925, the deck-facing wall) where the user marked it in slider.png:
world X ~1029..2997 (glass centred ~2013), an NW-corner room opening onto the deck.

The rough opening was cut in Main/build_mainframing.py (Ext_North_W split).  Here
we just link the door Part into House at its world placement.  The door's local
frame: +X width, +Y depth with the FRONT (exterior) face at +Y, sits on Z=0.  We
seat the exterior face flush with the wall's outer face (Y=7925), front facing +Y
(the deck), floor at world Z=2603.5.

Run OFFSCREEN GUI.  Do NOT recompute() House -- the assembly solver stalls.
"""
import os
import FreeCAD as App
try:
    import FreeCADGui as Gui  # noqa
except Exception:
    pass

R = "/home/joee/github/alieniron/home-cad"
DOOR_FC = os.path.join(R, "Library/ViWinTech/ThruBlack/ThruBlack-TraditionalSliding/"
                       "GVTS7280/ThruBlack_GVTS7280.FCStd")

log = open(os.path.join(R, "Main/_linkslider.txt"), "w", buffering=1)

dd = App.openDocument(DOOR_FC)
door = dd.getObject("Part")            # the wrapped App::Part
for o in dd.Objects:
    if o.TypeId.startswith("Part::") or o.TypeId == "App::Part":
        o.Visibility = True
        if getattr(o, "ViewObject", None):
            o.ViewObject.Visibility = True

# --- world placement --------------------------------------------------------
# door bbox local X[-76.2,1892.3] Y[-25.4,137.8] Z[0,2095.5]
WALL_Y = 7925.0            # wall outer face
FRONT_LOCAL_Y = 137.8     # door exterior face (max local Y)
GLASS_CX = 908.05         # door local X centre (( -76.2 + 1892.3 )/2)
TARGET_CX = 2013.0        # world X where the mark is centred
FLOOR_Z = 2603.5          # main-floor subfloor top

base = App.Vector(TARGET_CX - GLASS_CX, WALL_Y - FRONT_LOCAL_Y, FLOOR_Z)
plc = App.Placement(base, App.Rotation())      # front (+Y) already faces the deck

h = App.openDocument(os.path.join(R, "House/House.FCStd"))
lnk = h.getObject("Slider_Deck")
if lnk is None:
    lnk = h.addObject("App::Link", "Slider_Deck")
    lnk.Label = "Slider_Deck"
    lnk.LinkedObject = door
lnk.Placement = plc
lnk.Visibility = True
if getattr(lnk, "ViewObject", None):
    lnk.ViewObject.Visibility = True
dd.save()
h.save()
b = lnk.Shape.BoundBox
log.write("Slider_Deck world X[%.1f,%.1f] Y[%.1f,%.1f] Z[%.1f,%.1f]\n"
          % (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))
log.write("DONE\n")
log.close()
print("LINK_SLIDER_DONE")
