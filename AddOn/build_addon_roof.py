# -*- coding: utf-8 -*-
"""AddOn roof -- TIMBER FRAME section (the AddOn room itself, from the I-beam out
over the deck).  The short strip between the I-beam and the main house is a
SEPARATE piece: AddOn/build_roof_connector.py, which stays stick framed.

Anatomy (classic king-post frame):
  * 8x12 RIDGE BEAM, top face in the deck plane at the apex.
  * 5 BENTS of 6x10 PRINCIPAL RAFTERS, 2017 mm (6'-7") o.c., spaced OFF THE
    I-BEAM: world Y 8000.9 (the I-beam itself) / 10017.9 / 12034.9 / 14051.9 /
    16068.9 -- the last one stands out over the deck under the overhang.
  * A BOTTOM CHORD at every bent, and a KING POST on EVERY chord running up to
    the ridge.  The chord at world Y 8000.9 IS THE STEEL I-BEAM (it is not
    redrawn here -- it already exists in AddOn_Beams) but it still gets a king
    post, so all four chord lines carry one.
  * Angled STRUTS from each king post to its principal rafters.
  * 6x8 PURLINS bay-to-bay between the principal rafters, with 4x6 COMMON RAFTERS
    over them carrying the sheathing.

CHORD LEVEL -- the point of this rebuild: the chord TOP sits at the top of the
wall, Z 5041.9 world (8 ft over the subfloor), which is exactly the top of the
I-beam.  The chords are 14" deep like the I-beam, so their bottoms land on
Z 4686.3 too: chord and steel line up top AND bottom.

Because the roof was dropped 280 mm to match the main-house ridge, the deck plane
at the wall (Z 4995.5) is actually BELOW the wall top -- so a full wall-to-wall
chord at Z 5041.9 would poke out through the roof.  The chords are therefore
SHORTENED to |x| <= 3400 (6800 long instead of 8128), which keeps their top
corners under the rafter soffit (clearance 5.2 mm at the end).

OVERHANG: the Y1 end runs out to local Y 0 = world Y 16534, i.e. 2412 mm past the
outboard wall, sheltering the deck.  (An earlier commit wrongly trimmed this to
400 mm.)  The Y0 end of the TIMBER section stops at the I-beam.

Run headless:  freecadcmd build_addon_roof.py   (then recolor_brown.py offscreen)
Units: mm.
"""
import os
import FreeCAD as App
import Part

V = App.Vector

# world Y = 16534.31 + localY ; world Z = 6985.0 + localZ(final) = localZ(pre)+6705
W2L_Y = 16534.31
PRE2W_Z = 6705.0

ZSHIFT = -280.0
HALF = 4489.0          # eave X (half span incl. overhang)
WALL_HALF = 4064.0     # wall line
RIDGE_Z = 152.0        # deck plane at the ridge (pre-shift)
SLOPE = (RIDGE_Z - (-1905.0)) / (HALF - 19.0)   # 0.4602 == 5.52:12

RIDGE_HW = 101.6       # ridge beam 8 wide -> 203
RIDGE_D = 305.0        # 12 deep

PR_W = 152.0           # principal rafter 6x10
PR_D = 254.0
PUR_W = 152.0          # purlin 6x8
PUR_D = 203.0
CR_W = 102.0           # common rafter 4x6
CR_D = 152.0
CR_SP = 600.0
KP_W = 203.0           # king post 8x8
STRUT_HW = 76.0

# --- chords: top at the wall top, same depth as the I-beam ------------------
WALL_TOP_W = 5041.9                       # world: 8 ft over the subfloor
CHORD_TOP = WALL_TOP_W - PRE2W_Z          # -1663.1 pre-shift
CHORD_D = 355.6                           # 14", as the I-beam
CHORD_W = 203.0                           # 8" along Y
CHORD_HALF = 3400.0                       # shortened -- see the note above

# --- bents, spaced off the I-beam -------------------------------------------
IBEAM_WY = 8000.9
BENT_SP = 2017.0
BENT_WY = [IBEAM_WY + i * BENT_SP for i in range(5)]   # 8000.9 .. 16068.9
BENT_Y = [wy - W2L_Y for wy in BENT_WY]                # local
IBEAM_LY = BENT_Y[0]

Y1 = 0.0                # deck-side eave: 2412 past the outboard wall
Y0 = IBEAM_LY           # the timber section stops at the I-beam
GABLE_Y = 14051.9 - W2L_Y     # outboard wall centreline

DOC = "AddOn_RoofFrame"
doc = App.newDocument(DOC)


def z_deck(x):
    return RIDGE_Z - SLOPE * (abs(x) - 19.0)


def slab(sign, y, w, top_off, depth, x_in, x_out):
    """member along the slope: parallelogram in X-Z, extruded w along +Y."""
    xi, xo = sign * x_in, sign * x_out
    pts = [V(xi, y, z_deck(x_in) - top_off),
           V(xo, y, z_deck(x_out) - top_off),
           V(xo, y, z_deck(x_out) - top_off - depth),
           V(xi, y, z_deck(x_in) - top_off - depth)]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, w, 0))


solids = []

# --- ridge beam --------------------------------------------------------------
solids.append(("RidgeBeam", Part.makeBox(2 * RIDGE_HW, Y1 - Y0, RIDGE_D,
                                         V(-RIDGE_HW, Y0, RIDGE_Z - RIDGE_D))))

principals, chords, kings, struts = [], [], [], []
kp_top = RIDGE_Z - RIDGE_D          # underside of the ridge beam

for i, yc in enumerate(BENT_Y):
    y = min(max(yc - PR_W / 2.0, Y0), Y1 - PR_W)
    for s in (+1, -1):
        principals.append(slab(s, y, PR_W, 0.0, PR_D, RIDGE_HW, HALF))

    # bottom chord -- EXCEPT at the I-beam, which already is the chord there
    if i > 0:
        chords.append(Part.makeBox(2 * CHORD_HALF, CHORD_W, CHORD_D,
                                   V(-CHORD_HALF, yc - CHORD_W / 2.0,
                                     CHORD_TOP - CHORD_D)))

    # king post on EVERY chord (the I-beam's included), chord top -> ridge
    kings.append(Part.makeBox(KP_W, PR_W, kp_top - CHORD_TOP,
                              V(-KP_W / 2.0, y, CHORD_TOP)))

    # struts: king post -> principal rafter
    for s in (+1, -1):
        x0, z0 = s * KP_W / 2.0, CHORD_TOP + 500.0
        x1 = s * 2100.0
        z1 = z_deck(2100.0) - PR_D
        d = V(x1 - x0, 0, z1 - z0)
        n = (d.x ** 2 + d.z ** 2) ** 0.5
        px, pz = -d.z / n * STRUT_HW, d.x / n * STRUT_HW
        pts = [V(x0 + px, y, z0 + pz), V(x1 + px, y, z1 + pz),
               V(x1 - px, y, z1 - pz), V(x0 - px, y, z0 - pz)]
        struts.append(Part.Face(Part.makePolygon(pts + [pts[0]]))
                      .extrude(V(0, PR_W, 0)))

solids.append(("PrincipalRafters", Part.makeCompound(principals)))
solids.append(("BottomChords", Part.makeCompound(chords)))
solids.append(("KingPosts", Part.makeCompound(kings)))
solids.append(("Struts", Part.makeCompound(struts)))

# --- purlins: bay-to-bay, butting the principal rafters ---------------------
PUR_X = [1500.0, 2800.0, 4000.0]
purlins = []
for b in range(len(BENT_Y) - 1):
    ya = BENT_Y[b + 1] - PR_W / 2.0      # bents run low->high local Y
    yb = BENT_Y[b] + PR_W / 2.0
    ylen = ya - yb
    if ylen <= 0:
        continue
    for s in (+1, -1):
        for px in PUR_X:
            purlins.append(slab(s, yb, ylen, CR_D, PUR_D,
                                px - PUR_W / 2.0, px + PUR_W / 2.0))
# and the last bay: from the outermost bent out to the eave (over the deck)
for s in (+1, -1):
    for px in PUR_X:
        purlins.append(slab(s, BENT_Y[-1] + PR_W / 2.0,
                            Y1 - (BENT_Y[-1] + PR_W / 2.0), CR_D, PUR_D,
                            px - PUR_W / 2.0, px + PUR_W / 2.0))
solids.append(("Purlins", Part.makeCompound(purlins)))

# --- common rafters in each bay ---------------------------------------------
commons = []
edges = BENT_Y + [Y1]
for b in range(len(edges) - 1):
    ya = edges[b] + PR_W / 2.0
    yb = edges[b + 1] - (PR_W / 2.0 if b + 1 < len(BENT_Y) else 0.0)
    n = int((yb - ya) / CR_SP)
    if n < 1:
        continue
    step = (yb - ya - CR_W) / n
    for k in range(1, n):
        y = ya + k * step
        for s in (+1, -1):
            commons.append(slab(s, y, CR_W, 0.0, CR_D, RIDGE_HW, HALF))
solids.append(("CommonRafters", Part.makeCompound(commons)))

# --- gable studs on the outboard wall ---------------------------------------
gable = []
x = -WALL_HALF + 600.0
while x <= WALL_HALF - 600.0:
    ztop = z_deck(x) - PR_D
    if ztop - CHORD_TOP > 50 and abs(x) > KP_W:
        gable.append(Part.makeBox(89.0, 89.0, ztop - CHORD_TOP,
                                  V(x - 44.5, GABLE_Y - 44.5, CHORD_TOP)))
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
rep.write("TIMBER section: %d bents at %.0f o.c. (spaced off the I-beam)\n"
          % (len(BENT_Y), BENT_SP))
for i, (ly, wy) in enumerate(zip(BENT_Y, BENT_WY)):
    rep.write("  bent %d local Y=%9.1f world Y=%8.1f  chord=%s  king post=yes\n"
              % (i, ly, wy, "THE I-BEAM" if i == 0 else "timber 8x14"))
rep.write("chord top world Z=%.1f (= wall top = I-beam top); bottom %.1f "
          "(= I-beam soffit)\n" % (WALL_TOP_W, WALL_TOP_W - CHORD_D))
xe = CHORD_HALF
rep.write("chord half-length %.0f: rafter soffit there is world Z %.1f, "
          "chord top %.1f -> clearance %.1f mm\n"
          % (xe, z_deck(xe) - PR_D + PRE2W_Z, WALL_TOP_W,
             (z_deck(xe) - PR_D + PRE2W_Z) - WALL_TOP_W))
rep.write("length local Y[%.1f,%.1f] -> world Y[%.1f,%.1f] "
          "(overhang past the outboard wall = %.0f mm, over the deck)\n"
          % (Y0, Y1, Y0 + W2L_Y, Y1 + W2L_Y, (Y1 + W2L_Y) - 14122.0))
for o in objs:
    b = o.Shape.BoundBox
    rep.write("%-17s n=%3d  X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]\n"
              % (o.Name, len(o.Shape.Solids), b.XMin, b.XMax, b.YMin, b.YMax,
                 b.ZMin, b.ZMax))
rep.close()
print("ADDON_TIMBER_ROOF_DONE")
