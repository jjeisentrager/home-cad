# -*- coding: utf-8 -*-
"""Deck on the east side of the house, traced from the hand sketch in deck.png.

The sketch's brown outline was mapped pixel->world (see _scan/deckpix.py); the fit
is confirmed by two corners that land on real building corners: the sketch's
top-right vertex maps to (15352,14297) == the AddOn's outboard corner (15313,14122)
and its bottom-right vertex to (52,7924) == the house's NE corner (0,7925).

Deck outline (world mm), wrapping the AddOn and filling the notch north of it:
    (15313,14122) AddOn outboard-south corner
    (15313,18170) east, on the line of the AddOn's south wall
    ( 2602,18170) north along the outer edge
    (    0,15287) the chamfered corner
    (    0, 7925) the house's NE corner
    ( 7348, 7925) back along the house's east wall
    ( 7348,14122) up the AddOn's west wall
    -> close along the AddOn's outboard wall

Levels (world Z):
    decking top   2578.1   = 1" below the interior subfloor (2603.5), and 32 mm
                             below the slider sill (2610.5) -- inside the 1.5"
                             max threshold step (R311.3.1)
    joist top     2552.7    2x10 PT joists @ 16" o.c., running along Y
    joist bottom  2317.7
    beam          2082.7 .. 2317.7   3-ply 2x10 PT, dropped, running along X
    grade         1879.6

    Deck surface is 698.5 mm (27.5") above grade -- under 30", so NO GUARD is
    required (R312.1.1).  There are no stairs in the sketch, so none are modelled.

Joists span Y between the ledgers and the beam lines, so no span exceeds ~3.4 m
(11.2 ft) -- inside the 13'-7" allowed for 2x10 @ 16" o.c. (SPF, Table R507.6).

Everything is built in WORLD coords and clipped to the outline, so it links into
House at identity placement.

Run headless:  freecadcmd Deck/build_deck.py   (then link_deck.py offscreen)
Units: mm.
"""
import os
import FreeCAD as App
import Part

V = App.Vector
IN = 25.4

GRADE = 1879.6
DECK_TOP = 2603.5 - 1.0 * IN          # 2578.1
DECK_T = 25.4                          # 5/4 decking
JOIST_TOP = DECK_TOP - DECK_T          # 2552.7
JOIST_D = 235.0                        # 2x10
JOIST_BOT = JOIST_TOP - JOIST_D        # 2317.7
BEAM_TOP = JOIST_BOT
BEAM_D = 235.0
BEAM_BOT = BEAM_TOP - BEAM_D           # 2082.7  -> 8" over grade (PT)
BEAM_W = 114.3                         # 3-ply

JOIST_T = 38.1
JOIST_SP = 406.4                       # 16" o.c.
BOARD_W = 140.0
BOARD_GAP = 6.0
RIM = 38.1

# --- outline ----------------------------------------------------------------
POLY = [(15313.0, 14122.0), (15313.0, 18170.0), (2602.0, 18170.0),
        (0.0, 15287.0), (0.0, 7925.0), (7348.0, 7925.0), (7348.0, 14122.0)]

BEAM_Y = [11340.0, 14760.0, 18100.0]   # beam lines (the outer one set in 70 for
                                       # a small cantilever)
PIER_SP = 1959.0                       # as the AddOn: well inside the table


def poly_face(pts, z):
    vs = [V(x, y, z) for x, y in pts]
    return Part.Face(Part.makePolygon(vs + [vs[0]]))


def prism(pts, z0, z1):
    return poly_face(pts, z0).extrude(V(0, 0, z1 - z0))


def inside(x, y, pts=POLY):
    """even-odd point-in-polygon."""
    c = False
    n = len(pts)
    for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        if (y0 > y) != (y1 > y):
            xi = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
            if x < xi:
                c = not c
    return c


XS = [p[0] for p in POLY]
YS = [p[1] for p in POLY]
XMIN, XMAX = min(XS), max(XS)
YMIN, YMAX = min(YS), max(YS)

DOC = "Deck"
doc = App.newDocument(DOC)
objs = []


def add(name, shp):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shp
    return o


# --- decking boards: run along X, clipped to the outline --------------------
clip_deck = prism(POLY, DECK_TOP - DECK_T, DECK_TOP)
boards = []
y = YMIN
while y < YMAX:
    b = Part.makeBox(XMAX - XMIN, BOARD_W, DECK_T, V(XMIN, y, DECK_TOP - DECK_T))
    c = b.common(clip_deck)
    if c.Solids:
        boards.append(c)
    y += BOARD_W + BOARD_GAP
objs.append(add("Decking", Part.makeCompound(boards)))

# --- joists: run along Y at 16" o.c., clipped -------------------------------
clip_joist = prism(POLY, JOIST_BOT, JOIST_TOP)
inner = poly_face(POLY, JOIST_BOT).makeOffset2D(-RIM)
clip_inner = inner.extrude(V(0, 0, JOIST_TOP - JOIST_BOT))
joists = []
x = XMIN + JOIST_SP / 2.0
while x < XMAX:
    b = Part.makeBox(JOIST_T, YMAX - YMIN, JOIST_D, V(x, YMIN, JOIST_BOT))
    c = b.common(clip_inner)
    if c.Solids:
        joists.append(c)
    x += JOIST_SP
objs.append(add("Joists", Part.makeCompound(joists)))

# --- rim / ledger ring: the band around the whole outline -------------------
# (against the house and the AddOn walls this band IS the ledger)
rim = clip_joist.cut(clip_inner)
objs.append(add("RimAndLedger", rim))

# --- beams: dropped, run along X, clipped -----------------------------------
clip_beam = prism(POLY, BEAM_BOT, BEAM_TOP)
beams = []
for by in BEAM_Y:
    b = Part.makeBox(XMAX - XMIN, BEAM_W, BEAM_D,
                     V(XMIN, by - BEAM_W / 2.0, BEAM_BOT))
    c = b.common(clip_beam)
    if c.Solids:
        beams.append(c)
objs.append(add("Beams", Part.makeCompound(beams)))

# --- piers under the beams, only where they fall inside the deck ------------
PLATE_T = 1.0 * IN
PIER_D = 12.0 * IN
PIER_TOP = BEAM_BOT - PLATE_T
FOOT_S = 24.0 * IN
FOOT_T = 8.0 * IN
FOOT_BOT = GRADE - 42.0 * IN
FOOT_TOP = FOOT_BOT + FOOT_T

shafts, foots, plates = [], [], []
npier = 0
for by in BEAM_Y:
    x = XMIN + 150.0
    while x <= XMAX:
        if inside(x, by):
            shafts.append(Part.makeCylinder(PIER_D / 2.0, PIER_TOP - FOOT_TOP,
                                            V(x, by, FOOT_TOP), V(0, 0, 1)))
            foots.append(Part.makeBox(FOOT_S, FOOT_S, FOOT_T,
                                      V(x - FOOT_S / 2, by - FOOT_S / 2, FOOT_BOT)))
            plates.append(Part.makeBox(178.0, 178.0, PLATE_T,
                                       V(x - 89.0, by - 89.0, PIER_TOP)))
            npier += 1
        x += PIER_SP
objs.append(add("Piers", Part.makeCompound(shafts)))
objs.append(add("Footings", Part.makeCompound(foots)))
objs.append(add("BearingPlates", Part.makeCompound(plates)))

# --- exterior stairs at the SE corner ---------------------------------------
# SE corner of the deck = (X=15313 south edge, Y=18170 east edge).  Two flights,
# each set ~2 ft back from the corner along its own edge:
#   * "east"  flight descends toward +Y off the Y=18170 (east) edge
#   * "south" flight descends toward +X off the X=15313 (south) edge
# 27.5" total drop -> 4 risers @ 6.875" (<7.75" max), 3 open treads @ 11" run.
STAIR_RISERS = 4
STAIR_RISE = (DECK_TOP - GRADE) / STAIR_RISERS       # 174.6 mm (6.875")
STAIR_TREADS = STAIR_RISERS - 1                       # 3 treads down to grade
STAIR_RUN = 11.0 * IN                                 # 279.4 mm going
STAIR_W = 36.0 * IN                                   # 914.4 mm wide
TREAD_T = 38.1                                         # 2x tread stock
RISER_T = 19.0                                         # 3/4 riser board
STR_T = 38.1                                           # 2x12 stringer thickness
STR_D = 285.75                                         # 2x12 depth
GAP = 2.0 * 12.0 * IN                                  # 2 ft back from the corner
PAD_D = 36.0 * IN                                      # 36" landing pad (travel)
PAD_T = 101.6                                          # 4" slab
SE_X, SE_Y = 15313.0, 18170.0


def wbox(a, b):
    """axis-aligned box from two opposite world corner Vectors."""
    x0, x1 = sorted((a.x, b.x))
    y0, y1 = sorted((a.y, b.y))
    z0, z1 = sorted((a.z, b.z))
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def build_stair(mp, ext, width):
    """mp(u,v,z)->world Vector (u across width, v out from deck edge, z up);
    ext = stringer extrude vector; width = stair width.  Returns (wood, pad)."""
    wood = []
    for t in range(1, STAIR_TREADS + 1):                 # treads
        ztop = DECK_TOP - t * STAIR_RISE
        wood.append(wbox(mp(0.0, (t - 1) * STAIR_RUN, ztop - TREAD_T),
                         mp(width, t * STAIR_RUN, ztop)))
    for r in range(1, STAIR_RISERS + 1):                 # risers
        v = (r - 1) * STAIR_RUN
        wood.append(wbox(mp(0.0, v, DECK_TOP - r * STAIR_RISE),
                         mp(width, v + RISER_T, DECK_TOP - (r - 1) * STAIR_RISE)))
    for ue in (0.0, width - STR_T):                      # two stringers
        prof = [mp(ue, 0.0, DECK_TOP),
                mp(ue, STAIR_TREADS * STAIR_RUN, GRADE),
                mp(ue, STAIR_TREADS * STAIR_RUN, GRADE - STR_D),
                mp(ue, 0.0, DECK_TOP - STR_D)]
        f = Part.Face(Part.makePolygon(prof + [prof[0]]))
        wood.append(f.extrude(ext))
    pv = STAIR_TREADS * STAIR_RUN                         # landing pad at grade
    pad = wbox(mp(-50.0, pv, GRADE - PAD_T),
               mp(width + 50.0, pv + PAD_D, GRADE))
    return Part.makeCompound(wood), pad


W_EAST = 3.0 * STAIR_W                                    # east flight ~3x wide
W_SOUTH = STAIR_W
# east flight: width along X (2 ft back from the corner, running north), out +Y
mp_east = lambda u, v, z: V(SE_X - GAP - W_EAST + u, SE_Y + v, z)
# south flight: width along Y (2 ft back from the corner, running west), out +X
mp_south = lambda u, v, z: V(SE_X + v, SE_Y - GAP - W_SOUTH + u, z)
wood_e, pad_e = build_stair(mp_east, V(STR_T, 0, 0), W_EAST)
wood_s, pad_s = build_stair(mp_south, V(0, STR_T, 0), W_SOUTH)
objs.append(add("StairEast", wood_e))
objs.append(add("StairSouth", wood_s))
objs.append(add("StairPads", Part.makeCompound([pad_e, pad_s])))

part = doc.addObject("App::Part", "Part")
part.Label = "Deck"
for o in objs:
    part.addObject(o)
doc.recompute()

OUT = os.path.dirname(os.path.abspath(__file__))
doc.saveAs(os.path.join(OUT, DOC + ".FCStd"))

# area (shoelace)
a = 0.0
for i in range(len(POLY)):
    x0, y0 = POLY[i]
    x1, y1 = POLY[(i + 1) % len(POLY)]
    a += x0 * y1 - x1 * y0
area = abs(a) / 2.0

rep = open(os.path.join(OUT, "deck_report.txt"), "w")
rep.write("deck area = %.1f m2 (%.0f sq ft)\n" % (area / 1e6, area / 92903.0))
rep.write("decking top Z=%.1f (1\" below subfloor 2603.5; slider sill 2610.5)\n" % DECK_TOP)
rep.write("height above grade = %.1f mm (%.1f in) -> %s\n"
          % (DECK_TOP - GRADE, (DECK_TOP - GRADE) / IN,
             "no guard required (<30in)" if (DECK_TOP - GRADE) / IN < 30 else "GUARD REQUIRED"))
rep.write("joists 2x10 @ %.1f o.c. along Y; beams 3-ply 2x10 at Y=%s\n"
          % (JOIST_SP, BEAM_Y))
rep.write("piers: %d at %.0f mm o.c. along each beam\n" % (npier, PIER_SP))
for o in objs:
    b = o.Shape.BoundBox
    rep.write("%-14s n=%3d  X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]\n"
              % (o.Name, len(o.Shape.Solids), b.XMin, b.XMax, b.YMin, b.YMax,
                 b.ZMin, b.ZMax))
rep.close()
print("DECK_DONE")
