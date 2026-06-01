# -*- coding: utf-8 -*-
"""
Finish the kitchen assembly:
  1. Cut holes in the L-countertop for the SINK (bowl opening) and the
     STOVE (full-depth slot), so both appliances read through the counter.
  2. Force every solid / part / link visible (down into the library files),
     and re-write each file WITH its GuiDocument so visibility survives open.

MUST be run with the GUI layer up so ViewObjects exist and GuiDocument.xml is
written. Headless `freecadcmd` drops GuiDocument and hides everything. Use:

  QT_QPA_PLATFORM=offscreen \
    flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD \
    Kitchen/finish_kitchen.py
"""
import os
import FreeCAD as App
import FreeCADGui as Gui   # noqa: F401  (initialises ViewObjects + GuiDocument)
import Part

ROOT = "/home/joee/github/alieniron/home-cad"
LIB  = os.path.join(ROOT, "Library")
KIT  = os.path.join(ROOT, "Kitchen")
V = App.Vector
rep = open(os.path.join(ROOT, "finish_report.txt"), "w")
def L(*a): rep.write(" ".join(str(x) for x in a) + "\n")

def show(o, vis=True):
    o.Visibility = vis
    if o.ViewObject is not None:
        o.ViewObject.Visibility = vis

def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))

# ---------------------------------------------------------------------------
# 1. COUNTER: cut sink + stove holes into the L countertop (Body001 / CounterTop)
# ---------------------------------------------------------------------------
cdoc = App.openDocument(os.path.join(KIT, "Kitchen_Counter.FCStd"))
part = cdoc.getObject("Part")          # App::Part "Kitchen_Counter"
top  = cdoc.getObject("Body001")       # PartDesign Body "CounterTop" (the L top)

# Sink bowl opening (global coords) and full-depth stove slot (global coords)
sink_hole  = box(-2044.7, -1257.3, -508.0, -101.6, 913.0, 941.0)
stove_hole = box(-665.0,      5.0, -3862.0, -3098.0, 913.0, 941.0)
tool_shape = Part.makeCompound([sink_hole, stove_hole])

tool = cdoc.getObject("CounterTopHoleTool") or \
       cdoc.addObject("Part::Feature", "CounterTopHoleTool")
tool.Label = "CounterTop_Holes"
tool.Shape = tool_shape

cut = cdoc.getObject("CounterTop_Cut") or cdoc.addObject("Part::Cut", "CounterTop_Cut")
cut.Label = "CounterTop"
cut.Base = top
cut.Tool = tool

# make sure cut + tool live inside the linked App::Part
for o in (tool, cut):
    if o not in part.Group:
        part.addObject(o)

cdoc.recompute()

# visibility: base counter + island stay; old top hidden, holed top shown
show(cdoc.getObject("Body"));    show(cdoc.getObject("Pad"))           # base counter
show(part); show(cdoc.getObject("Part001"))                            # parts
show(cdoc.getObject("Body002")); show(cdoc.getObject("Pad003"))        # island base
show(cdoc.getObject("Body003")); show(cdoc.getObject("Pad004"))        # island top
show(top, False); show(cdoc.getObject("Pad002"), False)               # old solid top -> hide
show(tool, False)                                                     # cut tool -> hide
show(cut, True)                                                       # holed top -> show
cdoc.save()
L("counter: cut bbox", cut.Shape.BoundBox)
L("counter: holes solids in cut =", len(cut.Shape.Solids))

# ---------------------------------------------------------------------------
# 2. APPLIANCE LIBRARY FILES: show the App::Part + every solid feature
# ---------------------------------------------------------------------------
LIBS = [
    "LG_LRMXS2806S/LG_LRMXS2806S.FCStd",
    "LRGL5823S/LRGL5823S.FCStd",
    "KWT310-33/KWT310-33.FCStd",
    "WDP540HAMZ/WDP540HAMZ.FCStd",
]
for rel in LIBS:
    d = App.openDocument(os.path.join(LIB, rel))
    n = 0
    for o in d.Objects:
        if o.TypeId == "App::Part" or o.TypeId.startswith("Part::"):
            show(o, True); n += 1
    d.save()
    L("lib %-14s showed %d objects" % (d.Name, n))

# ---------------------------------------------------------------------------
# 3. ASSEMBLY: show the assembly + every link, then save (re-reads holed counter)
# ---------------------------------------------------------------------------
adoc = App.openDocument(os.path.join(KIT, "Kitchen_Assembly.FCStd"))
asm = adoc.getObject("Assembly")
show(asm, True)
for o in adoc.Objects:
    if o.TypeId in ("App::Link", "App::Part") or o.TypeId.startswith("Assembly::"):
        show(o, True)
adoc.recompute()
adoc.save()
L("assembly visible links:", [o.Name for o in adoc.Objects if o.TypeId == "App::Link"])
rep.close()
print("FINISH_DONE")
