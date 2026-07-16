# -*- coding: utf-8 -*-
"""
Kitchen cabinet layout -- shared data for the 2D planner and the FreeCAD builder.
Kitchen-native mm frame:  X=0 = counter/east(stove) wall, Y=0 = front/sink wall,
Z=0 = floor, room toward -X / -Y.  Along-wall coordinate is X on the FRONT wall
and Y on the EAST wall (both run 0 -> negative).

All widths are standard 3" increments; heights/depths are standard.  Small
fillers (<= ~2") take up slack between a cabinet run and an appliance/window.
"""
IN = 25.4

# ---- standard heights / depths (mm) ----
BASE_Z0, BASE_Z1 = 0.0, 876.0        # base box 34.5"
BASE_D           = 609.6             # base depth 24"
UP_Z0, UP_Z1     = 1397.0, 2311.0    # wall cab 36" tall, bottom ~55" AFF
UP_D             = 304.8             # wall depth 12"
OF_Z0, OF_Z1     = 1828.4, 2438.0    # over-fridge 24" tall
OF_D             = 609.6             # over-fridge depth 24"
CT_Z0, CT_Z1     = 876.0, 940.0      # countertop slab (keeps the 940 appliance datum)
CT_D             = 635.0             # counter depth 24" + 1" overhang

BASE_LEG = 914.4   # diagonal base corner 36" legs
UP_LEG   = 609.6   # diagonal upper corner 24" legs

# ---- box cabinets: (id, label, wall, a0, a1)  wall in {front, east} ----
# BASE  (z BASE_Z0..BASE_Z1, depth BASE_D)
# Corner: a 24" square corner base cabinet with an equal-width door on BOTH walls
# (built specially -- see CNR_BASE).  These box cabinets are the runs beyond it.
BASE = [
    ("B-F-21",   '21"',      "front",  -609.6,  -1143.4),
    ("B-F-sink", '36" sink', "front", -1193.6,  -2108.0),
    # end cabinet trimmed 30" -> 15" (removed 15" at the slider end).
    ("B-F-15",   '15"',      "front", -2717.6,  -3098.6),
    ("B-E-36",   '36"',      "east",   -609.6,  -1524.4),
    ("B-E-36c",  '36"',      "east",  -1524.4,  -2438.8),
    ("B-E-36b",  '36"',      "east",  -3208.0,  -4122.4),
    ("B-E-30",   '30"',      "east",  -4122.4,  -4884.4),
]
CNR_BASE = 609.6   # 24" square corner base cabinet; a 24" door faces each wall
# UPPER (z UP_Z0..UP_Z1, depth UP_D)
UPPER = [
    ("U-F-12", '12"', "front",  -609.6,  -914.4),   # small flank, front side of diagonal
    # two end uppers (24"+21") replaced by one 30" (removed 15" at the slider end).
    ("U-F-30", '30"', "front", -2336.5, -3098.5),
    ("U-E-12", '12"', "east",   -609.6,  -914.4),   # small flank, east side of diagonal
    ("U-E-36", '36"', "east",  -3208.0, -4122.4),
    ("U-E-30", '30"', "east",  -4122.4, -4884.4),
]
# over-fridge (z OF_Z0..OF_Z1, depth OF_D)
OVERFRIDGE = [
    ("U-E-OF", '36"', "east", -4901.0, -5815.4),
]

# ---- countertop slab segments: (wall, a0, a1) ----
COUNTER = [
    ("front",     0.0, -3149.5),   # corner -> slider (shortened with the run)
    ("east",      0.0, -2449.0),   # corner -> range
    ("east",  -3208.0, -4901.0),   # range  -> fridge
]

# ---- window slide needed for the east small flank cabinet ----
# WindowWall native near edge -838.5 -> -965.5  (slide 127 mm toward the stove).
WINDOW_SLIDE_MM = 127.0            # native -Y
FRAMING_RO_OLD  = 4572.0          # Wall_Right WindowWall center, wall-local X
FRAMING_RO_NEW  = 4445.0          # 4572 - 127


def widths_summary():
    """Return list of (id, label, wall, W_in, H_in, D_in, kind) for the summary."""
    rows = []
    def wid(a0, a1): return round(abs(a1 - a0) / IN, 1)
    for cid, lbl, wall, a0, a1 in BASE:
        rows.append((cid, "base", wall, wid(a0, a1), 34.5, 24.0))
    for cid, lbl, wall, a0, a1 in UPPER:
        rows.append((cid, "wall", wall, wid(a0, a1), 36.0, 12.0))
    rows.append(("U-CNR", "wall diagonal corner", "corner",
                 round(UP_LEG / IN, 1), 36.0, 12.0))
    for cid, lbl, wall, a0, a1 in OVERFRIDGE:
        rows.append((cid, "over-fridge", wall, wid(a0, a1), 24.0, 24.0))
    return rows
