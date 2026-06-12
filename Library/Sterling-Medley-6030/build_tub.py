# -*- coding: utf-8 -*-
"""
Build a simplified CAD model of the:
  Sterling (Kohler) Medley  30.13 x 60 in  White Vikrell
  Rectangle Alcove Soaking Bathtub - RIGHT-HAND DRAIN
  (Lowe's 1000132899)

Representative shell only.  Captures:
  - Alcove form: finished front apron + integral tile flange on the back wall
    and both end walls (3-sided nailing flange)
  - Rounded rectangular bathing well, ~16" deep (≈14" water depth)
  - Right-hand drain + overflow on the drain end
  - Correct overall envelope 60"L x 30-1/8"W x 20"H

Local frame (component convention):  X = length (60"), Y = width/depth with the
finished APRON at +Y, Z = up; origin back-left-bottom.  Tile flange runs along
the back (Y=0) and the two ends.

"Right-hand drain": drain location is read while *facing the apron* (standing on
the +Y side looking toward -Y).  Your right hand then points toward -X, so the
drain sits at the -X end (here X ≈ 10" from the X=0 end).

All Vikrell is white; the drain/overflow trim is chrome (set by name in
color_save.py / render_sw.py).  Loose Part::Features wrapped in an App::Part
"Part" so the model links like other Library components.

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

# --- Overall dimensions (Sterling Medley 30.13 x 60, right drain) -----------
L = 60.0 * IN          # length              = 1524.0
WD = 30.125 * IN       # width / depth       = 765.175
H = 20.0 * IN          # height              = 508.0

DECK = 2.0 * IN        # rim deck width      = 50.8
WALL = 2.0 * IN        # shell wall thickness
FLOOR_Z = 4.0 * IN     # bathing-well floor  = 101.6  (basin ~16" deep below rim)
FLANGE_H = 1.5 * IN    # tile flange rise above the deck
FLANGE_T = 12.0        # tile flange thickness

DOC = "Sterling-Medley-6030"
OUT = os.path.dirname(os.path.abspath(__file__))

doc = App.newDocument(DOC)


def box(l, w, h, x, y, z):
    return Part.makeBox(l, w, h, V(x, y, z))


def cyl(r, h, x, y, z, axis=(0, 0, 1)):
    return Part.makeCylinder(r, h, V(x, y, z), V(*axis))


def fillet_vertical(shp, r):
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


def add(name, shp):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shp
    return o


# --- Outer block, then carve the basin and hollow the underside -------------
body = box(L, WD, H, 0, 0, 0)

# Bathing well (rounded recess open at the top)
well = fillet_vertical(
    box(L - 2 * DECK, WD - 2 * DECK, (H + 10.0) - FLOOR_Z,
        DECK, DECK, FLOOR_Z), 150.0)
body = body.cut(well)

# Hollow the underside (apron skirt + walls, thin floor under the basin)
under = box(L - 2 * WALL, WD - 2 * WALL, (FLOOR_Z - IN), WALL, WALL, 0.0)
body = body.cut(under)

# Drain pocket + through-hole on the RIGHT-as-faced (-X) end
DRAIN_X = 10.0 * IN
DRAIN_Y = WD / 2.0
body = body.cut(cyl(35.0, 12.0, DRAIN_X, DRAIN_Y, FLOOR_Z - 6.0))   # shallow pocket
body = body.cut(cyl(20.0, FLOOR_Z + 10.0, DRAIN_X, DRAIN_Y, -5.0))  # waste hole

# Integral tile flange: back wall (Y=0) + both ends, none on the apron
fb = box(L, FLANGE_T, FLANGE_H, 0, 0, H)
fl = box(FLANGE_T, WD, FLANGE_H, 0, 0, H)
fr = box(FLANGE_T, WD, FLANGE_H, L - FLANGE_T, 0, H)
body = body.fuse(fb).fuse(fl).fuse(fr)
tub_o = add("TubShell", body)

# --- Chrome trim ------------------------------------------------------------
drain_o = add("Drain", cyl(33.0, 4.0, DRAIN_X, DRAIN_Y, FLOOR_Z - 6.0))
overflow_o = add("Overflow",
                 cyl(26.0, 8.0, DRAIN_X, DECK + 4.0, H - 4.0 * IN, axis=(0, -1, 0)))

doc.recompute()

# --- Wrap in an App::Part ---------------------------------------------------
part = doc.addObject("App::Part", "Part")
part.Label = "Medley_Tub_60x30_RH"
feats = [o for o in doc.Objects if o.TypeId.startswith("Part::")]
for o in feats:
    part.addObject(o)

# --- Colours / visibility (offscreen GUI save) ------------------------------
WHITE = (0.95, 0.95, 0.94)
CHROME = (0.55, 0.57, 0.60)
if App.GuiUp:
    for o in feats:
        vo = o.ViewObject
        vo.ShapeColor = CHROME if o.Name.startswith(("Drain", "Overflow")) else WHITE
        vo.Visibility = True
        o.Visibility = True
    part.ViewObject.Visibility = True

doc.recompute()

# --- Save / export ----------------------------------------------------------
doc.saveAs(os.path.join(OUT, DOC + ".FCStd"))
Part.export(feats, os.path.join(OUT, DOC + ".step"))
Mesh.Mesh(Part.makeCompound([o.Shape for o in feats]).tessellate(0.8)).write(
    os.path.join(OUT, DOC + ".stl"))

bb = Part.makeCompound([o.Shape for o in feats]).BoundBox
with open(os.path.join(OUT, "build_report.txt"), "w") as fh:
    fh.write("Sterling Medley 30.13x60 RH tub\n")
    fh.write("GuiUp=%s\n" % App.GuiUp)
    fh.write("overall L x W x H (in) = %.2f x %.2f x %.2f\n"
             % (bb.XLength / IN, bb.YLength / IN, bb.ZLength / IN))
    fh.write("basin floor Z (in) = %.2f, basin depth (in) = %.2f\n"
             % (FLOOR_Z / IN, (H - FLOOR_Z) / IN))
print("TUB_DONE")
