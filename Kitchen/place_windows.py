# -*- coding: utf-8 -*-
"""
Add two ViWinTech ThruBlack windows to the kitchen assembly:

  WindowWall  SG6036 (60"x36")  -> long-leg wall (X=0), between the corner and
                                   the stove, centered in that run.
  WindowSink  SG4836 (48"x36")  -> short-leg wall (Y=0), centered above the sink.

Window local frame (thrublack_lib): width +X, height +Z, depth +Y with the
EXTERIOR face at Y=0 and the interior toward +Y.  The kitchen interior is the
-X/-Y quadrant, so:
  - short-leg wall (Y=0, outside +Y): rotate 180 deg about Z (exterior -> +Y)
  - long-leg  wall (X=0, outside +X): rotate  90 deg about Z (exterior -> +X)

Both windows: heads/sills aligned, placement Z=1100 (sill ~160 mm above the
939.8 countertop).  Centers: sink at X=-1651; long-leg run mid at Y=-1849.8.

Run with the GUI layer up so colors + GuiDocument persist:
  flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD \
    Kitchen/place_windows.py
"""
import os
import FreeCAD as App
import FreeCADGui as Gui  # noqa: F401

V = App.Vector
R = App.Rotation
P = App.Placement
ROT90 = R(V(0, 0, 1), 90)
ROT180 = R(V(0, 0, 1), 180)

ROOT = "/home/joee/github/alieniron/home-cad"
LIB = os.path.join(ROOT, "Library")
KIT = os.path.join(ROOT, "Kitchen")
WIN = "ViWinTech/ThruBlack/ThruBlack-Glider/"

BLACK = (0.05, 0.05, 0.06, 1.0)     # ThruBlack vinyl
GLASS = (0.62, 0.74, 0.82, 1.0)     # glazing

# name, rel path, App::Part label, placement
WINDOWS = [
    ("WindowWall", WIN + "SG6036/ThruBlack_SG6036.FCStd", "ThruBlack_SG6036",
        P(V(0.0, -2605.45, 1100.0), ROT90)),
    ("WindowSink", WIN + "SG4836/ThruBlack_SG4836.FCStd", "ThruBlack_SG4836",
        P(V(-1047.75, 0.0, 1100.0), ROT180)),
]

log = open(os.path.join(ROOT, "win_report.txt"), "w")
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

# --- Phase 1: wrap each window's solids in an App::Part + apply colors -------
parts = {}
for name, rel, label, _pl in WINDOWS:
    d = App.openDocument(os.path.join(LIB, rel))
    existing = [o for o in d.Objects if o.TypeId == "App::Part"]
    if existing:
        part = existing[0]
    else:
        feats = [o for o in d.Objects if o.TypeId.startswith("Part::")]
        part = d.addObject("App::Part", "Part")
        part.Label = label
        for f in feats:
            part.addObject(f)
    for o in d.Objects:
        if o.TypeId.startswith("Part::"):
            paint(o, GLASS if "glass" in o.Name.lower() else BLACK)
            show(o, True)
        if o.TypeId == "App::Part":
            show(o, True)
    d.recompute()
    d.save()
    parts[name] = (d, part)
    L("phase1 %-11s wrapped+colored in %s" % (name, d.Name))

# --- Phase 2: link the windows into the assembly and place them -------------
adoc = App.openDocument(os.path.join(KIT, "Kitchen_Assembly.FCStd"))
assembly = adoc.getObject("Assembly")
for name, rel, label, pl in WINDOWS:
    d, part = parts[name]
    if adoc.getObject(name):
        adoc.removeObject(name)
    lk = adoc.addObject("App::Link", name)
    lk.Label = label
    lk.LinkedObject = part
    lk.Placement = pl
    assembly.addObject(lk)
    show(lk, True)
for o in adoc.Objects:
    if o.TypeId in ("App::Link", "App::Part") or o.TypeId.startswith("Assembly::"):
        show(o, True)
adoc.recompute()
adoc.save()

L("")
L("=== placed window global bounding boxes ===")
for name, rel, label, pl in WINDOWS:
    o = adoc.getObject(name)
    bb = o.Shape.BoundBox
    L("%-11s X[%8.1f,%8.1f] Y[%9.1f,%9.1f] Z[%7.1f,%7.1f]" %
      (name, bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))
log.close()
print("WINDOWS_DONE")
