"""Apply colors and save the FCStd. Run with the GUI: freecad color_save.py"""
import os, glob
import FreeCAD as App
import FreeCADGui as Gui

OUT = os.path.dirname(os.path.abspath(__file__))
doc = App.openDocument(glob.glob(os.path.join(OUT, "*.FCStd"))[0])
Gui.updateGui()

black = (0.11, 0.11, 0.12)        # ThruBlack vinyl
glass = (0.55, 0.66, 0.73)        # glazing
for o in doc.Objects:
    vo = o.ViewObject
    if vo is None:
        continue
    if "glass" in o.Name.lower():
        vo.ShapeColor = glass
        vo.Transparency = 35
    else:
        vo.ShapeColor = black

doc.save()
print("COLOR_DONE")
try:
    Gui.getMainWindow().close()
except Exception:
    pass
