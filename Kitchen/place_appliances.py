# -*- coding: utf-8 -*-
"""
Place kitchen appliances from the Library into Kitchen_Assembly.FCStd.

Layout (counter is an L-shape; long leg runs along -Y against wall X=0,
short leg runs along -X against wall Y=0; counter top Z=939.8, floor Z=0):

  Fridge     -> end of the long side (just past the counter end, back to wall)
  Range/Stove-> middle of the long side (back to wall, set into the run)
  Sink       -> middle of the short side (dropped into the countertop)
  Dishwasher -> end of the short side, under the counter (flush with the very end)

Each appliance's local frame: origin at back-left-bottom corner, width along
local +X, depth along local +Y (the FRONT face), height along local +Z.

Run:  freecadcmd Kitchen/place_appliances.py
"""
import os
import FreeCAD as App

V = App.Vector
R = App.Rotation
P = App.Placement

ROOT = "/home/joee/github/alieniron/home-cad"
LIB  = os.path.join(ROOT, "Library")
KIT  = os.path.join(ROOT, "Kitchen")

ROT90  = R(V(0, 0, 1), 90)    # local +Y front -> world -X  (faces long-side front)
ROT180 = R(V(0, 0, 1), 180)   # local +Y front -> world -Y  (faces short-side front)

# name -> (relative FCStd path, friendly Part label, link label, placement)
APPLIANCES = [
    ("Refrigerator", "LG_LRMXS2806S/LG_LRMXS2806S.FCStd", "Refrigerator",
        P(V(0.0,     -7867.6, 0.0),   ROT90)),
    ("Range",        "LRGL5823S/LRGL5823S.FCStd",         "Range_Stove",
        P(V(0.0,     -3859.2, 0.0),   ROT90)),
    ("Sink",         "KWT310-33/KWT310-33.FCStd",         "Sink",
        P(V(-1231.9, -25.4,   939.8), ROT180)),
    ("Dishwasher",   "WDP540HAMZ/WDP540HAMZ.FCStd",       "Dishwasher",
        P(V(-2695.6, 0.0,     0.0),   ROT180)),
]

log = open(os.path.join(ROOT, "place_report.txt"), "w")
def L(*a): log.write(" ".join(str(x) for x in a) + "\n")

# ---------------------------------------------------------------------------
# Phase 1: make each appliance linkable by wrapping its solids in an App::Part
# ---------------------------------------------------------------------------
parts = {}
for name, rel, part_label, _pl in APPLIANCES:
    fp = os.path.join(LIB, rel)
    d = App.openDocument(fp)
    existing = [o for o in d.Objects if o.TypeId == "App::Part"]
    if existing:
        part = existing[0]
        L("Phase1 %-12s reuse existing Part '%s'" % (name, part.Name))
    else:
        feats = [o for o in d.Objects if o.TypeId.startswith("Part::")]
        part = d.addObject("App::Part", "Part")
        part.Label = part_label
        for f in feats:
            part.addObject(f)
        L("Phase1 %-12s wrapped %d features in App::Part" % (name, len(feats)))
    d.recompute()
    d.save()
    parts[name] = (d, part)

# ---------------------------------------------------------------------------
# Phase 2: add links into the assembly and place them
# ---------------------------------------------------------------------------
adoc = App.openDocument(os.path.join(KIT, "Kitchen_Assembly.FCStd"))
assembly = adoc.getObject("Assembly")

for name, rel, part_label, pl in APPLIANCES:
    d, part = parts[name]
    # don't duplicate if rerun
    old = adoc.getObject(name)
    if old:
        adoc.removeObject(name)
    lk = adoc.addObject("App::Link", name)
    lk.Label = part_label
    lk.LinkedObject = part
    lk.Placement = pl
    assembly.addObject(lk)        # move into the Assembly group (like the counter/island)

adoc.recompute()
adoc.save()

# ---------------------------------------------------------------------------
# Report: global bounding boxes of the placed appliances
# ---------------------------------------------------------------------------
L("")
L("=== Placed appliance global bounding boxes ===")
for name, rel, part_label, pl in APPLIANCES:
    o = adoc.getObject(name)
    bb = o.Shape.BoundBox
    L("%-12s X[%8.1f,%8.1f] Y[%9.1f,%9.1f] Z[%7.1f,%7.1f]" % (
        name, bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))
L("")
L("Assembly.Group now: %s" % [x.Name for x in assembly.Group])
log.close()
print("DONE")
