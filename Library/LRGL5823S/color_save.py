"""Apply colors and save the FCStd. Run with GUI: freecad color_save.py"""
import os, glob
import FreeCAD as App
import FreeCADGui as Gui

OUT = os.path.dirname(os.path.abspath(__file__))
doc = App.openDocument(glob.glob(os.path.join(OUT, "*.FCStd"))[0])
Gui.updateGui()

steel = (0.74, 0.76, 0.78)
dark = (0.13, 0.13, 0.15)
DARK_PARTS = ("burner", "grate", "window", "knob", "display", "handle")
for o in doc.Objects:
    vo = o.ViewObject
    if vo is None:
        continue
    nm = o.Name.lower()
    vo.ShapeColor = dark if any(k in nm for k in DARK_PARTS) else steel

doc.save()
print("COLOR_DONE")
try:
    Gui.getMainWindow().close()
except Exception:
    pass
