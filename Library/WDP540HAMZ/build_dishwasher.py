# -*- coding: utf-8 -*-
"""
Build a simplified CAD model of the:
  Whirlpool Eco Series 24-in Top Control Built-in Dishwasher
  (model WDP540HAMZ)

General representation only - no moving parts. Captures:
  - Flat stainless front door panel (top-control => no visible front controls)
  - Top control console strip across the top edge of the door
  - Recessed "pocket handle" along the bottom of the control strip
  - Recessed toe-kick / lower access panel at the bottom
  - Correct overall outside dimensions

Run headless:  freecadcmd build_dishwasher.py

Units: millimetres.
"""

import os
import FreeCAD as App
import Part

IN = 25.4  # mm per inch

# --- Overall outside dimensions (WDP540HAMZ) -------------------------------
W = 23.875 * IN   # width  = 606.43 mm
H = 34.5 * IN     # height = 876.30 mm
D = 24.5 * IN     # depth  = 622.30 mm

# --- Design parameters ------------------------------------------------------
PANEL_T = 35.0    # how far the door / console stand out from the body
SIDE = 5.0        # side reveal of the door from the body edge
TOE_H = 90.0      # toe-kick height at the bottom
CTRL_H = 55.0     # height of the top control-console strip
GAP = 4.0         # reveal between door and console strip

BODY_D = D - PANEL_T          # cabinet box depth
FRONT = BODY_D                # Y of the body front face
PFRONT = D                    # Y of the door / console front face

OUT = os.path.dirname(os.path.abspath(__file__))
DOCNAME = "WDP540HAMZ"


def box(l, w, h, x, y, z):
    return Part.makeBox(l, w, h, App.Vector(x, y, z))


def add(name, shape):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shape
    return o


# --- build ------------------------------------------------------------------
doc = App.newDocument(DOCNAME)

# Cabinet body
cabinet = add("Cabinet", box(W, BODY_D, H, 0, 0, 0))

# Flat door panel
door_z1 = TOE_H
door_z2 = H - CTRL_H - GAP
door = add("Door", box(W - 2 * SIDE, PANEL_T, door_z2 - door_z1,
                       SIDE, FRONT, door_z1))

# Top control console strip
ctrl = box(W - 2 * SIDE, PANEL_T, CTRL_H, SIDE, FRONT, H - CTRL_H)

# Pocket handle: horizontal recess along the bottom of the console strip
ph_inset, ph_depth, ph_h = 70.0, 32.0, 32.0
pocket = box(W - 2 * ph_inset, ph_depth, ph_h,
             ph_inset, PFRONT - ph_depth, H - CTRL_H)
ctrl = ctrl.cut(pocket)

# Top control buttons: shallow recess on the TOP face of the console strip
cb_inset, cb_d = 45.0, 6.0
buttons = box(W - 2 * cb_inset, PANEL_T - 8, 12.0,
              cb_inset, FRONT + 4, H - cb_d)
ctrl = ctrl.cut(buttons)
control = add("Control_Panel", ctrl)

# Toe-kick / lower access panel (recessed relative to the door, darker)
toe = add("Toe_Kick", box(W - 2 * SIDE, 8.0, TOE_H - 4,
                          SIDE, BODY_D, 2.0))

doc.recompute()

# --- save / export ----------------------------------------------------------
fcstd = os.path.join(OUT, DOCNAME + ".FCStd")
step = os.path.join(OUT, DOCNAME + ".step")
stl = os.path.join(OUT, DOCNAME + ".stl")

doc.saveAs(fcstd)

solids = [cabinet, door, control, toe]
Part.export(solids, step)

import Mesh
compound = Part.makeCompound([o.Shape for o in solids])
Mesh.Mesh(compound.tessellate(1.0)).write(stl)

bb = compound.BoundBox
print("Saved: %s" % fcstd)
print("Saved: %s" % step)
print("Saved: %s" % stl)
print("Overall (mm)  W x H x D = %.1f x %.1f x %.1f"
      % (bb.XLength, bb.ZLength, bb.YLength))
print("Overall (in)  W x H x D = %.2f x %.2f x %.2f"
      % (bb.XLength / IN, bb.ZLength / IN, bb.YLength / IN))
