# -*- coding: utf-8 -*-
"""todo#2: rebuild the AddOn roof as a TIMBER FRAME (heavy exposed timbers) instead
of a stick-framed 16" o.c. rafter roof.  The main-house roof stays stick-framed;
only the AddOn is timber frame.

The roof ENVELOPE is unchanged from the previous build, so the existing House /
AddOn_Assembly link (placement untouched) still drops it onto the walls and the
cross-gable still dies into the main-house ridge:
  ridge along local Y at X=0, deck plane top Z=152 at the ridge,
  eave-to-eave X[-4489,4489], length Y[-12553,0], pitch ~5.5:12, then ZSHIFT -280.

Timber-frame anatomy (classic English purlin frame):
  * RIDGE BEAM        8x12, top face in the deck plane at the apex.
  * BENTS at 2511 mm (8'-3") o.c. -- 6 of them, not 16" o.c. sticks.  Each bent is
    a pair of PRINCIPAL RAFTERS (6x10) with their top faces in the deck plane.
  * TIE BEAMS (the "bottom chord") 8x10 -- only on EVERY OTHER bent, per the
    reference.  Those tied bents also get a KING POST and a pair of angled STRUTS.
  * The untied bents get a COLLAR TIE high up instead, so they still resist spread
    without a full bottom chord.
  * PURLINS 6x8 run bay-to-bay between the principal rafters (butting their sides,
    not passing through them), top face one common-rafter depth below the deck.
  * COMMON RAFTERS 4x6 at ~600 mm o.c. inside each bay, resting on the purlins and
    the ridge, tops in the deck plane -- they carry the sheathing.
  * Gable studs at the outer (Y1) end only; the Y0 end runs into the main roof.

Run headless:  freecadcmd build_addon_roof.py    (then color_roof.py offscreen)
Units: mm.
"""
import os
import FreeCAD as App
import Part

V = App.Vector

ZSHIFT = -280.0        # lower whole roof (matches main-house ridge height)
HALF = 4489.0          # eave X (half span, incl. overhang)
WALL_HALF = 4064.0     # wall bearing / rafter seat
RIDGE_Z = 152.0        # deck plane height at the ridge
RIDGE_HW = 101.6       # ridge beam half width (8x12 -> 203 wide)
RIDGE_D = 305.0        # ridge beam depth (12")
Y0, Y1 = -12553.0, 0.0
SLOPE = (RIDGE_Z - (-1905.0)) / (HALF - 19.0)   # 0.4602 -- unchanged pitch

NBAY = 5                                   # 6 bents
BENT_SP = (Y1 - Y0) / NBAY                 # 2510.6 mm o.c.

PR_W = 152.0           # principal rafter thickness along Y (6x10)
PR_D = 254.0           # principal rafter depth
PUR_W = 152.0          # purlin (6x8): 152 along the slope, 203 deep
PUR_D = 203.0
CR_W = 102.0           # common rafter (4x6)
CR_D = 152.0
CR_SP = 600.0
TIE_W = 203.0          # tie beam 8x10
TIE_D = 254.0
KP_W = 203.0           # king post 8x8
COL_W = 152.0          # collar tie 6x8
COL_D = 203.0

DOC = "AddOn_RoofFrame"
doc = App.newDocument(DOC)


def z_deck(x):
    """top of the roof deck plane at |x| (the sheathing plane)."""
    return RIDGE_Z - SLOPE * (abs(x) - 19.0)


def slab(sign, y, w, top_off, depth, x_in, x_out):
    """A member lying ALONG the slope: parallelogram in X-Z (plumb cut faces)
    whose top edge sits `top_off` below the deck plane, extruded `w` along +Y."""
    xi, xo = sign * x_in, sign * x_out
    pts = [V(xi, y, z_deck(x_in) - top_off),
           V(xo, y, z_deck(x_out) - top_off),
           V(xo, y, z_deck(x_out) - top_off - depth),
           V(xi, y, z_deck(x_in) - top_off - depth)]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, w, 0))


solids = []

# --- ridge beam: top face in the deck plane at the apex ----------------------
solids.append(("RidgeBeam", Part.makeBox(2 * RIDGE_HW, Y1 - Y0, RIDGE_D,
                                         V(-RIDGE_HW, Y0, RIDGE_Z - RIDGE_D))))

bent_y = [Y1 - i * BENT_SP for i in range(NBAY + 1)]   # 0 .. -12553

seat_z = z_deck(WALL_HALF)          # deck height over the wall
tie_top = seat_z - PR_D             # tie beam tucks under the principal rafters

principals, ties, kings, struts, collars = [], [], [], [], []

for i, yc in enumerate(bent_y):
    y = min(max(yc - PR_W / 2.0, Y0), Y1 - PR_W)      # keep inside the length
    for s in (+1, -1):
        principals.append(slab(s, y, PR_W, 0.0, PR_D, RIDGE_HW, HALF))

    tied = (i % 2 == 0)             # bottom chord on every OTHER bent only
    if tied:
        ties.append(Part.makeBox(2 * WALL_HALF, PR_W, TIE_D,
                                 V(-WALL_HALF, y, tie_top - TIE_D)))
        # king post: tie beam top -> underside of the ridge beam
        kp_top = RIDGE_Z - RIDGE_D
        kings.append(Part.makeBox(KP_W, PR_W, kp_top - tie_top,
                                  V(-KP_W / 2.0, y, tie_top)))
        # struts: king post -> principal rafter, ~45 deg
        for s in (+1, -1):
            x0 = s * KP_W / 2.0
            z0 = tie_top + 700.0
            x1 = s * 2100.0
            z1 = z_deck(2100.0) - PR_D
            d = V(x1 - x0, 0, z1 - z0)
            n = (d.x ** 2 + d.z ** 2) ** 0.5
            px, pz = -d.z / n * 76.0, d.x / n * 76.0     # 152 thick strut
            pts = [V(x0 + px, y, z0 + pz), V(x1 + px, y, z1 + pz),
                   V(x1 - px, y, z1 - pz), V(x0 - px, y, z0 - pz)]
            struts.append(Part.Face(Part.makePolygon(pts + [pts[0]]))
                          .extrude(V(0, PR_W, 0)))
    else:
        # untied bent: collar tie only (no bottom chord)
        col_z = z_deck(1800.0) - PR_D
        collars.append(Part.makeBox(2 * 1800.0, PR_W, COL_D,
                                    V(-1800.0, y, col_z - COL_D)))

solids.append(("PrincipalRafters", Part.makeCompound(principals)))
solids.append(("TieBeams", Part.makeCompound(ties)))
solids.append(("KingPosts", Part.makeCompound(kings)))
solids.append(("Struts", Part.makeCompound(struts)))
solids.append(("CollarTies", Part.makeCompound(collars)))

# --- purlins: bay-by-bay, butting the sides of the principal rafters ---------
# top face one common-rafter depth below the deck, so the commons land on them.
PUR_X = [1500.0, 2800.0, 4000.0]        # up-slope positions (horizontal run)
purlins = []
for b in range(NBAY):
    ya = bent_y[b] - PR_W / 2.0         # near face of this bent's principal
    yb = bent_y[b + 1] + PR_W / 2.0     # far face of the next one
    if b == 0:
        ya = Y1 - PR_W
    if b == NBAY - 1:
        yb = Y0 + PR_W
    ylen = ya - yb
    for s in (+1, -1):
        for px in PUR_X:
            purlins.append(slab(s, yb, ylen, CR_D, PUR_D,
                                px - PUR_W / 2.0, px + PUR_W / 2.0))
solids.append(("Purlins", Part.makeCompound(purlins)))

# --- common rafters: inside each bay, tops in the deck plane -----------------
commons = []
for b in range(NBAY):
    ya = bent_y[b] - PR_W / 2.0
    yb = bent_y[b + 1] + PR_W / 2.0
    n = int((ya - yb) / CR_SP)
    if n < 1:
        continue
    step = (ya - yb - CR_W) / n
    for k in range(1, n):
        y = yb + k * step
        for s in (+1, -1):
            commons.append(slab(s, y, CR_W, 0.0, CR_D, RIDGE_HW, HALF))
solids.append(("CommonRafters", Part.makeCompound(commons)))

# --- gable studs at the outer end only --------------------------------------
gable = []
yend = Y1 - PR_W
x = -WALL_HALF + 600.0
while x <= WALL_HALF - 600.0:
    ztop = z_deck(x) - PR_D
    zbot = tie_top
    if ztop - zbot > 50 and abs(x) > KP_W:
        gable.append(Part.makeBox(89.0, 89.0, ztop - zbot, V(x - 44.5, yend, zbot)))
    x += 600.0
solids.append(("GableStuds", Part.makeCompound(gable)))

# lower the whole roof (keeps pitch; matches main-house ridge height)
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
rep.write("bents=%d at %.1f mm (%.2f ft) o.c.  tied bents=%d  pitch=%.2f:12\n"
          % (len(bent_y), BENT_SP, BENT_SP / 304.8, len(ties), SLOPE * 12))
for o in objs:
    b = o.Shape.BoundBox
    rep.write("%-17s solids=%3d  X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]\n"
              % (o.Name, len(o.Shape.Solids), b.XMin, b.XMax, b.YMin, b.YMax,
                 b.ZMin, b.ZMax))
comp = Part.makeCompound([o.Shape for o in objs])
b = comp.BoundBox
rep.write("TOTAL X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]\n"
          % (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))
rep.close()
print("ADDON_TIMBER_ROOF_DONE")
