# -*- coding: utf-8 -*-
"""todo (windows): seat every window/door IN its framed rough opening, centered
in the wall depth, exterior face outward.

Single source of truth = the framing.  Each opening is defined in wall-build
coords (X=along wall, Y=thickness 0..88.9, Z=height); the window is placed by
the SAME transform that positions the wall in the assembly:
    win.Placement = framingLink.Placement * wall.Placement * Placement(offset)
with offset seating the component centre at (opening_x, wall_depth_centre,
opening_vertical_centre).  Window local axes (X=width, Z=height, -Y=exterior)
map 1:1 onto the wall's build axes, so exterior automatically faces out.

All 5 are rebuilt as top-level App::Links (the old WindowSink/WindowWall lived
in a different frame).  Windows use the SG4836 part; slider uses GVTS7280.
Run OFFSCREEN GUI.
"""
import os
import FreeCAD as App
try:
    import FreeCADGui as Gui  # noqa
except Exception:
    pass
V = App.Vector
R = App.Rotation
P = App.Placement
ROOT = "/home/joee/github/alieniron/home-cad"
rep = open(os.path.join(ROOT, "AddOn/_fixwin.txt"), "w", buffering=1)

d = App.openDocument(os.path.join(ROOT, "AddOn/AddOn_Assembly.FCStd"))
asm = d.getObject("Assembly")
M_fr = d.getObject("AddOnFraming001").Placement

# component Parts (reuse existing good links' targets)
sg = d.getObject("WindowFrontLeft").LinkedObject      # SG4836 Part
gv = d.getObject("Slider").LinkedObject               # GVTS7280 Part
SG_C = V(603.5, 24.0, 451.0)      # SG4836 local centre
GV_C = V(908.0, 56.5, 1048.0)     # GVTS7280 local centre

WT2 = 44.45                        # wall depth centre (3.5"/2)
WALLS = {
    "Front": P(V(0, 0, 0), R(V(0, 0, 1), 180)),
    "Right": P(V(0, -6096.0, 0), R(V(0, 0, 1), 90)),
    "Left":  P(V(-7924.8, 0, 0), R(V(0, 0, 1), 270)),
}
# name, component, wc, wall, along_x, sill, head
JOBS = [
    ("WindowSink",      sg, SG_C, "Front", 1651.0, 1018.0, 2084.0),
    ("Slider",          gv, GV_C, "Front", 4400.0,    0.0, 2110.0),
    ("WindowFrontLeft", sg, SG_C, "Front", 6273.8, 1018.0, 2084.0),
    ("WindowWall",      sg, SG_C, "Right", 4572.0, 1018.0, 2084.0),
    ("WindowWest",      sg, SG_C, "Left",  1350.0, 1018.0, 2084.0),
]

for name, comp, wc, wall, ax, sill, head in JOBS:
    vcen = (sill + head) / 2.0
    off = V(ax - wc.x, WT2 - wc.y, vcen - wc.z)
    placement = M_fr.multiply(WALLS[wall]).multiply(P(off, R()))
    old = d.getObject(name)
    if old is not None:
        d.removeObject(name)
    lk = d.addObject("App::Link", name)
    lk.Label = name
    lk.LinkedObject = comp
    lk.Placement = placement
    asm.addObject(lk)
    lk.Visibility = True
    if getattr(lk, "ViewObject", None) is not None:
        lk.ViewObject.Visibility = True

d.recompute()
d.save()

# verify
for name, comp, wc, wall, ax, sill, head in JOBS:
    o = d.getObject(name)
    b = o.Shape.BoundBox
    extn = o.Placement.Rotation.multVec(V(0, -1, 0))
    rep.write("%-16s WORLD X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f] ext->(%.2f,%.2f,%.2f)\n"
              % (name, b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax, extn.x, extn.y, extn.z))
rep.write("GuiUp=%s\n" % App.GuiUp)
rep.close()
print("FIXWIN_DONE")
