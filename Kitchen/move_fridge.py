# -*- coding: utf-8 -*-
"""Move the refrigerator one cabinet closer to the stove.

"One cabinet" = a full two-door base cabinet = 36" = 914.4 mm.

Counter-local frame (== assembly/world, the counter is grounded at the origin):
the long counter run goes along -Y, so the fridge at Y=-6723.2 moves +Y toward
the range at Y=-3207.8.  Gap between them: 2607 mm (102.6") -> 1693 mm (66.6").

The fridge is linked in three documents with the same local placement, so all
three get the same shift.  Run OFFSCREEN GUI so GuiDocument.xml survives:
  flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD move_fridge.py
NOTE: do NOT recompute() House -- the assembly solver on the nested drain
assemblies stalls for many minutes.  The links carry their own placement.
"""
import os
import FreeCAD as App
try:
    import FreeCADGui as Gui  # noqa
except Exception:
    pass

R = "/home/joee/github/alieniron/home-cad"
CABINET = 914.4          # 36" two-door base cabinet
DOCS = ["Kitchen/Kitchen_Assembly.FCStd", "AddOn/AddOn_Assembly.FCStd",
        "House/House.FCStd"]

log = open(os.path.join(R, "Kitchen/_movefridge.txt"), "w", buffering=1)
log.write("GuiUp=%s  shift=+%.1f mm along counter-local +Y\n" % (App.GuiUp, CABINET))

for rel in DOCS:
    d = App.openDocument(os.path.join(R, rel))
    f = d.getObject("Refrigerator")
    if f is None:
        log.write("%s: no Refrigerator link\n" % rel)
        App.closeDocument(d.Name)
        continue
    p = f.Placement
    old = p.Base.y
    p.Base.y = old + CABINET
    f.Placement = p
    f.Visibility = True
    if getattr(f, "ViewObject", None):
        f.ViewObject.Visibility = True
    d.save()
    b = f.Shape.BoundBox
    log.write("%-28s Y %.1f -> %.1f   fridge bb Y[%.0f,%.0f]\n"
              % (rel, old, p.Base.y, b.YMin, b.YMax))
    App.closeDocument(d.Name)

log.write("DONE\n")
log.close()
print("MOVE_FRIDGE_DONE")
