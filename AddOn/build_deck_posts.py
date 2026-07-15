# -*- coding: utf-8 -*-
"""6x6 posts carrying the AddOn roof where it OVERHANGS THE DECK.

After the roof was extended out to the deck's outboard edge (build_addon_roof.py),
the bottom chords of the two outermost bents float out over the deck with nothing
under them.  This drops a 6x6 wood post under EACH END of every chord that sits
past the outboard wall, standing on the decking and rising to the chord soffit --
i.e. porch columns at the roof's bearing points.

Built directly in WORLD coords (read from House.FCStd, so the posts always land
exactly under the real chords) and linked into House at identity placement.

Run headless:  freecadcmd AddOn/build_deck_posts.py   (then link_deck_posts.py
offscreen for the colour + House link).  Units: mm.
"""
import os
import FreeCAD as App
import Part

V = App.Vector
IN = 25.4

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POST = 5.5 * IN          # 6x6 nominal = 139.7 actual
WALL_Y = 14122.0         # outboard (front) wall: chords past this are over the deck

# --- read the real chord + deck geometry out of House -----------------------
h = App.openDocument(os.path.join(R, "House/House.FCStd"))
AP = h.getObject("AddOn").Placement
lnk = h.getObject("RoofFrame")
M = AP.multiply(lnk.Placement)
grp = {o.Name: o for o in lnk.LinkedObject.Group}
bc = grp["BottomChords"].Shape.copy()
bc.Placement = M.multiply(bc.Placement)

dl = h.getObject("Deck")
dg = {o.Name: o for o in dl.LinkedObject.Group}
dk = dg["Decking"].Shape.copy()
dk.Placement = dl.Placement.multiply(dk.Placement)
DECK_TOP = dk.BoundBox.ZMax          # 2578.1

# chords that overhang the deck, with their end X's, Y centre and soffit Z
posts_xy = []                        # (cx, cy, z_top)
for s in bc.Solids:
    b = s.BoundBox
    ycen = 0.5 * (b.YMin + b.YMax)
    if ycen <= WALL_Y:
        continue                     # over the room, borne by the wall
    z_top = b.ZMin                   # chord soffit
    for xend, inward in ((b.XMin, +1), (b.XMax, -1)):
        cx = xend + inward * POST / 2.0     # post tucked just under the chord end
        posts_xy.append((cx, ycen, z_top))

App.closeDocument(h.Name)

# --- build the posts --------------------------------------------------------
DOC = "AddOn_DeckPosts"
doc = App.newDocument(DOC)
objs = []
for i, (cx, cy, z_top) in enumerate(sorted(posts_xy)):
    box = Part.makeBox(POST, POST, z_top - DECK_TOP,
                       V(cx - POST / 2.0, cy - POST / 2.0, DECK_TOP))
    o = doc.addObject("Part::Feature", "DeckPost%d" % (i + 1))
    o.Shape = box
    objs.append(o)

part = doc.addObject("App::Part", "Part")
part.Label = "DeckPosts"
for o in objs:
    part.addObject(o)
doc.recompute()
doc.saveAs(os.path.join(R, "AddOn", DOC + ".FCStd"))

rep = open(os.path.join(R, "AddOn", "deck_posts_report.txt"), "w")
rep.write("deck top Z=%.1f  post section %.1f (6x6)\n" % (DECK_TOP, POST))
rep.write("%d posts under chords past the outboard wall (Y>%.0f):\n"
          % (len(objs), WALL_Y))
for o in objs:
    b = o.Shape.BoundBox
    rep.write("  %-10s X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]  H=%.0f\n"
              % (o.Name, b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax,
                 b.ZMax - b.ZMin))
rep.close()
print("DECK_POSTS_DONE %d posts" % len(objs))
