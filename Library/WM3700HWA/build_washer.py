# -*- coding: utf-8 -*-
"""
Build a simplified CAD model of the:
  LG 27" 4.5 cu. ft. Front-Load Steam Washer  (model WM3700HWA, white)

General representation only - no moving parts. Captures:
  - White cabinet body at the correct outside dimensions
  - Top control console with detergent drawer (left), display (centre) and
    a rotary dial / selector knob (right)
  - Large round porthole door: light bezel ring + bulging tinted glass window

Run headless:  freecadcmd build_washer.py

Units: millimetres.
"""

import os
import FreeCAD as App
import Part

IN = 25.4  # mm per inch

# --- Overall outside dimensions (WM3700HWA) --------------------------------
W = 27.0 * IN     # width  = 685.80 mm
H = 39.0 * IN     # height = 990.60 mm
D = 30.25 * IN    # depth  = 768.35 mm  (door closed)

PFRONT = D        # Y of the front face

OUT = os.path.dirname(os.path.abspath(__file__))
DOCNAME = "WM3700HWA"


def box(l, w, h, x, y, z):
    return Part.makeBox(l, w, h, App.Vector(x, y, z))


def cyl(r, h, x, y, z, dx=0, dy=1, dz=0):
    return Part.makeCylinder(r, h, App.Vector(x, y, z), App.Vector(dx, dy, dz))


def add(name, shape):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shape
    return o


# --- build ------------------------------------------------------------------
doc = App.newDocument(DOCNAME)

# Cabinet body
cabinet = add("Cabinet", box(W, D, H, 0, 0, 0))

# ---- Top control console ---------------------------------------------------
# A shallow inset band across the top of the front; features stand proud of it.
CON_H = 150.0                 # height of the console band
con_z0 = H - CON_H

# Detergent dispenser drawer (top-left), protruding with a grip lip
dd_x0, dd_w = 30.0, 250.0
dd_z0, dd_h = con_z0 + 15.0, 100.0
drawer = add("Detergent_Drawer",
             box(dd_w, 14.0, dd_h, dd_x0, PFRONT, dd_z0))
# grip lip along the bottom of the drawer
lip = add("Drawer_Handle",
          box(dd_w, 22.0, 12.0, dd_x0, PFRONT, dd_z0))

# Display panel (centre)
disp = add("Display",
           box(190.0, 5.0, 80.0, 315.0, PFRONT, con_z0 + 35.0))

# Rotary selector dial / knob (right)
dial = add("Dial",
           cyl(46.0, 26.0, 590.0, PFRONT, con_z0 + 75.0))

# ---- Round porthole door ---------------------------------------------------
cx = W / 2.0                  # door horizontal centre
cz = 18.0 * IN                # door centre height (~18" off the floor)
R_OUT = 188.0                 # outer bezel radius
R_GLASS = 150.0               # glass / window radius

# Bezel: annular ring standing proud of the front face
bezel_ring = cyl(R_OUT, 46.0, cx, PFRONT, cz)
bezel_ring = bezel_ring.cut(cyl(R_GLASS, 60.0, cx, PFRONT - 5.0, cz))
bezel = add("Door_Bezel", bezel_ring)

# Glass window: tinted disc set inside the bezel, with a shallow domed front
# for the classic porthole look (a spherical cap of the glass-radius circle).
Yf = PFRONT + 18.0           # glass cylinder front plane
BULGE = 22.0                 # how far the dome bulges past Yf
glass_cyl = cyl(R_GLASS, Yf - (PFRONT - 12.0), cx, PFRONT - 12.0, cz)
Rs = (R_GLASS ** 2 + BULGE ** 2) / (2.0 * BULGE)             # cap sphere radius
dome = Part.makeSphere(Rs, App.Vector(cx, Yf + BULGE - Rs, cz))
dome = dome.cut(box(2 * Rs + 40, 2 * Rs + 40, 2 * Rs + 40,
                    cx - Rs - 20, Yf - (2 * Rs + 40),
                    cz - Rs - 20))                            # keep front cap (y >= Yf)
glass = add("Door_Glass", glass_cyl.fuse(dome))

doc.recompute()

# --- save / export ----------------------------------------------------------
fcstd = os.path.join(OUT, DOCNAME + ".FCStd")
step = os.path.join(OUT, DOCNAME + ".step")
stl = os.path.join(OUT, DOCNAME + ".stl")

doc.saveAs(fcstd)

solids = [cabinet, drawer, lip, disp, dial, bezel, glass]
Part.export(solids, step)

import Mesh
compound = Part.makeCompound([o.Shape for o in solids])
Mesh.Mesh(compound.tessellate(1.0)).write(stl)

bb = compound.BoundBox
rep = open(os.path.join(OUT, "build_report.txt"), "w")
rep.write("Saved: %s\n" % fcstd)
rep.write("Saved: %s\n" % step)
rep.write("Saved: %s\n" % stl)
rep.write("Overall (mm)  W x H x D = %.1f x %.1f x %.1f\n"
          % (bb.XLength, bb.ZLength, bb.YLength))
rep.write("Overall (in)  W x H x D = %.2f x %.2f x %.2f\n"
          % (bb.XLength / IN, bb.ZLength / IN, bb.YLength / IN))
rep.close()
