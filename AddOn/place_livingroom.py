# -*- coding: utf-8 -*-
"""
Furnish the AddOn living area + add the open-wall beam line in AddOn_Assembly.

Everything is positioned in the KITCHEN-NATIVE frame (sink wall Y=0, stove wall
X=0, opposite-stove/west wall X=-7836, open wall Y=-6007, floor Z=0, ceiling
2438.4) and brought into the assembly's rotated world by composing with
Assembly001's placement (A1) -- the same transform the kitchen uses.

Adds:
  Slider  - ViWinTech ThruBlack GVTS7280 traditional sliding door, on the sink
            wall (Y=0) just west of the sink counter.
  TV      - 60" panel on the west wall (X=-7836), opposite the stove.
  Couch   - Edenfield sectional in front of the TV (faces -X), leaving a ~1.4 m
            passage to the slider between the couch and the island.
  Beams   - flush I-beam + 3 6x6 posts on the open wall (built in AddOn_Beams).

Run with the GUI layer up so colors + GuiDocument persist:
  flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD \
    AddOn/place_livingroom.py
"""
import os
import FreeCAD as App
import FreeCADGui as Gui  # noqa: F401

V = App.Vector
R = App.Rotation
P = App.Placement
ROOT = "/home/joee/github/alieniron/home-cad"
LIB = os.path.join(ROOT, "Library")
KIT = os.path.join(ROOT, "Kitchen")  # noqa
ADD = os.path.join(ROOT, "AddOn")
log = open(os.path.join(ROOT, "lr_report.txt"), "w")
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
        m = vo.ShapeAppearance[0]; m.DiffuseColor = rgba; vo.ShapeAppearance = [m]
    except Exception:
        pass

def wrap(doc, label):
    parts = [o for o in doc.Objects if o.TypeId == "App::Part"]
    if parts:
        return parts[0]
    feats = [o for o in doc.Objects if o.TypeId.startswith("Part::")]
    part = doc.addObject("App::Part", "Part"); part.Label = label
    for f in feats:
        part.addObject(f)
    return part

BLACK = (0.05, 0.05, 0.06, 1.0)
SCREEN = (0.12, 0.13, 0.15, 1.0)
STEEL = (0.40, 0.41, 0.43, 1.0)
WOOD = (0.62, 0.52, 0.35, 1.0)
FABRIC = (0.56, 0.53, 0.49, 1.0)
LEGDK = (0.20, 0.16, 0.12, 1.0)

DOOR_FC = os.path.join(LIB, "ViWinTech/ThruBlack/ThruBlack-TraditionalSliding/"
                       "GVTS7280/ThruBlack_GVTS7280.FCStd")
SOFA_FC = os.path.join(LIB, "Edenfield-29004S1/Edenfield-29004S1.FCStd")
TV_FC = os.path.join(LIB, "TV-60in/TV-60in.FCStd")
BEAM_FC = os.path.join(ADD, "AddOn_Beams.FCStd")

# --- Phase 1: prepare each linked file (wrap App::Part, colors, save) -------
dd = App.openDocument(DOOR_FC)
door_part = wrap(dd, "GVTS7280")
for o in dd.Objects:
    if o.TypeId.startswith("Part::") or o.TypeId == "App::Part":
        show(o, True)
dd.recompute(); dd.save()

sd = App.openDocument(SOFA_FC)
sofa_part = wrap(sd, "Edenfield_Sofa")
for o in sd.Objects:
    if o.TypeId.startswith("Part::"):
        paint(o, LEGDK if o.Name.lower().startswith("leg") else FABRIC)
        show(o, True)
    if o.TypeId == "App::Part":
        show(o, True)
sd.recompute(); sd.save()

td = App.openDocument(TV_FC)
tv_part = wrap(td, "TV_60in")
for o in td.Objects:
    if o.TypeId.startswith("Part::"):
        paint(o, SCREEN if o.Name.lower().startswith("screen") else BLACK)
        show(o, True)
    if o.TypeId == "App::Part":
        show(o, True)
td.recompute(); td.save()

bd = App.openDocument(BEAM_FC)
beam_part = wrap(bd, "Beams")
for o in bd.Objects:
    if o.TypeId.startswith("Part::"):
        paint(o, WOOD if o.Name.lower().startswith("post") else STEEL)
        show(o, True)
    if o.TypeId == "App::Part":
        show(o, True)
bd.recompute(); bd.save()
L("phase1 done: parts wrapped + colored")

# --- Phase 2: link into AddOn_Assembly with A1 o native --------------------
ad = App.openDocument(os.path.join(ADD, "AddOn_Assembly.FCStd"))
A1 = ad.getObject("Assembly001").Placement
assembly = ad.getObject("Assembly")

# native placements (in the kitchen frame)
ITEMS = [
    ("Slider", door_part, P(V(-3692.0, 0.0, 0.0), R(V(0, 0, 1), 180))),
    ("TV_60in", tv_part, P(V(-7747.0, -2152.4, 914.0), R(V(0, 0, 1), -90))),
    ("Couch", sofa_part, P(V(-4535.0, -4593.5, 0.0), R(V(0, 0, 1), 90))),
    ("Beams", beam_part, P(V(0, 0, 0), R())),
]
for name, part, pnat in ITEMS:
    old = ad.getObject(name)
    if old:
        ad.removeObject(name)
    lk = ad.addObject("App::Link", name)
    lk.Label = name
    lk.LinkedObject = part
    lk.Placement = A1.multiply(pnat)
    assembly.addObject(lk)
    show(lk, True)
for o in ad.Objects:
    if o.TypeId in ("App::Link", "App::Part") or o.TypeId.startswith("Assembly::"):
        show(o, True)
ad.recompute(); ad.save()

L("placed: %s" % [i[0] for i in ITEMS])
for name, _, _ in ITEMS:
    o = ad.getObject(name)
    bb = o.Shape.BoundBox
    L("  %-9s world X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]" %
      (name, bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))
log.close()
print("LR_DONE")
