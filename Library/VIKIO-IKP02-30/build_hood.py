# -*- coding: utf-8 -*-
"""
Build a simplified CAD model of the:
  VIKIO 30 in Ducted 800-CFM Recirculating Stainless Steel
  Wall-Mounted (pyramid chimney) Range Hood

General representation only - no moving parts. Captures:
  - Pyramid canopy (30 in wide), back flat against the wall
  - Telescopic chimney / duct cover rising above the canopy
  - Recessed underside with baffle filter panel + 2 LED lights
  - Front touchscreen control panel
  - Correct width / depth; representative (adjustable) chimney height

Run headless:  freecadcmd build_hood.py

Units: millimetres.  X = width, Y = depth (wall/back = y0, front = +Y), Z = up.
The canopy bottom (filter face) sits at Z = 0; the chimney rises above.
"""

import os
import FreeCAD as App
import Part

IN = 25.4

# --- Dimensions -------------------------------------------------------------
W = 30.0 * IN        # width = 762.0
D = 19.7 * IN        # depth = 500.4  (VIKIO pyramid wall hood)
CANOPY_H = 10.0 * IN     # pyramid canopy height = 254.0
TOTAL_H = 37.4 * IN      # representative assembled height = 950.0

# Chimney (duct cover) footprint - sits at the back (against the wall)
CH_W, CH_D = 240.0, 190.0       # lower chimney section
CH_W2, CH_D2 = 210.0, 165.0     # upper (telescopic) section

CX = W / 2.0
OUT = os.path.dirname(os.path.abspath(__file__))
DOCNAME = "VIKIO-IKP02-30"


def box(l, w, h, x, y, z):
    return Part.makeBox(l, w, h, App.Vector(x, y, z))


def cylz(r, h, x, y, z):
    return Part.makeCylinder(r, h, App.Vector(x, y, z), App.Vector(0, 0, 1))


def rect_wire(x0, x1, y0, y1, z):
    p = [App.Vector(x0, y0, z), App.Vector(x1, y0, z),
         App.Vector(x1, y1, z), App.Vector(x0, y1, z), App.Vector(x0, y0, z)]
    return Part.makePolygon(p)


def add(name, shape):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shape
    return o


# --- build ------------------------------------------------------------------
doc = App.newDocument(DOCNAME)

# Pyramid canopy: loft from the full bottom rectangle to the chimney footprint.
# Back edge stays at y = 0 (flat against the wall); front & sides slope up/in.
bottom = rect_wire(0, W, 0, D, 0)
top = rect_wire(CX - CH_W / 2, CX + CH_W / 2, 0, CH_D, CANOPY_H)
canopy = Part.makeLoft([bottom, top], True, True)   # solid, ruled (flat faces)

# Recess the underside and drop in a baffle filter + lights
recess = box(W - 100, D - 100, 18, 50, 50, -1)
canopy = canopy.cut(recess)
canopy_o = add("Canopy", canopy)

filt = add("Filter", box(W - 100, D - 100, 10, 50, 50, 2))
light_l = add("Light_L", cylz(22, 9, CX - 150, D - 130, 1))
light_r = add("Light_R", cylz(22, 9, CX + 150, D - 130, 1))

# Front touchscreen control panel (lower front)
control = add("Control_Panel", box(170, 12, 40, CX - 85, D - 52, 18))

# Telescopic chimney / duct cover (two sections, at the back)
ch_low_h = 360.0
ch_low = add("Chimney_Lower",
             box(CH_W, CH_D, ch_low_h, CX - CH_W / 2, 0, CANOPY_H))
ch_up_h = TOTAL_H - CANOPY_H - ch_low_h
ch_up = add("Chimney_Upper",
            box(CH_W2, CH_D2, ch_up_h, CX - CH_W2 / 2, 0, CANOPY_H + ch_low_h))

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
