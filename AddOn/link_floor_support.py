# -*- coding: utf-8 -*-
"""Colour AddOn_FloorSupport (PT beams brown, concrete grey, plates steel) and
link it into House.FCStd at identity placement (it is built in world coords).
Run OFFSCREEN GUI so GuiDocument.xml survives:
  flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD link_floor_support.py
"""
import os
import FreeCAD as App
try:
    import FreeCADGui as Gui  # noqa
except Exception:
    pass

R = "/home/joee/github/alieniron/home-cad"
BROWN = (0.55, 0.40, 0.24)
CONCRETE = (0.72, 0.72, 0.70)
STEEL = (0.45, 0.47, 0.50)
COLS = {"Beam_End": BROWN, "Beam_Mid": BROWN, "Piers": CONCRETE,
        "Footings": CONCRETE, "BearingPlates": STEEL}

log = open(os.path.join(R, "AddOn/_floorsupport_link.txt"), "w", buffering=1)
log.write("GuiUp=%s\n" % App.GuiUp)


def paint(o, col):
    vo = getattr(o, "ViewObject", None)
    o.Visibility = True
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


# 1) colour the source file
fs = App.openDocument(os.path.join(R, "AddOn/AddOn_FloorSupport.FCStd"))
for o in fs.Objects:
    if o.Name in COLS:
        paint(o, COLS[o.Name])
    elif o.TypeId == "App::Part":
        o.Visibility = True
        if getattr(o, "ViewObject", None):
            o.ViewObject.Visibility = True
fs.save()
log.write("coloured %s\n" % fs.Name)

# 2) link it into House
import time
t0 = time.time()


def T(msg):
    log.write("[%6.1fs] %s\n" % (time.time() - t0, msg))


T("opening House...")
h = App.openDocument(os.path.join(R, "House/House.FCStd"))
T("House open, %d objects" % len(h.Objects))
src = fs.getObject("Part")
lnk = h.getObject("FloorSupport")
if lnk is None:
    lnk = h.addObject("App::Link", "FloorSupport")
    lnk.Label = "AddOn_FloorSupport"
    lnk.LinkedObject = src
T("link created")
lnk.Placement = App.Placement()          # built in world coords
lnk.Visibility = True
if getattr(lnk, "ViewObject", None):
    lnk.ViewObject.Visibility = True
T("saving (no full recompute -- the assembly solver on the nested drain "
  "assemblies is what stalls)")
h.save()
T("saved")
log.write("DONE\n")
log.close()
print("LINK_DONE")
