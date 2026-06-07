# -*- coding: utf-8 -*-
"""
Build the L-counter base cabinets as APPEARANCE-ONLY casework: each cabinet is a
recessed carcass + toe kick + slab door / drawer fronts (separated by reveal
gaps) + dark bar pulls.  No moving parts -- it just reads as cabinets & drawers.

Also moves the dishwasher next to the sink base and opens its bay there, putting
a base cabinet back at the short-leg end.

Reference frame (counter-local == world): long leg runs -Y along wall X=0, front
faces -X; short leg runs -X along wall Y=0, front faces -Y; both 609.6 deep (24");
cabinet box top Z=914.4 (36"); countertop slab 914.4..939.8 (untouched).

Front detailing: panels are 19 mm slabs flush with the nominal front (-609.6),
the carcass behind them is recessed 19 mm so the 4 mm reveal gaps read as shadow
lines; pulls stand 14 mm proud and are dark.

Run with the GUI layer up so colors + GuiDocument persist:
  flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD \
    Kitchen/make_base_cabinets.py
"""
import os
import FreeCAD as App
import FreeCADGui as Gui  # noqa: F401
import Part

ROOT = "/home/joee/github/alieniron/home-cad"
KIT = os.path.join(ROOT, "Kitchen")
V = App.Vector

DEPTH = 609.6        # 24"
FRONT = -DEPTH       # nominal front plane (-609.6)
T = 19.0             # panel slab thickness
CARC = FRONT + T     # carcass front (recessed) = -590.6
TOP_Z = 914.4        # cabinet box top
TK_H = 101.6         # toe kick height
TK_SET = 76.2        # toe kick set-back
G = 4.0              # reveal gap
PP = 14.0            # pull proud depth
PT = 16.0            # pull bar cross-section
WHITE = (1.0, 1.0, 1.0, 1.0)
DARK = (0.13, 0.13, 0.14, 1.0)

log = open(os.path.join(ROOT, "cab_report.txt"), "w")
def L(*a): log.write(" ".join(str(x) for x in a) + "\n")

def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))

def show(o, vis=True):
    o.Visibility = vis
    if o.ViewObject is not None:
        o.ViewObject.Visibility = vis

def paint(o, rgba):
    vo = o.ViewObject
    vo.Transparency = 0
    vo.ShapeColor = rgba
    try:
        m = vo.ShapeAppearance[0]
        m.DiffuseColor = rgba
        vo.ShapeAppearance = [m]
    except Exception as e:
        L("paint err", o.Name, e)

# --- front-face panel + pull generation ------------------------------------
# orientation 'long': width axis = Y, front axis = X.
# orientation 'short': width axis = X, front axis = Y.
# config = list of bands top->bottom; band = (kind, cols, h)
#   kind 'drawer'|'door'; h = number(mm) | 'fill' | 'eq'
def face(orient, w0, w1, config):
    """Return (panel_solids[], pull_solids[]) for a cabinet front."""
    panels, pulls = [], []
    z0, z1 = TK_H, TOP_Z
    H = z1 - z0
    fixed = sum(b[2] for b in config if isinstance(b[2], (int, float)))
    nshare = sum(1 for b in config if b[2] in ("fill", "eq"))
    avail = H - 2 * G - (len(config) - 1) * G - fixed
    share = avail / nshare if nshare else 0.0

    def W(wa, wb, zb, zt):           # width-span panel/box at given Z band
        if orient == "long":
            return box(FRONT, CARC, wa, wb, zb, zt)
        return box(wa, wb, FRONT, CARC, zb, zt)

    def hpull(wa, wb, zc):           # horizontal pull (drawer), along width axis
        plen = min((wb - wa) * 0.5, 220.0)
        pc = (wa + wb) / 2.0
        a, b = pc - plen / 2, pc + plen / 2
        if orient == "long":
            return box(FRONT - PP, FRONT, a, b, zc - PT / 2, zc + PT / 2)
        return box(a, b, FRONT - PP, FRONT, zc - PT / 2, zc + PT / 2)

    def vpull(wc, zb, zt):           # vertical pull (door), along Z
        if orient == "long":
            return box(FRONT - PP, FRONT, wc - PT / 2, wc + PT / 2, zb, zt)
        return box(wc - PT / 2, wc + PT / 2, FRONT - PP, FRONT, zb, zt)

    ztop = z1 - G
    for kind, cols, h in config:
        bh = h if isinstance(h, (int, float)) else share
        zb, zt = ztop - bh, ztop
        Wt = w1 - w0
        pw = (Wt - 2 * G - (cols - 1) * G) / cols
        for c in range(cols):
            wa = w0 + G + c * (pw + G)
            wb = wa + pw
            panels.append(W(wa, wb, zb + G / 2, zt - G / 2))
            if kind == "drawer":
                pulls.append(hpull(wa, wb, zt - 38))
            else:  # door: vertical pull near the inner edge
                if cols > 1 and c == 0:
                    wc = wb - 45
                elif cols > 1 and c == cols - 1:
                    wc = wa + 45
                else:
                    wc = wb - 45
                pulls.append(vpull(wc, zb + 60, zt - 30))
        ztop = zb - G
    return panels, pulls

def carcass(orient, w0, w1, sink_shaft=False):
    if orient == "long":
        c = box(CARC, 0.0, w0, w1, TK_H, TOP_Z)
        p = box(CARC + (TK_SET - T), 0.0, w0, w1, 0.0, TK_H)  # toe kick
    else:
        c = box(w0, w1, CARC, 0.0, TK_H, TOP_Z)
        p = box(w0, w1, CARC + (TK_SET - T), 0.0, 0.0, TK_H)
    body = c.fuse(p)
    if sink_shaft:
        shaft = box(-2060.7, -1241.3, -524.0, -85.6, 705.0, TOP_Z + 1)
        body = body.cut(shaft)
    return body

def corner_unit():
    c = box(CARC, 0.0, CARC, 0.0, TK_H, TOP_Z)
    p = box(CARC + (TK_SET - T), 0.0, CARC + (TK_SET - T), 0.0, 0.0, TK_H)
    body = c.fuse(p)
    panels, pulls = [], []
    # door on the -X face (long-leg facing)
    pn, pu = face("long", FRONT + G, -G, [("door", 1, "fill")])
    panels += pn; pulls += pu
    # door on the -Y face (short-leg facing)
    pn, pu = face("short", FRONT + G, -G, [("door", 1, "fill")])
    panels += pn; pulls += pu
    body = body.fuse(panels)
    return body, pulls

# config presets
DD = [("drawer", 2, 180), ("door", 2, "fill")]   # 2 drawers / 2 doors
D2 = [("drawer", 1, 180), ("door", 2, "fill")]   # 1 drawer / 2 doors
D1 = [("drawer", 1, 180), ("door", 1, "fill")]   # 1 drawer / 1 door
DR3 = [("drawer", 1, "eq"), ("drawer", 1, "eq"), ("drawer", 1, "eq")]  # 3 drawers

# (name, orient, w0, w1, config, sink_shaft)
CABS = [
    # long leg (front -X): w0/w1 are Y (w0 = min/far-from-corner, w1 = max).
    # Layout: corner | L1 L2 | range | L3 L4 L5 | fridge | L6 L7 | wall.
    # (stove pulled 1 cab toward the corner; fridge pushed 1 cab toward the end)
    ("Cab_L1", "long", -1524.0, -609.6, DD, False),
    ("Cab_L2", "long", -2438.4, -1524.0, DD, False),
    # range gap Y[-3218.4,-2438.4]  (2 cabinets corner<->stove)
    ("Cab_L3", "long", -4132.8, -3218.4, DD, False),   # 3 cabinets stove<->fridge
    ("Cab_L4", "long", -5047.2, -4132.8, DD, False),
    ("Cab_L5", "long", -5809.2, -5047.2, D2, False),
    # fridge gap Y[-6729.2,-5809.2]  (2 cabinets fridge<->wall)
    ("Cab_L6", "long", -7298.4, -6729.2, D1, False),
    ("Cab_L7", "long", -7867.6, -7298.4, D1, False),
    # short leg (front -Y): w0/w1 are X.  DW now sits next to the sink base:
    #   Cab_S1 | SinkBase | DW gap | Cab_S_end
    ("Cab_S1",    "short", -1193.8, -609.6, D1, False),
    ("SinkBase",  "short", -2108.2, -1193.8, D2, True),
    ("Cab_S_end", "short", -3302.0, -2714.6, D1, False),
]

cd = App.openDocument(os.path.join(KIT, "Kitchen_Counter.FCStd"))
part = cd.getObject("Part")

# remove anything from previous runs
for o in list(cd.Objects):
    if o.Name.startswith("Cab_") or o.Name in ("SinkBase", "SinkBase_Pulls"):
        cd.removeObject(o.Name)

made = []   # (feature_name, rgba)

# corner
cbody, cpulls = corner_unit()
f = cd.addObject("Part::Feature", "Cab_Corner"); f.Label = "Cab_Corner"
f.Shape = cbody; part.addObject(f); made.append(("Cab_Corner", WHITE))
if cpulls:
    pf = cd.addObject("Part::Feature", "Cab_Corner_Pulls"); pf.Label = "Cab_Corner_Pulls"
    pf.Shape = Part.makeCompound(cpulls); part.addObject(pf)
    made.append(("Cab_Corner_Pulls", DARK))

for name, orient, w0, w1, cfg, sink in CABS:
    body = carcass(orient, w0, w1, sink)
    panels, pulls = face(orient, w0, w1, cfg)
    body = body.fuse(panels)
    f = cd.addObject("Part::Feature", name); f.Label = name
    f.Shape = body; part.addObject(f); made.append((name, WHITE))
    if pulls:
        pf = cd.addObject("Part::Feature", name + "_Pulls"); pf.Label = name + "_Pulls"
        pf.Shape = Part.makeCompound(pulls); part.addObject(pf)
        made.append((name + "_Pulls", DARK))

cd.recompute()
for name, rgba in made:
    o = cd.getObject(name)
    paint(o, rgba)
    show(o, True)

# countertop: rebuild the black slab from the clean L-pad (Body001) every run so
# this stays idempotent -- extend over the relocated end cabinets and cut the
# sink hole, the (relocated) stove slot, and a full gap for the (relocated) fridge.
top = cd.getObject("CounterTop_Cut")
slab = cd.getObject("Body001").Shape.copy()
slab = slab.fuse(box(-660.4, 0.0, -7918.4, -7010.4, 914.4, 939.8))  # end extension
sink_hole = box(-2060.7, -1241.3, -524.0, -85.6, 913.0, 941.0)
stove_slot = box(-665.0, 5.0, -3218.4, -2438.4, 913.0, 941.0)        # range gap
fridge_gap = box(-700.0, 5.0, -6729.2, -5809.2, 913.0, 941.0)        # fridge gap
top.Shape = slab.cut(Part.makeCompound([sink_hole, stove_slot, fridge_gap]))
top.recompute()
paint(top, (0.0, 0.0, 0.0, 1.0))   # keep it black
show(top, True)
L("countertop bbox now:", top.Shape.BoundBox, "solids=", len(top.Shape.Solids))

# hide the old solid base; keep the black countertop + island
for nm in ("Body", "Pad", "CounterBase_Cut"):
    if cd.getObject(nm):
        show(cd.getObject(nm), False)
for nm in ("CounterTop_Cut", "Part", "Part001",
           "Body002", "Pad003", "Body003", "Pad004"):
    if cd.getObject(nm):
        show(cd.getObject(nm), True)
cd.recompute()
cd.save()
L("features:", [m[0] for m in made])

# --- assembly: move the dishwasher next to the sink, refresh links ----------
ad = App.openDocument(os.path.join(KIT, "Kitchen_Assembly.FCStd"))
dw = ad.getObject("Dishwasher")
if dw:
    pl = dw.Placement
    pl.Base = V(-2108.2, 0.0, 0.0)   # max-X edge against the sink base
    dw.Placement = pl
    L("dishwasher moved to origin X=-2108.2")
rg = ad.getObject("Range")
if rg:
    pl = rg.Placement
    pl.Base = V(0.0, -3207.8, 0.0)   # pulled 1 cabinet toward the corner
    rg.Placement = pl
    L("range moved to origin Y=-3207.8")
fr = ad.getObject("Refrigerator")
if fr:
    pl = fr.Placement
    pl.Base = V(0.0, -6723.2, 0.0)   # pushed 1 cabinet toward the end
    fr.Placement = pl
    L("fridge moved to origin Y=-6723.2")
for o in ad.Objects:
    if o.TypeId in ("App::Link", "App::Part") or o.TypeId.startswith("Assembly::"):
        show(o, True)
    if o.TypeId == "App::Link":
        o.touch()
ad.recompute()
ad.save()
log.close()
print("CABINETS_DONE")
