"""Apply ShapeColors and re-save with a valid GuiDocument.
Run OFFSCREEN GUI:  flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD color_save.py
"""
import os, glob
import FreeCAD as App
try:
    import FreeCADGui as Gui
except Exception:
    Gui = None

OUT = os.path.dirname(os.path.abspath(__file__))
doc = App.openDocument(glob.glob(os.path.join(OUT, "*.FCStd"))[0])

WHITE = (0.95, 0.95, 0.93)
DARK = (0.22, 0.22, 0.25)
METAL = (0.60, 0.60, 0.62)


def color_for(name):
    if name.startswith("Box"):
        return DARK
    if name.startswith(("PlateScrew",)):
        return METAL
    return WHITE   # Plate, Recept, StrapFace, Toggle


for o in doc.Objects:
    if getattr(o, "ViewObject", None) is None:
        continue
    if not o.TypeId.startswith("Part::"):
        continue
    o.Visibility = True
    o.ViewObject.Visibility = True
    o.ViewObject.ShapeColor = color_for(o.Name)

doc.save()
print("COLOR_DONE")
