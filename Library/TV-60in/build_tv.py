# -*- coding: utf-8 -*-
"""
Build a simple 60" flat-panel (big-screen) TV for wall mounting.

60" 16:9 panel: ~52.3" x 29.4" active, ~53.2" x 30.4" overall with a thin
bezel; slim ~2" body.  Loose Part::Features wrapped in an App::Part so it can be
linked like the other components.

Local frame:  X = width, Z = height, Y = depth with the SCREEN facing +Y
(origin back-left-bottom; the panel back sits at Y=0).

Run headless:  freecadcmd build_tv.py
Units: millimetres.
"""
import os
import FreeCAD as App
import Part
import Mesh

IN = 25.4
W = 53.2 * IN        # overall width  = 1351.3
H = 30.4 * IN        # overall height = 772.2
D = 2.0 * IN         # body depth     = 50.8
BEZEL = 0.6 * IN     # screen bezel   = 15.2

DOC = "TV-60in"
doc = App.newDocument(DOC)

def box(l, w, h, x, y, z):
    return Part.makeBox(l, w, h, App.Vector(x, y, z))

def add(name, shp):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shp
    return o

# panel body (black), screen face toward +Y
add("Panel", box(W, D, H, 0, 0, 0))
# screen, slightly proud of the front face, inset by the bezel
add("Screen", box(W - 2 * BEZEL, 2.0, H - 2 * BEZEL, BEZEL, D, BEZEL))
# low-profile wall bracket centred on the back
add("Mount", box(0.30 * W, 12.0, 0.45 * H, 0.35 * W, -12.0, 0.30 * H))

part = doc.addObject("App::Part", "Part")
part.Label = "TV_60in"
for o in [o for o in doc.Objects if o.TypeId.startswith("Part::")]:
    part.addObject(o)
doc.recompute()

OUT = os.path.dirname(os.path.abspath(__file__))
doc.saveAs(os.path.join(OUT, DOC + ".FCStd"))
feats = [o for o in doc.Objects if o.TypeId.startswith("Part::")]
Part.export(feats, os.path.join(OUT, DOC + ".step"))
Mesh.Mesh(Part.makeCompound([o.Shape for o in feats]).tessellate(0.5)).write(
    os.path.join(OUT, DOC + ".stl"))
bb = Part.makeCompound([o.Shape for o in feats]).BoundBox
print("Saved TV  W x H x D (in) = %.1f x %.1f x %.1f"
      % (bb.XLength / IN, bb.ZLength / IN, bb.YLength / IN))
print("TV_DONE")
