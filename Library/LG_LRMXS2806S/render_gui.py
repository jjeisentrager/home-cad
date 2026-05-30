"""Open the model in the FreeCAD GUI, apply colors, save a preview PNG.
Run with the GUI binary:  freecad render_gui.py
"""
import os
import FreeCAD as App
import FreeCADGui as Gui

OUT = os.path.dirname(os.path.abspath(__file__))
doc = App.openDocument(os.path.join(OUT, "LG_LRMXS2806S.FCStd"))
Gui.updateGui()

steel = (0.74, 0.76, 0.78)
dark = (0.10, 0.10, 0.11)
for o in doc.Objects:
    vo = o.ViewObject
    if vo is None:
        continue
    n = o.Name.lower()
    vo.ShapeColor = dark if ("handle" in n or "dispenser" in n) else steel

doc.save()  # persist colors into the FCStd

v = Gui.activeDocument().activeView()
v.viewIsometric()
Gui.SendMsgToActiveView("ViewFit")
Gui.updateGui()
v.saveImage(os.path.join(OUT, "preview_iso.png"), 1100, 1500, "White")

v.viewFront()
Gui.SendMsgToActiveView("ViewFit")
Gui.updateGui()
v.saveImage(os.path.join(OUT, "preview_front.png"), 1000, 1500, "White")

print("RENDER_DONE")
try:
    Gui.getMainWindow().close()
except Exception:
    pass
