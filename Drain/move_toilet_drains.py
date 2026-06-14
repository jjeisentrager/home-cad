# -*- coding: utf-8 -*-
"""
Shift the two 3" closet-bend stubs so they sit under the (already code-spaced)
toilet outlets in House. Toilets/tub do NOT move.

Drain-local X maps to House world Y:  world_y = 7925 - local_x  (from the House
Drain link matrix). Targets = the toilet outlets:
  North    stub -> world Y 6743.7  (local_x 1181.3)   was 6639  (+104.7)
  Interior stub -> world Y 6032.5  (local_x 1892.5)   was 6129  (-96.7)

Each closet bend is an Elbow link fixed by a Fixed joint (Joint032 / Joint034).
Suppress those joints so the solver leaves the elbow where we place it, then set
the elbow placement. The interior move is AWAY from its branch pipe, so extend
that branch (Straight009 / Body027.Pad087) south to keep it connected; the north
move overlaps its branch (harmless), no pipe edit.

Run OFFSCREEN so GuiDocument.xml survives:
  flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD move_toilet_drains.py
"""
import os
import FreeCAD as App

R = "/home/joee/github/alieniron/home-cad"
d = App.openDocument(os.path.join(R, "Drain/DrainAssembly.FCStd"))

def wy(local_x):
    return 7925.0 - local_x

# 1) free the two closet bends from their Fixed joints
for jn in ("Joint032", "Joint034"):
    j = d.getObject(jn)
    j.Suppressed = True

# 2) place the elbows so their stub lands under the toilet outlet
NORTH_X = 1181.3      # -> world Y 6743.7
INTER_X = 1892.5      # -> world Y 6032.5
e_n = d.getObject("Elbow010")
e_i = d.getObject("Elbow011")
dn = NORTH_X - e_n.Placement.Base.x
di = INTER_X - e_i.Placement.Base.x
pn = e_n.Placement; pn.Base.x = NORTH_X; e_n.Placement = pn
pi = e_i.Placement; pi.Base.x = INTER_X; e_i.Placement = pi

# 3) interior branch moved away from its pipe -> extend Straight009 south by |di|
s_i = d.getObject("Straight009")
ps = s_i.Placement; ps.Base.x = ps.Base.x + di; s_i.Placement = ps   # origin (south end) follows the elbow
pad = d.getObject("Pad087")
pad.Length = pad.Length + di                                          # re-reach the (fixed) stack end

d.recompute()

# offscreen save (preserve GuiDocument)
d.save()

# report new world positions
def report():
    lines = ["GuiUp=%s" % App.GuiUp,
             "north elbow dx=%.1f  new Base.x=%.1f -> stub world Y=%.1f" % (dn, e_n.Placement.Base.x, wy(e_n.Placement.Base.x)),
             "inter elbow dx=%.1f  new Base.x=%.1f -> stub world Y=%.1f" % (di, e_i.Placement.Base.x, wy(e_i.Placement.Base.x)),
             "Straight009 Base.x=%.1f (south end world Y=%.1f)  Pad087.Length=%.1f -> north end world Y=%.1f"
             % (s_i.Placement.Base.x, wy(s_i.Placement.Base.x), pad.Length, wy(s_i.Placement.Base.x) + pad.Length)]
    open(os.path.join(R, "Drain/move_report.txt"), "w").write("\n".join(lines) + "\n")
report()
print("MOVE_DONE")
