# -*- coding: utf-8 -*-
"""
Place the bath fixtures into the House top assembly, aligned to the existing
drain stubs (world coords read from the DrainAssembly):

  Toilet (AS-Champion4)  x2  -- closet outlet (local 241.5, 304.8) over each
                                3" drain; tank to the Y=6388 wet wall.
    * North bath  : 3" stub (5869,6639), faces +Y  (no Z rotation)
    * Interior bath: 3" stub (7099,6129), faces -Y  (180 deg Z)
  Tub (Sterling-Medley-6030) -- drain (local 254, 382.6) over the interior
    bath's 2" stub (6291,5962); backs the Y=6388 wall, apron faces -Y, right-
    hand drain end against the V_n76 partition (180 deg Z).

Fixtures rest on the finished floor: Main subfloor top = world Z 2603.5.

Links are added directly to the House Assembly (same pattern as the Drain link)
with WORLD placements.  Run OFFSCREEN so GuiDocument.xml survives:
  flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD place_bath_fixtures.py
"""
import os
import FreeCAD as App

R = "/home/joee/github/alieniron/home-cad"
V = App.Vector
def Z(deg): return App.Rotation(V(0, 0, 1), deg)

FLOOR = 2603.5  # world Z of finished floor (Main subfloor top)

# linked library parts
toilet_doc = App.openDocument(os.path.join(R, "Library/AS-Champion4/AS-Champion4.FCStd"))
tub_doc = App.openDocument(os.path.join(R, "Library/Sterling-Medley-6030/Sterling-Medley-6030.FCStd"))
toilet_part = toilet_doc.getObject("Part")
tub_part = tub_doc.getObject("Part")

house = App.openDocument(os.path.join(R, "House/House.FCStd"))
asm = house.getObject("Assembly")

PLACEMENTS = [
    ("Toilet_NorthBath",   toilet_part, V(5627.5, 6334.2, FLOOR), Z(0)),
    ("Toilet_InteriorBath", toilet_part, V(7340.5, 6433.8, FLOOR), Z(180)),
    ("Tub_InteriorBath",   tub_part,    V(6545.0, 6344.6, FLOOR), Z(180)),
]

for name, part, base, rot in PLACEMENTS:
    old = house.getObject(name)
    if old is not None:
        house.removeObject(name)
    lnk = house.addObject("App::Link", name)
    lnk.LinkedObject = part
    lnk.Label = name
    lnk.Placement = App.Placement(base, rot)
    if asm is not None:
        asm.addObject(lnk)
    if App.GuiUp and lnk.ViewObject is not None:
        lnk.ViewObject.Visibility = True
    lnk.Visibility = True

house.recompute()
house.save()

# report
with open(os.path.join(R, "Bath/place_report.txt"), "w") as fh:
    fh.write("GuiUp=%s\n" % App.GuiUp)
    for name, part, base, rot in PLACEMENTS:
        o = house.getObject(name)
        fh.write("%-20s base=%s ang=%.0f  resolved=%s\n" %
                 (name, tuple(round(c, 1) for c in (base.x, base.y, base.z)),
                  rot.Angle * 180 / 3.141592653589793,
                  o is not None and o.LinkedObject is not None))
print("PLACE_DONE")
