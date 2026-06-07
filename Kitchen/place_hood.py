# -*- coding: utf-8 -*-
"""
Place the VIKIO IKP02-30 range hood over the stove in the kitchen assembly.

Hood local frame (build_hood): X = width (762, 30"), Y = depth (back/wall at
Y=0, front +Y, 500.4), Z = up with the canopy filter face at Z=0; total height
950.  Mounts like the range (ROT90: back -> wall X=0, front -> room -X), width
along world Y.

Placement: centered on the relocated range (range center Y=-2828.4), back to the
long-leg wall (X=0), filter face at Z=1650 (~700 mm above the 952.4 cooktop).

Run with the GUI layer up so colors + GuiDocument persist:
  flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD \
    Kitchen/place_hood.py
"""
import os
import FreeCAD as App
import FreeCADGui as Gui  # noqa: F401

V = App.Vector
R = App.Rotation
P = App.Placement
ROT90 = R(V(0, 0, 1), 90)

ROOT = "/home/joee/github/alieniron/home-cad"
LIB = os.path.join(ROOT, "Library")
KIT = os.path.join(ROOT, "Kitchen")

STEEL = (0.741, 0.761, 0.78, 0.0)
DARK = (0.129, 0.129, 0.149, 0.0)
LIGHT = (0.86, 0.86, 0.80, 0.0)

NAME = "Hood"
REL = "VIKIO-IKP02-30/VIKIO-IKP02-30.FCStd"
LABEL = "VIKIO_IKP02_30"
PLACE = P(V(0.0, -3209.4, 1650.0), ROT90)   # back X=0, width Y[-3209.4,-2447.4]

log = open(os.path.join(ROOT, "hood_report.txt"), "w")
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

def color_for(name):
    n = name.lower()
    if "filter" in n or "control" in n:
        return DARK
    if "light" in n:
        return LIGHT
    return STEEL

# --- Phase 1: wrap hood solids in an App::Part + color ----------------------
d = App.openDocument(os.path.join(LIB, REL))
existing = [o for o in d.Objects if o.TypeId == "App::Part"]
if existing:
    part = existing[0]
else:
    feats = [o for o in d.Objects if o.TypeId.startswith("Part::")]
    part = d.addObject("App::Part", "Part")
    part.Label = LABEL
    for f in feats:
        part.addObject(f)
for o in d.Objects:
    if o.TypeId.startswith("Part::"):
        paint(o, color_for(o.Name))
        show(o, True)
    if o.TypeId == "App::Part":
        show(o, True)
d.recompute()
d.save()
L("phase1 wrapped+colored hood in", d.Name)

# --- Phase 2: link into the assembly and place ------------------------------
adoc = App.openDocument(os.path.join(KIT, "Kitchen_Assembly.FCStd"))
assembly = adoc.getObject("Assembly")
if adoc.getObject(NAME):
    adoc.removeObject(NAME)
lk = adoc.addObject("App::Link", NAME)
lk.Label = LABEL
lk.LinkedObject = part
lk.Placement = PLACE
assembly.addObject(lk)
show(lk, True)
for o in adoc.Objects:
    if o.TypeId in ("App::Link", "App::Part") or o.TypeId.startswith("Assembly::"):
        show(o, True)
adoc.recompute()
adoc.save()
bb = adoc.getObject(NAME).Shape.BoundBox
L("hood placed: X[%.1f,%.1f] Y[%.1f,%.1f] Z[%.1f,%.1f]" %
  (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))
log.close()
print("HOOD_DONE")
