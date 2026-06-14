# -*- coding: utf-8 -*-
"""In DrainAddOn (copy of DrainLaundry), lengthen the grounded Straight (Pad031)
so that, once placed by the House link M3, the final segment becomes a tall
vertical DROP from the AddOn cabinet (Z~2985) down into the basement (~Z500)
toward the main drain. Headless; GuiDocument re-injected by the shell."""
import os, FreeCAD as App
R = "/home/joee/github/alieniron/home-cad"
d = App.openDocument(os.path.join(R, "Drain/DrainAddOn.FCStd"))
pad = d.getObject("Pad031"); body = pad.InList[0]
# pick the PartDesign::Body parent
body = next((o for o in pad.InList if o.TypeId == "PartDesign::Body"), body)
pad.setExpression('Length', None)
pad.Length = 2485.0
pad.touch(); body.touch()
d.recompute([pad, body], True, True)
d.save()
rep = open(os.path.join(R, "Drain/addon_drop_report.txt"), "w")
rep.write("Pad031.Length=%.1f body=%s bodylen=%.1f\n" % (
    pad.Length.Value, body.Name, body.Shape.BoundBox.XLength))
rep.close()
print("LENGTHEN_DONE")
