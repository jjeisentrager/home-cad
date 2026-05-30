"""Apply colors and save the FCStd. Run with the GUI: freecad color_save.py"""
import os, glob
import FreeCAD as App
import FreeCADGui as Gui

OUT = os.path.dirname(os.path.abspath(__file__))
doc = App.openDocument(glob.glob(os.path.join(OUT, "*.FCStd"))[0])
Gui.updateGui()

steel = (0.74, 0.76, 0.78)
dark = (0.17, 0.17, 0.19)
for o in doc.Objects:
    vo = o.ViewObject
    if vo is None:
        continue
    nm = o.Name.lower()
    vo.ShapeColor = dark if ("toe" in nm or "kick" in nm) else steel

doc.save()
print("COLOR_DONE")
try:
    Gui.getMainWindow().close()
except Exception:
    pass
