"""Apply colors and save the FCStd. Run with GUI: freecad color_save.py"""
import os, glob
import FreeCAD as App
import FreeCADGui as Gui

OUT = os.path.dirname(os.path.abspath(__file__))
doc = App.openDocument(glob.glob(os.path.join(OUT, "*.FCStd"))[0])
Gui.updateGui()

fabric = (0.80, 0.74, 0.63)   # linen
dark = (0.18, 0.16, 0.14)     # feet
for o in doc.Objects:
    vo = o.ViewObject
    if vo is None:
        continue
    vo.ShapeColor = dark if "leg" in o.Name.lower() else fabric

doc.save()
print("COLOR_DONE")
try:
    Gui.getMainWindow().close()
except Exception:
    pass
