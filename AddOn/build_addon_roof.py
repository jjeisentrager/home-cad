# -*- coding: utf-8 -*-
"""todo#1: rebuild the AddOn roof as a CLEAN gable so the rafters actually seat
against a continuous ridge board (the old interactive PartDesign truss had a
messy ridge/rafter junction).

Built in the SAME local frame as the old AddOn_RoofFrame so the existing House/
AddOn_Assembly link (placement unchanged) still drops it onto the walls:
  ridge along local Y at X=0, ridge top Z=152, eave bottom ~Z=-1905,
  eave-to-eave X[-4489,4489], length Y[-8890,0]  (pitch ~5.5:12).
Members: continuous ridge board, rafter pairs seating on the ridge sides,
ceiling joists (bottom chord) tying the rafter feet, gable-end studs.
Wrapped in App::Part "Part" (label RoofFrame) for the link.

Run headless:  freecadcmd build_addon_roof.py   (then recolor_brown.py offscreen)
Units: mm.
"""
import os
import FreeCAD as App
import Part
import Mesh

V = App.Vector
HALF = 4489.0          # eave X (half span, incl overhang)
WALL_HALF = 4064.0     # rafter seat / wall bearing (425 overhang)
RIDGE_Z = 152.0        # ridge top
RIDGE_HW = 19.0        # ridge board half width (X[-19,19])
RD = 184.0             # rafter / ridge depth (2x8, plumb)
RT = 38.0              # rafter thickness (along Y)
Y0, Y1 = -8890.0, 0.0  # ridge length span
SPACING = 406.4        # 16" o.c.
SLOPE = (RIDGE_Z - (-1905.0)) / (HALF - RIDGE_HW)   # ~0.460 (5.5:12)
CJ_D = 140.0           # ceiling joist depth (2x6)

DOC = "AddOn_RoofFrame"
doc = App.newDocument(DOC)
solids = []


def add(name, shp):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shp
    return o


def z_top(x):
    """rafter top-edge Z at |x| (from ridge side to eave)."""
    return RIDGE_Z - SLOPE * (abs(x) - RIDGE_HW)


def rafter(sign, y):
    """one rafter solid: parallelogram in X-Z extruded RT along +Y at y."""
    x_in = sign * RIDGE_HW
    x_out = sign * HALF
    zt_in = RIDGE_Z
    zt_out = z_top(HALF)
    pts = [V(x_in, y, zt_in), V(x_out, y, zt_out),
           V(x_out, y, zt_out - RD), V(x_in, y, zt_in - RD)]
    face = Part.Face(Part.makePolygon(pts + [pts[0]]))
    return face.extrude(V(0, RT, 0))


# ridge board (continuous), top at RIDGE_Z
solids.append(("Ridge", Part.makeBox(2 * RIDGE_HW, (Y1 - Y0), RD,
                                     V(-RIDGE_HW, Y0, RIDGE_Z - RD))))

# rafters both sides at 16" o.c.
y = Y1
i = 0
rafters = []
while y >= Y0 - 1e-6:
    yy = max(y - RT, Y0)         # keep within length
    rafters.append(Part.makeCompound([rafter(+1, yy), rafter(-1, yy)]))
    y -= SPACING
    i += 1
solids.append(("Rafters", Part.makeCompound(rafters)))

# ceiling joists (bottom chord) tying rafter feet, at wall-top level
seat_z = z_top(WALL_HALF)        # rafter top at wall
cj = []
y = Y1
while y >= Y0 - 1e-6:
    yy = max(y - RT, Y0)
    cj.append(Part.makeBox(2 * WALL_HALF, RT, CJ_D,
                           V(-WALL_HALF, yy, seat_z - RD - CJ_D)))
    y -= SPACING
solids.append(("CeilingJoists", Part.makeCompound(cj)))

# gable-end studs at Y0 and Y1
gable = []
for yend in (Y1 - RT, Y0):
    x = -WALL_HALF + 600.0
    while x <= WALL_HALF - 600.0:
        ztop = z_top(x) - RD              # underside of rafter at this x
        zbot = seat_z - RD                # top of ceiling joist line
        if ztop - zbot > 50:
            gable.append(Part.makeBox(RT, RT, ztop - zbot, V(x - RT / 2, yend, zbot)))
        x += 600.0
solids.append(("GableStuds", Part.makeCompound(gable)))

objs = [add(n, s) for n, s in solids]
part = doc.addObject("App::Part", "Part")
part.Label = "RoofFrame"
for o in objs:
    part.addObject(o)
doc.recompute()

OUT = os.path.dirname(os.path.abspath(__file__))
doc.saveAs(os.path.join(OUT, DOC + ".FCStd"))
comp = Part.makeCompound([o.Shape for o in objs])
b = comp.BoundBox
print("AddOn roof rebuilt  X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]  rafters=%d pitch=%.2f:12"
      % (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax, len(rafters), SLOPE * 12))
print("ADDON_ROOF_DONE")
