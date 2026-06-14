# -*- coding: utf-8 -*-
"""
Build a simplified CAD model of the:
  Mustee Utilatub  (Model 19)
  23 x 23.5 in  1-Basin  White  Freestanding Laundry / Utility Sink with Drain

Representative only - no faucet, no supply lines.  Captures:
  - Single molded thermoplastic basin (23 W x 23.5 D), ~13" deep, rolled rim
  - Freestanding: four tubular steel legs to a 34" overall rim height
  - Lower brace frame tying the legs together
  - Center drain: strainer flange in the basin floor + outlet stub below

Local frame (component convention):  X = width, Y = depth with the FRONT at +Y,
Z = up; origin back-left-bottom.  Wall side at Y=0, legs feet on Z=0.

Body is white; legs/braces are gray steel, feet + drain are dark (set by name
in render_sw.py and below for the offscreen GUI save).  Loose Part::Features
wrapped in an App::Part "Part" so the model links like other Library components.

Run (saves a proper GuiDocument via the offscreen Qt platform):
  flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD build_tub.py
Units: millimetres.
"""
import os
import FreeCAD as App
import Part
import Mesh

V = App.Vector
IN = 25.4

# --- Overall dimensions (Mustee Utilatub 19 spec) ---------------------------
W = 23.0 * IN          # overall width            = 584.2
DEPTH = 23.5 * IN      # overall depth            = 596.9
HT = 34.0 * IN         # overall rim height       = 863.6
BASIN_D = 13.0 * IN    # interior basin depth     = 330.2

WALL = 38.0            # molded wall / rim border thickness
BOT_T = 30.0           # molded basin bottom slab thickness

CX = W / 2.0
CY = DEPTH / 2.0

# Derived Z planes
FLOOR_Z = HT - BASIN_D            # basin interior floor (top of slab) = 533.4
TUB_BOT_Z = FLOOR_Z - BOT_T       # underside of molded body           = 503.4

DOC = "Mustee-19"
OUT = os.path.dirname(os.path.abspath(__file__))

doc = App.newDocument(DOC)


def box(l, w, h, x, y, z):
    return Part.makeBox(l, w, h, V(x, y, z))


def cyl(r, h, x, y, z):
    return Part.makeCylinder(r, h, V(x, y, z), V(0, 0, 1))


def add(name, shp):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shp
    return o


def fillet_vertical(shp, r):
    """Round all vertical (Z-parallel) edges -> soft molded form."""
    edges = []
    for e in shp.Edges:
        p, q = e.Vertexes[0].Point, e.Vertexes[-1].Point
        if abs(p.x - q.x) < 1e-6 and abs(p.y - q.y) < 1e-6 and abs(p.z - q.z) > 1e-6:
            edges.append(e)
    if not edges:
        return shp
    try:
        return shp.makeFillet(r, edges)
    except Exception:
        return shp


# --- Molded basin body ------------------------------------------------------
# Outer shell (rounded corners), basin cavity hollowed from the top.
outer = fillet_vertical(box(W, DEPTH, HT - TUB_BOT_Z, 0, 0, TUB_BOT_Z), 28.0)
cav = fillet_vertical(
    box(W - 2 * WALL, DEPTH - 2 * WALL, BASIN_D + 10.0,
        WALL, WALL, FLOOR_Z), 22.0)
tub = outer.cut(cav)

# Center drain bore through the bottom slab
DRAIN_R = 22.0
drain_y = CY                       # centered front-to-back
bore = cyl(DRAIN_R, BOT_T + 4.0, CX, drain_y, TUB_BOT_Z - 2.0)
tub = tub.cut(bore)
tub_o = add("Tub", tub)

# --- Drain: strainer flange (in floor) + outlet stub (below) ----------------
ring = cyl(34.0, 4.0, CX, drain_y, FLOOR_Z - 1.0).cut(
    cyl(DRAIN_R - 4.0, 8.0, CX, drain_y, FLOOR_Z - 3.0))
drainring_o = add("DrainRing", ring)
stub = cyl(DRAIN_R, 70.0, CX, drain_y, TUB_BOT_Z - 64.0).cut(
    cyl(DRAIN_R - 5.0, 80.0, CX, drain_y, TUB_BOT_Z - 70.0))
drainstub_o = add("DrainStub", stub)

# --- Legs: four tubular steel posts + leveling feet -------------------------
LEG = 25.4                         # 1" square tube
INSET = 22.0                       # set in from each corner
FOOT_H = 14.0
leg_xy = [(INSET, INSET),
          (W - INSET - LEG, INSET),
          (INSET, DEPTH - INSET - LEG),
          (W - INSET - LEG, DEPTH - INSET - LEG)]
leg_os, foot_os = [], []
for i, (lx, ly) in enumerate(leg_xy, 1):
    leg = box(LEG, LEG, TUB_BOT_Z - FOOT_H, lx, ly, FOOT_H)
    leg_os.append(add("Leg%d" % i, leg))
    foot = cyl(15.0, FOOT_H, lx + LEG / 2.0, ly + LEG / 2.0, 0.0)
    foot_os.append(add("Foot%d" % i, foot))

# --- Lower brace frame tying the legs (square tube, ~5" up) -----------------
BR = 19.0
bz = 120.0
brace_os = []
# front & back braces (run in X)
for j, by in enumerate([INSET + (LEG - BR) / 2.0,
                        DEPTH - INSET - LEG + (LEG - BR) / 2.0]):
    brace_os.append(add("BraceX%d" % j,
                        box(W - 2 * INSET, BR, BR, INSET, by, bz)))
# left & right braces (run in Y)
for j, bx in enumerate([INSET + (LEG - BR) / 2.0,
                        W - INSET - LEG + (LEG - BR) / 2.0]):
    brace_os.append(add("BraceY%d" % j,
                        box(BR, DEPTH - 2 * INSET, BR, bx, INSET, bz)))

doc.recompute()

# --- Wrap in an App::Part so it links like other Library components ----------
part = doc.addObject("App::Part", "Part")
part.Label = "Mustee_Utilatub_19"
feats = [o for o in doc.Objects if o.TypeId.startswith("Part::")]
for o in feats:
    part.addObject(o)


# --- Colours / visibility (only when the Gui layer is up: offscreen save) ----
WHITE = (0.93, 0.93, 0.91)
STEEL = (0.62, 0.64, 0.66)
DARK = (0.20, 0.21, 0.23)


def colour_for(name):
    if name.startswith(("Leg", "Brace")):
        return STEEL
    if name.startswith(("Foot", "Drain")):
        return DARK
    return WHITE


if App.GuiUp:
    for o in feats:
        vo = o.ViewObject
        vo.ShapeColor = colour_for(o.Name)
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
    fh.write("Mustee-19 Utilatub laundry/utility sink\n")
    fh.write("GuiUp=%s\n" % App.GuiUp)
    fh.write("overall W x D x H (in) = %.2f x %.2f x %.2f\n"
             % (bb.XLength / IN, bb.YLength / IN, bb.ZLength / IN))
    fh.write("overall W x D x H (mm) = %.1f x %.1f x %.1f\n"
             % (bb.XLength, bb.YLength, bb.ZLength))
    fh.write("rim height (in) = %.2f  basin depth (in) = %.2f\n"
             % (HT / IN, BASIN_D / IN))
print("TUB_DONE")
