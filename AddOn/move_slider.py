# -*- coding: utf-8 -*-
"""Give the slider clearance from the counter and the window.

Before: the slider actually OVERLAPPED the counter by 31 mm and sat 210 mm from
the window (the earlier +200 mm nudge toward the counter went too far).  The wall
run between the window and the counter is 2147.6 mm and the slider is 1968.5 mm
wide, so there is only 179.1 mm of slack -- 4" on BOTH sides (203.2 mm) does not
fit.  Centring it is the most spacing available: 89.5 mm (3.52") each side.

That is a -120.45 mm shift in WORLD X.  build_framing.py moves the rough opening
by the same amount (wall-local x runs opposite world X, so its centre goes
4400.0 -> 4520.5); this script moves the slider link to match, in every document
that positions it.

Run OFFSCREEN GUI (GuiDocument + colours survive):
  flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD move_slider.py
Do NOT recompute() House -- the assembly solver on the nested drain assemblies
stalls for many minutes.
"""
import os
import FreeCAD as App
try:
    import FreeCADGui as Gui  # noqa
except Exception:
    pass

R = "/home/joee/github/alieniron/home-cad"
DX_WORLD = -120.45          # world X shift

log = open(os.path.join(R, "AddOn/_slidermove.txt"), "w", buffering=1)
log.write("GuiUp=%s  world dX=%.2f\n" % (App.GuiUp, DX_WORLD))

# the slider link's Placement lives in the AddOn-local frame, so rotate the world
# delta back through the AddOn assembly's rotation
h = App.openDocument(os.path.join(R, "House/House.FCStd"))
AP = h.getObject("AddOn").Placement
d_local = AP.Rotation.inverted().multVec(App.Vector(DX_WORLD, 0, 0))
log.write("AddOn-local delta = (%.3f, %.3f, %.3f)\n" % (d_local.x, d_local.y, d_local.z))

a = App.openDocument(os.path.join(R, "AddOn/AddOn_Assembly.FCStd"))
for rel, doc in [("House/House.FCStd", h), ("AddOn/AddOn_Assembly.FCStd", a)]:
    sl = doc.getObject("Slider")
    if sl is None:
        log.write("%s: no Slider link\n" % rel)
        continue
    p = sl.Placement
    old = App.Vector(p.Base)
    p.Base = old + d_local
    sl.Placement = p
    sl.Visibility = True
    if getattr(sl, "ViewObject", None):
        sl.ViewObject.Visibility = True
    doc.save()
    log.write("%-28s Base (%.1f,%.1f,%.1f) -> (%.1f,%.1f,%.1f)\n"
              % (rel, old.x, old.y, old.z, p.Base.x, p.Base.y, p.Base.z))

log.write("DONE\n")
log.close()
print("MOVE_SLIDER_DONE")
