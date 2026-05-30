# -*- coding: utf-8 -*-
"""
Build a simplified CAD model of the:
  LG 30-in 5-Burner 5.8-cu ft Air Fry Convection Freestanding Natural Gas Range
  (model LRGL5823S)

General representation only - no moving parts. Captures:
  - Main oven cabinet at counter height
  - Rear backguard / control panel with 5 control knobs + display
  - Cooktop with 5 sealed burners and continuous grates
  - Oven door with window and bar handle
  - Storage drawer with handle
  - Correct overall outside dimensions

Run headless:  freecadcmd build_range.py

Units: millimetres.  X = width, Y = depth (front = +Y), Z = up.
"""

import os
import FreeCAD as App
import Part

IN = 25.4

# --- Overall dimensions (LRGL5823S) ----------------------------------------
W = 29.875 * IN     # width             = 758.83
H = 47.3125 * IN    # height to backguard= 1201.74
D = 28.9375 * IN    # depth w/ handle    = 735.01
COOKTOP_H = 36.0 * IN   # cooktop surface height = 914.40

# --- Design parameters ------------------------------------------------------
D_BODY = 680.0      # cabinet / door-face plane (front)
PANEL_T = 35.0      # door & drawer protrusion
D_CORE = D_BODY - PANEL_T
PLATE_T = 16.0      # cooktop plate thickness
BG_DEPTH = 65.0     # backguard depth (at the rear)
MARGIN = 6.0        # side reveal for front panels

FRONT = D_CORE
PFRONT = D_BODY
CX = W / 2.0

OUT = os.path.dirname(os.path.abspath(__file__))
DOCNAME = "LRGL5823S"


def box(l, w, h, x, y, z):
    return Part.makeBox(l, w, h, App.Vector(x, y, z))


def cylz(r, h, x, y, z):
    return Part.makeCylinder(r, h, App.Vector(x, y, z), App.Vector(0, 0, 1))


def cyly(r, h, x, y, z):
    return Part.makeCylinder(r, h, App.Vector(x, y, z), App.Vector(0, 1, 0))


def cylx(r, h, x, y, z):
    return Part.makeCylinder(r, h, App.Vector(x, y, z), App.Vector(1, 0, 0))


def add(name, shape):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shape
    return o


def hbar(zc, x1, x2, off, r):
    """Horizontal bar handle on the front face."""
    yb = PFRONT + off
    bar = cylx(r, x2 - x1, x1, yb, zc)
    post = box(24, off, 24, 0, PFRONT, zc - 12)
    p1 = post.copy(); p1.translate(App.Vector(x1 + 30, 0, 0))
    p2 = post.copy(); p2.translate(App.Vector(x2 - 54, 0, 0))
    return bar.fuse(p1).fuse(p2)


# --- build ------------------------------------------------------------------
doc = App.newDocument(DOCNAME)

# Main oven cabinet
cabinet = add("Body", box(W, D_CORE, COOKTOP_H, 0, 0, 0))

# Cooktop plate
cooktop = add("Cooktop", box(W, D_BODY, PLATE_T, 0, 0, COOKTOP_H))
top_z = COOKTOP_H + PLATE_T

# Backguard / rear control panel
backguard = add("Backguard", box(W, BG_DEPTH, H - COOKTOP_H, 0, 0, COOKTOP_H))

# Oven door (with window recess + dark glass) and handle
door_z1, door_z2 = 290.0, COOKTOP_H - 22.0
door = box(W - 2 * MARGIN, PANEL_T, door_z2 - door_z1, MARGIN, FRONT, door_z1)
win_w = W - 2 * 150.0
win_z1, win_z2 = door_z1 + 150.0, door_z2 - 80.0
recess = box(win_w, 22, win_z2 - win_z1, CX - win_w / 2, PFRONT - 22, win_z1)
door = door.cut(recess)
oven_door = add("Oven_Door", door)
glass = add("Oven_Window", box(win_w - 24, 14, win_z2 - win_z1 - 24,
                               CX - (win_w - 24) / 2, PFRONT - 19, win_z1 + 12))
h_oven = add("Handle_OvenDoor", hbar(door_z2 - 45, MARGIN + 60, W - MARGIN - 60,
                                     off=40, r=14))

# Storage drawer + handle
dr_z1, dr_z2 = 40.0, 270.0
drawer = add("Storage_Drawer", box(W - 2 * MARGIN, PANEL_T, dr_z2 - dr_z1,
                                   MARGIN, FRONT, dr_z1))
h_draw = add("Handle_Drawer", hbar(dr_z2 - 40, MARGIN + 60, W - MARGIN - 60,
                                   off=32, r=12))

# 5 sealed burners
burner_pos = [(205, 250), (W - 205, 250),        # rear L / R
              (205, 540), (W - 205, 540),        # front L / R
              (CX, 395)]                          # center
burners = None
for (bx, by) in burner_pos:
    base = cylz(50, 10, bx, by, top_z)
    cap = cylz(40, 16, bx, by, top_z)
    b = base.fuse(cap)
    burners = b if burners is None else burners.fuse(b)
burners_o = add("Burners", burners)

# Continuous grates (simple lattice)
grate = None
gz, gh, gw = top_z, 22.0, 14.0
gx0, gx1, gy0, gy1 = 55.0, W - 55.0, 95.0, 635.0
for gx in [120, 280, 430, 580, 670]:
    bar = box(gw, gy1 - gy0, gh, gx - gw / 2, gy0, gz)
    grate = bar if grate is None else grate.fuse(bar)
for gy in [170, 320, 470, 600]:
    bar = box(gx1 - gx0, gw, gh, gx0, gy - gw / 2, gz)
    grate = grate.fuse(bar)
grates_o = add("Grates", grate)

# Control knobs on the backguard (facing front, +Y)
knobs = None
kz = COOKTOP_H + (H - COOKTOP_H) * 0.42
for i in range(5):
    kx = 90.0 + (W - 180.0) * i / 4.0
    k = cyly(18, 28, kx, BG_DEPTH, kz)
    knobs = k if knobs is None else knobs.fuse(k)
knobs_o = add("Knobs", knobs)

# Control display
display = add("Display", box(230, 8, 60, CX - 115, BG_DEPTH - 4,
                             COOKTOP_H + (H - COOKTOP_H) * 0.70))

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
print("Overall (mm)  W x H x D = %.1f x %.1f x %.1f"
      % (bb.XLength, bb.ZLength, bb.YLength))
print("Overall (in)  W x H x D = %.2f x %.2f x %.2f"
      % (bb.XLength / IN, bb.ZLength / IN, bb.YLength / IN))
