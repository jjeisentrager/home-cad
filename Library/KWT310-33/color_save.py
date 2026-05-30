"""Apply stainless color and save the FCStd. Run with GUI: freecad color_save.py"""
import os, glob
import FreeCAD as App
import FreeCADGui as Gui

OUT = os.path.dirname(os.path.abspath(__file__))
doc = App.openDocument(glob.glob(os.path.join(OUT, "*.FCStd"))[0])
Gui.updateGui()

steel = (0.75, 0.77, 0.79)
for o in doc.Objects:
    if o.ViewObject is not None:
        o.ViewObject.ShapeColor = steel

doc.save()
print("COLOR_DONE")
try:
    Gui.getMainWindow().close()
except Exception:
    pass
