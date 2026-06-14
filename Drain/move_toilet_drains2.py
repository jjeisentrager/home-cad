# -*- coding: utf-8 -*-
"""Move the two 3" closet stubs under the toilet outlets. freecadcmd version:
avoids the assembly-wide solver (which hangs offscreen). Only Body027 is
recomputed (for the branch-pipe length); link placements & joint-suppress are
direct properties needing no solve. GuiDocument is re-injected afterward.
"""
import os
import FreeCAD as App
R = "/home/joee/github/alieniron/home-cad"
d = App.openDocument(os.path.join(R, "Drain/DrainAssembly.FCStd"))

def wy(x): return 7925.0 - x

for jn in ("Joint032", "Joint034"):
    d.getObject(jn).Suppressed = True

NORTH_X, INTER_X = 1181.3, 1892.5
e_n, e_i = d.getObject("Elbow010"), d.getObject("Elbow011")
dn = NORTH_X - e_n.Placement.Base.x
di = INTER_X - e_i.Placement.Base.x
p = e_n.Placement; p.Base.x = NORTH_X; e_n.Placement = p
p = e_i.Placement; p.Base.x = INTER_X; e_i.Placement = p

s_i = d.getObject("Straight009")
p = s_i.Placement; p.Base.x = p.Base.x + di; s_i.Placement = p
pad = d.getObject("Pad087")
pad.Length = pad.Length.Value + di

# recompute ONLY the branch-pipe body (skip the assembly solver)
App.getDocument(d.Name).getObject("Body027").recompute()

d.save()
open(os.path.join(R, "Drain/move_report.txt"), "w").write(
    "north dx=%.1f Base.x=%.1f stubY=%.1f\ninter dx=%.1f Base.x=%.1f stubY=%.1f\n"
    "Straight009 Base.x=%.1f southY=%.1f Pad087=%.1f northY=%.1f\n" % (
        dn, e_n.Placement.Base.x, wy(e_n.Placement.Base.x),
        di, e_i.Placement.Base.x, wy(e_i.Placement.Base.x),
        s_i.Placement.Base.x, wy(s_i.Placement.Base.x), pad.Length.Value,
        wy(s_i.Placement.Base.x) + pad.Length.Value))
print("MOVE2_DONE")
