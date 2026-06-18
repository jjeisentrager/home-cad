# -*- coding: utf-8 -*-
"""todo#2 (part 1): build a main-house gable roof.

Geometry is in TRUE WORLD coords (the Foundation frame: X[0,17043] Y[0,7925],
which House resolves 1:1), so a House link with identity placement drops it
correctly onto the main house.  Ridge runs along the LONG axis (X) at mid-span
Y=3962.5; rafters slope in Y down to eaves at the Y=0 and Y=7925 walls.  Wall-
top (rafter seat) at Z=5041 (subfloor top 2603.5 + 8' wall); pitch 5.5:12 to
match the AddOn roof; ridge top Z~6857.  ~400mm eave overhang.

Members: continuous ridge board, rafter pairs seating on the ridge, ceiling
joists, gable-end studs at X=0 and X=17043.  Wrapped in App::Part "Part".

Run headless:  freecadcmd build_main_roof.py   (then color brown offscreen)
Units: mm.
"""
import os
import FreeCAD as App
import Part

V = App.Vector
X0, X1 = 0.0, 17043.0       # house length (ridge runs along X)
YMID = 3962.5               # ridge Y (mid-span)
HALF = 3962.5               # ridge to wall (Y)
EAVE_Z = 5041.0             # wall top / rafter seat
OVER = 400.0                # eave overhang
RIDGE_HW = 19.0
RD = 235.0                  # rafter depth (2x10, plumb)
RT = 38.0                   # rafter thickness (along X)
SPACING = 406.4
SLOPE = 5.5 / 12.0
CJ_D = 140.0
RIDGE_Z = EAVE_Z + SLOPE * HALF        # ~6857

DOC = "MainRoof"
doc = App.newDocument(DOC)


def add(name, shp):
    o = doc.addObject("Part::Feature", name); o.Shape = shp; return o


def z_top(y):
    """rafter top-edge Z at distance |y-YMID| from ridge."""
    return RIDGE_Z - SLOPE * (abs(y - YMID) - RIDGE_HW)


def rafter(sign, x):
    """rafter parallelogram in Y-Z, extruded RT along +X at x. sign=+1 east(+Y)."""
    y_in = YMID + sign * RIDGE_HW
    y_out = YMID + sign * (HALF + OVER)
    zt_in = RIDGE_Z
    zt_out = z_top(y_out)
    pts = [V(x, y_in, zt_in), V(x, y_out, zt_out),
           V(x, y_out, zt_out - RD), V(x, y_in, zt_in - RD)]
    face = Part.Face(Part.makePolygon(pts + [pts[0]]))
    return face.extrude(V(RT, 0, 0))


solids = []
# ridge board
solids.append(("Ridge", Part.makeBox((X1 - X0), 2 * RIDGE_HW, RD,
                                      V(X0, YMID - RIDGE_HW, RIDGE_Z - RD))))
# rafters both sides
rafters = []
x = X0
while x <= X1 - 1e-6:
    xx = min(x, X1 - RT)
    rafters.append(Part.makeCompound([rafter(+1, xx), rafter(-1, xx)]))
    x += SPACING
solids.append(("Rafters", Part.makeCompound(rafters)))
# ceiling joists across the width at wall top
cj = []
x = X0
while x <= X1 - 1e-6:
    xx = min(x, X1 - RT)
    cj.append(Part.makeBox(RT, 2 * HALF, CJ_D, V(xx, 0.0, EAVE_Z - CJ_D)))
    x += SPACING
solids.append(("CeilingJoists", Part.makeCompound(cj)))
# gable studs at X0 and X1
gable = []
for xend in (X0, X1 - RT):
    y = YMID - HALF + 600.0
    while y <= YMID + HALF - 600.0:
        ztop = z_top(y) - RD
        if ztop - EAVE_Z > 50:
            gable.append(Part.makeBox(RT, RT, ztop - EAVE_Z, V(xend, y - RT / 2, EAVE_Z)))
        y += 600.0
solids.append(("GableStuds", Part.makeCompound(gable)))

objs = [add(n, s) for n, s in solids]
part = doc.addObject("App::Part", "Part"); part.Label = "MainRoof"
for o in objs:
    part.addObject(o)
doc.recompute()

OUT = os.path.dirname(os.path.abspath(__file__))
doc.saveAs(os.path.join(OUT, DOC + ".FCStd"))
comp = Part.makeCompound([o.Shape for o in objs]); b = comp.BoundBox
print("Main roof built  X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]  rafters=%d ridgeZ=%.0f"
      % (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax, len(rafters), RIDGE_Z))
print("MAIN_ROOF_DONE")
