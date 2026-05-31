"""Apply framing colors and save the FCStd. Run with GUI: freecad color_save.py

Wood tone for stud-wall parts; off-white for a finished (solid block) wall.
Picks the color by overall thickness so it works in either mode.
"""
import os, glob
import FreeCAD as App
import FreeCADGui as Gui

OUT = os.path.dirname(os.path.abspath(__file__))
doc = App.openDocument(os.path.join(OUT, "AddOn_Framing.FCStd"))
Gui.updateGui()

wood = (0.82, 0.68, 0.45)
drywall = (0.93, 0.93, 0.90)

# A finished wall is one solid block (1 solid); a stud wall is many.
for o in doc.Objects:
    sh = getattr(o, "Shape", None)
    if sh is None or o.ViewObject is None:
        continue
    o.ViewObject.ShapeColor = drywall if len(sh.Solids) <= 1 else wood

doc.save()
print("COLOR_DONE")
try:
    Gui.getMainWindow().close()
except Exception:
    pass
