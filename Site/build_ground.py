# -*- coding: utf-8 -*-
"""Site ground / grade surface, built in WORLD coords so it links into House at
identity placement.

Grade level comes straight from the AddOn: the top of the AddOn subfloor is at
Z 2603.5 and the outside ground is 28.5" below it, so

    GRADE = 2603.5 - 28.5*25.4 = 1879.6

Sanity checks against that number:
  * AddOn joist bottoms sit at Z 2362.2 -> 19.0" over grade (clears the 18" rule)
  * the pier footings bottom out at Z 812.8 -> 42" below grade = the frost line
  * the foundation top is Z 2337 -> the wall stands 457 mm (18") proud of grade

The surface is a gentle contoured terrain, NOT a flat plane, so it reads as real
dirt -- but it is flattened back to exactly GRADE within 1.5 m of the buildings
(and eased in over the next 3.5 m), so the foundation, the AddOn piers and the
deck all meet clean, level ground.

The main-house footprint is CUT OUT of the solid (there is a basement under it).
The ground runs continuously UNDER the AddOn, which is correct -- that is an open
crawl space on piers, and the pier footings are buried in this solid.

Run headless:  freecadcmd Site/build_ground.py   (then link_ground.py offscreen)
Units: mm.
"""
import math
import os
import FreeCAD as App
import Part

V = App.Vector
IN = 25.4

GRADE = 2603.5 - 28.5 * IN          # 1879.6
BOT = 600.0                         # underside of the ground slab (below the
                                    # footings, which bottom out at 812.8)

# --- extent: the house plus a generous apron (room for the deck to the east) --
X0, X1 = -7000.0, 25000.0
Y0, Y1 = -7000.0, 23000.0
STEP = 1000.0

# --- buildings, for the flattening mask and the basement cut -----------------
HOUSE = (0.0, 17043.0, 0.0, 7925.0)          # main house footprint (basement)
ADDON = (7348.0, 15313.0, 7975.0, 14122.0)   # AddOn (crawl -- ground runs under)

FLAT = 1500.0        # dead flat within this distance of a building
EASE = 3500.0        # then ease up to full contour over this much more
AMP = 180.0          # contour amplitude (mm)


def rect_dist(x, y, r):
    """distance from (x,y) to rectangle r, 0 if inside."""
    dx = max(r[0] - x, 0.0, x - r[1])
    dy = max(r[2] - y, 0.0, y - r[3])
    return math.hypot(dx, dy)


def z_ground(x, y):
    d = min(rect_dist(x, y, HOUSE), rect_dist(x, y, ADDON))
    m = (d - FLAT) / EASE
    m = 0.0 if m < 0.0 else (1.0 if m > 1.0 else m)
    m = m * m * (3 - 2 * m)                  # smoothstep
    c = (math.sin(x / 5200.0) * math.cos(y / 6100.0)
         + 0.55 * math.sin((x + 1.3 * y) / 8700.0)
         + 0.30 * math.cos((x - 0.7 * y) / 3900.0))
    return GRADE + AMP * m * c / 1.85


nx = int(round((X1 - X0) / STEP))
ny = int(round((Y1 - Y0) / STEP))
pts = [[V(X0 + i * STEP, Y0 + j * STEP,
          z_ground(X0 + i * STEP, Y0 + j * STEP))
        for j in range(ny + 1)] for i in range(nx + 1)]

faces = []

# top surface: two triangles per grid cell
for i in range(nx):
    for j in range(ny):
        a, b = pts[i][j], pts[i + 1][j]
        c, d = pts[i + 1][j + 1], pts[i][j + 1]
        faces.append(Part.Face(Part.makePolygon([a, b, c, a])))
        faces.append(Part.Face(Part.makePolygon([a, c, d, a])))

# bottom
bl = [V(X0, Y0, BOT), V(X1, Y0, BOT), V(X1, Y1, BOT), V(X0, Y1, BOT)]
faces.append(Part.Face(Part.makePolygon(bl + [bl[0]])))

# sides: follow the contoured edge
def wall(edge_pts, flip=False):
    for k in range(len(edge_pts) - 1):
        p, q = edge_pts[k], edge_pts[k + 1]
        quad = [V(p.x, p.y, BOT), V(q.x, q.y, BOT), q, p]
        if flip:
            quad.reverse()
        faces.append(Part.Face(Part.makePolygon(quad + [quad[0]])))

wall([pts[i][0] for i in range(nx + 1)])
wall([pts[i][ny] for i in range(nx + 1)], True)
wall([pts[0][j] for j in range(ny + 1)], True)
wall([pts[nx][j] for j in range(ny + 1)])

shell = Part.makeShell(faces)
ground = Part.makeSolid(shell)
if not ground.isValid():
    ground = ground.removeSplitter()

# cut the basement out from under the main house
cut = Part.makeBox(HOUSE[1] - HOUSE[0], HOUSE[3] - HOUSE[2], 4000.0,
                   V(HOUSE[0], HOUSE[2], BOT - 500.0))
ground = ground.cut(cut)

DOC = "Ground"
doc = App.newDocument(DOC)
o = doc.addObject("Part::Feature", "Ground")
o.Shape = ground
part = doc.addObject("App::Part", "Part")
part.Label = "Ground"
part.addObject(o)
doc.recompute()

OUT = os.path.dirname(os.path.abspath(__file__))
doc.saveAs(os.path.join(OUT, DOC + ".FCStd"))

b = ground.BoundBox
rep = open(os.path.join(OUT, "ground_report.txt"), "w")
rep.write("GRADE = %.1f  (2603.5 subfloor top - 28.5in)\n" % GRADE)
rep.write("bb X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.1f,%.1f]  valid=%s solids=%d\n"
          % (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax,
             ground.isValid(), len(ground.Solids)))
zs = [z_ground(X0 + i * STEP, Y0 + j * STEP)
      for i in range(nx + 1) for j in range(ny + 1)]
rep.write("contour range Z %.1f .. %.1f (flat = %.1f at the buildings)\n"
          % (min(zs), max(zs), GRADE))
for nm, x, y in (("at the AddOn front wall", 11400.0, 14300.0),
                 ("at the house SE corner", 17100.0, 7900.0),
                 ("out east (deck area)", 18000.0, 12000.0)):
    rep.write("  %-24s (%.0f,%.0f) -> Z %.1f\n" % (nm, x, y, z_ground(x, y)))
rep.close()
print("GROUND_DONE")
