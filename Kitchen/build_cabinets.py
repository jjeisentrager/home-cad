# -*- coding: utf-8 -*-
"""
Build REAL kitchen cabinet units (base + wall) complete with doors, plus the two
diagonal corner cabinets and a countertop slab, from Kitchen/cabinet_layout.py.
Saves Kitchen_Cabinets.FCStd (App::Part "Part", label Kitchen_Cabinets) to link
into the assembly.  Kitchen-native mm frame (X=0 east/stove wall, Y=0 front/sink
wall, room toward -X/-Y).

Each box cabinet = a carcass box set back by the door thickness + face panel(s):
base cabinets get a top drawer front + door(s) below; sink base + wall cabinets
get door(s) only.  Single door up to 22" wide, double doors above.  The diagonal
corners are a pentagon carcass + one angled door on the 45 face.

Run OFFSCREEN GUI (GuiDocument + colours survive):
  flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD Kitchen/build_cabinets.py
"""
import os, sys, math
import FreeCAD as App
import Part
try:
    import FreeCADGui as Gui  # noqa: F401
except Exception:
    pass

V = App.Vector
KIT = "/home/joee/github/alieniron/home-cad/Kitchen"
sys.path.insert(0, KIT)
import cabinet_layout as L

log = open(os.path.join(KIT, "cabinets_report.txt"), "w", buffering=1)
def W(*a): log.write(" ".join(str(x) for x in a) + "\n")

DOOR_T = 18.0     # door / drawer front thickness (sits PROUD of the carcass)
REVEAL = 6.0      # gap around a face panel
GAP    = 6.0      # gap between double doors
DRAWER_H = 152.0  # base cabinet top drawer band (6")
DBL = 560.0       # width above which a door becomes a pair


def box(dx, dy, dz, x, y, z):
    return Part.makeBox(dx, dy, dz, V(x, y, z))


def face_panels(wall, amin, amax, depth, fz0, fz1, split):
    """Front panels (doors/drawer) at the cabinet face."""
    out = []
    w = amax - amin
    spans = [(amin + REVEAL, amax - REVEAL)]
    if split and w > DBL:
        mid = (amin + amax) / 2.0
        spans = [(amin + REVEAL, mid - GAP / 2.0), (mid + GAP / 2.0, amax - REVEAL)]
    for a0, a1 in spans:
        pw = a1 - a0
        if wall == "east":      # wall X=0; door sits PROUD in front of the carcass
            out.append(box(DOOR_T, pw, fz1 - fz0, -(depth + DOOR_T), a0, fz0))
        else:                   # wall Y=0
            out.append(box(pw, DOOR_T, fz1 - fz0, a0, -(depth + DOOR_T), fz0))
    return out


def cabinet(wall, a0, a1, z0, z1, depth, is_base, is_sink):
    amin, amax = sorted([a0, a1])
    solids = []
    # carcass (full depth; doors sit proud in front of it)
    if wall == "east":
        solids.append(box(depth, amax - amin, z1 - z0, -depth, amin, z0))
    else:
        solids.append(box(amax - amin, depth, z1 - z0, amin, -depth, z0))
    # face panels
    if is_base and not is_sink:
        solids += face_panels(wall, amin, amax, depth, z1 - DRAWER_H + REVEAL, z1 - REVEAL, split=False)
        solids += face_panels(wall, amin, amax, depth, z0 + REVEAL, z1 - DRAWER_H - REVEAL, split=True)
    else:
        solids += face_panels(wall, amin, amax, depth, z0 + REVEAL, z1 - REVEAL, split=True)
    return solids


def diagonal(leg, sd, z0, z1):
    """Pentagon carcass + one door on the 45 diagonal face."""
    pts = [V(0, 0, z0), V(0, -leg, z0), V(-sd, -leg, z0), V(-leg, -sd, z0), V(-leg, 0, z0)]
    carc = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, 0, z1 - z0))
    face_len = (leg - sd) * math.sqrt(2.0)
    mid = V(-(sd + leg) / 2.0, -(leg + sd) / 2.0, z0)
    nrm = V(-1 / math.sqrt(2.0), -1 / math.sqrt(2.0), 0)   # into the room
    dw = face_len - 2 * REVEAL
    door = box(dw, DOOR_T, (z1 - z0) - 2 * REVEAL, -dw / 2.0, -DOOR_T / 2.0, REVEAL)
    c = mid.add(nrm.multiply(DOOR_T))          # sit the door proud of the 45 face
    door.Placement = App.Placement(c, App.Rotation(V(0, 0, 1), 135))
    return [carc, door]


doc = App.newDocument("Kitchen_Cabinets")
feats = []


def add(name, solids, color):
    o = doc.addObject("Part::Feature", name)
    o.Shape = solids[0] if len(solids) == 1 else Part.makeCompound(solids)
    o.Label = name
    feats.append((o, color))
    return o


WHITE = (0.93, 0.93, 0.93)
DARK = (0.12, 0.12, 0.14)

# ---- base cabinets (runs beyond the corner) ----
# the two corner-flanking cabinets get full-height doors (no drawer), matching
# the corner cabinet, so the whole corner cluster is drawer-free.
NO_DRAWER = {"B-F-21", "B-E-36"}
for cid, lbl, wall, a0, a1 in L.BASE:
    doors_only = ("sink" in cid) or (cid in NO_DRAWER)
    add(cid, cabinet(wall, a0, a1, L.BASE_Z0, L.BASE_Z1, L.BASE_D, True, doors_only), WHITE)

# ---- corner base cabinet: 24" square carcass, an equal-width door on BOTH walls
# (symmetric -- a cabinet face on the front wall AND the stove wall) ----
cw = L.CNR_BASE
z0b, z1b, dzb = L.BASE_Z0, L.BASE_Z1, L.BASE_Z1 - L.BASE_Z0
carc = box(cw, cw, dzb, -cw, -cw, z0b)
dF = box(cw - 2 * REVEAL, DOOR_T, dzb - 2 * REVEAL, -cw + REVEAL, -(cw + DOOR_T), z0b + REVEAL)
dE = box(DOOR_T, cw - 2 * REVEAL, dzb - 2 * REVEAL, -(cw + DOOR_T), -cw + REVEAL, z0b + REVEAL)
add("B-Cnr", [carc, dF, dE], WHITE)

# ---- wall cabinets ----
for cid, lbl, wall, a0, a1 in L.UPPER:
    add(cid, cabinet(wall, a0, a1, L.UP_Z0, L.UP_Z1, L.UP_D, False, False), WHITE)
# wall diagonal corner
add("U-CNR", diagonal(L.UP_LEG, L.UP_D, L.UP_Z0, L.UP_Z1), WHITE)
# over-fridge
for cid, lbl, wall, a0, a1 in L.OVERFRIDGE:
    add(cid, cabinet(wall, a0, a1, L.OF_Z0, L.OF_Z1, L.OF_D, False, False), WHITE)

# ---- countertop slab, with a hole cut over the sink so the bowl shows through ----
# Sink footprint (kitchen-native) X[-2070,-1232] Y[-584,-25]; inset ~40 mm for the
# rim ledge, cut clear through the 64 mm top.
sink_hole = box(758.0, 479.0, L.CT_Z1 - L.CT_Z0 + 12.0, -2030.0, -544.0, L.CT_Z0 - 6.0)
ct = []
for wall, a0, a1 in L.COUNTER:
    amin, amax = sorted([a0, a1])
    if wall == "east":
        seg = box(L.CT_D, amax - amin, L.CT_Z1 - L.CT_Z0, -L.CT_D, amin, L.CT_Z0)
    else:
        seg = box(amax - amin, L.CT_D, L.CT_Z1 - L.CT_Z0, amin, -L.CT_D, L.CT_Z0)
        seg = seg.cut(sink_hole)          # front segment holds the sink
    ct.append(seg)
add("Countertop", [Part.makeCompound(ct)], DARK)

# ---- wrap + colour + save ----
part = doc.addObject("App::Part", "Part")
part.Label = "Kitchen_Cabinets"
for o, col in feats:
    part.addObject(o)
    o.Visibility = True
    if getattr(o, "ViewObject", None) is not None:
        o.ViewObject.Visibility = True
        o.ViewObject.ShapeColor = col
part.Visibility = True
doc.recompute()
doc.saveAs(os.path.join(KIT, "Kitchen_Cabinets.FCStd"))

W("Kitchen_Cabinets saved with %d features" % len(feats))
for o, col in feats:
    b = o.Shape.BoundBox
    W("  %-10s X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]" %
      (o.Name, b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))
Part.export([o for o, _ in feats], os.path.join(KIT, "Kitchen_Cabinets.step"))
doc.save()
log.close()
print("CABINETS_DONE")
