# -*- coding: utf-8 -*-
"""
Link Kitchen_UpperCabinets into AddOn_Assembly (top Assembly group at the A1
kitchen placement, like the Electrical link) and into House.FCStd (a direct
App::Link, placed kitchen-native -> House-world).  Reports window counts so we
can confirm nothing was dropped.

NOTE: AddOn_Assembly is recomputed+saved (fine; matches build_electrical.py).
House is saved WITHOUT recompute -- recomputing House hangs on the nested
assembly solver.

Run OFFSCREEN GUI:
  flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD Kitchen/link_upper_cabinets.py
"""
import os
import FreeCAD as App
try:
    import FreeCADGui as Gui  # noqa: F401
except Exception:
    pass

ROOT = "/home/joee/github/alieniron/home-cad"
log = open(os.path.join(ROOT, "Kitchen/link_cabinets_report.txt"), "w", buffering=1)
def L(*a): log.write(" ".join(str(x) for x in a) + "\n")


def show(o, vis=True):
    o.Visibility = vis
    if getattr(o, "ViewObject", None) is not None:
        o.ViewObject.Visibility = vis


# target Part in the cabinets doc
cd = App.openDocument(os.path.join(ROOT, "Kitchen/Kitchen_UpperCabinets.FCStd"))
cab_part = [o for o in cd.Objects if o.TypeId == "App::Part"][0]

# --- 1) AddOn_Assembly ---
ad = App.openDocument(os.path.join(ROOT, "AddOn/AddOn_Assembly.FCStd"))
A1 = ad.getObject("Assembly001").Placement
asm = ad.getObject("Assembly")
before = [o.Name for o in asm.Group if o.Name.startswith("Window")]
old = ad.getObject("UpperCabinets")
if old:
    ad.removeObject("UpperCabinets")
lk = ad.addObject("App::Link", "UpperCabinets")
lk.Label = "UpperCabinets"
lk.LinkedObject = cab_part
lk.Placement = A1
asm.addObject(lk)
show(lk, True)
ad.recompute()
ad.save()
after = [o.Name for o in asm.Group if o.Name.startswith("Window")]
L("AddOn_Assembly windows before=%s after=%s" % (before, after))
L("AddOn_Assembly UpperCabinets bbox X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]" %
  (lk.Shape.BoundBox.XMin, lk.Shape.BoundBox.XMax, lk.Shape.BoundBox.YMin,
   lk.Shape.BoundBox.YMax, lk.Shape.BoundBox.ZMin, lk.Shape.BoundBox.ZMax))

# --- 2) House (no recompute) ---
hd = App.openDocument(os.path.join(ROOT, "House/House.FCStd"))
comp = hd.getObject("AddOn").Placement.multiply(hd.getObject("Assembly001").Placement)
hasm = hd.getObject("Assembly")
oldh = hd.getObject("UpperCabinets")
if oldh:
    hd.removeObject("UpperCabinets")
hlk = hd.addObject("App::Link", "UpperCabinets")
hlk.Label = "UpperCabinets"
hlk.LinkedObject = cab_part
hlk.Placement = comp
hasm.addObject(hlk)
show(hlk, True)
hd.save()                      # NO recompute (House solver hangs)
L("House UpperCabinets added; placement base=(%.1f,%.1f,%.1f)" %
  (comp.Base.x, comp.Base.y, comp.Base.z))
log.close()
print("LINK_CABINETS_DONE")
