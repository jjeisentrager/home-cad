# -*- coding: utf-8 -*-
"""
Build a simplified CAD model of the:
  Kraus Kore Drop-in / Undermount 33 x 22 in Stainless Steel Single Bowl
  16-Gauge Workstation Kitchen Sink   (model KWT310-33)

General representation only - no moving parts. Captures:
  - Flat mounting deck / rim (33 x 22 in) with 2 faucet/accessory holes
  - Single rectangular bowl (31 x 16 x 9 in)
  - Integrated "workstation" ledge/track along the front & back of the bowl
  - Rear drain opening
  - Correct overall outside dimensions

Run headless:  freecadcmd build_sink.py

Units: millimetres.  Orientation: X = length, Y = width (front/back),
Z = up.  The rim top sits at Z = 0; the bowl drops below.
"""

import os
import FreeCAD as App
import Part

IN = 25.4  # mm per inch

# --- Dimensions (KWT310-33) -------------------------------------------------
L = 33.0 * IN        # outer length = 838.2
Wd = 22.0 * IN       # outer width  = 558.8
DEPTH = 9.0 * IN     # bowl depth   = 228.6
BOWL_L = 31.0 * IN   # bowl length  = 787.4
BOWL_W = 16.0 * IN   # bowl width   = 406.4

# --- Design parameters ------------------------------------------------------
DECK_T = 8.0         # mounting deck / rim thickness
WALL_T = 12.0        # bowl wall thickness
BOT_T = 12.0         # bowl bottom thickness
LEDGE_W = 24.0       # workstation ledge depth (into the bowl)
LEDGE_DROP = 28.0    # how far the ledge sits below the rim
LEDGE_T = 10.0       # ledge thickness

CX = L / 2.0
CY = Wd / 2.0

OUT = os.path.dirname(os.path.abspath(__file__))
DOCNAME = "KWT310-33"


def box(l, w, h, x, y, z):
    return Part.makeBox(l, w, h, App.Vector(x, y, z))


def cyl(r, h, x, y, z):
    return Part.makeCylinder(r, h, App.Vector(x, y, z), App.Vector(0, 0, 1))


def add(name, shape):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shape
    return o


# --- build ------------------------------------------------------------------
doc = App.newDocument(DOCNAME)

# Mounting deck / rim: flat plate with the bowl opening cut out
deck = box(L, Wd, DECK_T, 0, 0, -DECK_T)
opening = box(BOWL_L, BOWL_W, DECK_T + 2, CX - BOWL_L / 2, CY - BOWL_W / 2, -DECK_T - 1)
deck = deck.cut(opening)

# Two faucet / accessory holes through the rear deck
back_mid = (CY + BOWL_W / 2 + Wd) / 2.0     # middle of the rear deck strip
faucet = cyl(18.0, DECK_T + 4, CX, back_mid, -DECK_T - 2)
soap = cyl(14.0, DECK_T + 4, CX - 130.0, back_mid, -DECK_T - 2)
deck = deck.cut(faucet).cut(soap)
deck_o = add("Deck_Rim", deck)

# Bowl: outer solid minus inner cavity
bo = box(BOWL_L + 2 * WALL_T, BOWL_W + 2 * WALL_T, DEPTH,
         CX - BOWL_L / 2 - WALL_T, CY - BOWL_W / 2 - WALL_T, -DEPTH)
cav = box(BOWL_L, BOWL_W, DEPTH,
          CX - BOWL_L / 2, CY - BOWL_W / 2, -(DEPTH - BOT_T))
bowl = bo.cut(cav)

# Rear drain opening in the bowl floor
drain = cyl(45.0, BOT_T + 4, CX, CY - 40.0, -DEPTH - 2)
bowl = bowl.cut(drain)

# Workstation ledge/track along the front and back inner walls
front_ledge = box(BOWL_L, LEDGE_W, LEDGE_T,
                  CX - BOWL_L / 2, CY - BOWL_W / 2, -LEDGE_DROP - LEDGE_T)
back_ledge = box(BOWL_L, LEDGE_W, LEDGE_T,
                 CX - BOWL_L / 2, CY + BOWL_W / 2 - LEDGE_W, -LEDGE_DROP - LEDGE_T)
bowl = bowl.fuse(front_ledge).fuse(back_ledge)
bowl_o = add("Bowl", bowl)

doc.recompute()

# --- save / export ----------------------------------------------------------
fcstd = os.path.join(OUT, DOCNAME + ".FCStd")
step = os.path.join(OUT, DOCNAME + ".step")
stl = os.path.join(OUT, DOCNAME + ".stl")

doc.saveAs(fcstd)

solids = [deck_o, bowl_o]
Part.export(solids, step)

import Mesh
compound = Part.makeCompound([o.Shape for o in solids])
Mesh.Mesh(compound.tessellate(1.0)).write(stl)

bb = compound.BoundBox
print("Saved: %s" % fcstd)
print("Saved: %s" % step)
print("Saved: %s" % stl)
print("Overall (mm)  L x W x Depth = %.1f x %.1f x %.1f"
      % (bb.XLength, bb.YLength, bb.ZLength))
print("Overall (in)  L x W x Depth = %.2f x %.2f x %.2f"
      % (bb.XLength / IN, bb.YLength / IN, bb.ZLength / IN))
