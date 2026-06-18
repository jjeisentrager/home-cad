# -*- coding: utf-8 -*-
"""
Create the AddOn electrical assembly (AddOn_Electrical.FCStd) and place duplex
receptacles + toggle switches around the AddOn room per NEC 210.52 spacing, then
link the whole electrical assembly into AddOn_Assembly so it lands in the room.

Kitchen-native room frame (same as place_livingroom.py):
  east/counter wall  X=0          west/TV wall  X=-7836
  front/sink+slider  Y=0          open wall     Y=-6007 (open to house)
  floor Z=0, ceiling 2438.4.  Native -> AddOn world via Assembly001 placement A1.

Device local frame (Outlet-Duplex / Switch-Toggle): X=width, +Y=front (out of
wall), Z=up; finished wall surface at local Y=63.5, plate centre at local
(34.925, 63.5, 57.15).  The wall helpers seat the wall-surface on the wall face,
point the front into the room, and centre the plate at (along-wall, height).

Heights AFF (= native Z): wall receptacle 300, countertop GFCI 1050, switch 1220.

Run OFFSCREEN GUI (colors + GuiDocument survive):
  flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD AddOn/build_electrical.py
"""
import os
import FreeCAD as App
try:
    import FreeCADGui as Gui  # noqa: F401
except Exception:
    pass

V = App.Vector
R = App.Rotation
P = App.Placement
ROOT = "/home/joee/github/alieniron/home-cad"
LIB = os.path.join(ROOT, "Library")
ADD = os.path.join(ROOT, "AddOn")
log = open(os.path.join(ROOT, "AddOn/electrical_report.txt"), "w", buffering=1)
def L(*a): log.write(" ".join(str(x) for x in a) + "\n")

OUTLET_FC = os.path.join(LIB, "Outlet-Duplex/Outlet-Duplex.FCStd")
SWITCH_FC = os.path.join(LIB, "Switch-Toggle/Switch-Toggle.FCStd")

PLATE_W2 = 34.925      # PLATE_W/2
PLATE_Z2 = 57.15       # PLATE_H/2
BOXD = 63.5            # wall-surface offset (device local Y of wall face)

WEST_X = -7836.0       # west interior wall face


def show(o, vis=True):
    o.Visibility = vis
    if getattr(o, "ViewObject", None) is not None:
        o.ViewObject.Visibility = vis


def part_of(doc):
    ps = [o for o in doc.Objects if o.TypeId == "App::Part"]
    return ps[0]


# wall -> (base vector, rotation) so the plate centre lands at (along, height)
def place(wall, along, height):
    if wall == "east":     # X=0, front faces -X (into room)
        return P(V(BOXD, along - PLATE_W2, height - PLATE_Z2), R(V(0, 0, 1), 90))
    if wall == "west":     # X=WEST_X, front faces +X
        return P(V(WEST_X - BOXD, along + PLATE_W2, height - PLATE_Z2),
                 R(V(0, 0, 1), -90))
    if wall == "front":    # Y=0, front faces -Y
        return P(V(along + PLATE_W2, BOXD, height - PLATE_Z2), R(V(0, 0, 1), 180))
    raise ValueError(wall)


# name, kind, wall, along-wall position (native), height AFF
DEVICES = [
    # EAST wall = kitchen counter long side -> countertop GFCI + far general
    ("Outlet_E1", "outlet", "east",  -600.0, 1050.0),
    ("Outlet_E2", "outlet", "east", -1900.0, 1050.0),
    ("Outlet_E3", "outlet", "east", -3100.0, 1050.0),
    ("Outlet_E4", "outlet", "east", -5400.0,  300.0),
    # FRONT wall = sink + slider: one countertop GFCI by sink, switch by slider
    ("Outlet_F1", "outlet", "front", -700.0, 1050.0),
    ("Switch_Slider", "switch", "front", -2650.0, 1220.0),
    # WEST wall = living area (TV at Y -2152..-3504): general receptacles
    ("Outlet_W1", "outlet", "west",  -700.0,  300.0),
    ("Outlet_W2", "outlet", "west", -2828.0,  300.0),
    ("Outlet_W3", "outlet", "west", -5300.0,  300.0),
    ("Switch_Passage", "switch", "west", -5600.0, 1220.0),
]

# --- load device library parts ---
od = App.openDocument(OUTLET_FC); outlet_part = part_of(od)
sd = App.openDocument(SWITCH_FC); switch_part = part_of(sd)
L("outlet part=%s  switch part=%s" % (outlet_part.Name, switch_part.Name))

# --- build the electrical assembly document ---
# Save the (empty) owner doc to disk FIRST so cross-document App::Links resolve.
ELEC_FC = os.path.join(ADD, "AddOn_Electrical.FCStd")
ed = App.newDocument("AddOn_Electrical")
ed.saveAs(ELEC_FC)
grp = ed.addObject("App::Part", "Electrical")
grp.Label = "AddOn_Electrical"
for name, kind, wall, along, h in DEVICES:
    lk = ed.addObject("App::Link", name)
    lk.Label = name
    lk.LinkedObject = outlet_part if kind == "outlet" else switch_part
    lk.Placement = place(wall, along, h)
    grp.addObject(lk)
    show(lk, True)
show(grp, True)
ed.recompute()
ed.save()
L("AddOn_Electrical saved with %d devices" % len(DEVICES))
for o in ed.Objects:
    if o.TypeId == "App::Link":
        bb = o.Shape.BoundBox
        L("  %-15s native X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]" %
          (o.Name, bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))

# --- link the electrical assembly into AddOn_Assembly (place in the room) ---
ad = App.openDocument(os.path.join(ADD, "AddOn_Assembly.FCStd"))
A1 = ad.getObject("Assembly001").Placement
assembly = ad.getObject("Assembly")
old = ad.getObject("Electrical")
if old:
    ad.removeObject("Electrical")
elk = ad.addObject("App::Link", "Electrical")
elk.Label = "Electrical"
elk.LinkedObject = grp
elk.Placement = A1
assembly.addObject(elk)
show(elk, True)
ad.recompute()
ad.save()
bb = elk.Shape.BoundBox
L("")
L("Electrical link in AddOn_Assembly  world X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]"
  % (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))
log.close()
print("ELECTRICAL_DONE")
