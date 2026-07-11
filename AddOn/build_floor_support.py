# -*- coding: utf-8 -*-
"""AddOn floor support: two dropped beams on concrete piers under the floor joists
(deck-style pier + beam, no posts -- only 28.5" from grade to top of subfloor).

Built directly in WORLD (House) coordinates so it links into House.FCStd at
identity placement.

World facts this is pinned to (measured from House.FCStd):
  AddOn joists   run along Y, bottom Z=2362.2, top Z=2590.8 (228.6 deep, 16" o.c.)
                 bearing at the house rim Y~7977 -> outboard end Y~14035
  subfloor top   Z=2603.5   -> grade = 2603.5 - 28.5" = Z 1879.6
  front wall     Y[13982,14122]  (outboard, gable end)
  side walls     X[7348,7477] and X[15184,15313]  (run along Y, ON the outer joists)
  floor width    X[7360.8, 15312.7]

Design (sizes from IRC/MRC 2021 tables):
  * Beams are DROPPED (joists bear on top), 3-ply 2x12 PT (114.3 x 285.75).
    Beam top = joist bottom = Z 2362.2 -> beam bottom Z 2076.4 = 7.75" over grade.
    Under 12" over exposed ground, so the girders MUST be pressure-treated
    (R317.1); joist bottom is 19.0" over grade, just clear of the 18" joist rule.
  * Beam 1 sits directly under the outboard front wall (Y 14040) -- the wall +
    roof load lands on the beam, NOT on a cantilever.  Beam 2 is midway back to
    the house (Y 11008).  Joist spans become 3031 / 3032 mm (9'-11" each).
    2x10 @ 16" o.c. is good to 15'-5" (SPF, Table R502.3.1(2)) / 14'-0" (SP), so
    the EXISTING JOISTS ARE FINE -- no lumber change needed (2x8 would also pass
    at 12'-3", but 2x10 keeps insulation depth and matches the house rim).
  * Beam sized off deck-beam Table R507.5(1): 3-2x12 SPF at a 10 ft joist span
    allows an 11'-3" beam span.  We use 5 piers per beam at 1959 mm (6'-5") o.c.
    -- a large margin, deliberately, because Beam 1 also carries the exterior
    wall + roof (a load case the deck tables do not cover).
  * The two end piers sit directly under the side walls, which run along Y on the
    outer joists and bring roof load down at exactly those points.
  * Pier = 12" round shaft on a 24" sq footing whose BOTTOM is at the Michigan
    42" frost line (R403.1.4 -- conditioned addition, no deck exception).
    Bearing >= 3" full beam width (R507.5.1) via a 1" galvanized STANDOFF base
    cast onto an anchor bolt (R507.5.2: positive connection, nails not allowed).

Run headless:  freecadcmd build_floor_support.py   (then color_floor_support.py
offscreen for colors)   Units: mm.
"""
import os
import FreeCAD as App
import Part

V = App.Vector

IN = 25.4

# --- world reference levels -------------------------------------------------
SUBFLOOR_TOP = 2603.5
GRADE = SUBFLOOR_TOP - 28.5 * IN          # 1879.6
JOIST_BOT = 2362.2                        # beams tuck under this

# --- beam: 3-ply 2x12 pressure treated --------------------------------------
PLY = 38.1                                # 1.5"
NPLY = 3
BEAM_W = NPLY * PLY                       # 114.3 (across = along Y)
BEAM_D = 11.25 * IN                       # 285.75 deep
BEAM_TOP = JOIST_BOT
BEAM_BOT = BEAM_TOP - BEAM_D              # 2076.45  -> 7.75" over grade (PT)

BEAM_X0, BEAM_X1 = 7360.8, 15312.7        # full floor width

BEAM_Y = [14040.0, 11008.0]               # end beam (under front wall), mid beam

# --- piers -------------------------------------------------------------------
PLATE_T = 1.0 * IN                        # galv. standoff base (1" off concrete)
PLATE_S = 178.0                           # 7" square base -- >3" bearing, full
                                          # beam width (114.3)
PIER_D = 12.0 * IN                        # 305 round shaft
PIER_TOP = BEAM_BOT - PLATE_T
FOOT_S = 24.0 * IN                        # 610 square footing
FOOT_T = 8.0 * IN                         # 203 thick
FROST = 42.0 * IN                         # Michigan frost depth
FOOT_BOT = GRADE - FROST                  # bearing below frost line
FOOT_TOP = FOOT_BOT + FOOT_T

PIER_X = [7412.5, 9371.4, 11330.3, 13289.2, 15248.1]   # ends under the side walls

DOC = "AddOn_FloorSupport"
doc = App.newDocument(DOC)


def add(name, shp):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shp
    return o


objs = []

# --- beams: three plies each, so the built-up beam reads as real lumber ------
for bi, cy in enumerate(BEAM_Y):
    plies = []
    y0 = cy - BEAM_W / 2.0
    for p in range(NPLY):
        plies.append(Part.makeBox(BEAM_X1 - BEAM_X0, PLY, BEAM_D,
                                  V(BEAM_X0, y0 + p * PLY, BEAM_BOT)))
    objs.append(add("Beam_%s" % ("End" if bi == 0 else "Mid"),
                    Part.makeCompound(plies)))

# --- piers + footings + bearing plates --------------------------------------
shafts, foots, plates = [], [], []
for cy in BEAM_Y:
    for cx in PIER_X:
        shafts.append(Part.makeCylinder(PIER_D / 2.0, PIER_TOP - FOOT_TOP,
                                        V(cx, cy, FOOT_TOP), V(0, 0, 1)))
        foots.append(Part.makeBox(FOOT_S, FOOT_S, FOOT_T,
                                  V(cx - FOOT_S / 2, cy - FOOT_S / 2, FOOT_BOT)))
        plates.append(Part.makeBox(PLATE_S, PLATE_S, PLATE_T,
                                   V(cx - PLATE_S / 2, cy - PLATE_S / 2, PIER_TOP)))
objs.append(add("Piers", Part.makeCompound(shafts)))
objs.append(add("Footings", Part.makeCompound(foots)))
objs.append(add("BearingPlates", Part.makeCompound(plates)))

part = doc.addObject("App::Part", "Part")
part.Label = "FloorSupport"
for o in objs:
    part.addObject(o)
doc.recompute()

OUT = os.path.dirname(os.path.abspath(__file__))
doc.saveAs(os.path.join(OUT, DOC + ".FCStd"))

rep = open(os.path.join(OUT, "floor_support_report.txt"), "w")
rep.write("grade Z=%.1f  joist bottom Z=%.1f  subfloor top Z=%.1f\n"
          % (GRADE, JOIST_BOT, SUBFLOOR_TOP))
rep.write("beam 3-ply 2x10 PT: %.1f wide x %.1f deep, Z[%.1f,%.1f]  (%.2f in over grade)\n"
          % (BEAM_W, BEAM_D, BEAM_BOT, BEAM_TOP, (BEAM_BOT - GRADE) / IN))
rep.write("beam Y centres: %s\n" % BEAM_Y)
rep.write("joist spans: house(7977)->mid=%.0f  mid->end=%.0f  cantilever=%.0f mm\n"
          % (BEAM_Y[1] - 7977, BEAM_Y[0] - BEAM_Y[1], 14035 - BEAM_Y[0]))
rep.write("piers: %d per beam at X=%s  spacing=%.0f mm (%.2f ft)\n"
          % (len(PIER_X), PIER_X, PIER_X[1] - PIER_X[0], (PIER_X[1] - PIER_X[0]) / 304.8))
rep.write("pier shaft d=%.0f  Z[%.1f,%.1f]; footing %.0f sq x %.0f, Z[%.1f,%.1f] (frost %.0f)\n"
          % (PIER_D, FOOT_TOP, PIER_TOP, FOOT_S, FOOT_T, FOOT_BOT, FOOT_TOP, FROST))
for o in objs:
    b = o.Shape.BoundBox
    rep.write("%-14s X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]\n"
              % (o.Name, b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))
rep.close()
print("FLOOR_SUPPORT_DONE")
