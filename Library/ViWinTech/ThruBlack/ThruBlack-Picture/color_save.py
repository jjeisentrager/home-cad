"""Apply ThruBlack/glass colors to every size variant under this folder and
resave each .FCStd. Run with the GUI:  freecad color_save.py"""
import os, glob
import FreeCAD as App
import FreeCADGui as Gui

OUT = os.path.dirname(os.path.abspath(__file__))
black = (0.11, 0.11, 0.12)        # ThruBlack vinyl
glass = (0.55, 0.66, 0.73)        # glazing

for fc in sorted(glob.glob(os.path.join(OUT, "**", "*.FCStd"), recursive=True)):
    doc = App.openDocument(fc)
    Gui.updateGui()
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
    App.closeDocument(doc.Name)
    print("colored", os.path.basename(fc))

print("COLOR_DONE")
try:
    Gui.getMainWindow().close()
except Exception:
    pass
