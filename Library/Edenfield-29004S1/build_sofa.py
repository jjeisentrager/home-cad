# -*- coding: utf-8 -*-
"""
Build a simplified CAD model of the:
  Ashley Edenfield 3-Piece Sectional with Chaise  (LAF chaise, model 29004S1)

General representation only - no moving parts. Captures:
  - L-shaped sectional: full-width sofa run + left-facing chaise projecting out
  - Upholstered base, backrest, two outer arms (middle is armless loveseat)
  - Individual seat cushions (1 chaise + 3 sofa) and back cushions
  - Simple feet
  - Correct overall outside dimensions

Run headless:  freecadcmd build_sofa.py

Units: millimetres.  X = width, Y = depth (back/wall = y0, front = +Y), Z = up.
Chaise is on the LEFT (low X) and projects forward (+Y).
"""

import os
import FreeCAD as App
import Part

IN = 25.4

# --- Overall dimensions -----------------------------------------------------
W = 139.0 * IN       # overall width  = 3530.6
DEP = 89.0 * IN      # overall depth  = 2260.6
HGT = 35.0 * IN      # overall height = 889.0

# --- Upholstery proportions -------------------------------------------------
LEG_H = 4.0 * IN          # clearance / feet height = 101.6
SEAT_H = 19.0 * IN        # top of seat cushion = 482.6
CUSHION_T = 5.0 * IN      # seat cushion thickness = 127.0
ARM_H = 26.0 * IN         # arm height = 660.4
ARM_W = 6.0 * IN          # arm width  = 152.4
BACK_THK = 8.0 * IN       # backrest thickness = 203.2
SOFA_DEPTH = 38.0 * IN    # depth of the sofa run = 965.2
CHAISE_W = 38.0 * IN      # width of the chaise column = 965.2

BASE_TOP = SEAT_H - CUSHION_T      # top of the seat platform = 355.6
GAP = 16.0                          # gap between cushions

OUT = os.path.dirname(os.path.abspath(__file__))
DOCNAME = "Edenfield-29004S1"


def box(l, w, h, x, y, z):
    return Part.makeBox(l, w, h, App.Vector(x, y, z))


def add(name, shape):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shape
    return o


# --- build ------------------------------------------------------------------
doc = App.newDocument(DOCNAME)

# L-shaped upholstered base (sofa run + chaise column), under the cushions
base_h = BASE_TOP - LEG_H
run = box(W, SOFA_DEPTH, base_h, 0, 0, LEG_H)
col = box(CHAISE_W, DEP, base_h, 0, 0, LEG_H)
add("Base", run.fuse(col))

# Backrest frame along the wall side (Y = 0), full width
add("Backrest", box(W, BACK_THK, HGT - LEG_H, 0, 0, LEG_H))

# Outer arms (middle loveseat is armless)
add("Arm_Left", box(ARM_W, DEP, ARM_H - LEG_H, 0, 0, LEG_H))               # chaise side
add("Arm_Right", box(ARM_W, SOFA_DEPTH, ARM_H - LEG_H, W - ARM_W, 0, LEG_H))  # sofa side

# Seat cushions ------------------------------------------------------------
# Chaise seat (one long cushion, projects forward to full depth)
add("SeatCushion_Chaise",
    box(CHAISE_W - ARM_W - GAP, DEP - BACK_THK - GAP, CUSHION_T,
        ARM_W + GAP / 2, BACK_THK + GAP / 2, BASE_TOP))

# Sofa seats: 3 cushions across the remaining width
sofa_x0, sofa_x1 = CHAISE_W, W - ARM_W
seg = (sofa_x1 - sofa_x0) / 3.0
for i in range(3):
    x = sofa_x0 + i * seg
    add("SeatCushion_Sofa%d" % (i + 1),
        box(seg - GAP, SOFA_DEPTH - BACK_THK - GAP, CUSHION_T,
            x + GAP / 2, BACK_THK + GAP / 2, BASE_TOP))

# Back cushions ------------------------------------------------------------
back_y0 = BACK_THK
back_d = 150.0
bc_z0, bc_z1 = SEAT_H + 10.0, HGT - 60.0
segments = [(ARM_W, CHAISE_W)]                       # chaise back
for i in range(3):                                    # sofa backs
    segments.append((sofa_x0 + i * seg, sofa_x0 + (i + 1) * seg))
for j, (x0, x1) in enumerate(segments):
    add("BackCushion_%d" % (j + 1),
        box(x1 - x0 - GAP, back_d, bc_z1 - bc_z0,
            x0 + GAP / 2, back_y0, bc_z0))

# Feet (6 corners of the L footprint) -------------------------------------
foot = 55.0
corners = [(0, 0), (W, 0), (W, SOFA_DEPTH),
           (CHAISE_W, SOFA_DEPTH), (CHAISE_W, DEP), (0, DEP)]
for k, (cx, cy) in enumerate(corners):
    x = min(max(cx - foot / 2, 0), W - foot)
    y = min(max(cy - foot / 2, 0), DEP - foot)
    add("Leg_%d" % (k + 1), box(foot, foot, LEG_H, x, y, 0))

doc.recompute()

# --- save / export ----------------------------------------------------------
fcstd = os.path.join(OUT, DOCNAME + ".FCStd")
step = os.path.join(OUT, DOCNAME + ".step")
stl = os.path.join(OUT, DOCNAME + ".stl")

doc.saveAs(fcstd)
solids = [o for o in doc.Objects]
Part.export(solids, step)

import Mesh
compound = Part.makeCompound([o.Shape for o in solids])
Mesh.Mesh(compound.tessellate(1.0)).write(stl)

bb = compound.BoundBox
print("Saved: %s" % fcstd)
print("Saved: %s" % step)
print("Saved: %s" % stl)
print("Overall (mm)  W x D x H = %.1f x %.1f x %.1f"
      % (bb.XLength, bb.YLength, bb.ZLength))
print("Overall (in)  W x D x H = %.2f x %.2f x %.2f"
      % (bb.XLength / IN, bb.YLength / IN, bb.ZLength / IN))
