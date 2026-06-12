# -*- coding: utf-8 -*-
"""
Build the structural beam line that carries the AddOn roof across the opening in
the main house's north (outer) wall -- a flush steel W14 I-beam plus four 6x6
wood support posts. These were previously modelled in the AddOn (AddOn_Beams);
they now live in the MAIN assembly so they belong to the house structure.

Modelled in the MainFraming LOCAL frame (same frame as build_mainframing.py):
  X = long axis, Y = short axis (north wall centerline at +154"), Z = up,
  floor (top of subfloor) at Z=0.  Main/Main.FCStd links this App::Part "Beams"
  at the same placement as MainFraming (8521.7, 3962.4, 12.7) so it lines up.

Layout (world X via Main = local + 8521.7):
  - I-beam CENTER on the north-wall centerline (Y = 154" = world 7874).
  - Opening spans local x -46.2"..267.4" (world 7349..15314), matching the
    Ext_North_W/E gap.
  - 4 posts: one at each opening edge + two evenly spaced (3 equal bays). The
    east post sits at the wall behind the fridge (the opening's east edge); the
    beam is extended to bear on it. The fridge is not moved.

Run:  flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD build_beams.py
Units: millimetres.
"""
import os
import FreeCAD as App
import Part
import Mesh

IN = 25.4

# --- references (MainFraming local frame) ----------------------------------
Y_WALL = 154.0 * IN              # north-wall centerline = beam & post centerline
CEIL = 96.0 * IN                 # 2438.4  (beam top; AddOn ceiling level)

# --- I-beam (steel W14 section) --------------------------------------------
BEAM_DEPTH = 14.0 * IN           # 355.6
FLANGE_W = 6.5 * IN              # 165.1
FLANGE_T = 0.6 * IN              # 15.2
WEB_T = 0.4 * IN                 # 10.2
BEAM_TOP = CEIL
BEAM_BOT = CEIL - BEAM_DEPTH     # 2082.8

# --- posts (6x6 nominal = 5.5" actual) -------------------------------------
POST = 5.5 * IN                  # 139.7
POST_TOP = BEAM_BOT              # floor -> underside of beam

# --- opening + post X positions (local inches) -----------------------------
X_W = -46.2 * IN                 # west opening edge (Ext_North_W east end)
X_E = 267.4 * IN                 # east opening edge (Ext_North_E west end = wall behind fridge)
SPAN = X_E - X_W
POSTS_X = [X_W, X_W + SPAN / 3.0, X_W + 2.0 * SPAN / 3.0, X_E]   # 4 posts, 3 equal bays

DOC = "MainBeams"
doc = App.newDocument(DOC)

def box(l, w, h, x, y, z):
    return Part.makeBox(l, w, h, App.Vector(x, y, z))

def add(name, shp):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shp
    return o

# I-beam: extend past the end posts so it fully bears on them / into the walls.
bx0 = X_W - POST / 2.0
blen = (X_E + POST / 2.0) - bx0
y0 = Y_WALL - FLANGE_W / 2.0
bot = box(blen, FLANGE_W, FLANGE_T, bx0, y0, BEAM_BOT)
top = box(blen, FLANGE_W, FLANGE_T, bx0, y0, BEAM_TOP - FLANGE_T)
web = box(blen, WEB_T, BEAM_DEPTH - 2 * FLANGE_T, bx0, Y_WALL - WEB_T / 2.0,
          BEAM_BOT + FLANGE_T)
add("IBeam", bot.fuse(top).fuse(web))

names = ["Post_West", "Post_Mid1", "Post_Mid2", "Post_East"]
for nm, xc in zip(names, POSTS_X):
    add(nm, box(POST, POST, POST_TOP, xc - POST / 2.0, Y_WALL - POST / 2.0, 0.0))

part = doc.addObject("App::Part", "Beams")
part.Label = "Beams"
feats = [o for o in doc.Objects if o.TypeId.startswith("Part::")]
for o in feats:
    part.addObject(o)

doc.recompute()

if App.GuiUp:
    for o in feats + [part]:
        if o.ViewObject is not None:
            o.ViewObject.Visibility = True

OUT = os.path.dirname(os.path.abspath(__file__))
doc.saveAs(os.path.join(OUT, DOC + ".FCStd"))
Part.export(feats, os.path.join(OUT, DOC + ".step"))
Mesh.Mesh(Part.makeCompound([o.Shape for o in feats]).tessellate(1.0)).write(
    os.path.join(OUT, DOC + ".stl"))
print("Posts (world X): %s" % [round(x / IN * 25.4 + 8521.7) for x in POSTS_X])
print("I-beam world X: %.0f .. %.0f" % (bx0 + 8521.7, bx0 + blen + 8521.7))
print("BEAMS_DONE")
