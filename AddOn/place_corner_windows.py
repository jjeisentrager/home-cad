# -*- coding: utf-8 -*-
"""
Add two ViWinTech ThruBlack SG4836 windows to the AddOn assembly, flanking the
front-LEFT corner -- the corner diagonally opposite the sink/counter corner that
already carries WindowSink (front wall) + WindowWall (right wall).

Kitchen-native frame (same as place_livingroom.py): front/sink wall Y=0, right/
stove wall X=0, west/left wall X=-7924.8 (outer face), open wall Y=-6096 (no
framing), floor Z=0, ceiling 2438.4.  Native placements are composed with
Assembly001's placement (A1) to land in the assembly's rotated world.

The existing pair (place_windows.py):
  WindowSink  front wall (Y=0), glazing center X=-1651, ROT180 (exterior +Y)
  WindowWall  right wall (X=0), glazing center Y=-1524, ROT90  (exterior +X)

New pair, mirrored into the front-left corner:
  WindowFrontLeft  front wall (Y=0),       glazing center X=-6273.8, ROT180
  WindowWest       west wall (X=-7924.8),  glazing center Y=-1350,   ROT270
                   (exterior -X; sits between the corner and the TV, which
                    occupies the west wall Y -2152..-3504)

SG4836 local frame: width +X, height +Z, depth +Y with the EXTERIOR face at the
-Y side; glazing center sits at local X=603.25.  Base positions back out that
offset so the glazing lands on the target center.  Z=1100 matches the existing
windows (aligned heads/sills).

Run with the GUI layer up so colors + GuiDocument persist:
  flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD \
    AddOn/place_corner_windows.py
"""
import os
import FreeCAD as App
import FreeCADGui as Gui  # noqa: F401

V = App.Vector
R = App.Rotation
P = App.Placement
ROT180 = R(V(0, 0, 1), 180)
ROT270 = R(V(0, 0, 1), 270)

ROOT = "/home/joee/github/alieniron/home-cad"
LIB = os.path.join(ROOT, "Library")
ADD = os.path.join(ROOT, "AddOn")
WIN = "ViWinTech/ThruBlack/ThruBlack-Glider/SG4836/ThruBlack_SG4836.FCStd"

BLACK = (0.05, 0.05, 0.06, 1.0)     # ThruBlack vinyl
GLASS = (0.62, 0.74, 0.82, 1.0)     # glazing

# name, native placement (kitchen frame)
WINDOWS = [
    ("WindowFrontLeft", P(V(-5670.55, 0.0, 1100.0), ROT180)),
    ("WindowWest",      P(V(-7924.8, -746.75, 1100.0), ROT270)),
]

log = open(os.path.join(ROOT, "_scan/corner_win_report.txt"), "w", buffering=1)
def L(*a): log.write(" ".join(str(x) for x in a) + "\n")

def show(o, vis=True):
    o.Visibility = vis
    if o.ViewObject is not None:
        o.ViewObject.Visibility = vis

def paint(o, rgba):
    vo = o.ViewObject
    if vo is None:
        return
    vo.Transparency = 0
    vo.ShapeColor = rgba
    try:
        m = vo.ShapeAppearance[0]
        m.DiffuseColor = rgba
        vo.ShapeAppearance = [m]
    except Exception:
        pass

# --- Phase 1: wrap the SG4836 solids in an App::Part + apply colors ----------
wd = App.openDocument(os.path.join(LIB, WIN))
existing = [o for o in wd.Objects if o.TypeId == "App::Part"]
if existing:
    win_part = existing[0]
else:
    feats = [o for o in wd.Objects if o.TypeId.startswith("Part::")]
    win_part = wd.addObject("App::Part", "Part")
    win_part.Label = "ThruBlack_SG4836"
    for f in feats:
        win_part.addObject(f)
for o in wd.Objects:
    if o.TypeId.startswith("Part::"):
        paint(o, GLASS if "glass" in o.Name.lower() else BLACK)
        show(o, True)
    if o.TypeId == "App::Part":
        show(o, True)
wd.recompute()
wd.save()
L("phase1: SG4836 wrapped+colored in %s (part=%s)" % (wd.Name, win_part.Name))

# --- Phase 2: link the windows into AddOn_Assembly with A1 o native ----------
ad = App.openDocument(os.path.join(ADD, "AddOn_Assembly.FCStd"))
A1 = ad.getObject("Assembly001").Placement
assembly = ad.getObject("Assembly")

for name, pnat in WINDOWS:
    old = ad.getObject(name)
    if old:
        ad.removeObject(name)
    lk = ad.addObject("App::Link", name)
    lk.Label = name
    lk.LinkedObject = win_part
    lk.Placement = A1.multiply(pnat)
    assembly.addObject(lk)
    show(lk, True)

for o in ad.Objects:
    if o.TypeId in ("App::Link", "App::Part") or o.TypeId.startswith("Assembly::"):
        show(o, True)
ad.recompute()
ad.save()

L("")
L("=== placed window world bounding boxes ===")
for name, _ in WINDOWS:
    o = ad.getObject(name)
    bb = o.Shape.BoundBox
    L("%-16s X[%8.1f,%8.1f] Y[%9.1f,%9.1f] Z[%7.1f,%7.1f]" %
      (name, bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))
log.close()
print("CORNER_WINDOWS_DONE")
