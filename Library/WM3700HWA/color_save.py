"""Apply colors and save the FCStd. Run with the GUI (offscreen):
   flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD color_save.py
"""
import os, glob
import FreeCAD as App
import FreeCADGui as Gui

OUT = os.path.dirname(os.path.abspath(__file__))
doc = App.openDocument(glob.glob(os.path.join(OUT, "*.FCStd"))[0])
Gui.updateGui()

white = (0.96, 0.96, 0.97)   # cabinet / drawer / bezel (white machine)
light = (0.80, 0.82, 0.84)   # bezel ring metal
dark = (0.17, 0.17, 0.19)    # display / dial
glass = (0.10, 0.12, 0.15)   # tinted porthole glass

for o in doc.Objects:
    vo = o.ViewObject
    if vo is None:
        continue
    nm = o.Name.lower()
    if "glass" in nm:
        vo.ShapeColor = glass
    elif "display" in nm or "dial" in nm:
        vo.ShapeColor = dark
    elif "bezel" in nm:
        vo.ShapeColor = light
    else:                      # cabinet, drawer, handle
        vo.ShapeColor = white

doc.save()
print("COLOR_DONE")
try:
    Gui.getMainWindow().close()
except Exception:
    pass
