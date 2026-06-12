# -*- coding: utf-8 -*-
"""
Build a simplified CAD model of the:
  KOHLER Caxton  (K-20000)
  20.25 in Vitreous China Undermount Rectangular Transitional White
  Bathroom Sink (lavatory)

Per the user's request the FAUCET and the two HOT/COLD HANDLES are modelled as
part of the sink so the whole fixture links/places as a single component.  (A
real undermount lav has no deck holes - the faucet is counter- or wall-mounted
behind the bowl; here it is built into the part, sitting just behind the back
rim edge where a widespread faucet would land on the countertop.)

Representative china + chrome trim only - no working parts.  Captures:
  - Flat undermount rim/flange (20-7/16 x 15-5/16 in) with rounded corners
  - Rounded-rectangular bathing well (~17-1/4 x 12-1/4 in, ~8-1/8 in deep)
  - Centre drain + chrome pop-up flange
  - A transitional gooseneck spout (chrome) arching over the basin centre
  - Two chrome lever handles on an 8 in widespread, flanking the spout

Local frame (component convention):  X = width (20-7/16"), Y = depth with the
FRONT rim at +Y, Z = up.  Following the kitchen-sink exception, the rim top
plane sits at Z = 0; the bowl hangs to negative Z and the faucet rises to
positive Z.  The faucet/handles sit just BEHIND the back rim edge at negative Y
(toward the wall), as they would on the counter behind an undermount basin.

All china is white; faucet / handles / drain trim are chrome (set by name in
build / color_save.py / render_sw.py).  Loose Part::Features wrapped in an
App::Part "Part" so the model links like the other Library components.

Run (saves a proper GuiDocument via the offscreen Qt platform):
  flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD build_sink.py
Units: millimetres.
"""
import os
import FreeCAD as App
import Part
import Mesh

V = App.Vector
IN = 25.4

# --- Overall dimensions (KOHLER Caxton K-20000 spec sheet) ------------------
L = 20.4375 * IN       # outer rim width (20-7/16")   = 519.11
Wd = 15.3125 * IN      # outer rim depth (15-5/16")   = 388.94
BOWL_L = 17.25 * IN    # basin length (X)             = 438.15
BOWL_W = 12.25 * IN    # basin width  (Y)             = 311.15
DEPTH = 8.125 * IN     # basin depth below rim        = 206.38

# --- Design parameters ------------------------------------------------------
DECK_T = 8.0           # rim / mounting flange thickness
WALL_T = 10.0          # bowl wall thickness
BOT_T = 12.0           # bowl bottom thickness
RIM_R = 45.0           # outer rim corner radius
BOWL_OR = 55.0         # bowl outer corner radius
BOWL_IR = 48.0         # basin inner corner radius
DRAIN_R = 18.0         # drain opening radius (1.25" pop-up)

CX = L / 2.0
# basin centred in the rim
BX0 = (L - BOWL_L) / 2.0          # 40.48
BY0 = (Wd - BOWL_W) / 2.0         # 38.90
BCY = BY0 + BOWL_W / 2.0          # basin centre Y = 194.47

# faucet / handle line: just behind the back rim edge (toward the wall)
FY = -30.0                        # 30 mm behind Y=0
SPREAD = 8.0 * IN                 # widespread handle spacing = 203.2

DOC = "KOHLER-Caxton"
OUT = os.path.dirname(os.path.abspath(__file__))

doc = App.newDocument(DOC)


def box(l, w, h, x, y, z):
    return Part.makeBox(l, w, h, V(x, y, z))


def cyl(r, h, x, y, z, ax=(0, 0, 1)):
    return Part.makeCylinder(r, h, V(x, y, z), V(*ax))


def _vert_edges(shp):
    out = []
    for e in shp.Edges:
        p, q = e.Vertexes[0].Point, e.Vertexes[-1].Point
        if abs(p.x - q.x) < 1e-6 and abs(p.y - q.y) < 1e-6 and abs(p.z - q.z) > 1e-6:
            out.append(e)
    return out


def fillet_vertical(shp, r):
    """Round all vertical (Z-parallel) edges -> rounded-rectangle plan form."""
    edges = _vert_edges(shp)
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


# --- Rim / undermount flange (white) ----------------------------------------
# Flat plate, top plane at Z=0, rounded outer corners, basin opening cut out.
flange = fillet_vertical(box(L, Wd, DECK_T, 0, 0, -DECK_T), RIM_R)
opening = fillet_vertical(
    box(BOWL_L, BOWL_W, DECK_T + 2, BX0, BY0, -DECK_T - 1), BOWL_IR)
flange = flange.cut(opening)
flange_o = add("Rim_Flange", flange)

# --- Bowl (white): rounded outer shell, hollowed basin, drain cut -----------
bo = fillet_vertical(
    box(BOWL_L + 2 * WALL_T, BOWL_W + 2 * WALL_T, DEPTH,
        BX0 - WALL_T, BY0 - WALL_T, -DEPTH), BOWL_OR)
cav = fillet_vertical(
    box(BOWL_L, BOWL_W, DEPTH, BX0, BY0, -(DEPTH - BOT_T)), BOWL_IR)
bowl = bo.cut(cav)
# round the bottom horizontal edges a little for a softer china form
try:
    bot_edges = [e for e in bowl.Edges
                 if all(abs(v.Point.z - (-DEPTH)) < 1e-6 for v in e.Vertexes)]
    if bot_edges:
        bowl = bowl.makeFillet(20.0, bot_edges)
except Exception:
    pass
# centre drain hole through the basin floor
drain_hole = cyl(DRAIN_R, BOT_T + 6, CX, BCY, -DEPTH - 2)
bowl = bowl.cut(drain_hole)
bowl_o = add("Bowl", bowl)

# --- Drain trim (chrome): pop-up flange ring at the basin floor -------------
floor_top = -(DEPTH - BOT_T)
drain_ring = cyl(DRAIN_R + 6, 4.0, CX, BCY, floor_top - 1).cut(
    cyl(DRAIN_R - 2, 6.0, CX, BCY, floor_top - 2))
drain_o = add("Drain_Trim", drain_ring)

# --- Faucet (chrome): escutcheon + riser + gooseneck arch + downspout -------
TUBE_R = 14.0
ZTOP = 150.0           # height of the arch's straight legs
ARCH_R = (BCY - FY) / 2.0   # ring radius so legs land at the riser & basin centre
ARCH_CY = FY + ARCH_R       # arch centre Y

base = cyl(24.0, 10.0, CX, FY, 0)                       # escutcheon
riser = cyl(TUBE_R, ZTOP, CX, FY, 0)                    # back leg (vertical)
# gooseneck: top half of a torus whose axis is X (ring lies in the Y-Z plane)
full_torus = Part.makeTorus(ARCH_R, TUBE_R, V(CX, ARCH_CY, ZTOP), V(1, 0, 0))
keep = box(120, BCY - FY + 80, 160, CX - 60, FY - 40, ZTOP)   # z >= ZTOP half
arch = full_torus.common(keep)
# front downspout + aerator over the basin centre
downspout = cyl(TUBE_R, 32.0, CX, BCY, ZTOP - 32.0)
aerator = cyl(16.0, 8.0, CX, BCY, ZTOP - 40.0)
faucet = base.fuse([riser, arch, downspout, aerator])
faucet_o = add("Faucet", faucet)


def handle(sx, name):
    hbase = cyl(18.0, 8.0, sx, FY, 0)
    post = cyl(9.0, 60.0, sx, FY, 0)
    lever = cyl(7.0, 70.0, sx, FY - 10.0, 62.0, ax=(0, 1, 0))   # points forward
    cap = Part.makeSphere(8.0, V(sx, FY + 60.0, 62.0))
    return add(name, hbase.fuse([post, lever, cap]))


handle_l = handle(CX - SPREAD / 2.0, "Handle_Cold")
handle_r = handle(CX + SPREAD / 2.0, "Handle_Hot")

doc.recompute()

# --- Wrap in an App::Part so it links like other Library components ----------
part = doc.addObject("App::Part", "Part")
part.Label = "Caxton_Lavatory"
feats = [o for o in doc.Objects if o.TypeId.startswith("Part::")]
for o in feats:
    part.addObject(o)

# --- Colours / visibility (only when the Gui layer is up: offscreen save) ----
WHITE = (0.94, 0.94, 0.93)
CHROME = (0.55, 0.57, 0.60)


def is_chrome(name):
    return any(name.startswith(p) for p in ("Faucet", "Handle", "Drain"))


if App.GuiUp:
    for o in feats:
        vo = o.ViewObject
        vo.ShapeColor = CHROME if is_chrome(o.Name) else WHITE
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
    fh.write("KOHLER-Caxton K-20000 undermount lavatory (with faucet+handles)\n")
    fh.write("GuiUp=%s\n" % App.GuiUp)
    fh.write("rim outer W x D (in) = %.2f x %.2f\n" % (L / IN, Wd / IN))
    fh.write("basin L x W x depth (in) = %.2f x %.2f x %.2f\n"
             % (BOWL_L / IN, BOWL_W / IN, DEPTH / IN))
    fh.write("overall bbox X x Y x Z (mm) = %.1f x %.1f x %.1f\n"
             % (bb.XLength, bb.YLength, bb.ZLength))
    fh.write("overall bbox X x Y x Z (in) = %.2f x %.2f x %.2f\n"
             % (bb.XLength / IN, bb.YLength / IN, bb.ZLength / IN))
    fh.write("faucet top Z (mm) = %.1f  (%.2f in above rim)\n"
             % (bb.ZMax, bb.ZMax / IN))
print("CAXTON_DONE")
