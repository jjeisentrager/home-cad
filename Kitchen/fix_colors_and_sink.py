# -*- coding: utf-8 -*-
"""
Fix-up pass after the appliance placement / counter holes:

  1. Cut the SINK opening through BOTH the L countertop AND the base counter
     (CounterBase) so the sink basin is visible -- previously only the top was
     cut. The stove slot is also taken full-height through the base counter so
     the range no longer intersects solid cabinetry.
  2. Restore colors that were lost when the appliance files were first saved
     headless (which dropped GuiDocument and reset every ShapeColor to default
     gray). Colors are read back from the committed originals (d845fa1) and
     re-applied; the holed counter pieces inherit the base=white / top=black.

MUST run with the GUI layer up (offscreen) so colors + GuiDocument persist:
  flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD \
    Kitchen/fix_colors_and_sink.py
"""
import os
import FreeCAD as App
import FreeCADGui as Gui   # noqa: F401
import Part

H = "/home/joee/github/alieniron/home-cad/"
LIB = H + "Library/"
KIT = H + "Kitchen/"
V = App.Vector
log = open(H + "fix_report.txt", "w")
def L(*a): log.write(" ".join(str(x) for x in a) + "\n")

def color_of(o):
    c = o.ViewObject.ShapeColor
    return (c[0], c[1], c[2])

def set_color(o, rgb):
    o.ViewObject.ShapeColor = (rgb[0], rgb[1], rgb[2])
    try:
        ap = o.ViewObject.ShapeAppearance
        if ap:
            m = ap[0]; m.DiffuseColor = (rgb[0], rgb[1], rgb[2], 0.0)
            o.ViewObject.ShapeAppearance = [m]
    except Exception:
        pass

def show(o, vis=True):
    o.Visibility = vis
    if o.ViewObject is not None:
        o.ViewObject.Visibility = vis

def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))

# ---------------------------------------------------------------------------
# 1. COUNTER: read original base/top colors, then cut base + top
# ---------------------------------------------------------------------------
oc = App.openDocument(H + "_old_counter.FCStd")
base_color = color_of(oc.getObject("Body"))      # white
top_color  = color_of(oc.getObject("Body001"))   # black
L("counter original colors: base", base_color, "top", top_color)
App.closeDocument(oc.Name)

cd = App.openDocument(KIT + "Kitchen_Counter.FCStd")
part = cd.getObject("Part")
Body = cd.getObject("Body")        # CounterBase  (Z 0..914.4)
Body001 = cd.getObject("Body001")  # CounterTop   (Z 914.4..939.8)

# remove the previous (top-only) cut + tool so we can rebuild cleanly
for nm in ("CounterTop_Cut", "CounterBase_Cut", "CounterTopHoleTool"):
    if cd.getObject(nm):
        cd.removeObject(nm)

# Stove slot: full height (severs base + top). Sink shaft: bowl-outer footprint
# +4 mm, from just below the basin (705) up through the countertop (941).
stove = box(-665.0, 5.0, -3862.0, -3098.0, -1.0, 941.0)
sink  = box(-2060.7, -1241.3, -524.0, -85.6, 705.0, 941.0)
tool  = Part.makeCompound([stove, sink])

base_cut = cd.addObject("Part::Feature", "CounterBase_Cut"); base_cut.Label = "CounterBase"
base_cut.Shape = Body.Shape.cut(tool)
top_cut = cd.addObject("Part::Feature", "CounterTop_Cut"); top_cut.Label = "CounterTop"
top_cut.Shape = Body001.Shape.cut(tool)
for o in (base_cut, top_cut):
    if o not in part.Group:
        part.addObject(o)

cd.recompute()
set_color(base_cut, base_color)
set_color(top_cut, top_color)
# hide the original solids, show the holed ones
for nm in ("Body", "Pad", "Body001", "Pad002"):
    if cd.getObject(nm):
        show(cd.getObject(nm), False)
show(base_cut, True); show(top_cut, True)
cd.save()
L("counter base_cut solids:", len(base_cut.Shape.Solids),
  " top_cut solids:", len(top_cut.Shape.Solids))

# ---------------------------------------------------------------------------
# 2. APPLIANCES: copy each object's original ShapeColor back, keep visible
# ---------------------------------------------------------------------------
APPS = [
    ("_old_fridge.FCStd", "LG_LRMXS2806S/LG_LRMXS2806S.FCStd"),
    ("_old_range.FCStd",  "LRGL5823S/LRGL5823S.FCStd"),
    ("_old_sink.FCStd",   "KWT310-33/KWT310-33.FCStd"),
    ("_old_dw.FCStd",     "WDP540HAMZ/WDP540HAMZ.FCStd"),
]
for old_rel, cur_rel in APPS:
    od = App.openDocument(H + old_rel)
    cmap = {}
    for o in od.Objects:
        if o.TypeId.startswith("Part::") and o.ViewObject is not None:
            cmap[o.Name] = color_of(o)
    App.closeDocument(od.Name)

    d = App.openDocument(LIB + cur_rel)
    applied = 0
    for o in d.Objects:
        if o.TypeId == "App::Part" or o.TypeId.startswith("Part::"):
            show(o, True)
        if o.Name in cmap:
            set_color(o, cmap[o.Name]); applied += 1
    d.save()
    L("appliance %-14s restored %d/%d colors" % (d.Name, applied, len(cmap)))

# ---------------------------------------------------------------------------
# 3. ASSEMBLY: refresh so it re-reads the recut counter; keep links visible
# ---------------------------------------------------------------------------
adoc = App.openDocument(KIT + "Kitchen_Assembly.FCStd")
for o in adoc.Objects:
    if o.TypeId in ("App::Link", "App::Part") or o.TypeId.startswith("Assembly::"):
        show(o, True)
adoc.recompute()
adoc.save()
log.close()
print("FIX_DONE")
