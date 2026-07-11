# -*- coding: utf-8 -*-
"""AddOn roof -- CONNECTOR section: the short strip between the I-beam and the
main house, where the AddOn's gable dies into the main-house ridge.

This is a SEPARATE piece of the assembly from AddOn_RoofFrame (the timber frame
over the room itself).  It stays STICK FRAMED, so it matches the rest of the
house roof: 2x10 rafters at 16" o.c. on a 38-wide ridge board, 5.52:12 -- the
same members as Main/build_main_roof.py.

Same roof-local frame as AddOn_RoofFrame, so it links into House with the same
placement:
    world Y = 16534.31 + localY      world Z = 6985.0 + localZ(final)
Runs from the main-house ridge (local Y -12553 -> world Y 3981, vs the main ridge
at 3962.5) to the I-beam centreline (local Y -8533.4 -> world Y 8000.9), where
the timber frame takes over.

Run headless:  freecadcmd build_roof_connector.py  (then link_roof_connector.py)
Units: mm.
"""
import os
import FreeCAD as App
import Part

V = App.Vector

W2L_Y = 16534.31

ZSHIFT = -280.0
HALF = 4489.0
WALL_HALF = 4064.0
RIDGE_Z = 152.0
RIDGE_HW = 19.0        # ridge board, 38 total -- as the main roof
RD = 235.0             # 2x10 rafters -- as the main roof
RT = 38.0
SPACING = 406.4        # 16" o.c.
SLOPE = (RIDGE_Z - (-1905.0)) / (HALF - RIDGE_HW)

Y0 = -12553.0                    # dies into the main-house ridge
Y1 = 8000.9 - W2L_Y              # the I-beam centreline (-8533.4)

DOC = "AddOn_RoofConnector"
doc = App.newDocument(DOC)


def z_deck(x):
    return RIDGE_Z - SLOPE * (abs(x) - RIDGE_HW)


def rafter(sign, y):
    xi, xo = sign * RIDGE_HW, sign * HALF
    zi, zo = RIDGE_Z, z_deck(HALF)
    pts = [V(xi, y, zi), V(xo, y, zo), V(xo, y, zo - RD), V(xi, y, zi - RD)]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, RT, 0))


solids = [("Ridge", Part.makeBox(2 * RIDGE_HW, Y1 - Y0, RD,
                                 V(-RIDGE_HW, Y0, RIDGE_Z - RD)))]

rafters = []
y = Y1
while y >= Y0 - 1e-6:
    yy = max(y - RT, Y0)
    rafters.append(Part.makeCompound([rafter(+1, yy), rafter(-1, yy)]))
    y -= SPACING
solids.append(("Rafters", Part.makeCompound(rafters)))

# ceiling joists tying the rafter feet, as the main roof does
seat = z_deck(WALL_HALF)
cj = []
y = Y1
while y >= Y0 - 1e-6:
    yy = max(y - RT, Y0)
    cj.append(Part.makeBox(2 * WALL_HALF, RT, 140.0,
                           V(-WALL_HALF, yy, seat - RD - 140.0)))
    y -= SPACING
solids.append(("CeilingJoists", Part.makeCompound(cj)))

solids = [(n, s.translated(V(0, 0, ZSHIFT))) for n, s in solids]

objs = []
for n, s in solids:
    o = doc.addObject("Part::Feature", n)
    o.Shape = s
    objs.append(o)
part = doc.addObject("App::Part", "Part")
part.Label = "RoofConnector"
for o in objs:
    part.addObject(o)
doc.recompute()

OUT = os.path.dirname(os.path.abspath(__file__))
doc.saveAs(os.path.join(OUT, DOC + ".FCStd"))

rep = open(os.path.join(OUT, "roof_connector_report.txt"), "w")
rep.write("STICK section (separate assembly piece), 2x10 @ %.1f o.c., %.2f:12\n"
          % (SPACING, SLOPE * 12))
rep.write("local Y[%.1f,%.1f] -> world Y[%.1f,%.1f]  (main ridge 3962.5 .. "
          "I-beam 8000.9)\n" % (Y0, Y1, Y0 + W2L_Y, Y1 + W2L_Y))
rep.write("rafters=%d\n" % len(rafters))
for o in objs:
    b = o.Shape.BoundBox
    rep.write("%-15s n=%3d  X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]\n"
              % (o.Name, len(o.Shape.Solids), b.XMin, b.XMax, b.YMin, b.YMax,
                 b.ZMin, b.ZMax))
rep.close()
print("ROOF_CONNECTOR_DONE")
