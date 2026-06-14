# -*- coding: utf-8 -*-
"""Wrap the dryer (DLGX3701W) and washer (WM3700HWA) loose Part::Feature solids
in an App::Part named 'Part' (idempotent) so they can be linked into an assembly,
matching the convention used by the bath/kitchen library parts. Run OFFSCREEN so
GuiDocument.xml (colors) survive:
  flatpak run --env=QT_QPA_PLATFORM=offscreen org.freecad.FreeCAD wrap_laundry_parts.py
"""
import os, FreeCAD as App
R = "/home/joee/github/alieniron/home-cad"
rep = open(os.path.join(R, "Library/wrap_report.txt"), "w", buffering=1)
def P(*a): rep.write(" ".join(str(x) for x in a) + "\n"); rep.flush()

JOBS = [
    ("Library/DLGX3701W/DLGX3701W.FCStd", "DLGX3701W"),
    ("Library/WM3700HWA/WM3700HWA.FCStd", "WM3700HWA"),
]
for path, label in JOBS:
    d = App.openDocument(os.path.join(R, path))
    part = d.getObject("Part")
    if part is None:
        part = d.addObject("App::Part", "Part")
        part.Label = label
    # move every loose Part::Feature into the Part
    feats = [o for o in d.Objects if o.TypeId == "Part::Feature"]
    moved = 0
    for f in feats:
        if f not in part.Group:
            part.addObject(f)
            moved += 1
    if App.GuiUp and part.ViewObject is not None:
        part.Visibility = True
        part.ViewObject.Visibility = True
        for f in feats:
            if f.ViewObject is not None:
                f.ViewObject.Visibility = True
    d.recompute()
    d.save()
    bb = part.Shape.BoundBox if part.Shape and not part.Shape.isNull() else None
    P("%s: Part=%s label=%s moved=%d children=%d GuiUp=%s bbox=%s" % (
        label, part.Name, part.Label, moved, len(part.Group), App.GuiUp,
        None if bb is None else "X[%.1f,%.1f]Y[%.1f,%.1f]Z[%.1f,%.1f]" % (
            bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax)))
P("DONE"); rep.close(); print("WRAP_DONE")
