# -*- coding: utf-8 -*-
"""
Create the Main electrical assembly (Main_Electrical.FCStd) and place the
kitchen-end switch + receptacle that belong on the wall which CONTINUES past
the AddOn into the Main structure, then link it into Main.FCStd.

The AddOn kitchen-counter wall (fridge/range side) aligns with MainFraming's
interior partition **V_p267** (native X[6744,6820], Y[2032,3861]).  The AddOn
opening ends at native Y~3861; V_p267 runs SOUTH from there into the house.
The fridge sits just NW of V_p267's north end, room on the WEST (-X) side, so
these devices mount on V_p267's **west face (native X=6744), facing -X**:

  - Switch  : near the far (south) end of the wall  (native Y ~ 2200)
  - Outlet  : ~halfway between the fridge end and the wall end (native Y ~ 2950)

Coordinates are MainFraming-native (same frame as V_p267 above).  The assembly
link into Main.FCStd copies MainFraming's own link placement so the devices sit
on the framing exactly.

Run OFFSCREEN GUI (GuiDocument survives so the user's file opens correctly):
  flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD Main/build_main_electrical.py
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
MAIN = os.path.join(ROOT, "Main")
log = open(os.path.join(MAIN, "main_electrical_report.txt"), "w", buffering=1)
def L(*a): log.write(" ".join(str(x) for x in a) + "\n")

OUTLET_FC = os.path.join(LIB, "Outlet-Duplex/Outlet-Duplex.FCStd")
SWITCH_FC = os.path.join(LIB, "Switch-Toggle/Switch-Toggle.FCStd")

PLATE_W2 = 34.925      # PLATE_W/2
PLATE_Z2 = 57.15       # PLATE_H/2
BOXD = 63.5            # wall-surface offset (device local Y of wall face)

# V_p267 west face (the kitchen-counter continuation wall)
WALLX = 6744.0


def show(o, vis=True):
    o.Visibility = vis
    if getattr(o, "ViewObject", None) is not None:
        o.ViewObject.Visibility = vis


def part_of(doc):
    return [o for o in doc.Objects if o.TypeId == "App::Part"][0]


# west face at X=WALLX, front faces -X (into the kitchen); plate lands at
# (WALLX, along, height).  Mirrors build_electrical.py's "east" wall helper.
def place_westface(along, height):
    return P(V(WALLX + BOXD, along - PLATE_W2, height - PLATE_Z2),
             R(V(0, 0, 1), 90))


# name, kind, along-wall (native Y), height AFF
DEVICES = [
    # switch pushed toward the far (south) end of the wall
    ("Switch_FridgeR", "switch", 2200.0, 1220.0),
    # receptacle ~halfway between the fridge end (~3861) and the wall end (2032)
    ("Outlet_FridgeB", "outlet", 2950.0, 1050.0),
]

# --- load device library parts ---
od = App.openDocument(OUTLET_FC); outlet_part = part_of(od)
sd = App.openDocument(SWITCH_FC); switch_part = part_of(sd)
L("outlet part=%s  switch part=%s" % (outlet_part.Name, switch_part.Name))

# --- build the Main electrical assembly document ---
ELEC_FC = os.path.join(MAIN, "Main_Electrical.FCStd")
ed = App.newDocument("Main_Electrical")
ed.saveAs(ELEC_FC)                      # on disk first so cross-doc links resolve
grp = ed.addObject("App::Part", "Electrical")
grp.Label = "Main_Electrical"
for name, kind, along, h in DEVICES:
    lk = ed.addObject("App::Link", name)
    lk.Label = name
    lk.LinkedObject = outlet_part if kind == "outlet" else switch_part
    lk.Placement = place_westface(along, h)
    grp.addObject(lk)
    show(lk, True)
show(grp, True)
ed.recompute()
ed.save()
L("Main_Electrical saved with %d devices" % len(DEVICES))
for o in ed.Objects:
    if o.TypeId == "App::Link":
        bb = o.Shape.BoundBox
        L("  %-15s native X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]" %
          (o.Name, bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))

# --- link the electrical assembly into Main.FCStd (align to the framing) ---
md = App.openDocument(os.path.join(MAIN, "Main.FCStd"))
assembly = md.getObject("Assembly")
mf = md.getObject("MainFraming")        # copy the framing link's placement
frame_pl = mf.Placement
old = md.getObject("Electrical")
if old:
    md.removeObject("Electrical")
elk = md.addObject("App::Link", "Electrical")
elk.Label = "Electrical"
elk.LinkedObject = grp
elk.Placement = App.Placement(frame_pl.Base, frame_pl.Rotation)
assembly.addObject(elk)
show(elk, True)
md.recompute()
md.save()
bb = elk.Shape.BoundBox
L("Electrical link in Main.FCStd  frame X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]"
  % (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))
log.close()
print("MAIN_ELECTRICAL_DONE")
