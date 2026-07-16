# -*- coding: utf-8 -*-
"""
Swap the continuous L-counter + old upper-cabinet block for the new real cabinet
units, and slide the stove-wall window, in AddOn_Assembly and House.

Per assembly:
  * slide WindowWall / WindowWall001 by 127 mm toward the stove
    (native -Y ; world-frame copy = +127 X, native-frame copy = -127 Y),
  * hide the old Kitchen_Counter link (its base+top is replaced by real cabinets;
    Kitchen_Island is left as-is),
  * remove the old UpperCabinets link,
  * add a Cabinets link -> Kitchen_Cabinets "Part".

House is saved WITHOUT recompute (its solver hangs).
Run OFFSCREEN GUI.
"""
import os
import FreeCAD as App
try:
    import FreeCADGui as Gui  # noqa: F401
except Exception:
    pass

ROOT = "/home/joee/github/alieniron/home-cad"
log = open(os.path.join(ROOT, "Kitchen/integrate_report.txt"), "w", buffering=1)
def L(*a): log.write(" ".join(str(x) for x in a) + "\n")


def show(o, vis):
    o.Visibility = vis
    if getattr(o, "ViewObject", None) is not None:
        o.ViewObject.Visibility = vis


cd = App.openDocument(os.path.join(ROOT, "Kitchen/Kitchen_Cabinets.FCStd"))
cab_part = [o for o in cd.Objects if o.TypeId == "App::Part"][0]


def do(fname, placement):
    d = App.openDocument(os.path.join(ROOT, fname))
    # 1) slide windows
    for nm in ("WindowWall", "WindowWall001"):
        ob = d.getObject(nm)
        if ob is None:
            continue
        b = ob.Placement.Base
        if abs(b.x) > 1000:
            nb = App.Vector(b.x + 127.0, b.y, b.z)     # world-frame copy
        else:
            nb = App.Vector(b.x, b.y - 127.0, b.z)     # native-frame copy
        ob.Placement = App.Placement(nb, ob.Placement.Rotation)
    # 2) hide old counter L-run
    kc = d.getObject("Kitchen_Counter")
    if kc:
        show(kc, False)
        L("%s: hid Kitchen_Counter" % fname)
    # 3) remove old uppers
    up = d.getObject("UpperCabinets")
    if up:
        d.removeObject("UpperCabinets")
        L("%s: removed UpperCabinets" % fname)
    # 4) add new cabinets link
    old = d.getObject("Cabinets")
    if old:
        d.removeObject("Cabinets")
    asm = d.getObject("Assembly")
    lk = d.addObject("App::Link", "Cabinets")
    lk.Label = "Cabinets"
    lk.LinkedObject = cab_part
    lk.Placement = placement
    asm.addObject(lk)
    show(lk, True)
    d.save()                 # no recompute
    L("%s: added Cabinets link at base=(%.0f,%.0f,%.0f)" %
      (fname, placement.Base.x, placement.Base.y, placement.Base.z))
    return d


# AddOn: kitchen-native placement = Assembly001 (A1)
ad = App.openDocument(os.path.join(ROOT, "AddOn/AddOn_Assembly.FCStd"))
A1 = ad.getObject("Assembly001").Placement
App.closeDocument(ad.Name)
do("AddOn/AddOn_Assembly.FCStd", A1)

# House: kitchen-native -> world = AddOn o Assembly001
hd = App.openDocument(os.path.join(ROOT, "House/House.FCStd"))
comp = hd.getObject("AddOn").Placement.multiply(hd.getObject("Assembly001").Placement)
App.closeDocument(hd.Name)
do("House/House.FCStd", comp)

log.close()
print("INTEGRATE_DONE")
