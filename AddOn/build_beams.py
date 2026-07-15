# -*- coding: utf-8 -*-
"""
Build the structural beam line for the AddOn's OPEN wall (the studless side where
the addition meets the original house): a flush steel I-beam carrying the roof,
plus four 6x6 wood support posts: one flush at each end (the east one tucked
behind the fridge at the X=0 corner) and two evenly spaced in the middle.

These are modelled in the KITCHEN-NATIVE coordinate frame (the same frame the
kitchen uses inside AddOn_Assembly): X = along the open wall, Y = depth (open
wall at Y=-6007), Z = up (floor 0, ceiling 2438.4).  AddOn_Assembly links this
App::Part "Beams" and applies Assembly001's placement to bring it into world.

Run headless:  freecadcmd build_beams.py
Units: millimetres.
"""
import os
import FreeCAD as App
import Part
import Mesh

IN = 25.4

# --- room references (native frame) ----------------------------------------
Y_OPEN = -6007.0         # open-wall centerline (framing native ~ -6096 + offset)
CEIL = 96.0 * IN         # 2438.4
X_E = 0.0                # east end (stove-wall corner)
X_W = -7836.0            # west end (opposite-stove wall)

# --- I-beam (steel W-section, ~14") ----------------------------------------
BEAM_DEPTH = 14.0 * IN   # 355.6
FLANGE_W = 6.5 * IN      # 165.1
FLANGE_T = 0.6 * IN      # 15.2
WEB_T = 0.4 * IN         # 10.2
BEAM_TOP = CEIL
BEAM_BOT = CEIL - BEAM_DEPTH      # 2082.8
LEN = X_E - X_W                    # 7836

# --- posts (6x6 nominal = 5.5" actual) -------------------------------------
POST = 5.5 * IN          # 139.7
POST_TOP = BEAM_BOT      # posts run floor -> underside of beam

DOC = "AddOn_Beams"
doc = App.newDocument(DOC)

def box(l, w, h, x, y, z):
    return Part.makeBox(l, w, h, App.Vector(x, y, z))

def add(name, shp):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shp
    return o

y0 = Y_OPEN - FLANGE_W / 2.0
bot = box(LEN, FLANGE_W, FLANGE_T, X_W, y0, BEAM_BOT)
top = box(LEN, FLANGE_W, FLANGE_T, X_W, y0, BEAM_TOP - FLANGE_T)
web = box(LEN, WEB_T, BEAM_DEPTH - 2 * FLANGE_T, X_W, Y_OPEN - WEB_T / 2.0,
          BEAM_BOT + FLANGE_T)
add("IBeam", bot.fuse(top).fuse(web))

py = Y_OPEN - POST / 2.0
# Four posts under the beam: one flush at each END (the east one tucks BEHIND the
# fridge at the X=0 corner, so it is hidden), plus TWO evenly spaced in the middle.
# The end posts bear on the building corners; the two middle posts break up the
# 7836 mm (25'-9") open span into four equal bays.
x_east = X_E - POST          # -139.7  flush at the east end, behind the fridge
x_west = X_W                 # -7836   flush at the west corner
c_east = x_east + POST / 2.0
c_west = x_west + POST / 2.0
step = (c_east - c_west) / 3.0
POST_C = [c_east - i * step for i in range(4)]        # east -> west, even spacing
POST_NAMES = ["Post_East", "Post_Mid1", "Post_Mid2", "Post_West"]
for nm, cx in zip(POST_NAMES, POST_C):
    add(nm, box(POST, POST, POST_TOP, cx - POST / 2.0, py, 0.0))

part = doc.addObject("App::Part", "Beams")
part.Label = "Beams"
for o in [o for o in doc.Objects if o.TypeId.startswith("Part::")]:
    part.addObject(o)
doc.recompute()

OUT = os.path.dirname(os.path.abspath(__file__))
doc.saveAs(os.path.join(OUT, DOC + ".FCStd"))
feats = [o for o in doc.Objects if o.TypeId.startswith("Part::")]
Part.export(feats, os.path.join(OUT, DOC + ".step"))
Mesh.Mesh(Part.makeCompound([o.Shape for o in feats]).tessellate(1.0)).write(
    os.path.join(OUT, DOC + ".stl"))
print("I-beam span (mm) = %.1f  %d posts at X = %s" %
      (LEN, len(POST_C), ", ".join("%.0f" % c for c in POST_C)))
print("BEAMS_DONE")
