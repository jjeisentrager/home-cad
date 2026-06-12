# -*- coding: utf-8 -*-
"""
Build a simplified CAD model of the:
  American Standard Champion 4  (767AA001.020)
  White Elongated *Chair Height* 12-in Rough-In 1.6 GPF Soft-Close 2-piece Toilet

Representative china only - no flush internals.  Captures:
  - Two-piece form: separate tank + bowl
  - Elongated bowl, chair/comfort-height rim (16.5") and ~17" seat top
  - Closed seat + lid, side flush lever
  - Correct overall envelope  30-7/8"H x 29-3/16"D x 19"W, 12" rough-in

Local frame (component convention):  X = width, Y = depth with the FRONT of the
bowl at +Y, Z = up; origin back-left-bottom.  The tank back sits at Y=0 (the
finished wall); the closet outlet centre is ROUGH = 12" forward of that wall.

All porcelain is white; the lever is chrome (set by name in color_save.py /
render_sw.py).  Loose Part::Features wrapped in an App::Part "Part" so the model
links like the other Library components.

Run (saves a proper GuiDocument via the offscreen Qt platform):
  flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD build_toilet.py
Units: millimetres.
"""
import os
import FreeCAD as App
import Part
import Mesh

V = App.Vector
IN = 25.4

# --- Overall dimensions (American Standard 767AA001.020 spec sheet) ----------
W = 19.0 * IN          # overall width            = 482.6
DEPTH = 29.1875 * IN   # overall depth (29-3/16") = 741.4
HT = 30.875 * IN       # overall height (30-7/8") = 784.2
RIM = 16.5 * IN        # bowl rim height          = 419.1
ROUGH = 12.0 * IN      # rough-in (outlet c/l from wall) = 304.8 (documented, not cut)

CX = W / 2.0
DOC = "AS-Champion4"
OUT = os.path.dirname(os.path.abspath(__file__))

doc = App.newDocument(DOC)


def box(l, w, h, x, y, z):
    return Part.makeBox(l, w, h, V(x, y, z))


def _vert_edges(shp):
    out = []
    for e in shp.Edges:
        p, q = e.Vertexes[0].Point, e.Vertexes[-1].Point
        if abs(p.x - q.x) < 1e-6 and abs(p.y - q.y) < 1e-6 and abs(p.z - q.z) > 1e-6:
            out.append((e, p.y))
    return out


def fillet_vertical(shp, r):
    """Round all vertical (Z-parallel) edges to give the china its soft form."""
    edges = [e for e, _ in _vert_edges(shp)]
    if not edges:
        return shp
    try:
        return shp.makeFillet(r, edges)
    except Exception:
        return shp


def fillet_front(shp, r):
    """Round only the FRONT vertical edges (max-Y) -> elongated nose, square
    back so the bowl meets the tank with no gap."""
    ve = _vert_edges(shp)
    if not ve:
        return shp
    ymax = max(y for _, y in ve)
    edges = [e for e, y in ve if abs(y - ymax) < 1.0]
    if not edges:
        return shp
    try:
        return shp.makeFillet(r, edges)
    except Exception:
        return shp


def add(name, shp):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shp
    return o


# --- Tank (rear piece, against the wall at Y=0) -----------------------------
tank_d = 8.0 * IN                      # front-to-back = 203.2
tank_body = fillet_vertical(
    box(W, tank_d, (HT - IN) - 14.0 * IN, 0, 0, 14.0 * IN), 25.0)
tank_o = add("Tank", tank_body)
# Lid overhangs front/back only (keeps overall width = 19")
tank_lid = fillet_vertical(box(W, tank_d + 12.0, IN, 0, -6.0, HT - IN), 28.0)
tanklid_o = add("TankLid", tank_lid)

# --- Bowl (front piece): rim slab + tapered pedestal, basin hollowed ---------
bowl_w = 14.5 * IN                     # 368.3 outer rim width
bx0 = CX - bowl_w / 2.0                # 57.15
by0 = 150.0                            # square back tucks under the tank front
by1 = DEPTH                            # 741.4 (bowl front)

rim_z0 = RIM - 3.0 * IN                # 342.9
rim = fillet_front(box(bowl_w, by1 - by0, RIM - rim_z0, bx0, by0, rim_z0), 150.0)

ped_w = 9.0 * IN                       # 228.6 narrow foot
ped = fillet_vertical(
    box(ped_w, 12.0 * IN, rim_z0, CX - ped_w / 2.0, by0 + 76.0, 0.0), 90.0)

bowl = rim.fuse(ped)

# Basin recess (hollow the top of the bowl)
cav_w = 11.0 * IN                      # 279.4
cav = fillet_vertical(
    box(cav_w, (by1 - 30.0) - (by0 + 50.0), (RIM + 10.0) - 190.0,
        CX - cav_w / 2.0, by0 + 50.0, 190.0), 100.0)
bowl = bowl.cut(cav)
bowl_o = add("Bowl", bowl)

# --- Seat + closed lid (chair height: seat top ~17") ------------------------
seat_out = fillet_front(box(bowl_w, by1 - by0, 0.5 * IN, bx0, by0, RIM), 150.0)
seat_hole = fillet_vertical(
    box(cav_w, (by1 - 30.0) - (by0 + 80.0), IN, CX - cav_w / 2.0, by0 + 80.0, RIM - 5.0),
    100.0)
seat_o = add("Seat", seat_out.cut(seat_hole))
lid = fillet_front(box(bowl_w, by1 - by0, 0.5 * IN, bx0, by0, RIM + 0.5 * IN), 150.0)
lid_o = add("SeatLid", lid)

# --- Flush lever (chrome) on the front-left of the tank ---------------------
lever = box(2.0 * IN, 1.2 * IN, 0.8 * IN, 1.5 * IN, tank_d, HT - 3.4 * IN)
lever_o = add("Lever", lever)

doc.recompute()

# --- Wrap in an App::Part so it links like other Library components ----------
part = doc.addObject("App::Part", "Part")
part.Label = "Champion4_Toilet"
feats = [o for o in doc.Objects if o.TypeId.startswith("Part::")]
for o in feats:
    part.addObject(o)

# --- Colours / visibility (only when the Gui layer is up: offscreen save) ----
WHITE = (0.94, 0.94, 0.93)
CHROME = (0.55, 0.57, 0.60)
if App.GuiUp:
    for o in feats:
        vo = o.ViewObject
        vo.ShapeColor = CHROME if o.Name.startswith("Lever") else WHITE
        vo.Visibility = True
        o.Visibility = True
    part.ViewObject.Visibility = True

doc.recompute()

# --- Save / export ----------------------------------------------------------
doc.saveAs(os.path.join(OUT, DOC + ".FCStd"))
Part.export(feats, os.path.join(OUT, DOC + ".step"))
Mesh.Mesh(Part.makeCompound([o.Shape for o in feats]).tessellate(0.6)).write(
    os.path.join(OUT, DOC + ".stl"))

bb = Part.makeCompound([o.Shape for o in feats]).BoundBox
with open(os.path.join(OUT, "build_report.txt"), "w") as fh:
    fh.write("AS-Champion4 toilet\n")
    fh.write("GuiUp=%s\n" % App.GuiUp)
    fh.write("overall W x D x H (in) = %.2f x %.2f x %.2f\n"
             % (bb.XLength / IN, bb.YLength / IN, bb.ZLength / IN))
    fh.write("rim height (in) = %.2f\n" % (RIM / IN))
print("TOILET_DONE")
