"""Apply colors and save the FCStd. Run with GUI: freecad color_save.py"""
import os, glob
import FreeCAD as App
import FreeCADGui as Gui

OUT = os.path.dirname(os.path.abspath(__file__))
doc = App.openDocument(glob.glob(os.path.join(OUT, "*.FCStd"))[0])
Gui.updateGui()

steel = (0.75, 0.77, 0.79)
dark = (0.14, 0.14, 0.16)
light = (0.92, 0.91, 0.84)
for o in doc.Objects:
    vo = o.ViewObject
    if vo is None:
        continue
    nm = o.Name.lower()
    if "light" in nm:
        vo.ShapeColor = light
    elif "filter" in nm or "control" in nm:
        vo.ShapeColor = dark
    else:
        vo.ShapeColor = steel

doc.save()
print("COLOR_DONE")
try:
    Gui.getMainWindow().close()
except Exception:
    pass
