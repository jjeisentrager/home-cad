# -*- coding: utf-8 -*-
"""todo#5 + #6: color the AddOn + main framing and the I-beam supports brown wood.
Sets ShapeColor + ShapeAppearance diffuse on every Part:: solid in each source
file so the colour propagates through the assembly links. Run OFFSCREEN GUI.
"""
import os
import FreeCAD as App
try:
    import FreeCADGui as Gui  # noqa
except Exception:
    pass

R = "/home/joee/github/alieniron/home-cad"
BROWN = (0.55, 0.40, 0.24)          # brown wood
BROWN4 = (0.55, 0.40, 0.24, 1.0)
log = open(os.path.join(R, "_recolor_rep.txt"), "w", buffering=1)

FILES = [
    "AddOn/AddOn_Framing.FCStd",
    "Main/MainFraming.FCStd",
    "AddOn/AddOn_Beams.FCStd",
    "Main/MainBeams.FCStd",
    "AddOn/AddOn_RoofFrame.FCStd",   # timber frame -- exposed, so it wants wood
]

for rel in FILES:
    path = os.path.join(R, rel)
    if not os.path.exists(path):
        log.write("MISSING %s\n" % rel)
        continue
    d = App.openDocument(path)
    n = 0
    for o in d.Objects:
        if not o.TypeId.startswith("Part::"):
            continue
        vo = getattr(o, "ViewObject", None)
        if vo is None:
            continue
        o.Visibility = True
        vo.Visibility = True
        try:
            vo.ShapeColor = BROWN
        except Exception:
            pass
        try:
            m = vo.ShapeAppearance[0]
            m.DiffuseColor = BROWN4
            vo.ShapeAppearance = [m]
        except Exception:
            pass
        n += 1
    d.save()
    log.write("%s : colored %d Part objects, GuiUp=%s\n" % (rel, n, App.GuiUp))
    App.closeDocument(d.Name)

log.close()
print("RECOLOR_DONE")
