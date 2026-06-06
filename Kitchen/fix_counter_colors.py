# -*- coding: utf-8 -*-
"""Re-apply the kitchen counter colors as fully-OPAQUE materials and refresh
the assembly link.

The previous pass (fix_colors_and_sink.py) wrote the cut features' material
DiffuseColor with an alpha of 0.0 (e.g. CounterTop_Cut = (0,0,0,0.0)).  The
well-behaved island bodies use alpha 1.0.  On a GUI reopen the alpha-0.0
material can be discarded and the feature falls back to default gray -- which
reads as "the counter colors disappeared".  Here we rewrite them with a clean
opaque Material (alpha 1.0, Transparency 0) so they survive reopen, then
re-save the counter + assembly with the GUI layer up so GuiDocument persists.

Run with the GUI layer up (offscreen):
  flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD \
    Kitchen/fix_counter_colors.py
"""
import FreeCAD as App
import FreeCADGui as Gui  # noqa: F401

H = "/home/joee/github/alieniron/home-cad/"
KIT = H + "Kitchen/"
WHITE = (1.0, 1.0, 1.0)
BLACK = (0.0, 0.0, 0.0)
log = open(H + "counter_color_report.txt", "w")
def L(*a): log.write(" ".join(str(x) for x in a) + "\n")

def paint(o, rgb):
    """Set a fully-opaque shape color via both legacy + material APIs."""
    vo = o.ViewObject
    rgba = (rgb[0], rgb[1], rgb[2], 1.0)
    vo.Transparency = 0
    vo.ShapeColor = rgba
    try:
        sa = vo.ShapeAppearance
        m = sa[0]
        m.DiffuseColor = rgba
        try: m.Transparency = 0.0
        except Exception: pass
        vo.ShapeAppearance = [m]
    except Exception as e:
        L("   appearance err", o.Name, e)
    L("painted", o.Name, "->", tuple(round(x, 3) for x in vo.ShapeColor))

def show(o, vis=True):
    o.Visibility = vis
    if o.ViewObject is not None:
        o.ViewObject.Visibility = vis

# --- counter ---------------------------------------------------------------
cd = App.openDocument(KIT + "Kitchen_Counter.FCStd")
targets = {
    "CounterBase_Cut": WHITE,   # L-counter cabinet base
    "CounterTop_Cut":  BLACK,   # L-counter top
    "Body002": WHITE, "Pad003": WHITE,   # island base
    "Body003": BLACK, "Pad004": BLACK,   # island top
}
for nm, rgb in targets.items():
    o = cd.getObject(nm)
    if o:
        paint(o, rgb)
# keep the holed cut features visible, originals hidden
for nm in ("Body", "Pad", "Body001", "Pad002"):
    if cd.getObject(nm):
        show(cd.getObject(nm), False)
for nm in ("CounterBase_Cut", "CounterTop_Cut"):
    if cd.getObject(nm):
        show(cd.getObject(nm), True)
cd.recompute()
cd.save()
L("counter saved")

# --- assembly: refresh links so they re-read the recolored counter ---------
ad = App.openDocument(KIT + "Kitchen_Assembly.FCStd")
for o in ad.Objects:
    if o.TypeId in ("App::Link", "App::Part") or o.TypeId.startswith("Assembly::"):
        show(o, True)
    if o.TypeId == "App::Link":
        o.touch()
ad.recompute()
ad.save()
L("assembly saved")
log.close()
print("COLOR_FIX_DONE")
