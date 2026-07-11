# -*- coding: utf-8 -*-
"""AddOn roof: STICK FRAMED above the chord line (so it matches the main-house
roof), carried on heavy TIMBER BOTTOM CHORDS -- and the existing steel I-BEAM is
one of those chords, with the others spaced off it.

The I-beam (AddOn/AddOn_Beams.FCStd) is the flush beam across the AddOn's open
side, where the addition meets the house:  world X[7348,15185] Y[7893,8109]
Z[4686,5042].  It runs in the SAME direction as the roof's bottom chords, so it
serves as the chord at that end.  Chords are then spaced at equal bays from the
I-beam centreline (world Y 8000.9) out to the gable wall (world Y 14051.9):
3 bays of 2017 mm (6'-7"), giving timber chords at world Y 10017.9 / 12034.9 /
14051.9.  The I-beam itself is NOT redrawn here -- it already exists.

Frame mapping (measured from House.FCStd, see _scan/roofmap.py):
    world Y = 16534.31 + localY      world Z = 6985.0 + localZ(final)
Everything below is built PRE-SHIFT and then translated by ZSHIFT at the end.

Stick framing matches Main/build_main_roof.py: 2x10 rafters (235 deep, 38 thick)
at 406.4 (16") o.c. on a 38-wide ridge board, 5.5:12.

ROOF LENGTH FIX: the Y1 end used to run to world Y 16534, i.e. 2.4 m past the
outboard wall (the main roof only overhangs 400).  Y1 is now set so the roof
overhangs that wall by 400, like the main roof.  The Y0 end is unchanged -- it
still dies into the main-house ridge (world Y ~3982 vs the main ridge at 3962.5).

Run headless:  freecadcmd build_addon_roof.py   (then recolor_brown.py offscreen)
Units: mm.
"""
import os
import FreeCAD as App
import Part

V = App.Vector

ZSHIFT = -280.0        # keeps the AddOn ridge level with the main-house ridge
HALF = 4489.0          # eave X (half span incl. 425 overhang)
WALL_HALF = 4064.0     # wall bearing
RIDGE_Z = 152.0        # deck plane at the ridge (pre-shift)
RIDGE_HW = 19.0        # ridge board half width (38 total) -- as the main roof
RD = 235.0             # rafter depth: 2x10, as the main roof
RT = 38.0              # rafter thickness
SPACING = 406.4        # 16" o.c.
SLOPE = (RIDGE_Z - (-1905.0)) / (HALF - RIDGE_HW)   # 0.4602 == 5.52:12

# --- length, in roof-local Y (world Y = 16534.31 + localY) -------------------
Y_WALL_OUT = -2412.3   # outboard wall outer face (world 14122)
Y1 = Y_WALL_OUT + 400.0            # 400 overhang past it, like the main roof
Y0 = -12553.0                      # unchanged: dies into the main-house ridge

# --- bottom chords: heavy timber, spaced off the I-beam ---------------------
# world Y 8000.9 (the I-BEAM, not drawn here) / 10017.9 / 12034.9 / 14051.9
CHORD_Y = [-6516.5, -4499.5, -2482.5]   # local Y of the three timber chords
CHORD_W = 203.0        # 8" along Y
CHORD_D = 254.0        # 10" deep
GABLE_Y = -2482.5      # gable wall centreline (the last chord doubles as its tie)

DOC = "AddOn_RoofFrame"
doc = App.newDocument(DOC)


def z_deck(x):
    """top of the sheathing plane at |x|."""
    return RIDGE_Z - SLOPE * (abs(x) - RIDGE_HW)


def rafter(sign, y):
    """one rafter: parallelogram in X-Z (plumb cuts) extruded RT along +Y."""
    xi, xo = sign * RIDGE_HW, sign * HALF
    zi, zo = RIDGE_Z, z_deck(HALF)
    pts = [V(xi, y, zi), V(xo, y, zo), V(xo, y, zo - RD), V(xi, y, zi - RD)]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, RT, 0))


solids = []

# --- ridge board -------------------------------------------------------------
solids.append(("Ridge", Part.makeBox(2 * RIDGE_HW, Y1 - Y0, RD,
                                     V(-RIDGE_HW, Y0, RIDGE_Z - RD))))

# --- rafters, 16" o.c., both slopes -----------------------------------------
rafters = []
y = Y1
while y >= Y0 - 1e-6:
    yy = max(y - RT, Y0)
    rafters.append(Part.makeCompound([rafter(+1, yy), rafter(-1, yy)]))
    y -= SPACING
solids.append(("Rafters", Part.makeCompound(rafters)))

# --- bottom chords: tuck under the rafter feet -------------------------------
chord_top = z_deck(WALL_HALF) - RD       # underside of the rafters at the wall
chords = []
for cy in CHORD_Y:
    chords.append(Part.makeBox(2 * WALL_HALF, CHORD_W, CHORD_D,
                               V(-WALL_HALF, cy - CHORD_W / 2.0,
                                 chord_top - CHORD_D)))
solids.append(("BottomChords", Part.makeCompound(chords)))

# --- gable studs on the outboard wall (its chord is the tie) -----------------
gable = []
x = -WALL_HALF + 600.0
while x <= WALL_HALF - 600.0:
    ztop = z_deck(x) - RD
    if ztop - chord_top > 50:
        gable.append(Part.makeBox(89.0, 89.0, ztop - chord_top,
                                  V(x - 44.5, GABLE_Y - 44.5, chord_top)))
    x += 600.0
solids.append(("GableStuds", Part.makeCompound(gable)))

solids = [(n, s.translated(V(0, 0, ZSHIFT))) for n, s in solids]


def add(name, shp):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shp
    return o


objs = [add(n, s) for n, s in solids]
part = doc.addObject("App::Part", "Part")
part.Label = "RoofFrame"
for o in objs:
    part.addObject(o)
doc.recompute()

OUT = os.path.dirname(os.path.abspath(__file__))
doc.saveAs(os.path.join(OUT, DOC + ".FCStd"))

rep = open(os.path.join(OUT, "roof_report.txt"), "w")
rep.write("stick framed: 2x10 rafters @ %.1f o.c., %.2f:12, ridge board %.0f wide\n"
          % (SPACING, SLOPE * 12, 2 * RIDGE_HW))
rep.write("rafters=%d  timber chords=%d (+ the I-beam = 4 chords total)\n"
          % (len(rafters), len(CHORD_Y)))
rep.write("chord top (world Z) = %.1f ; I-beam soffit = 4686.3, I-beam top = 5041.9\n"
          % (chord_top + ZSHIFT + 6985.0))
for cy in CHORD_Y:
    rep.write("  chord local Y=%9.1f -> world Y=%.1f\n" % (cy, 16534.31 + cy))
rep.write("roof local Y[%.1f,%.1f] -> world Y[%.1f,%.1f]  (outboard wall face "
          "world 14122 -> 400 overhang)\n" % (Y0, Y1, 16534.31 + Y0, 16534.31 + Y1))
for o in objs:
    b = o.Shape.BoundBox
    rep.write("%-14s n=%3d  X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]\n"
              % (o.Name, len(o.Shape.Solids), b.XMin, b.XMax, b.YMin, b.YMax,
                 b.ZMin, b.ZMax))
rep.close()
print("ADDON_ROOF_DONE")
