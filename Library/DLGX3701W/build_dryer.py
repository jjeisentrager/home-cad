# -*- coding: utf-8 -*-
"""
Build a simplified CAD model of the:
  LG DLGX3701W 7.4 cu.ft. Ultra Large Capacity Front-Load Dryer (white)

General representation only - no moving parts. Captures:
  - White cabinet box (front-load laundry appliance)
  - Top control console with a recessed dark display strip
  - Signature large round front door: white plastic ring + recessed dark
    tinted glass porthole
  - Recessed finger grip on the door for opening
  - Four dark leveling feet (height included in the overall dimension)
  - Correct overall outside dimensions

Run headless:  freecadcmd build_dryer.py
Then apply colors with the GUI:  color_save.py   (offscreen GUI)

Units: millimetres.   Local frame: origin at back-left-bottom corner,
+X = width, +Y = depth (FRONT face at +Y), +Z = height (up).
"""

import os
import FreeCAD as App
import Part

IN = 25.4  # mm per inch

# --- Overall outside dimensions (DLGX3701W) --------------------------------
W = 27.0 * IN      # width  = 685.80 mm
H = 38.6875 * IN   # height = 982.66 mm
D = 30.25 * IN     # depth  = 768.35 mm  (door closed)

# --- Design parameters ------------------------------------------------------
DOOR_PROUD = 45.0     # how far the round door stands out from the cabinet face
FOOT_H = 28.0         # leveling-foot height (cabinet sits on top of the feet)
SIDE = 6.0            # side reveal

BODY_D = D - DOOR_PROUD       # cabinet box depth
FRONT = BODY_D                # Y of the cabinet front face
PFRONT = D                    # Y of the door front face
BODY_Z0 = FOOT_H              # cabinet bottom (feet below)

# Console (top front control panel)
CON_H = 115.0                 # console height
CON_PROUD = 28.0              # how far the console stands proud of the cabinet

# Round door
DOOR_R = 250.0                # outer door radius (~19.7" dia)
GLASS_R = 188.0               # tinted-glass radius
GLASS_RECESS = 14.0           # how far the glass sits behind the door face
DOOR_CZ = BODY_Z0 + 0.40 * (H - BODY_Z0)   # door centre height

OUT = os.path.dirname(os.path.abspath(__file__))
DOCNAME = "DLGX3701W"


def box(l, w, h, x, y, z):
    return Part.makeBox(l, w, h, App.Vector(x, y, z))


def cyl_y(r, length, x, y, z):
    """Cylinder with its axis along +Y, base centre at (x, y, z)."""
    return Part.makeCylinder(r, length, App.Vector(x, y, z), App.Vector(0, 1, 0))


def add(name, shape):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shape
    return o


# --- build ------------------------------------------------------------------
doc = App.newDocument(DOCNAME)

# Cabinet body (sits on top of the leveling feet)
cabinet = add("Cabinet", box(W, BODY_D, H - FOOT_H, 0, 0, BODY_Z0))

# Top control console - stands slightly proud of the cabinet front
con_z0 = H - CON_H
console = box(W - 2 * SIDE, BODY_D + CON_PROUD, CON_H, SIDE, 0, con_z0)
# Recessed dark display strip on the console front face
disp_w, disp_h, disp_d = W * 0.55, 46.0, 8.0
disp_x = (W - disp_w) / 2.0
disp_z = con_z0 + (CON_H - disp_h) / 2.0
display_cut = box(disp_w, disp_d + 1, disp_h,
                  disp_x, BODY_D + CON_PROUD - disp_d, disp_z)
console = console.cut(display_cut)
console = add("Console", console)
# The dark display itself, filling the recess
display = add("Display", box(disp_w, disp_d, disp_h,
                             disp_x, BODY_D + CON_PROUD - disp_d, disp_z))

# Round door: white ring (annulus) protruding from the cabinet face
cx = W / 2.0
door_outer = cyl_y(DOOR_R, DOOR_PROUD, cx, FRONT, DOOR_CZ)
door_bore = cyl_y(GLASS_R, DOOR_PROUD + 2, cx, FRONT - 1, DOOR_CZ)
door_ring = add("Door_Ring", door_outer.cut(door_bore))

# Tinted glass porthole, recessed behind the door face
glass_len = DOOR_PROUD - GLASS_RECESS
glass = add("Door_Glass", cyl_y(GLASS_R, glass_len, cx, FRONT, DOOR_CZ))

# Recessed finger grip on the left side of the door (dark)
grip_w, grip_h, grip_d = 26.0, 150.0, 22.0
grip = add("Handle", box(grip_w, grip_d, grip_h,
                         cx - DOOR_R - grip_w * 0.3,
                         PFRONT - grip_d, DOOR_CZ - grip_h / 2.0))

# Four dark leveling feet
feet = []
fr = 24.0
for i, (fx, fy) in enumerate([
        (fr, fr), (W - 2 * fr, fr),
        (fr, BODY_D - 2 * fr), (W - 2 * fr, BODY_D - 2 * fr)]):
    feet.append(add("Foot_%d" % (i + 1), box(fr, fr, FOOT_H, fx, fy, 0)))

doc.recompute()

# --- save / export ----------------------------------------------------------
fcstd = os.path.join(OUT, DOCNAME + ".FCStd")
step = os.path.join(OUT, DOCNAME + ".step")
stl = os.path.join(OUT, DOCNAME + ".stl")

doc.saveAs(fcstd)

solids = [cabinet, console, display, door_ring, glass, grip] + feet
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
