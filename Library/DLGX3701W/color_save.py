"""Apply colors and save the FCStd. Run with the GUI (offscreen):
   flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD color_save.py
Saving under the Gui layer keeps a proper GuiDocument.xml (visibility survives)."""
import os, glob
import FreeCAD as App
import FreeCADGui as Gui

OUT = os.path.dirname(os.path.abspath(__file__))
doc = App.openDocument(glob.glob(os.path.join(OUT, "*.FCStd"))[0])
Gui.updateGui()

white = (0.95, 0.95, 0.96)   # DLGX3701W white cabinet / door ring
dark = (0.13, 0.13, 0.15)    # glass, display, handle, feet


def is_dark(nm):
    return any(k in nm for k in ("glass", "display", "handle", "foot", "window"))


for o in doc.Objects:
    vo = o.ViewObject
    if vo is None:
        continue
    nm = o.Name.lower()
    vo.ShapeColor = dark if is_dark(nm) else white
    vo.Visibility = True

doc.save()
print("COLOR_DONE")
try:
    Gui.getMainWindow().close()
except Exception:
    pass
